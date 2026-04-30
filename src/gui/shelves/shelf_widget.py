from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QToolButton, QVBoxLayout, QWidget,
)

from src.database.models.book import Book
from src.database.models.shelf import Shelf
from src.gui.books.book_select_dialog import BookSelectDialog


class ShelfWidget(QWidget):

    def __init__(self, shelf: Shelf, parent=None):
        super().__init__(parent)
        self.shelf = shelf

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(800)
        self._save_timer.timeout.connect(self._save_description)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_description())
        layout.addWidget(self._build_book_list(), stretch=1)

        self._load_books()
        self._refresh_stats()

    # ── Построение UI ─────────────────────────────────────────────────────────

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        row = QHBoxLayout(header)
        row.setContentsMargins(6, 3, 6, 3)

        self._info_btn = QToolButton()
        self._info_btn.setText('ℹ')
        self._info_btn.setCheckable(True)
        self._info_btn.setToolTip('Описание полки')
        self._info_btn.toggled.connect(self._on_info_toggled)
        row.addWidget(self._info_btn)

        self._stats_label = QLabel()
        row.addWidget(self._stats_label, stretch=1)

        self._add_btn = QPushButton('+')
        self._add_btn.setFixedWidth(28)
        self._add_btn.setToolTip('Добавить книги на полку')
        self._add_btn.clicked.connect(self._on_add_books)
        row.addWidget(self._add_btn)

        return header

    def _build_description(self) -> QTextEdit:
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText('Описание полки…')
        self._desc_edit.setFixedHeight(72)
        self._desc_edit.setVisible(False)
        self._desc_edit.setText(self.shelf.description or '')
        self._desc_edit.textChanged.connect(self._on_desc_changed)
        return self._desc_edit

    def _build_book_list(self) -> QListWidget:
        self._book_list = QListWidget()
        self._book_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._book_list.customContextMenuRequested.connect(self._show_context_menu)
        return self._book_list

    # ── Шапка ─────────────────────────────────────────────────────────────────

    def _on_info_toggled(self, checked: bool) -> None:
        self._desc_edit.setVisible(checked)
        if not checked:
            self._save_timer.stop()
            self._save_description()

    # ── Книги ─────────────────────────────────────────────────────────────────

    def _load_books(self) -> None:
        self._book_list.clear()
        for book in self.shelf.get_books():
            self._add_book_item(book)

    def _add_book_item(self, book: Book) -> None:
        item = QListWidgetItem(book.title)
        item.setData(Qt.ItemDataRole.UserRole, book)
        self._book_list.addItem(item)

    def _on_add_books(self) -> None:
        already_on_shelf = self.shelf.get_books()
        dlg = BookSelectDialog(preselected=already_on_shelf, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        already_ids = {b.id for b in already_on_shelf}
        added = False
        for book in dlg.selected_books:
            if book.id not in already_ids:
                self.shelf.add_book(book)
                self._add_book_item(book)
                added = True
        if added:
            self._refresh_stats()

    # ── Статистика ────────────────────────────────────────────────────────────

    def _refresh_stats(self) -> None:
        book_count = self._book_list.count()
        parts = [f'{book_count} {self._books_word(book_count)}']
        total_pages = sum(
            self._book_list.item(i).data(Qt.ItemDataRole.UserRole).pages or 0
            for i in range(book_count)
        )
        if total_pages:
            parts.append(f'{total_pages:,} стр.'.replace(',', ' '))
        self._stats_label.setText(' · '.join(parts))

    @staticmethod
    def _books_word(n: int) -> str:
        if 11 <= n % 100 <= 19:
            return 'книг'
        r = n % 10
        if r == 1:
            return 'книга'
        if 2 <= r <= 4:
            return 'книги'
        return 'книг'

    # ── Описание ─────────────────────────────────────────────────────────────

    def _on_desc_changed(self) -> None:
        self._save_timer.start()

    def _save_description(self) -> None:
        text = self._desc_edit.toPlainText().strip() or None
        if text != self.shelf.description:
            self.shelf.description = text
            self.shelf.save()

    # ── Контекстное меню ─────────────────────────────────────────────────────

    def _show_context_menu(self, pos) -> None:
        from PyQt6.QtWidgets import QMenu
        if self._book_list.itemAt(pos) is None:
            return
        menu = QMenu(self)
        menu.addAction('Редактировать', self._on_book_edit)
        menu.addAction('Открыть',       self._on_book_open)
        menu.addSeparator()
        menu.addAction('Убрать с полки', self._on_book_remove)
        menu.exec(self._book_list.mapToGlobal(pos))

    def _on_book_edit(self):   pass
    def _on_book_open(self):   pass
    def _on_book_remove(self): pass
