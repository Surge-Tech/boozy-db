from __future__ import annotations

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from boozydb.models import Ingredient, Recipe

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_recipe(**kwargs: object) -> Recipe:
    defaults: dict[str, object] = {"name": "Test Recipe"}
    defaults.update(kwargs)
    return Recipe(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------------

class TestIngredient:
    def test_minimal(self) -> None:
        ing = Ingredient(item="lime juice")
        assert ing.item == "lime juice"
        assert ing.amount == ""
        assert ing.unit == ""

    def test_full(self) -> None:
        ing = Ingredient(item="gin", amount="2", unit="oz")
        assert ing.item == "gin"
        assert ing.amount == "2"
        assert ing.unit == "oz"

    def test_item_strips_whitespace(self) -> None:
        ing = Ingredient(item="  lime juice  ")
        assert ing.item == "lime juice"

    def test_item_empty_raises(self) -> None:
        with pytest.raises(ValidationError):
            Ingredient(item="")

    def test_item_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError):
            Ingredient(item="   ")

    def test_amount_is_string(self) -> None:
        ing = Ingredient(item="gin", amount="2.5")
        assert isinstance(ing.amount, str)
        assert ing.amount == "2.5"

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            Ingredient(item="gin", unknown_field="x")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Recipe — basic construction
# ---------------------------------------------------------------------------

class TestRecipeBasic:
    def test_minimal(self) -> None:
        r = make_recipe()
        assert r.name == "Test Recipe"
        assert r.ingredients == []
        assert r.instructions == []
        assert r.glass == ""
        assert r.tags == []
        assert r.spirit is None
        assert r.servings == 1 if hasattr(r, "servings") else True  # field absent is fine

    def test_id_is_uuid(self) -> None:
        r = make_recipe()
        assert isinstance(r.id, UUID)

    def test_created_at_is_datetime(self) -> None:
        r = make_recipe()
        assert isinstance(r.created_at, datetime)
        assert r.created_at.tzinfo is not None

    def test_extra_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            Recipe(name="x", bogus=True)  # type: ignore[call-arg]

    def test_name_empty_raises(self) -> None:
        with pytest.raises(ValidationError):
            make_recipe(name="")

    def test_name_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError):
            make_recipe(name="   ")


# ---------------------------------------------------------------------------
# Recipe — name normalization (title case)
# ---------------------------------------------------------------------------

class TestRecipeNameTitleCase:
    def test_lowercase_to_title(self) -> None:
        r = make_recipe(name="negroni")
        assert r.name == "Negroni"

    def test_uppercase_to_title(self) -> None:
        r = make_recipe(name="OLD FASHIONED")
        assert r.name == "Old Fashioned"

    def test_mixed_to_title(self) -> None:
        r = make_recipe(name="margarita-strawberry")
        assert r.name == "Margarita-Strawberry"

    def test_strips_whitespace_before_title(self) -> None:
        r = make_recipe(name="  martini  ")
        assert r.name == "Martini"

    def test_already_title_unchanged(self) -> None:
        r = make_recipe(name="Blue Hawaii")
        assert r.name == "Blue Hawaii"


# ---------------------------------------------------------------------------
# Recipe — tags validator
# ---------------------------------------------------------------------------

class TestRecipeTags:
    def test_lowercased(self) -> None:
        r = make_recipe(tags=["Classic", "SWEET"])
        assert "classic" in r.tags
        assert "sweet" in r.tags

    def test_sorted(self) -> None:
        r = make_recipe(tags=["sweet", "classic"])
        assert r.tags == ["classic", "sweet"]

    def test_deduplicated(self) -> None:
        r = make_recipe(tags=["classic", "Classic", "CLASSIC"])
        assert r.tags == ["classic"]

    def test_none_becomes_empty_list(self) -> None:
        r = make_recipe(tags=None)
        assert r.tags == []

    def test_empty_strings_removed(self) -> None:
        r = make_recipe(tags=["", "classic", "  "])
        assert r.tags == ["classic"]


# ---------------------------------------------------------------------------
# Recipe — spirit validator
# ---------------------------------------------------------------------------

class TestRecipeSpirit:
    def test_lowercased(self) -> None:
        r = make_recipe(spirit="GIN")
        assert r.spirit == "gin"

    def test_strips_whitespace(self) -> None:
        r = make_recipe(spirit="  rum  ")
        assert r.spirit == "rum"

    def test_none_stays_none(self) -> None:
        r = make_recipe(spirit=None)
        assert r.spirit is None

    def test_empty_string_becomes_none(self) -> None:
        r = make_recipe(spirit="")
        assert r.spirit is None

    def test_whitespace_only_becomes_none(self) -> None:
        r = make_recipe(spirit="   ")
        assert r.spirit is None


# ---------------------------------------------------------------------------
# Recipe.new()
# ---------------------------------------------------------------------------

class TestRecipeNew:
    def test_generates_uuid(self) -> None:
        r = Recipe.new("Martini")
        assert isinstance(r.id, UUID)

    def test_two_new_have_different_ids(self) -> None:
        assert Recipe.new("A").id != Recipe.new("A").id

    def test_applies_name_normalization(self) -> None:
        r = Recipe.new("old fashioned")
        assert r.name == "Old Fashioned"

    def test_accepts_kwargs(self) -> None:
        r = Recipe.new("Negroni", spirit="gin", glass="rocks")
        assert r.spirit == "gin"
        assert r.glass == "rocks"

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises((ValidationError, TypeError)):
            Recipe.new("")  # empty name should fail


# ---------------------------------------------------------------------------
# Recipe — source field
# ---------------------------------------------------------------------------

class TestRecipeSource:
    def test_none_default(self) -> None:
        r = make_recipe()
        assert r.source is None

    def test_value_stored(self) -> None:
        r = make_recipe(source="Harry Craddock, 1930")
        assert r.source == "Harry Craddock, 1930"

    def test_empty_string_becomes_none(self) -> None:
        r = make_recipe(source="")
        assert r.source is None

    def test_whitespace_only_becomes_none(self) -> None:
        r = make_recipe(source="   ")
        assert r.source is None

    def test_strips_whitespace(self) -> None:
        r = make_recipe(source="  IBA Official  ")
        assert r.source == "IBA Official"


# ---------------------------------------------------------------------------
# Recipe — glass normalization
# ---------------------------------------------------------------------------

class TestRecipeGlass:
    def test_lowercased(self) -> None:
        r = make_recipe(glass="Rocks")
        assert r.glass == "rocks"

    def test_strips_whitespace(self) -> None:
        r = make_recipe(glass="  coupe  ")
        assert r.glass == "coupe"

    def test_alias_tall_becomes_highball(self) -> None:
        r = make_recipe(glass="tall")
        assert r.glass == "highball"

    def test_alias_martini_glass_becomes_martini(self) -> None:
        r = make_recipe(glass="martini glass")
        assert r.glass == "martini"

    def test_alias_irish_coffee_glass_becomes_mug(self) -> None:
        r = make_recipe(glass="Irish coffee glass")
        assert r.glass == "mug"

    def test_unknown_glass_preserved(self) -> None:
        r = make_recipe(glass="snifter")
        assert r.glass == "snifter"
