from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from src.database.models.author import Author
from src.gui.authors.author_select_widget import AuthorSelectWidget


class AuthorSelectDialog(QDialog):

    def __init__(self, preselected: list[Author] = (), parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор авторов')
        self.setMinimumSize(450, 480)

        layout = QVBoxLayout(self)

        self._widget = AuthorSelectWidget(preselected, self)
        layout.addWidget(self._widget, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def selected_authors(self) -> list[Author]:
        return self._widget.selected_authors
