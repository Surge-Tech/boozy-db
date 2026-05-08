# BoozyDB

A professional, tablet-first cocktail recipe catalog for bars, home bartenders, and enthusiasts. Browse a curated collection of classic and modern recipes with beautiful glass illustrations, ingredient lists, and detailed instructions—all with zero database setup required.

**Primary Interface:** Responsive web app optimized for tablets and desktop browsers.  
**Secondary:** CLI for recipe management, debugging, and quick lookups.

Licensed under [GNU AGPL v3](LICENSE.md).

---

## Quick Start

### Web Catalog (Tablet-Friendly)

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run the dev server
cd web
python app.py

# 3. Open your browser
# http://localhost:5000
```

Features:
- ✓ Search by name, spirit, or flavor tags
- ✓ Dark and light modes
- ✓ High-quality SVG glass illustrations
- ✓ Ingredient lists with measurements
- ✓ Step-by-step instructions with visual badges
- ✓ Metadata: spirit type, glass type, created date, flavor profile
- ✓ Fully responsive (desktop, tablet, mobile)

### CLI (Debug/Management)

The CLI is available for recipe management and quick terminal lookups:

```bash
boozydb list              # Show all recipes in a table
boozydb list --spirit gin # Filter by spirit type
boozydb show negroni      # Display full recipe details
boozydb add               # Interactively add a new recipe
boozydb edit negroni      # Edit an existing recipe
boozydb delete negroni    # Delete a recipe
boozydb random --tag classic  # Random recipe with filters
```

See [CLAUDE.md](CLAUDE.md) for full CLI documentation.

---

## Project Structure

```
boozy-db/
├── web/                      # Flask web app (primary interface)
│   ├── app.py               # Server and route handlers
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Layout with navbar/search
│   │   ├── index.html       # Recipe gallery (grid view)
│   │   └── recipe_detail.html # Full recipe page
│   ├── static/              # CSS, JavaScript, SVG assets
│   │   ├── style.css        # Professional styling (dark/light modes)
│   │   ├── theme.js         # Dark/light mode toggle
│   │   └── glasses.js       # SVG glass illustrations
│   └── README.md            # Web deployment guide
├── src/boozydb/             # Recipe engine (shared by web + CLI)
│   ├── cli.py               # Typer CLI entry point
│   ├── models.py            # Pydantic recipe validation
│   ├── query.py             # Filtering and sorting
│   ├── render.py            # Rich terminal rendering
│   ├── util.py              # Utilities (slugify, etc.)
│   └── storage/             # JSON and SQLite backends
├── data/
│   ├── recipes/             # JSON recipe files (UUID-named)
│   ├── images/              # ASCII art and visual assets
│   └── templates/           # Recipe schema reference
├── tests/                   # Unit tests (pytest)
├── pyproject.toml           # Dependencies and build config
└── CLAUDE.md                # Codebase documentation

```

---

## Deployment

### Development (Localhost)

```bash
cd web
python app.py
# → http://localhost:5000
```

### Production Static Build (GitHub Pages)

Coming soon: Static site generator for production deployment via GitHub Pages.

```bash
# (Future) Build static HTML from all recipes
python web/generate_static.py --output ./docs

# Push to GitHub Pages
git push origin main
```

---

## Recipe Management

All recipes are stored as JSON files in `data/recipes/`. Each recipe is validated with [Pydantic](https://docs.pydantic.dev/) on read/write.

**Recipe Schema:**
```json
{
  "id": "uuid-here",
  "name": "Recipe Name",
  "spirit": "gin",
  "glass": "coupe",
  "tags": ["classic", "citrus"],
  "ingredients": [
    { "amount": "2", "unit": "oz", "item": "gin" },
    { "amount": "0.75", "unit": "oz", "item": "lime juice" }
  ],
  "instructions": [
    "Add ingredients to shaker with ice.",
    "Shake until chilled.",
    "Strain into coupe."
  ],
  "source": "Optional source or attribution",
  "created_at": "2025-12-21T04:25:35+00:00"
}
```

**Add a new recipe:**
```bash
boozydb add
```

**Edit an existing recipe:**
```bash
boozydb edit daiquiri
```

**Delete a recipe:**
```bash
boozydb delete daiquiri --yes
```

---

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Activate virtual environment (Windows)
.\activate.ps1
```

### Testing

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=src
```

### Linting

```bash
# Check code style
ruff check src tests

# Auto-format code
ruff format src tests
```

### Environment Variables

```bash
# Print warnings for recipes that fail to load
$env:BOOZYDB_DEBUG = "1"
boozydb list
```

---

## Roadmap

- **Static Site Generation** — Build HTML catalog for GitHub Pages
- **Advanced Search** — Full-text search, faceted filters
- **Batch Import** — Load recipes from CSV or API
- **SQLite Backend** — Scalable backend for large catalogs
- **TUI** — Terminal UI with [Textual](https://textual.textualize.io/)
- **Recipe Sync** — Multi-user sync and conflict resolution

---

## Architecture Notes

The codebase is split into three layers:

1. **Storage** (`src/boozydb/storage/`) — JSON or SQLite backends
2. **Models** (`src/boozydb/models.py`) — Pydantic validation
3. **Presentation** — CLI (Rich) or Web (Flask/Jinja2)

This design allows recipes to be managed via CLI or programmatically, while the web interface focuses on presentation and discovery.

---

## License

GNU Affero General Public License v3 ([LICENSE.md](LICENSE.md))
