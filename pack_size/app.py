import time
import tkinter as tk

import pyperclip
from pynput import keyboard
from pynput.keyboard import Controller, Key

from . import calc, mods, settings

multiplier = None   # asked once, then kept
known_mods = []


def ask_multiplier():
    global multiplier
    if multiplier is not None:
        return multiplier

    window = tk.Tk()
    window.title("Atlas Percentage Increase")
    tk.Label(window, text="Input your Atlas' percentage increase for explicit map modifiers "
                          "(e.g., 78 for 1.78):").pack(pady=10)
    entry = tk.Entry(window)
    entry.insert(0, f"{round((settings.ATLAS_MULTIPLIER - 1) * 100):g}")
    entry.pack(pady=5)
    error = tk.Label(window, text="", fg="red")
    error.pack()

    def submit():
        global multiplier
        try:
            multiplier = calc.multiplier_from_percent(float(entry.get()))
        except ValueError:
            error.config(text="Please enter a valid number!")
            return
        window.destroy()

    tk.Button(window, text="Submit", command=submit).pack(pady=10)
    window.eval(f"tk::PlaceWindow {window.winfo_toplevel()} center")
    window.mainloop()
    return multiplier


def show_popup(text):
    window = tk.Tk()
    window.title("Pack Size Result")
    box = tk.Text(window, wrap="word", padx=20, pady=20)
    box.insert("1.0", text)
    box.configure(state="disabled")
    box.pack()
    tk.Button(window, text="OK", command=window.destroy).pack(pady=10)
    window.eval(f"tk::PlaceWindow {window.winfo_toplevel()} center")
    window.after(settings.POPUP_SECONDS * 1000, window.destroy)
    window.mainloop()


def copy_item_text():
    # Ctrl+Alt+C is the game's "copy advanced item text"
    controller = Controller()
    for key in (Key.alt, Key.ctrl, "c"):
        controller.press(key)
    time.sleep(0.1)
    for key in ("c", Key.ctrl, Key.alt):
        controller.release(key)
    time.sleep(0.3)  # let the clipboard update


def on_trigger():
    pyperclip.copy("")  # so an earlier copy is not read as the item
    copy_item_text()
    text = pyperclip.paste().strip()
    if not text:
        show_popup("No item text copied. Hover over a map and press the key again.")
        return

    mult = ask_multiplier()
    if mult is None:  # the prompt was closed
        return
    matches = mods.match(text, known_mods)
    if not matches:
        show_popup("No known map modifiers found.")
        return
    total, details = calc.calculate(matches, mult)
    percent = calc.roll_percent(total, settings.ROLL_MIN, settings.ROLL_MAX)
    show_popup(f"Calculated Pack Size: {total}/{settings.ROLL_MAX} ({percent}% roll)\n\nDetails:\n"
               + "\n".join(details))


def on_press(key):
    if key == keyboard.KeyCode.from_char(settings.HOTKEY):
        on_trigger()


def run():
    global known_mods
    known_mods = mods.load()
    print(f"Loaded {len(known_mods)} modifiers. Press '{settings.HOTKEY}' to calculate.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
