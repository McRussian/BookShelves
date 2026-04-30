from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QVBoxLayout,
)

from src.database.models.shelf import Shelf


class ShelfOpenDialog(QDialog):
    """Список всех полок пользователя.

    Показывает: активные (открываются при старте) и неактивные.
    Двойной клик или кнопка «Открыть» — открывает выбранную полку.
    Чекбокс «при запуске» — переключает is_active.
    """

    def __init__(self, shelves: list[Shelf], open_ids: set[int], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Полки')
        self.setMinimumWidth(360)
        self._selected_shelf: Shelf | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Выберите полку для открытия:'))

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        layout.addWidget(self._list)

        layout.addWidget(QLabel('✓ — открывается при запуске'))

        buttons = QDialogButtonBox()
        self._open_btn = buttons.addButton('Открыть', QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Close)
        buttons.accepted.connect(self._on_open)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._open_btn.setEnabled(False)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        self._list.itemDoubleClicked.connect(lambda _: self._on_open())
        self._list.itemChanged.connect(self._on_item_changed)

        self._populate(shelves, open_ids)

    def _populate(self, shelves: list[Shelf], open_ids: set[int]) -> None:
        self._list.blockSignals(True)
        for shelf in shelves:
            label = shelf.name
            if shelf.id in open_ids:
                label += '  (открыта)'
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, shelf)
            item.setCheckState(
                Qt.CheckState.Checked if shelf.is_active else Qt.CheckState.Unchecked
            )
            if shelf.id in open_ids:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._list.addItem(item)
        self._list.blockSignals(False)

    def _on_selection_changed(self, current: QListWidgetItem | None, _) -> None:
        enabled = current is not None and bool(current.flags() & Qt.ItemFlag.ItemIsEnabled)
        self._open_btn.setEnabled(enabled)

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        shelf: Shelf = item.data(Qt.ItemDataRole.UserRole)
        shelf.is_active = item.checkState() == Qt.CheckState.Checked
        shelf.save()

    def _on_open(self) -> None:
        item = self._list.currentItem()
        if item is None or not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
            return
        self._selected_shelf = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    @property
    def selected_shelf(self) -> Shelf | None:
        return self._selected_shelf
