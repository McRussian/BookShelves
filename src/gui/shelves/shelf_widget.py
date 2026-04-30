from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.database.models.shelf import Shelf


class ShelfWidget(QWidget):

    def __init__(self, shelf: Shelf, parent=None):
        super().__init__(parent)
        self.shelf = shelf

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f'Полка: {shelf.name}'))
        layout.addStretch()
