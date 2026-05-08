from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, render_template, request

from boozydb.storage.base import StoreConfig
from boozydb.storage.json_store import JsonStore

app = Flask(__name__, template_folder="templates")

data_dir = Path(__file__).parent.parent / "data"
cfg = StoreConfig(data_dir=data_dir)
store = JsonStore(cfg)

GLASS_SVGS = {
    "coupe": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="coupe-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.4" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.1" />
    </linearGradient>
    <linearGradient id="coupe-stem" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
  </defs>
  <path d="M 25 20 Q 30 10 50 10 Q 70 10 75 20 Q 80 35 70 55 Q 60 70 50 80 L 50 80 Q 40 70 30 55 Q 20 35 25 20 Z" fill="url(#coupe-grad)" stroke="currentColor" stroke-width="1.5" opacity="0.8"/>
  <path d="M 25 20 Q 30 10 50 10 Q 70 10 75 20" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <rect x="48" y="80" width="4" height="50" fill="url(#coupe-stem)" stroke="currentColor" stroke-width="0.8" opacity="0.6"/>
  <ellipse cx="50" cy="130" rx="12" ry="4" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
  <path d="M 35 35 Q 40 30 45 35" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.4"/>
</svg>""",
    "rocks": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="rocks-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.35" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.05" />
    </linearGradient>
  </defs>
  <path d="M 20 15 L 80 15 Q 82 15 82 17 L 82 130 Q 82 135 77 140 L 23 140 Q 18 135 18 130 L 18 17 Q 18 15 20 15 Z" fill="url(#rocks-grad)" stroke="currentColor" stroke-width="1.5"/>
  <path d="M 20 15 L 80 15" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.5"/>
  <line x1="30" y1="40" x2="70" y2="40" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
  <line x1="28" y1="70" x2="72" y2="70" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
  <line x1="32" y1="100" x2="68" y2="100" stroke="currentColor" stroke-width="0.5" opacity="0.15"/>
</svg>""",
    "martini": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="martini-grad" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.45" />
      <stop offset="40%" style="stop-color:currentColor;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.1" />
    </linearGradient>
  </defs>
  <path d="M 20 20 L 80 20 Q 75 40 60 65 Q 50 80 50 90 L 50 90 Q 50 80 40 65 Q 25 40 20 20 Z" fill="url(#martini-grad)" stroke="currentColor" stroke-width="1.5"/>
  <path d="M 20 20 L 80 20" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.6"/>
  <path d="M 48 90 L 48 130" stroke="currentColor" stroke-width="1" opacity="0.5"/>
  <circle cx="50" cy="90" r="2" fill="currentColor" opacity="0.4"/>
  <ellipse cx="50" cy="130" rx="8" ry="3" fill="currentColor" opacity="0.2" stroke="currentColor" stroke-width="0.8"/>
  <path d="M 35 35 Q 40 28 45 35" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.35"/>
</svg>""",
    "highball": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="highball-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0" />
      <stop offset="20%" style="stop-color:currentColor;stop-opacity:0.35" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.15" />
      <stop offset="80%" style="stop-color:currentColor;stop-opacity:0.35" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    <linearGradient id="highball-inner" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.25" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.05" />
    </linearGradient>
  </defs>
  <path d="M 25 15 L 75 15 Q 78 15 78 18 L 78 125 Q 78 130 75 135 L 25 135 Q 22 130 22 125 L 22 18 Q 22 15 25 15 Z" fill="url(#highball-inner)" stroke="currentColor" stroke-width="1.5"/>
  <path d="M 25 15 L 75 15" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.5"/>
  <rect x="26" y="20" width="48" height="110" fill="url(#highball-grad)" opacity="0.6"/>
  <path d="M 32 40 Q 50 38 68 40" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.3"/>
</svg>""",
    "flute": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="flute-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0" />
      <stop offset="30%" style="stop-color:currentColor;stop-opacity:0.4" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.2" />
      <stop offset="70%" style="stop-color:currentColor;stop-opacity:0.4" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
  </defs>
  <path d="M 35 12 L 42 12 Q 45 12 45 15 L 45 115 Q 44 125 42 135 L 35 135 Q 33 125 32 115 L 32 15 Q 32 12 35 12 Z" fill="url(#flute-grad)" stroke="currentColor" stroke-width="1.3" opacity="0.8"/>
  <path d="M 55 12 L 62 12 Q 65 12 65 15 L 65 115 Q 64 125 62 135 L 55 135 Q 53 125 52 115 L 52 15 Q 52 12 55 12 Z" fill="url(#flute-grad)" stroke="currentColor" stroke-width="1.3" opacity="0.6"/>
  <path d="M 35 12 L 65 12" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <path d="M 32 30 Q 50 28 68 30" fill="none" stroke="#ffffff" stroke-width="0.7" opacity="0.25"/>
  <ellipse cx="50" cy="135" rx="10" ry="2" fill="currentColor" opacity="0.15"/>
</svg>""",
    "wine glass": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wine-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.4" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.05" />
    </linearGradient>
    <linearGradient id="wine-stem" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.25" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
  </defs>
  <path d="M 28 15 Q 35 10 50 10 Q 65 10 72 15 Q 78 25 75 45 Q 70 65 50 75 Q 30 65 25 45 Q 22 25 28 15 Z" fill="url(#wine-grad)" stroke="currentColor" stroke-width="1.4"/>
  <path d="M 28 15 Q 35 10 50 10 Q 65 10 72 15" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.6"/>
  <rect x="48" y="75" width="4" height="40" fill="url(#wine-stem)" stroke="currentColor" stroke-width="0.7"/>
  <ellipse cx="50" cy="115" rx="14" ry="4" fill="url(#wine-stem)" stroke="currentColor" stroke-width="0.8" opacity="0.5"/>
  <path d="M 40 30 Q 45 25 50 30 Q 55 25 60 30" fill="none" stroke="#ffffff" stroke-width="0.7" opacity="0.4"/>
</svg>""",
    "mug": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="mug-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.35" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.05" />
    </linearGradient>
  </defs>
  <path d="M 22 18 L 68 18 Q 72 18 72 22 L 72 85 Q 72 90 68 90 L 22 90 Q 18 90 18 85 L 18 22 Q 18 18 22 18 Z" fill="url(#mug-grad)" stroke="currentColor" stroke-width="1.5"/>
  <path d="M 22 18 L 68 18" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.5"/>
  <path d="M 72 35 Q 78 35 80 42 Q 82 50 80 58 Q 78 65 72 65" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.7"/>
  <path d="M 72 40 Q 76 40 77 42 Q 78 50 77 58 Q 76 60 72 60" fill="none" stroke="#ffffff" stroke-width="0.6" opacity="0.3"/>
  <line x1="25" y1="50" x2="65" y2="50" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
  <ellipse cx="45" cy="90" rx="24" ry="4" fill="currentColor" opacity="0.15" stroke="currentColor" stroke-width="0.7"/>
</svg>""",
    "julep cup": """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="julep-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0" />
      <stop offset="20%" style="stop-color:currentColor;stop-opacity:0.3" />
      <stop offset="50%" style="stop-color:currentColor;stop-opacity:0.15" />
      <stop offset="80%" style="stop-color:currentColor;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </linearGradient>
    <linearGradient id="julep-inner" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:currentColor;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:currentColor;stop-opacity:0.05" />
    </linearGradient>
  </defs>
  <path d="M 18 15 L 82 15 Q 85 15 85 18 L 85 110 Q 85 115 82 120 L 18 120 Q 15 115 15 110 L 15 18 Q 15 15 18 15 Z" fill="url(#julep-inner)" stroke="currentColor" stroke-width="1.5"/>
  <path d="M 18 15 L 82 15" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.5"/>
  <rect x="20" y="20" width="60" height="95" fill="url(#julep-grad)"/>
  <path d="M 28 40 Q 50 38 72 40" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.25"/>
  <ellipse cx="50" cy="120" rx="32" ry="5" fill="currentColor" opacity="0.15" stroke="currentColor" stroke-width="0.8"/>
</svg>""",
}


@app.route("/")
def index():
    recipes = sorted(store.list_all(), key=lambda r: r.name)
    search = request.args.get("q", "").lower()
    if search:
        recipes = [
            r for r in recipes
            if search in r.name.lower()
            or (r.spirit and search in r.spirit.lower())
            or any(search in tag for tag in r.tags)
        ]
    return render_template("index.html", recipes=recipes, glass_svgs=GLASS_SVGS)


@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id: str):
    recipe = store.get(recipe_id)
    if not recipe:
        return "Recipe not found", 404
    return render_template(
        "recipe_detail.html", recipe=recipe, glass_svgs=GLASS_SVGS
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
