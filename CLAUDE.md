# CLAUDE.md

## Project Overview

BoozyDB is a CLI-first cocktail recipe catalog. Recipes are stored as individual UUID-named JSON files under `data/recipes/`, validated on every read/write with Pydantic, and displayed in the terminal using Rich tables and panels. There is no database setup — the JSON files are the database.

## Tech Stack

- **Python 3.11+** — required minimum
- **Pydantic 2.7+** — model definition and validation
- **Typer 0.12+** — CLI framework
- **Rich 13.7+** — terminal rendering (tables, panels, colors)
- **Hatchling** — build backend
- **pytest 8+** and **Ruff 0.4+** — dev dependencies

## Essential Commands

```powershell
# Activate the venv (Windows)
.\activate.ps1

# Install in editable mode (runtime only)
pip install -e .

# Install with dev dependencies (needed to run tests/linter)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a specific test file
pytest tests/test_models.py

# Lint
ruff check src tests

# Format (ruff handles both)
ruff format src tests

# Run the CLI
boozydb list
boozydb list --spirit gin --sort created
boozydb show negroni
boozydb add
boozydb edit negroni
boozydb delete negroni
boozydb random --tag classic
```

## Project Structure

```
src/boozydb/
├── cli.py          # Typer app; all commands (list, show, add, edit, delete, random)
├── models.py       # Pydantic models: Recipe, Ingredient
├── query.py        # filter_recipes(), sort_recipes(), Query dataclass
├── render.py       # Rich rendering: render_recipe(), render_recipe_list()
├── util.py         # slugify() — used everywhere for case-insensitive matching
└── storage/
    ├── base.py     # Store protocol + StoreConfig dataclass
    ├── json_store.py  # JsonStore — the only active backend
    └── sqlite_store.py  # Empty placeholder for future SQLite backend

data/
├── recipes/        # One UUID.json file per recipe (11 shipped)
│   └── templates/  # !template.json — reference schema for new recipes
└── images/         # ASCII art and image assets (unused by CLI currently)

tests/
├── test_models.py  # Ingredient and Recipe validation
├── test_query.py   # filter_recipes() and sort_recipes()
└── test_storage.py # JsonStore CRUD via a tmp_path fixture
```

## Key Files

- [src/boozydb/cli.py](src/boozydb/cli.py) — entry point; `_resolve_recipe()` handles partial name/ID matching
- [src/boozydb/models.py](src/boozydb/models.py) — single source of truth for the data schema
- [src/boozydb/storage/json_store.py](src/boozydb/storage/json_store.py) — all disk I/O
- [pyproject.toml](pyproject.toml) — dependencies, Ruff config, pytest config, CLI entrypoint

## Recipe JSON Schema

Every recipe file in `data/recipes/` must conform to this shape (enforced by Pydantic):

```json
{
  "id": "<uuid4>",
  "name": "Title-Cased String",
  "spirit": "lowercase or null",
  "glass": "string",
  "tags": ["sorted", "lowercase", "deduped"],
  "ingredients": [
    { "amount": "1", "unit": "oz", "item": "non-empty string" }
  ],
  "instructions": ["Step text..."],
  "created_at": "2025-12-21T04:25:35+00:00"
}
```

## Code Style and Conventions

- **`from __future__ import annotations`** at the top of every source file.
- **`model_config = ConfigDict(extra="forbid")`** on all Pydantic models — unknown fields are rejected.
- `Recipe.new()` classmethod is the canonical constructor for new recipes (wraps `__init__`).
- `store.save(recipe)` handles both create and update — no separate `update()` method.
- `slugify()` from `util.py` is used for all case-insensitive string comparisons (name matching, filtering).
- Rich markup strings (`[bold red]...[/bold red]`) are used directly in `console.print()` — never build them in render.py then re-print.
- Ruff line length is **100** characters; `E501` (line-too-long) is ignored in lint.
- Selected Ruff rules: `E`, `F`, `W`, `I` (isort).

## Environment Setup

No `.env` file is required. One optional env var:

```powershell
$env:BOOZYDB_DEBUG = "1"   # print warnings for recipe files that fail to load
```

The CLI resolves the data directory from the **current working directory** (`Path.cwd() / "data"`). Run `boozydb` commands from the repo root, or pass `--data-dir <path>` to override.

## Testing Approach

Tests live in `tests/` and use `pytest` with `tmp_path` for storage tests (no shared state). Three test files map directly to three source modules:

| File | Covers |
|---|---|
| `test_models.py` | Pydantic validation, field normalization |
| `test_query.py` | `filter_recipes()`, `sort_recipes()`, all sort keys |
| `test_storage.py` | `JsonStore` CRUD, debug flag, malformed JSON handling |

Run `pytest` from the repo root before committing. There is no pre-commit hook configured.

## Common Pitfalls

- **Run from repo root.** The CLI resolves data at `./data` relative to CWD. Running `boozydb list` from a subdirectory will create a new empty `data/` there.
- **Tags are always sorted and lowercased.** The `_tags_normalize` validator sorts and deduplicates on every write. Don't rely on insertion order.
- **`store.save()` overwrites by ID.** Editing a recipe and changing its `name` does not change the filename — the UUID is the key.
- **`JsonStore.list_all()` silently skips invalid files** unless `BOOZYDB_DEBUG=1`. A malformed JSON file in `data/recipes/` disappears from all listings without error.
- **`_resolve_recipe()` has a resolution priority:** exact UUID → UUID prefix → exact slug → slug substring → ambiguity error. A short name like "gin" may match multiple recipes.
- **`sqlite_store.py` is a placeholder** — it contains only a comment. Do not import or reference it.
