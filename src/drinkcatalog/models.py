from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item: str = Field(..., description="Canonical ingredient name (e.g., 'lime juice').")
    amount: Optional[float] = Field(None, description="Numeric amount if applicable.")
    unit: Optional[str] = Field(None, description="Unit, e.g. oz, ml, dash, tsp, parts.")
    prep: Optional[str] = Field(None, description="Preparation note, e.g. 'freshly squeezed'.")
    optional: bool = Field(False, description="Whether the ingredient is optional.")

    @field_validator("item")
    @classmethod
    def _item_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("ingredient.item must be non-empty")
        return v

    @field_validator("unit")
    @classmethod
    def _unit_normalize(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip().lower()
        return v or None


class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: Optional[str] = None

    base_spirits: List[str] = Field(default_factory=list, description="Lowercase spirit categories.")
    tags: List[str] = Field(default_factory=list, description="Lowercase tags.")
    method: Optional[str] = None
    glassware: Optional[str] = None
    ice: Optional[str] = None
    garnish: List[str] = Field(default_factory=list)

    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)

    notes: Optional[str] = None
    source: Optional[str] = None
    image: Optional[str] = None  # relative path string

    servings: int = 1
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)

    @field_validator("name")
    @classmethod
    def _name_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("recipe.name must be non-empty")
        return v

    @field_validator("base_spirits", "tags", mode="before")
    @classmethod
    def _normalize_str_list(cls, v):
        if v is None:
            return []
        return v

    @field_validator("base_spirits")
    @classmethod
    def _base_spirits_lower(cls, v: List[str]) -> List[str]:
        out = []
        for s in v:
            s2 = s.strip().lower()
            if s2:
                out.append(s2)
        return sorted(set(out))

    @field_validator("tags")
    @classmethod
    def _tags_lower(cls, v: List[str]) -> List[str]:
        out = []
        for t in v:
            t2 = t.strip().lower()
            if t2:
                out.append(t2)
        return sorted(set(out))

    @field_validator("method")
    @classmethod
    def _method_lower(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip().lower()
        return v or None

    @field_validator("garnish", mode="before")
    @classmethod
    def _garnish_default(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]
        return v

    @field_validator("garnish")
    @classmethod
    def _garnish_clean(cls, v: List[str]) -> List[str]:
        out = []
        for g in v:
            g2 = g.strip()
            if g2:
                out.append(g2)
        return out

    @classmethod
    def new(cls, name: str, **kwargs) -> "Recipe":
        import uuid
        rid = kwargs.pop("id", None) or str(uuid.uuid4())
        now = utc_now_iso()
        return cls(id=rid, name=name, created_at=now, updated_at=now, **kwargs)

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def parsed_updated_at(self) -> datetime:
        return datetime.fromisoformat(self.updated_at.replace("Z", "+00:00"))
