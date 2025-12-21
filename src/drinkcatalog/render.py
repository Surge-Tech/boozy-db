from __future__ import annotations

from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from drinkcatalog.models import Recipe

console = Console()


def render_recipe_list(recipes: Iterable[Recipe]) -> None:
    table = Table(title="Drink Catalog", show_lines=False)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Spirits")
    table.add_column("Method", style="dim")
    table.add_column("Tags", style="dim")

    for r in recipes:
        table.add_row(
            r.id[:8],
            r.name,
            ", ".join(r.base_spirits) if r.base_spirits else "-",
            r.method or "-",
            ", ".join(r.tags) if r.tags else "-",
        )
    console.print(table)


def render_recipe(recipe: Recipe) -> None:
    header = Text(recipe.name, style="bold")
    if recipe.description:
        header.append(f"\n{recipe.description}")

    meta_lines = []
    if recipe.base_spirits:
        meta_lines.append(f"[bold]Base spirits:[/bold] {', '.join(recipe.base_spirits)}")
    if recipe.method:
        meta_lines.append(f"[bold]Method:[/bold] {recipe.method}")
    if recipe.glassware:
        meta_lines.append(f"[bold]Glassware:[/bold] {recipe.glassware}")
    if recipe.ice:
        meta_lines.append(f"[bold]Ice:[/bold] {recipe.ice}")
    if recipe.garnish:
        meta_lines.append(f"[bold]Garnish:[/bold] {', '.join(recipe.garnish)}")
    if recipe.tags:
        meta_lines.append(f"[bold]Tags:[/bold] {', '.join(recipe.tags)}")
    if recipe.image:
        meta_lines.append(f"[bold]Image:[/bold] {recipe.image}")
    if recipe.source:
        meta_lines.append(f"[bold]Source:[/bold] {recipe.source}")

    meta = "\n".join(meta_lines) if meta_lines else ""

    ing_table = Table(title="Ingredients", show_header=True, header_style="bold")
    ing_table.add_column("Amount")
    ing_table.add_column("Ingredient")
    ing_table.add_column("Notes", style="dim")

    for ing in recipe.ingredients:
        amt = ""
        if ing.amount is not None:
            amt = f"{ing.amount:g} {ing.unit}" if ing.unit else f"{ing.amount:g}"
        elif ing.unit:
            amt = ing.unit
        notes_bits = []
        if ing.prep:
            notes_bits.append(ing.prep)
        if ing.optional:
            notes_bits.append("optional")
        notes = ", ".join(notes_bits) if notes_bits else "-"
        ing_table.add_row(amt or "-", ing.item, notes)

    steps_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(recipe.steps)]) if recipe.steps else "-"

    console.print(Panel.fit(header, subtitle=f"ID: {recipe.id}"))
    if meta:
        console.print(Panel(meta, title="Details"))
    console.print(ing_table)
    console.print(Panel(steps_text, title="Steps"))
    if recipe.notes:
        console.print(Panel(recipe.notes, title="Notes", border_style="dim"))
