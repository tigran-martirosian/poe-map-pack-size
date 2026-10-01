from pack_size import mods

IIQ = "13% increased Quantity of Items found in this Area"
IIR = "8% increased Rarity of Items found in this Area"


def mod(name, pack_size, *lines):
    shared = [IIQ, IIR, f"{pack_size}% increased Pack size"]
    return {"id": name, "name": name, "kind": "prefix", "pack_size": pack_size, "stat_lines": shared + list(lines)}


# a few entries as the wiki lists them
MODS = [
    mod("Fecund", 5, "(30-39)% more Monster Life"),
    mod("Twinned", 7, "Area contains two Unique Bosses"),
    mod("of Giants", 5, "Monsters have 70% increased Area of Effect"),
    mod("Abhorrent", 6, "Area is inhabited by Abominations"),
    mod("of Stasis", 6, "Players cannot Regenerate Life, Mana or Energy Shield"),
    mod("of Stasis", 12, "Players cannot Regenerate Life, Mana or Energy Shield"),
    mod("Hexed", 6, "Monsters are Hexproof", "Monsters have 20% increased Speed"),
    mod("Sturdy", 4, "Monsters are Hexproof"),
]

PLAIN_COPY = """Item Class: Maps
Rarity: Rare
Dread Maze
Strand Map
--------
Map Tier: 14
Item Quantity: +62% (augmented)
--------
Item Level: 83
--------
Monster Level: 83
--------
35% more Monster Life
Area contains two Unique Bosses
Monsters have 70% increased Area of Effect
5% increased Pack size
7% increased Pack size
5% increased Pack size
Players cannot be frozen by anything
--------
Travel to this Map by using it in a personal Map Device.
"""

ADVANCED_COPY = """Item Class: Maps
Rarity: Rare
Dread Maze
Strand Map
--------
Map Tier: 14
--------
Item Level: 83
--------
{ Prefix Modifier "Fecund" (Tier: 2) — Monster }
35(30-39)% more Monster Life
5% increased Pack size
13% increased Quantity of Items found in this Area — Unscalable Value

{ Prefix Modifier "Twinned" (Tier: 1) }
Area contains two Unique Bosses
7% increased Pack size

{ Suffix Modifier "of Giants" (Tier: 2) — Monster }
Monsters have 70% increased Area of Effect
5% increased Pack size

{ Suffix Modifier "of Pain" (Tier: 1) }
Players take 5% more damage
--------
Travel to this Map by using it in a personal Map Device.
"""


def names(matches):
    return sorted(matches)


def test_numbers_and_ranges_are_wildcards():
    assert mods.normalise("(30-39)% more Monster Life") == mods.normalise("35% more Monster Life")
    assert mods.normalise("35(30-39)% more Monster Life") == mods.normalise("(30-39)% more Monster Life")
    assert mods.normalise("Players have -12% to all maximum Resistances") == \
        mods.normalise("Players have (-12--9)% to all maximum Resistances")


def test_plain_copy_matches_stat_lines():
    found = mods.match(PLAIN_COPY, MODS)
    assert names(found) == [("Fecund", 5), ("Twinned", 7), ("of Giants", 5)]


def test_advanced_copy_matches_by_name():
    found = mods.match(ADVANCED_COPY, MODS)
    assert names(found) == [("Fecund", 5), ("Twinned", 7), ("of Giants", 5)]


def test_name_is_preferred_when_the_wording_is_unknown():
    text = '{ Prefix Modifier "Abhorrent" (Tier: 1) }\nSome new wording the wiki does not have yet\n6% increased Pack size\n'
    assert mods.match(text, MODS) == [("Abhorrent", 6)]


def test_modifier_is_not_counted_twice():
    assert len(mods.match(ADVANCED_COPY + "\n" + ADVANCED_COPY, MODS)) == 3
    # named in a header and also listed as a plain line
    both = ADVANCED_COPY + "Area contains two Unique Bosses\n"
    assert names(mods.match(both, MODS)) == [("Fecund", 5), ("Twinned", 7), ("of Giants", 5)]
    # two lines that fit the same modifier
    assert mods.match("Area is inhabited by Abominations\nArea is inhabited by Abominations\n", MODS) == [("Abhorrent", 6)]


def test_a_line_belongs_to_one_modifier_only():
    # "Hexed" needs two lines and takes the Hexproof line first, so "Sturdy" is not counted too
    text = "Monsters are Hexproof\nMonsters have 20% increased Speed\n"
    assert mods.match(text, MODS) == [("Hexed", 6)]
    assert mods.match("Monsters are Hexproof\n", MODS) == [("Sturdy", 4)]


def test_unknown_lines_are_ignored():
    assert mods.match("Item Class: Maps\nSomething nobody has heard of\n", MODS) == []
    assert mods.match("", MODS) == []


def test_same_name_different_value_follows_the_items_pack_size_line():
    line = "Players cannot Regenerate Life, Mana or Energy Shield\n"
    assert mods.match(line + "12% increased Pack size\n", MODS) == [("of Stasis", 12)]
    assert mods.match(line + "6% increased Pack size\n", MODS) == [("of Stasis", 6)]
    assert mods.match(line, MODS) == [("of Stasis", 6)]


def test_shipped_snapshot_loads():
    data = mods.load()
    assert len(data) > 100
    assert {"id", "name", "kind", "stat_lines", "pack_size"} <= set(data[0])
