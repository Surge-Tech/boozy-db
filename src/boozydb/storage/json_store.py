from __future__ import annotations

import os
import sys

import json
from pathlib import Path
from typing import Optional

from boozydb.models import Recipe
from boozydb.storage.base import Store, StoreConfig


class JsonStore(Store):
    def __init__(self, cfg: StoreConfig):
        self.cfg = cfg
        self.cfg.recipes_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, recipe_id: str) -> Path:
        return self.cfg.recipes_dir / f"{recipe_id}.json"

    def list(self) -> list[Recipe]:
        recipes: list[Recipe] = []
        debug = os.getenv("BOOZYDB_DEBUG", "").strip() == "1"
        for p in sorted(self.cfg.recipes_dir.glob("*.json")):
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                recipes.append(Recipe.model_validate(obj))
            except Exception as e:
                if debug:
                    print(f"[boozydb] Skipping invalid recipe file: {p} ({e})", file = sys.stderr)
                continue
        return recipes

    def get(self, recipe_id: str) -> Optional[Recipe]:
        p = self._path_for(recipe_id)
        if not p.exists():
            return None
        obj = json.loads(p.read_text(encoding="utf-8"))
        return Recipe.model_validate(obj)

    def save(self, recipe: Recipe) -> None:
        recipe.touch()
        p = self._path_for(recipe.id)
        p.write_text(json.dumps(recipe.model_dump(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def delete(self, recipe_id: str) -> bool:
        p = self._path_for(recipe_id)
        if p.exists():
            p.unlink()
            return True
        return False
