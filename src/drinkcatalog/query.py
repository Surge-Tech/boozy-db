from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Optional

from drinkcatalog.models import Recipe
from drinkcatalog.util import slugify


@dataclass(frozen=True)
class Query:
    q: Optional[str] = None
    spirit: Optional[str] = None
    tag: Optional[str] = None
    ingredient: Optional[str] = None
    method: Optional[str] = None


def _matches_text(recipe: Recipe, q: str) -> bool:
    qn = slugify(q)
    if qn in slugify(recipe.name):
        return True
    if recipe.description and qn in slugify(recipe.description):
        return True
    if any(qn in slugify(t) for t in recipe.tags):
        return True
    if any(qn in slugify(s) for s in recipe.base_spirits):
        return True
    if any(qn in slugify(ing.item) for ing in recipe.ingredients):
        return True
    return False


def filter_recipes(recipes: Iterable[Recipe], query: Query) -> list[Recipe]:
    out: list[Recipe] = []
    for r in recipes:
        if query.q and not _matches_text(r, query.q):
            continue
        if query.spirit and query.spirit.strip().lower() not in r.base_spirits:
            continue
        if query.tag and query.tag.strip().lower() not in r.tags:
            continue
        if query.method and (r.method or "").lower() != query.method.strip().lower():
            continue
        if query.ingredient:
            needle = slugify(query.ingredient)
            if not any(needle in slugify(ing.item) for ing in r.ingredients):
                continue
        out.append(r)
    return out


def sort_recipes(recipes: list[Recipe], sort: str) -> list[Recipe]:
    sort = (sort or "name").strip().lower()
    if sort == "name":
        return sorted(recipes, key=lambda r: slugify(r.name))
    if sort in ("updated", "updated_at", "recent"):
        return sorted(recipes, key=lambda r: r.parsed_updated_at(), reverse=True)
    if sort == "random":
        recipes = list(recipes)
        random.shuffle(recipes)
        return recipes
    return sorted(recipes, key=lambda r: slugify(r.name))
