from __future__ import annotations

from boozydb.models import Ingredient, Recipe
from boozydb.query import Query, filter_recipes, sort_recipes
from boozydb.util import slugify

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_recipe(
    name: str = "Test",
    spirit: str | None = None,
    tags: list[str] | None = None,
    ingredients: list[Ingredient] | None = None,
    created_at: str | None = None,
) -> Recipe:
    kwargs: dict[str, object] = {
        "spirit": spirit,
        "tags": tags or [],
        "ingredients": ingredients or [],
    }
    r = Recipe.new(name, **kwargs)
    if created_at is not None:
        r.created_at = r.created_at.fromisoformat(created_at) if hasattr(r.created_at, "fromisoformat") else r.created_at  # noqa: B009
        from datetime import datetime
        r.created_at = datetime.fromisoformat(created_at)
    return r


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_lowercases(self) -> None:
        assert slugify("Gin") == "gin"

    def test_spaces_become_dashes(self) -> None:
        assert slugify("lime juice") == "lime-juice"

    def test_strips_special_chars(self) -> None:
        assert slugify("gin & tonic!") == "gin-tonic"

    def test_empty_string(self) -> None:
        assert slugify("") == ""

    def test_numbers_preserved(self) -> None:
        assert slugify("recipe 42") == "recipe-42"


# ---------------------------------------------------------------------------
# filter_recipes — empty query returns all
# ---------------------------------------------------------------------------

class TestFilterRecipesEmpty:
    def test_no_filters_returns_all(self) -> None:
        recipes = [make_recipe("Martini"), make_recipe("Negroni")]
        assert len(filter_recipes(recipes, Query())) == 2

    def test_empty_list_returns_empty(self) -> None:
        assert filter_recipes([], Query()) == []


# ---------------------------------------------------------------------------
# filter_recipes — free-text (q)
# ---------------------------------------------------------------------------

class TestFilterRecipesQ:
    def test_matches_name(self) -> None:
        recipes = [make_recipe("Martini"), make_recipe("Negroni")]
        result = filter_recipes(recipes, Query(q="martini"))
        assert len(result) == 1
        assert result[0].name == "Martini"

    def test_case_insensitive(self) -> None:
        result = filter_recipes([make_recipe("Old Fashioned")], Query(q="OLD"))
        assert len(result) == 1

    def test_matches_spirit(self) -> None:
        r = make_recipe("Negroni", spirit="gin")
        assert len(filter_recipes([r], Query(q="gin"))) == 1

    def test_matches_tag(self) -> None:
        r = make_recipe("Negroni", tags=["bitter", "classic"])
        assert len(filter_recipes([r], Query(q="bitter"))) == 1

    def test_matches_ingredient(self) -> None:
        ing = Ingredient(item="lime juice", amount="1", unit="oz")
        r = make_recipe("Daiquiri", ingredients=[ing])
        assert len(filter_recipes([r], Query(q="lime"))) == 1

    def test_no_match_returns_empty(self) -> None:
        assert filter_recipes([make_recipe("Martini")], Query(q="daiquiri")) == []


# ---------------------------------------------------------------------------
# filter_recipes — spirit filter
# ---------------------------------------------------------------------------

class TestFilterRecipesSpirit:
    def test_exact_match(self) -> None:
        gin = make_recipe("Negroni", spirit="gin")
        rum = make_recipe("Daiquiri", spirit="rum")
        result = filter_recipes([gin, rum], Query(spirit="gin"))
        assert len(result) == 1
        assert result[0].name == "Negroni"

    def test_case_insensitive(self) -> None:
        r = make_recipe("Negroni", spirit="gin")
        assert len(filter_recipes([r], Query(spirit="GIN"))) == 1

    def test_none_spirit_excluded(self) -> None:
        r = make_recipe("Mystery", spirit=None)
        assert filter_recipes([r], Query(spirit="gin")) == []

    def test_no_match_returns_empty(self) -> None:
        r = make_recipe("Negroni", spirit="gin")
        assert filter_recipes([r], Query(spirit="vodka")) == []


# ---------------------------------------------------------------------------
# filter_recipes — tag filter
# ---------------------------------------------------------------------------

class TestFilterRecipesTag:
    def test_exact_match(self) -> None:
        classic = make_recipe("Martini", tags=["classic"])
        tropical = make_recipe("Blue Hawaii", tags=["tropical"])
        result = filter_recipes([classic, tropical], Query(tag="classic"))
        assert len(result) == 1
        assert result[0].name == "Martini"

    def test_case_insensitive(self) -> None:
        r = make_recipe("Martini", tags=["classic"])
        assert len(filter_recipes([r], Query(tag="CLASSIC"))) == 1

    def test_no_match_returns_empty(self) -> None:
        r = make_recipe("Martini", tags=["classic"])
        assert filter_recipes([r], Query(tag="tropical")) == []


# ---------------------------------------------------------------------------
# filter_recipes — ingredient filter
# ---------------------------------------------------------------------------

class TestFilterRecipesIngredient:
    def test_substring_match(self) -> None:
        ing = Ingredient(item="lime juice", amount="1", unit="oz")
        r = make_recipe("Daiquiri", ingredients=[ing])
        assert len(filter_recipes([r], Query(ingredient="lime"))) == 1

    def test_no_match_returns_empty(self) -> None:
        ing = Ingredient(item="gin", amount="2", unit="oz")
        r = make_recipe("Martini", ingredients=[ing])
        assert filter_recipes([r], Query(ingredient="rum")) == []

    def test_no_ingredients_excluded(self) -> None:
        r = make_recipe("Empty")
        assert filter_recipes([r], Query(ingredient="gin")) == []


# ---------------------------------------------------------------------------
# filter_recipes — combined filters
# ---------------------------------------------------------------------------

class TestFilterRecipesCombined:
    def test_spirit_and_tag(self) -> None:
        a = make_recipe("Martini", spirit="gin", tags=["classic"])
        b = make_recipe("Gimlet", spirit="gin", tags=["tart"])
        c = make_recipe("Manhattan", spirit="whiskey", tags=["classic"])
        result = filter_recipes([a, b, c], Query(spirit="gin", tag="classic"))
        assert len(result) == 1
        assert result[0].name == "Martini"

    def test_q_and_tag(self) -> None:
        a = make_recipe("Classic Martini", tags=["classic"])
        b = make_recipe("Modern Martini", tags=["modern"])
        result = filter_recipes([a, b], Query(q="martini", tag="classic"))
        assert len(result) == 1
        assert result[0].name == "Classic Martini"


# ---------------------------------------------------------------------------
# sort_recipes
# ---------------------------------------------------------------------------

class TestSortRecipes:
    def test_sort_by_name(self) -> None:
        recipes = [make_recipe("Negroni"), make_recipe("Daiquiri"), make_recipe("Martini")]
        result = sort_recipes(recipes, "name")
        assert [r.name for r in result] == ["Daiquiri", "Martini", "Negroni"]

    def test_default_sort_is_name(self) -> None:
        recipes = [make_recipe("Negroni"), make_recipe("Daiquiri")]
        assert sort_recipes(recipes, "")[0].name == "Daiquiri"

    def test_sort_by_spirit(self) -> None:
        recipes = [
            make_recipe("B", spirit="whiskey"),
            make_recipe("A", spirit="gin"),
            make_recipe("C", spirit=None),
        ]
        result = sort_recipes(recipes, "spirit")
        assert result[0].spirit == "gin"
        assert result[1].spirit == "whiskey"

    def test_sort_by_created_recent_first(self) -> None:
        old = make_recipe("Old", created_at="2024-01-01T00:00:00+00:00")
        new = make_recipe("New", created_at="2025-06-01T00:00:00+00:00")
        result = sort_recipes([old, new], "created")
        assert result[0].name == "New"

    def test_sort_by_created_at_alias(self) -> None:
        old = make_recipe("Old", created_at="2024-01-01T00:00:00+00:00")
        new = make_recipe("New", created_at="2025-06-01T00:00:00+00:00")
        result = sort_recipes([old, new], "created_at")
        assert result[0].name == "New"

    def test_sort_by_random_returns_all(self) -> None:
        recipes = [make_recipe(f"R{i}") for i in range(8)]
        result = sort_recipes(recipes, "random")
        assert len(result) == 8
        assert {r.name for r in result} == {r.name for r in recipes}

    def test_unknown_sort_falls_back_to_name(self) -> None:
        recipes = [make_recipe("Negroni"), make_recipe("Daiquiri")]
        assert sort_recipes(recipes, "bogus")[0].name == "Daiquiri"

    def test_sort_empty_list(self) -> None:
        assert sort_recipes([], "name") == []
