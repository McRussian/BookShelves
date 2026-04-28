from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QMessageBox, QPushButton, QTreeWidgetItem,
)

from src.gui.app_signals import app_signals
from src.gui.books.book_checkable_widget import BookCheckableWidget


class BookManageWidget(BookCheckableWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._edit_btn = QPushButton('Редактировать')
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._on_edit)

        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete)

        bottom = QHBoxLayout()
        bottom.addWidget(self._edit_btn)
        bottom.addWidget(self._delete_btn)
        bottom.addStretch()
        self.layout().addLayout(bottom)

        self._tree.itemSelectionChanged.connect(self._update_edit_btn)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    # ── Обновление кнопок ─────────────────────────────────────────────────────

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        super()._on_item_changed(item, column)
        self._update_delete_btn()

    def _execute_search(self) -> None:
        super()._execute_search()
        self._update_edit_btn()
        self._update_delete_btn()

    def _update_edit_btn(self) -> None:
        self._edit_btn.setEnabled(len(self._tree.selectedItems()) == 1)

    def _update_delete_btn(self) -> None:
        self._delete_btn.setEnabled(bool(self._preselected_ids))

    # ── Действия ─────────────────────────────────────────────────────────────

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        book = item.data(0, Qt.ItemDataRole.UserRole)
        if book is not None:
            self._open_edit_dialog(book)

    def _on_edit(self) -> None:
        selected = self._tree.selectedItems()
        if len(selected) != 1:
            return
        book = selected[0].data(0, Qt.ItemDataRole.UserRole)
        if book is not None:
            self._open_edit_dialog(book)

    def _open_edit_dialog(self, book) -> None:
        from src.gui.books.book_dialog import BookDialog
        dlg = BookDialog(book, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._execute_search()

    def _on_delete(self) -> None:
        books = [self._preselected_cache[bid] for bid in list(self._preselected_ids)]
        if not books:
            return
        names = '\n'.join(f'«{b.title}»' for b in books)
        reply = QMessageBox.question(
            self, 'Удаление',
            f'Удалить из базы данных?\n\n{names}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for book in books:
            self._preselected_ids.discard(book.id)
            self._preselected_cache.pop(book.id, None)
            book.delete_instance()
        app_signals.db_changed.emit()
        self._execute_search()
