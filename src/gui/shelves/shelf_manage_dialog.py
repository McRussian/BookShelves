from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout,
)

from src.database.models.shelf import Shelf


class ShelfManageDialog(QDialog):
    """Управление полками: открытие закрытых и удаление."""

    def __init__(self, shelves: list[Shelf], open_ids: set[int], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Полки')
        self.setMinimumWidth(360)
        self._open_ids = open_ids
        self._opened_shelf: Shelf | None = None

        layout = QVBoxLayout(self)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        layout.addWidget(self._list)

        btn_row = QHBoxLayout()
        self._open_btn = QPushButton('Открыть')
        self._open_btn.clicked.connect(self._on_open)
        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addWidget(self._open_btn)
        btn_row.addWidget(self._delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        close_btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btns.rejected.connect(self.reject)
        layout.addWidget(close_btns)

        self._open_btn.setEnabled(False)
        self._delete_btn.setEnabled(False)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        self._list.itemDoubleClicked.connect(lambda _: self._on_open())

        self._populate(shelves)

    def _populate(self, shelves: list[Shelf]) -> None:
        self._list.clear()
        for shelf in shelves:
            label = shelf.name
            if shelf.id in self._open_ids:
                label += '  (открыта)'
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, shelf)
            self._list.addItem(item)

    def _current_shelf(self) -> Shelf | None:
        item = self._list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _on_selection_changed(self) -> None:
        shelf = self._current_shelf()
        self._delete_btn.setEnabled(shelf is not None)
        self._open_btn.setEnabled(
            shelf is not None and shelf.id not in self._open_ids
        )

    def _on_open(self) -> None:
        shelf = self._current_shelf()
        if shelf is None or shelf.id in self._open_ids:
            return
        self._opened_shelf = shelf
        self.accept()

    def _on_delete(self) -> None:
        shelf = self._current_shelf()
        if shelf is None:
            return
        reply = QMessageBox.question(
            self, 'Удалить полку',
            f'Удалить полку «{shelf.name}»?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        shelf.delete_instance()
        self._open_ids.discard(shelf.id)
        row = self._list.currentRow()
        self._list.takeItem(row)
        self._on_selection_changed()

    @property
    def opened_shelf(self) -> Shelf | None:
        return self._opened_shelf
