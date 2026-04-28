from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from src.database.models.tag import Tag
from src.gui.widgets.tag_select_widget import TagSelectWidget


class TagSelectDialog(QDialog):
    """Диалог выбора тегов для привязки к объекту (книге и т.п.)."""

    def __init__(self, preselected: list[Tag], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор тегов')
        self.setMinimumSize(440, 420)

        layout = QVBoxLayout(self)
        self._widget = TagSelectWidget(preselected, self)
        layout.addWidget(self._widget, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def selected_tags(self) -> list[Tag]:
        return self._widget.selected_tags
