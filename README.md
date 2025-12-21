# Drink Catalog (CLI-first)

A CLI-first catalog for alcoholic drink recipes. Recipes are stored as individual JSON files under `data/recipes/`.

## Quickstart

```bash
not there yet
```

## Data layout

- `data/recipes/<id>.json` — one file per recipe.
- `data/images/` — optional images referenced by relative path (e.g., `data/images/negroni.jpg`).

## Next steps

- Add an index cache (`data/index.json`) for faster search.
- Add a TUI layer (Rich Layout or Textual) while keeping the CLI.
- Add a SQLite backend (placeholder file included).
