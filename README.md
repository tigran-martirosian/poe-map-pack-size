# Map Pack Size Calculator

I played Path of Exile and wanted to see a map's pack size right away instead of adding up its modifiers by hand. I wrote the first version in November 2024 as a small script and shared it with other players.

You hover over a map item in the game and press a hotkey. A small window shows the total pack size of the map's modifiers and how good the roll is.

## How it works

- The tool presses Ctrl+Alt+C for you (the game's "copy advanced item text") and reads the clipboard.
- It matches the map's modifiers against the modifier list from the [Path of Exile wiki](https://www.poewiki.net/wiki/List_of_map_mods), which is saved in `data/map_mods.json`. A modifier is counted once.
- Each modifier adds `floor(pack size * multiplier)`. The multiplier comes from the Atlas passive tree: 78% increased effect gives 1.78. The tool asks for your percentage the first time you press the hotkey.
- The window shows the total, one line per modifier, and how good the roll is within the range 56 to 86. That's the range for an 8-modifier map with my Atlas setup.

The code is in `pack_size/`: `wiki.py` downloads the list, `mods.py` matches item text to modifiers, `calc.py` holds the maths and `app.py` is the hotkey and the tkinter window.

## Run

Windows, Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pack_size
```

Press `j` with the map under the mouse in the game. The hotkey is global, so any `j` you type in any program triggers it. `python -m pack_size update` downloads the modifier list again.

## Test

```
pytest
```

The tests use made-up item texts and a small saved API response and make no network calls.

## Limitations

- Windows only. It uses `pynput` for the hotkey and `pyperclip` for the clipboard.
- The numbers are only as good as the wiki for the current game version. Where the wiki lists a modifier several times with different pack sizes, the tool takes the one shown on the item, or else the lowest.
- The tests use item texts I wrote by hand. The matching hasn't been re-checked against text copied from the game since I moved to the wiki data.
- The roll rating is fixed for 78%. With another Atlas percentage the total is right, but the rating isn't.

## Data licence

The modifier data comes from the Path of Exile Wiki and is available under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). The data file is derived from it and carries the same licence. This is a fan tool and is not affiliated with Grinding Gear Games.
