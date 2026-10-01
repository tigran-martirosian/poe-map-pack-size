import argparse

from . import wiki


def main():
    parser = argparse.ArgumentParser(prog="pack_size", description="Pack size calculator for map modifiers.")
    parser.add_argument("command", nargs="?", choices=["update"],
                        help="'update' downloads the modifier list from the wiki; no argument starts the tool")
    args = parser.parse_args()

    if args.command == "update":
        print(f"Saved {wiki.update()} modifiers.")
    else:
        from . import app  # imported here so 'update' works without the keyboard libraries
        app.run()


main()
