from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "map_mods.json"

# Effect of map modifiers with my Atlas passive tree: 78% increased effect.
ATLAS_MULTIPLIER = 1.78
# Range I rate a roll against, for an 8-modifier map at 1.78.
# 56 is the lowest possible total: 8 x floor(4 x 1.78).
ROLL_MIN = 56
ROLL_MAX = 86

HOTKEY = "j"
POPUP_SECONDS = 20
