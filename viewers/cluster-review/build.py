"""Package the dependency-free Cluster Review board. Run from any directory; --check detects drift."""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent
DEST = ROOT / "plugins/aipos/skills/aipos-problem-clustering/scripts/assets"


def assets() -> dict:
    app = (SOURCE / "app.mjs").read_text(encoding="utf-8")
    first, rest = app.split("\n", 1)
    if not first.startswith("import ") or "from './model.mjs';" not in first:
        raise SystemExit("Unexpected app import; update the dependency-free build.")
    return {"template.html": (SOURCE / "template.html").read_text(encoding="utf-8"),
            "style.css": (SOURCE / "style.css").read_text(encoding="utf-8"),
            "board.mjs": (SOURCE / "model.mjs").read_text(encoding="utf-8") + "\n" + rest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, text in assets().items():
        dest = DEST / name
        if args.check:
            if not dest.exists() or dest.read_text(encoding="utf-8") != text:
                raise SystemExit(f"Stale packaged board asset: {name}")
        else:
            DEST.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
    print("Cluster Review assets match source." if args.check else "Packaged three Cluster Review assets.")


if __name__ == "__main__":
    main()
