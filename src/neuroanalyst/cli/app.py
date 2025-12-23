import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from neuroanalyst.models.recipe.core import (
    LogicRecipe,
    ProcessDirRecipe,
    PipelineRecipe,
    create_logic_from_recipe,
    create_process_dir_from_recipe,
    construct_pipeline_from_recipe
)

from typing import Any, Type, Union, get_args, get_origin

import typer, questionary
from rich.console import Console
from rich.panel import Panel
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

console = Console()
app = typer.Typer()

class PydanticRecipeWizard:
    """
    Interactive wizard that fills a Pydantic model sequentially.
    Pydantic v2 safe: never propagates PydanticUndefined.
    """

    def __init__(self, model_cls: Type[BaseModel]):
        self.model_cls = model_cls

    # -------------------------
    # Public API
    # -------------------------

    def run(self) -> BaseModel:
        console.rule(f"[bold blue]Create {self.model_cls.__name__}")

        values: dict[str, Any] = {}

        for field_name, field in self.model_cls.model_fields.items():
            value = self._ask_field(field_name, field)

            # CRITICAL: omit unset fields entirely
            if value is PydanticUndefined:
                continue

            values[field_name] = value

        return self.model_cls(**values)

    # -------------------------
    # Field dispatcher
    # -------------------------

    def _ask_field(self, name: str, field: FieldInfo) -> Any:
        annotation = field.annotation
        description = field.description or ""

        # Optional[T]
        if self._is_optional(annotation):
            if not questionary.confirm(
                f"Set optional field '{name}'?",
                default=False,
            ).ask():
                return PydanticUndefined
            annotation = self._unwrap_optional(annotation)

        console.print(f"\n[bold]{name}[/bold]: {description}")

        # List[T]
        if self._is_list(annotation):
            return self._ask_list(annotation)

        # Nested Pydantic model
        if self._is_pydantic_model(annotation):
            return self._ask_nested_model(annotation)

        # Primitive / dict
        return self._ask_primitive(name, annotation, field)

    # -------------------------
    # Prompt handlers
    # -------------------------

    def _ask_primitive(self, name: str, annotation: Any, field: FieldInfo) -> Any:
        default = self._safe_default(field)

        if annotation is bool:
            return questionary.confirm(
                name,
                default=default if isinstance(default, bool) else False,
            ).ask()

        prompt_kwargs = {}
        if default not in (None, ""):
            prompt_kwargs["default"] = str(default)

        raw = questionary.text(name, **prompt_kwargs).ask()

        if raw in ("", None):
            return PydanticUndefined

        return self._cast_value(raw, annotation)

    def _ask_list(self, annotation: Any) -> Any:
        item_type = get_args(annotation)[0]
        items = []

        console.print("[italic]Add items (at least one required)[/italic]")

        while True:
            if self._is_pydantic_model(item_type):
                item = self._ask_nested_model(item_type)
            else:
                raw = questionary.text("Item value").ask()
                if raw in ("", None):
                    continue
                item = self._cast_value(raw, item_type)

            items.append(item)

            if not questionary.confirm("Add another?", default=False).ask():
                break

        return items

    def _ask_nested_model(self, model_cls: Type[BaseModel]) -> dict:
        wizard = PydanticRecipeWizard(model_cls)
        model = wizard.run()
        return model.model_dump(exclude_unset=True)

    # -------------------------
    # Type helpers
    # -------------------------

    def _safe_default(self, field: FieldInfo) -> Any:
        """
        Return a prompt-safe default.
        Never expose PydanticUndefined or default_factory().
        """
        if field.default is not PydanticUndefined:
            return field.default
        return None

    def _is_optional(self, annotation: Any) -> bool:
        return (
            get_origin(annotation) is Union
            and type(None) in get_args(annotation)
        )

    def _unwrap_optional(self, annotation: Any) -> Any:
        return next(arg for arg in get_args(annotation) if arg is not type(None))

    def _is_list(self, annotation: Any) -> bool:
        return get_origin(annotation) is list

    def _is_pydantic_model(self, annotation: Any) -> bool:
        return isinstance(annotation, type) and issubclass(annotation, BaseModel)

    def _cast_value(self, value: str, annotation: Any) -> Any:
        try:
            return annotation(value)
        except Exception:
            return value

def main():
    console.print(
        Panel(
            "Press [bold]Ctrl+C[/bold] to cancel at any time",
            title="NeuCLI",
        )
    )
    typer.echo("Welcome to NeuroAnalyst CLI")
    typer.echo("Create a Logic, Process, or Pipeline from a recipe file.")
    choice = questionary.select(
        "Select component type to create:",
        choices=[
            "Logic",
            "Process",
            "Pipeline",
        ],
    ).ask()
    
    if choice == "Logic":
        recipe_model = LogicRecipe
        creator_func = create_logic_from_recipe
    elif choice == "Process":
        recipe_model = ProcessDirRecipe
        creator_func = create_process_dir_from_recipe
    elif choice == "Pipeline":
        recipe_model = PipelineRecipe
        creator_func = construct_pipeline_from_recipe
    else:
        console.print("[red]Invalid choice. Exiting.[/red]")
        return
    wizard = PydanticRecipeWizard(recipe_model)
    recipe_instance = wizard.run()
    creator_func(recipe_instance)

@app.command()
def start():
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Operation cancelled by user.[/red]")
        raise typer.Exit(code=130)
    except EOFError:
        console.print("\n[red]No input provided. Exiting.[/red]")
        raise typer.Exit(code=130)

if __name__ == "__main__":
    typer.run(main)