from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from boozydb.models import Ingredient, Recipe
from boozydb.query import Query, filter_recipes, sort_recipes
from boozydb.render import render_recipe, render_recipe_list
from boozydb.storage import JsonStore, StoreConfig
from boozydb.util import slugify

app = typer.Typer(add_completion=False, help="Drink recipe catalog (CLI-first).")
console = Console()


def _default_data_dir() -> Path:
    return Path.cwd() / "data"


def _store(data_dir: Optional[Path] = None) -> JsonStore:
    data_dir = data_dir or _default_data_dir()
    cfg = StoreConfig(data_dir=data_dir)
    return JsonStore(cfg)


@app.command("list")
def list_cmd(
    q: Optional[str] = typer.Option(None, "--q", help="Free-text query (matches name/tags/ingredients)."),
    spirit: Optional[str] = typer.Option(None, "--spirit", help="Filter by base spirit (e.g., gin)."),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag (e.g., classic)."),
    ingredient: Optional[str] = typer.Option(None, "--ingredient", help="Filter by ingredient substring (e.g., lime)."),
    method: Optional[str] = typer.Option(None, "--method", help="Filter by method (shake/stir/build/etc.)."),
    sort: str = typer.Option("name", "--sort", help="Sort: name | updated | random."),
    limit: int = typer.Option(200, "--limit", help="Max recipes to display."),
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", help="Override data directory (default: ./data)."),
):
    store = _store(data_dir)
    recipes = store.list()
    filtered = filter_recipes(recipes, Query(q=q, spirit=spirit, tag=tag, ingredient=ingredient, method=method))
    sorted_recipes = sort_recipes(filtered, sort)[: max(1, limit)]
    render_recipe_list(sorted_recipes)
    console.print(f"\n[dim]Showing {len(sorted_recipes)} of {len(filtered)} matched (from {len(recipes)} total).[/dim]")


@app.command("show")
def show_cmd(
    id_or_name: str = typer.Argument(..., help="Recipe ID (full or prefix) or recipe name/slug."),
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", help="Override data directory (default: ./data)."),
):
    store = _store(data_dir)
    recipes = store.list()

    needle = id_or_name.strip()
    needle_slug = slugify(needle)

    exact = store.get(needle)
    if exact is not None:
        render_recipe(exact)
        raise typer.Exit(0)

    prefix_matches = [r for r in recipes if r.id.startswith(needle)]
    if len(prefix_matches) == 1:
        render_recipe(prefix_matches[0])
        raise typer.Exit(0)

    name_matches = [r for r in recipes if slugify(r.name) == needle_slug]
    if len(name_matches) == 1:
        render_recipe(name_matches[0])
        raise typer.Exit(0)

    contains = [r for r in recipes if needle_slug in slugify(r.name)]
    if len(contains) == 1:
        render_recipe(contains[0])
        raise typer.Exit(0)

    candidates = prefix_matches or name_matches or contains
    if candidates:
        console.print("[bold]Multiple matches. Try a longer id prefix or a more specific name.[/bold]")
        for r in candidates[:25]:
            console.print(f"- {r.id[:8]}  {r.name}")
        raise typer.Exit(1)

    console.print("[bold red]No recipe found.[/bold red]")
    raise typer.Exit(1)


@app.command("add")
def add_cmd(
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", help="Override data directory (default: ./data)."),
):
    store = _store(data_dir)

    name = typer.prompt("Name").strip()
    description = typer.prompt("Description (optional)", default="").strip() or None
    base_spirits = typer.prompt("Base spirits (comma-separated, optional)", default="").strip()
    tags = typer.prompt("Tags (comma-separated, optional)", default="").strip()
    method = typer.prompt("Method (optional)", default="").strip() or None
    glassware = typer.prompt("Glassware (optional)", default="").strip() or None
    ice = typer.prompt("Ice (optional)", default="").strip() or None
    garnish = typer.prompt("Garnish (comma-separated, optional)", default="").strip()
    source = typer.prompt("Source (optional)", default="").strip() or None
    image = typer.prompt("Image path (optional)", default="").strip() or None

    recipe = Recipe.new(
        name=name,
        description=description,
        base_spirits=[s.strip() for s in base_spirits.split(",") if s.strip()] if base_spirits else [],
        tags=[t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        method=method,
        glassware=glassware,
        ice=ice,
        garnish=[g.strip() for g in garnish.split(",") if g.strip()] if garnish else [],
        source=source,
        image=image,
    )

    console.print("\nEnter ingredients. Leave ingredient name empty to stop.\n")
    while True:
        item = typer.prompt("Ingredient", default="").strip()
        if not item:
            break
        amt_raw = typer.prompt("Amount (optional)", default="").strip()
        unit = typer.prompt("Unit (optional)", default="").strip() or None
        prep = typer.prompt("Prep/notes (optional)", default="").strip() or None
        optional = typer.confirm("Optional ingredient?", default=False)

        amount = None
        if amt_raw:
            try:
                amount = float(amt_raw)
            except ValueError:
                console.print("[yellow]Could not parse amount; storing as blank.[/yellow]")

        recipe.ingredients.append(Ingredient(item=item, amount=amount, unit=unit, prep=prep, optional=optional))

    console.print("\nEnter steps. Leave blank to stop.\n")
    while True:
        step = typer.prompt("Step", default="").strip()
        if not step:
            break
        recipe.steps.append(step)

    store.save(recipe)
    console.print(f"[green]Saved[/green] {recipe.name} (id: {recipe.id})")


@app.command("delete")
def delete_cmd(
    recipe_id: str = typer.Argument(..., help="Recipe ID (full id preferred)."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Do not prompt for confirmation."),
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", help="Override data directory (default: ./data)."),
):
    store = _store(data_dir)
    recipe = store.get(recipe_id)
    if recipe is None:
        console.print("[red]No such recipe id.[/red]")
        raise typer.Exit(1)
    if not yes and not typer.confirm(f"Delete '{recipe.name}' ({recipe.id})?", default=False):
        raise typer.Exit(0)
    ok = store.delete(recipe_id)
    if ok:
        console.print("[green]Deleted.[/green]")
    else:
        console.print("[red]Could not delete.[/red]")
        raise typer.Exit(1)
