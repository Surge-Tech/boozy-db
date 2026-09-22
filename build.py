#!/usr/bin/env python3
"""Build script: reads data/recipes/*.json and writes docs/recipes.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
RECIPES_DIR = ROOT / "data" / "recipes"
DOCS_DIR = ROOT / "docs"

GLASS_ALIASES = {"tall": "highball", "martini glass": "martini", "irish coffee glass": "mug"}


def normalize_glass(glass: str) -> str:
    s = glass.strip().lower()
    return GLASS_ALIASES.get(s, s)


def load_recipe(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "glass" in data:
            data["glass"] = normalize_glass(data["glass"])
        return data
    except Exception as exc:
        print(f"  skip {path.name}: {exc}", file=sys.stderr)
        return None


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)

    recipes = []
    for f in sorted(RECIPES_DIR.glob("*.json")):
        if f.name.startswith("!"):
            continue
        r = load_recipe(f)
        if r is not None:
            recipes.append(r)

    recipes.sort(key=lambda r: r.get("name", "").lower())

    out = DOCS_DIR / "recipes.json"
    out.write_text(json.dumps(recipes, ensure_ascii=False, indent=None), encoding="utf-8")
    print(f"Wrote {len(recipes)} recipes -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
