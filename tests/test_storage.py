from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import pytest

from boozydb.models import Ingredient, Recipe
from boozydb.storage.base import StoreConfig
from boozydb.storage.json_store import JsonStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path: Path) -> JsonStore:
    return JsonStore(StoreConfig(data_dir=tmp_path))


def make_recipe(name: str = "Test Recipe", **kwargs: object) -> Recipe:
    return Recipe.new(name, **kwargs)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestJsonStoreInit:
    def test_creates_recipes_dir(self, tmp_path: Path) -> None:
        JsonStore(StoreConfig(data_dir=tmp_path / "new_data"))
        assert (tmp_path / "new_data" / "recipes").is_dir()

    def test_existing_recipes_dir_ok(self, store: JsonStore) -> None:
        JsonStore(store.cfg)


# ---------------------------------------------------------------------------
# list_all()
# ---------------------------------------------------------------------------

class TestJsonStoreListAll:
    def test_empty_store_returns_empty(self, store: JsonStore) -> None:
        assert store.list_all() == []

    def test_returns_saved_recipe(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        results = store.list_all()
        assert len(results) == 1
        assert results[0].name == "Martini"

    def test_returns_all_saved_recipes(self, store: JsonStore) -> None:
        r1, r2 = make_recipe("Martini"), make_recipe("Negroni")
        store.save(r1)
        store.save(r2)
        ids = {r.id for r in store.list_all()}
        assert ids == {r1.id, r2.id}

    def test_skips_invalid_json_silently(self, store: JsonStore) -> None:
        (store.cfg.recipes_dir / "broken.json").write_text("not json", encoding="utf-8")
        assert store.list_all() == []

    def test_skips_invalid_schema_silently(self, store: JsonStore) -> None:
        (store.cfg.recipes_dir / "bad.json").write_text(json.dumps({"id": "x"}), encoding="utf-8")
        assert store.list_all() == []

    def test_skips_corrupt_returns_valid(self, store: JsonStore) -> None:
        (store.cfg.recipes_dir / "broken.json").write_text("bad", encoding="utf-8")
        r = make_recipe("Daiquiri")
        store.save(r)
        results = store.list_all()
        assert len(results) == 1
        assert results[0].name == "Daiquiri"

    def test_debug_prints_warning(
        self, store: JsonStore, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BOOZYDB_DEBUG", "1")
        (store.cfg.recipes_dir / "broken.json").write_text("bad", encoding="utf-8")
        store.list_all()
        assert "broken.json" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestJsonStoreGet:
    def test_get_existing(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        fetched = store.get(str(r.id))
        assert fetched is not None
        assert fetched.id == r.id
        assert fetched.name == "Martini"

    def test_get_missing_returns_none(self, store: JsonStore) -> None:
        assert store.get("nonexistent-id") is None

    def test_get_roundtrip_preserves_fields(self, store: JsonStore) -> None:
        ing = Ingredient(item="gin", amount="2", unit="oz")
        r = make_recipe(
            "Negroni",
            spirit="gin",
            glass="rocks",
            tags=["classic"],
            ingredients=[ing],
            instructions=["Stir with ice", "Strain"],
            source="Harry Craddock, 1930",
        )
        store.save(r)
        fetched = store.get(str(r.id))
        assert fetched is not None
        assert fetched.spirit == "gin"
        assert fetched.glass == "rocks"
        assert "classic" in fetched.tags
        assert fetched.ingredients[0].item == "gin"
        assert fetched.instructions == ["Stir with ice", "Strain"]
        assert fetched.source == "Harry Craddock, 1930"

    def test_id_survives_roundtrip_as_uuid(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        fetched = store.get(str(r.id))
        assert isinstance(fetched.id, UUID)  # type: ignore[union-attr]
        assert fetched.id == r.id  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# save()
# ---------------------------------------------------------------------------

class TestJsonStoreSave:
    def test_creates_json_file(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        assert (store.cfg.recipes_dir / f"{r.id}.json").exists()

    def test_file_is_valid_json(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        p = store.cfg.recipes_dir / f"{r.id}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["name"] == "Martini"
        assert data["id"] == str(r.id)

    def test_id_serialised_as_string(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        p = store.cfg.recipes_dir / f"{r.id}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(data["id"], str)

    def test_created_at_serialised_as_string(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        p = store.cfg.recipes_dir / f"{r.id}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert isinstance(data["created_at"], str)

    def test_overwrite_existing(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        d = r.model_dump(mode="json")
        d["name"] = "Dry Martini"
        from boozydb.models import Recipe as R
        updated = R.model_validate(d)
        store.save(updated)
        fetched = store.get(str(r.id))
        assert fetched is not None
        assert fetched.name == "Dry Martini"

    def test_file_ends_with_newline(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        content = (store.cfg.recipes_dir / f"{r.id}.json").read_text(encoding="utf-8")
        assert content.endswith("\n")


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestJsonStoreDelete:
    def test_delete_returns_true(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        assert store.delete(str(r.id)) is True

    def test_delete_removes_file(self, store: JsonStore) -> None:
        r = make_recipe("Martini")
        store.save(r)
        store.delete(str(r.id))
        assert store.get(str(r.id)) is None

    def test_delete_missing_returns_false(self, store: JsonStore) -> None:
        assert store.delete("nonexistent-id") is False

    def test_delete_leaves_others_intact(self, store: JsonStore) -> None:
        r1, r2 = make_recipe("Martini"), make_recipe("Negroni")
        store.save(r1)
        store.save(r2)
        store.delete(str(r1.id))
        remaining = store.list_all()
        assert len(remaining) == 1
        assert remaining[0].id == r2.id


# ---------------------------------------------------------------------------
# StoreConfig
# ---------------------------------------------------------------------------

class TestStoreConfig:
    def test_recipes_dir(self, tmp_path: Path) -> None:
        cfg = StoreConfig(data_dir=tmp_path)
        assert cfg.recipes_dir == tmp_path / "recipes"

    def test_images_dir(self, tmp_path: Path) -> None:
        cfg = StoreConfig(data_dir=tmp_path)
        assert cfg.images_dir == tmp_path / "images"
