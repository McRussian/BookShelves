from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from src.gui.books.book_manage_widget import BookManageWidget


class BookManageDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Поиск книг')
        self.setMinimumSize(700, 520)

        layout = QVBoxLayout(self)

        self._widget = BookManageWidget(self)
        layout.addWidget(self._widget, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
