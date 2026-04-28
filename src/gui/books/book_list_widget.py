from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from src.database.models.author import Author
from src.database.models.book import Book, BookAuthor
from src.gui.authors.author_select_dialog import AuthorSelectDialog
from src.gui.genres.genre_search_dialog import GenreSearchDialog
from src.gui.tags.tag_select_dialog import TagSelectDialog
from src.gui.widgets.chips_widget import ChipsWidget

SEARCH_MIN_CHARS = 2
SEARCH_DEBOUNCE_MS = 250


def build_book_results(
    text: str,
    author_ids: list,
    tag_ids: list,
    genre_ids: list,
    preselected_cache: dict,
) -> list:
    """DB search + preselected books always included even when not matching."""
    has_db_criteria = bool(text) or bool(author_ids) or bool(tag_ids) or bool(genre_ids)
    if has_db_criteria:
        matched = list(Book.search(text, author_ids, tag_ids, genre_ids))
        matched_ids = {b.id for b in matched}
        extra = [b for b in preselected_cache.values() if b.id not in matched_ids]
        return extra + matched
    return list(preselected_cache.values())


class BookListWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по названию или автору...')
        self._search.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._search)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(SEARCH_DEBOUNCE_MS)
        self._timer.timeout.connect(self._execute_search)

        # Author filter row
        author_row = QHBoxLayout()
        author_row.addWidget(QLabel('Авторы:'))
        self._author_chips = ChipsWidget()
        self._author_chips.item_removed.connect(self._on_filter_changed)
        author_row.addWidget(self._author_chips, stretch=1)
        author_btn = QPushButton('Выбрать...')
        author_btn.setFixedWidth(90)
        author_btn.clicked.connect(self._on_select_author_filter)
        author_row.addWidget(author_btn)
        layout.addLayout(author_row)

        # Tag filter row
        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel('Теги:'))
        self._tag_chips = ChipsWidget()
        self._tag_chips.item_removed.connect(self._on_filter_changed)
        tag_row.addWidget(self._tag_chips, stretch=1)
        tag_btn = QPushButton('Выбрать...')
        tag_btn.setFixedWidth(90)
        tag_btn.clicked.connect(self._on_select_tag_filter)
        tag_row.addWidget(tag_btn)
        layout.addLayout(tag_row)

        # Genre filter row
        genre_row = QHBoxLayout()
        genre_row.addWidget(QLabel('Жанры:'))
        self._genre_chips = ChipsWidget()
        self._genre_chips.item_removed.connect(self._on_filter_changed)
        genre_row.addWidget(self._genre_chips, stretch=1)
        genre_btn = QPushButton('Выбрать...')
        genre_btn.setFixedWidth(90)
        genre_btn.clicked.connect(self._on_select_genre_filter)
        genre_row.addWidget(genre_btn)
        layout.addLayout(genre_row)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(['Название', 'Авторы', 'Файл'])
        self._tree.setRootIsDecorated(False)
        layout.addWidget(self._tree, stretch=1)

    # ── Критерии поиска ───────────────────────────────────────────────────────

    def _has_criteria(self) -> bool:
        text = self._search.text().strip()
        return (
            len(text) >= SEARCH_MIN_CHARS
            or bool(self._author_chips.all_data())
            or bool(self._tag_chips.all_data())
            or bool(self._genre_chips.all_data())
        )

    # ── Поиск ────────────────────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        self._timer.start()

    def _on_filter_changed(self) -> None:
        self._timer.stop()
        self._execute_search()

    def _execute_search(self) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        self._tree.blockSignals(False)

        if not self._has_criteria():
            return

        text = self._search.text().strip()
        author_ids = [a.id for a in self._author_chips.all_data()]
        tag_ids = [t.id for t in self._tag_chips.all_data()]
        genre_ids = [g.id for g in self._genre_chips.all_data()]

        books = self._get_search_results(text, author_ids, tag_ids, genre_ids)
        author_map = self._load_author_names(books)
        self._populate(books, author_map)

    def _get_search_results(
        self, text: str, author_ids: list, tag_ids: list, genre_ids: list,
    ) -> list[Book]:
        return list(Book.search(text, author_ids, tag_ids, genre_ids))

    def _load_author_names(self, books: list[Book]) -> dict[int, str]:
        book_ids = [b.id for b in books]
        groups: dict[int, list[str]] = {}
        if book_ids:
            for ba in (BookAuthor
                       .select(BookAuthor, Author)
                       .join(Author)
                       .where(BookAuthor.book.in_(book_ids))):
                groups.setdefault(ba.book_id, []).append(ba.author.full_name)
        return {bid: ', '.join(names) for bid, names in groups.items()}

    def _populate(self, books: list[Book], author_map: dict[int, str]) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        for book in books:
            filename = Path(book.file_path).name
            authors_str = author_map.get(book.id, '')
            self._add_book_item(book, authors_str, filename)
        self._tree.resizeColumnToContents(0)
        self._tree.resizeColumnToContents(1)
        self._tree.blockSignals(False)

    def _add_book_item(self, book: Book, authors_str: str, filename: str) -> None:
        item = QTreeWidgetItem([book.title, authors_str, filename])
        item.setData(0, Qt.ItemDataRole.UserRole, book)
        self._tree.addTopLevelItem(item)

    # ── Выбор фильтров ────────────────────────────────────────────────────────

    def _on_select_author_filter(self) -> None:
        current = self._author_chips.all_data()
        dlg = AuthorSelectDialog(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._author_chips.set_items([(a.full_name, a) for a in dlg.selected_authors])
            self._on_filter_changed()

    def _on_select_tag_filter(self) -> None:
        current = self._tag_chips.all_data()
        dlg = TagSelectDialog(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._tag_chips.set_items([(t.name, t) for t in dlg.selected_tags])
            self._on_filter_changed()

    def _on_select_genre_filter(self) -> None:
        current = self._genre_chips.all_data()
        dlg = GenreSearchDialog(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._genre_chips.set_items([(g.name, g) for g in dlg.selected_genres])
            self._on_filter_changed()
