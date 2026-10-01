import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date

from . import settings

API_URL = "https://www.poewiki.net/w/api.php"
SOURCE_URL = "https://www.poewiki.net/wiki/List_of_map_mods"
USER_AGENT = "poe-map-pack-size (student project, reads map modifier data from the wiki API)"
PAGE_SIZE = 500
PAUSE_SECONDS = 1.0
KINDS = {"1": "prefix", "2": "suffix"}


def build_url(offset):
    params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "mods,mod_stats",
        "join_on": "mods._pageID=mod_stats._pageID",
        "fields": "mods.id=mod_id,mods.name=name,mods.stat_text=stat_text,"
                  "mods.generation_type=generation_type,mod_stats.min=min,mod_stats.max=max",
        # domain 5 is map mods; generation type 1 is prefix, 2 is suffix
        "where": 'mods.domain=5 AND mods.generation_type IN (1,2) AND mod_stats.id="map_pack_size_+%"',
        "limit": PAGE_SIZE,
        "offset": offset,
    }
    return API_URL + "?" + urllib.parse.urlencode(params)


def get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_rows(fetch=get_json, sleep=time.sleep):
    rows = []
    while True:
        data = fetch(build_url(len(rows)))
        if "error" in data:
            raise RuntimeError(data["error"].get("info", "the wiki API returned an error"))
        page = [item["title"] for item in data["cargoquery"]]
        if not page:
            return rows
        rows += page
        sleep(PAUSE_SECONDS)


def clean_lines(text):
    # the API sends the stat text as wiki markup with <br> between lines
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"</?span[^>]*>", "", text)
    return [line.strip() for line in text.split("\n") if line.strip()]


def number(text):
    value = float(text)
    return int(value) if value.is_integer() else value


def parse_row(row):
    return {
        "id": row["mod_id"],
        "name": html.unescape(row["name"]),
        "kind": KINDS[row["generation_type"]],
        "stat_lines": clean_lines(row["stat_text"]),
        "pack_size": number(row["min"]),
        "pack_size_max": number(row["max"]),
    }


def update(path=settings.DATA_FILE, fetch=get_json, sleep=time.sleep):
    rows = fetch_rows(fetch, sleep)
    if not rows:
        raise RuntimeError("the wiki returned no modifiers, so the data file was left as it was")
    mods = sorted((parse_row(row) for row in rows), key=lambda m: (m["name"], m["id"]))
    data = {
        "source": SOURCE_URL,
        "license": "CC BY-NC-SA 3.0, https://www.poewiki.net/wiki/Path_of_Exile_Wiki:Copyrights",
        "fetched": date.today().isoformat(),
        "mods": mods,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(mods)
