from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

from boozydb.models import Recipe


class Store(Protocol):
    def list(self) -> list[Recipe]: ...
    def get(self, recipe_id: str) -> Optional[Recipe]: ...
    def save(self, recipe: Recipe) -> None: ...
    def delete(self, recipe_id: str) -> bool: ...


@dataclass(frozen=True)
class StoreConfig:
    data_dir: Path

    @property
    def recipes_dir(self) -> Path:
        return self.data_dir / "recipes"

    @property
    def images_dir(self) -> Path:
        return self.data_dir / "images"
