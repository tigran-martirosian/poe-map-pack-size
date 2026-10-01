import json
from pathlib import Path

import pytest

from pack_size import wiki

PAGES = json.loads((Path(__file__).parent / "sample_pages.json").read_text(encoding="utf-8"))


def fake_fetch(pages, urls):
    pages = iter(pages)

    def fetch(url):
        urls.append(url)
        return next(pages)

    return fetch


def test_fetch_rows_pages_until_an_empty_page():
    urls, pauses = [], []
    rows = wiki.fetch_rows(fake_fetch(PAGES, urls), pauses.append)
    assert [r["mod_id"] for r in rows] == ["TestModB", "TestModA", "TestModC"]
    assert [u.split("offset=")[1] for u in urls] == ["0", "2", "3"]
    assert all("limit=500" in u for u in urls)
    assert pauses == [wiki.PAUSE_SECONDS, wiki.PAUSE_SECONDS]


def test_url_asks_for_map_pack_size_prefixes_and_suffixes():
    url = wiki.build_url(0)
    assert "mods.domain%3D5" in url
    assert "IN+%281%2C2%29" in url
    assert "map_pack_size_%2B%25" in url


def test_parse_row_cleans_wiki_markup():
    mod = wiki.parse_row(PAGES[0]["cargoquery"][0]["title"])
    assert mod["kind"] == "suffix"
    assert mod["pack_size"] == 5
    assert mod["stat_lines"] == [
        "13% increased Quantity of Items found in this Area",
        "5% increased Pack size",
        "Monsters have 30% increased Speed",
    ]


def test_parse_row_keeps_apostrophes_and_ranges():
    mod = wiki.parse_row(PAGES[0]["cargoquery"][1]["title"])
    assert mod["name"] == "Kira's"
    assert (mod["pack_size"], mod["pack_size_max"]) == (30, 60)


def test_update_writes_a_sorted_snapshot(tmp_path):
    path = tmp_path / "data" / "map_mods.json"
    count = wiki.update(path, fake_fetch(PAGES, []), lambda seconds: None)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert count == 3
    assert [m["name"] for m in data["mods"]] == ["Kira's", "Mighty", "Zealous"]
    assert data["source"] == wiki.SOURCE_URL
    assert data["fetched"]


def test_update_keeps_the_old_file_when_nothing_comes_back(tmp_path):
    path = tmp_path / "map_mods.json"
    path.write_text("old", encoding="utf-8")
    with pytest.raises(RuntimeError):
        wiki.update(path, fake_fetch([{"cargoquery": []}], []), lambda seconds: None)
    assert path.read_text(encoding="utf-8") == "old"


def test_api_error_is_reported():
    with pytest.raises(RuntimeError, match="bad query"):
        wiki.fetch_rows(lambda url: {"error": {"info": "bad query"}}, lambda seconds: None)
