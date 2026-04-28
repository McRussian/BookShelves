from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from src.gui.authors.author_manage_widget import AuthorManageWidget


class AuthorManageDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Управление авторами')
        self.setMinimumSize(450, 480)

        layout = QVBoxLayout(self)

        self._widget = AuthorManageWidget(self)
        layout.addWidget(self._widget, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
