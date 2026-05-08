# BoozyDB Web Preview

This is a Flask development server for previewing the BoozyDB recipe gallery and recipe detail pages.

## Setup

1. Install Flask (if not already installed):
```powershell
pip install -e ".[dev]"
```

2. Run the server:
```powershell
cd web
python app.py
```

3. Open your browser to `http://localhost:5000`

## Features

- **Gallery View**: Browse all recipes as a grid of cards
- **Dark/Light Mode Toggle**: Switch between dark and light themes (persists in localStorage)
- **CSS Glass Art**: Stylized glass containers using CSS clip-paths (not ASCII)
- **Single Column Layout**: Vertical layout that adapts to different screen sizes
- **Recipe Detail Pages**: Click any recipe card to view full details

## Design Notes

- Glass shapes are created with CSS `clip-path` for clean, scalable rendering
- Dark mode uses cyan/magenta/yellow colors matching the CLI
- Light mode provides a clean contrast with cooler accent colors
- Recipe cards feature the spirit, tags, and glass visualization at a glance
- Detail pages show ingredients, instructions, metadata, and source information

## Next Steps

Once you're happy with this design, we'll:
1. Create a static site generator to build HTML files from all recipes
2. Set up GitHub Pages deployment
3. Optionally add filtering/search functionality
