"""
Interactive wizard for filling Pydantic models via CLI prompts.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from neuroanalyst.utils.constants import get_project_root

from typing import Any, Type, Optional, Union, get_args, get_origin
import os

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from rich.console import Console
import questionary

class PydanticWizard:
    """
    Interactive wizard that fills a Pydantic model sequentially.
    """

    def __init__(self, model_cls: Type[BaseModel], console: Console):
        self.model_cls = model_cls
        self.console = console

    # -------------------------
    # Public API
    # -------------------------

    def run(self, default_values: Optional[dict[str, Any]] = None) -> BaseModel:
        self.console.rule(f"[bold blue]Create {self.model_cls.__name__}")
        
        if default_values is None:
            default_values = {}
            
        values: dict[str, Any] = {}
        
        values.update(default_values)

        for field_name, field in self.model_cls.model_fields.items():
            if field_name in values:
                continue
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

        # List[T]
        if self._is_list(annotation):
            return self._ask_list(annotation)
        
        # FilePath / DirectoryPath
        if self._is_path(annotation):
            return self._ask_path(name, annotation)

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

        self.console.print("[italic]Add items (at least one required)[/italic]")

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
    
    def _ask_path(self, name: str, annotation: Any) -> Any:
        prompt_kwargs = {}
        prompt_kwargs["message"] = f"Enter path for '{name}':"
        prompt_kwargs["default"] = os.path.join(str(get_project_root()), "src", "neuroanalyst","models","process","logic","code","python","samples")
        
        raw = questionary.path(**prompt_kwargs).ask()
        
        if raw in ("", None):
            return PydanticUndefined
        
        return Path(raw)

    def _ask_nested_model(self, model_cls: Type[BaseModel]) -> dict:
        wizard = PydanticWizard(model_cls)
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
    
    def _is_path(self, annotation: Any) -> bool:
        return annotation.__name__ in ("FilePath", "DirectoryPath", "Path")

    def _cast_value(self, value: str, annotation: Any) -> Any:
        try:
            return annotation(value)
        except Exception:
            return value