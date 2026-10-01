import json
import re
from collections import Counter

from . import settings

# a number, a range like (20-29), or a rolled value with its range like 27(20-29)
NUMBER = re.compile(
    r"[+-]?\d+(?:\.\d+)?\([^)]*\)"
    r"|[+-]?\(?[+-]?\d+(?:\.\d+)?(?:\s*[-–]+\s*[+-]?\d+(?:\.\d+)?)?\)?"
)
SHARED = re.compile(r"#% increased (?:quantity of items found in this area|rarity of items found in this area|pack size)")
HEADER = re.compile(r'^\{\s*(?:Prefix|Suffix) Modifier "([^"]+)"')
PACK_LINE = re.compile(r"(\d+(?:\.\d+)?)% increased pack size", re.IGNORECASE)


def load(path=settings.DATA_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["mods"]


def normalise(line):
    return re.sub(r"\s+", " ", NUMBER.sub("#", line)).strip().lower()


def signature(mod):
    # the lines that identify a mod; every map mod also carries the shared quantity, rarity and pack size lines
    lines = (normalise(line) for line in mod["stat_lines"])
    return tuple(line for line in lines if not SHARED.fullmatch(line))


def split_item(text):
    """Returns the modifiers the advanced copy names, with their lines, and all other lines."""
    named, loose, block = [], [], None
    for line in text.splitlines():
        line = line.split(" — ")[0].strip()
        if not line:
            continue
        header = HEADER.match(line)
        if header:
            block = []
            named.append((header.group(1), block))
        elif line.startswith("{") or line.startswith("--"):
            block = None
        else:
            (loose if block is None else block).append(line)
    return named, loose


def pack_values(lines):
    return {float(v) for v in PACK_LINE.findall("\n".join(lines))}


def pick_value(variants, seen_on_item):
    # same name, different pack size: prefer the one the item's own pack size line shows
    values = sorted({v["pack_size"] for v in variants})
    return ([v for v in values if v in seen_on_item] or values)[0]


def match(text, mods):
    """Returns a list of (modifier name, pack size), each modifier at most once."""
    by_name = {}
    for mod in mods:
        by_name.setdefault(mod["name"], []).append(mod)

    named, loose = split_item(text)
    found = {}
    for name, lines in named:
        variants = by_name.get(name)
        if not variants:
            loose += lines
            continue
        wanted = {normalise(line) for line in lines}
        fits = [v for v in variants if set(signature(v)) <= wanted] or variants
        found.setdefault(name, pick_value(fits, pack_values(lines)))

    available = Counter(normalise(line) for line in loose)
    seen = pack_values(loose)
    longest = lambda variants: max(len(signature(v)) for v in variants)
    for name, variants in sorted(by_name.items(), key=lambda item: -longest(item[1])):
        if name in found:
            continue
        fits = [v for v in variants if signature(v) and not Counter(signature(v)) - available]
        if fits:
            available -= Counter(signature(max(fits, key=lambda v: len(signature(v)))))
            found[name] = pick_value(fits, seen)
    return list(found.items())
