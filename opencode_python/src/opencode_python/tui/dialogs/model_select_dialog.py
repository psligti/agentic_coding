from typing import Any, Dict, List, Optional, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, DataTable, Footer


class ModelSelectDialog(ModalScreen[str]):
    def __init__(
        self,
        title: str = "Select model",
        available_models: Optional[List[Dict[str, Any]]] = None,
        provider_default: str = "default",
        on_select: Optional[Callable[[str], None]] = None
    ):
        super().__init__()
        self.title = title
        self.available_models = available_models or []
        self.provider_default = provider_default
        self.on_select = on_select
        self._result: Optional[str] = None
        self._selected_model: Optional[str] = None

    def compose(self) -> ComposeResult:
        container = Vertical()

        if self.title:
            yield Label(self.title)

        data_table = DataTable(id="model_table")
        data_table.add_column("Model")
        data_table.add_column("Provider")
        yield data_table

        for model in self.available_models:
            row_id = f"model_{model['value']}"
            data_table.add_row(
                model.get("title", str(model.get("value", ""))),
                model.get("provider", self.provider_default),
                key=row_id
            )

        yield container

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.focus()
        table.cursor_type = "row"
        table.zebra_stripes = True

    def close_dialog(self, value: Optional[str] = None) -> None:
        self._result = value
        self._selected_model = value
        self.dismiss()

    def get_result(self) -> Optional[str]:
        return self._result

    def action_enter(self) -> None:
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row_id = table.get_row_at(table.cursor_row)
            for model in self.available_models:
                if f"model_{model['value']}" == row_id:
                    self.close_dialog(model["value"])
                    if self.on_select:
                        self.on_select(model["value"])
                    break
        else:
            self.close_dialog(None)

    def action_escape(self) -> None:
        self.close_dialog(None)

    def action_cancel(self) -> None:
        self.action_escape()

    def action_select(self) -> None:
        self.action_enter()
