from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeWidgetItem

from src.database.models.book import Book
from src.gui.books.book_list_widget import BookListWidget, build_book_results


class BookCheckableWidget(BookListWidget):

    def __init__(self, preselected: list[Book] = (), parent=None):
        self._preselected_ids: set[int] = {b.id for b in preselected}
        self._preselected_cache: dict[int, Book] = {b.id: b for b in preselected}
        super().__init__(parent)

        self._tree.itemChanged.connect(self._on_item_changed)

        if self._preselected_cache:
            self._execute_search()

    # ── Критерии поиска ───────────────────────────────────────────────────────

    def _has_criteria(self) -> bool:
        return super()._has_criteria() or bool(self._preselected_cache)

    # ── Заполнение ────────────────────────────────────────────────────────────

    def _get_search_results(
        self, text: str, author_ids: list, tag_ids: list, genre_ids: list,
    ) -> list[Book]:
        return build_book_results(text, author_ids, tag_ids, genre_ids, self._preselected_cache)

    def _add_book_item(self, book: Book, authors_str: str, filename: str) -> None:
        item = QTreeWidgetItem([book.title, authors_str, filename])
        item.setData(0, Qt.ItemDataRole.UserRole, book)
        item.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsUserCheckable
        )
        item.setCheckState(
            0,
            Qt.CheckState.Checked if book.id in self._preselected_ids else Qt.CheckState.Unchecked,
        )
        self._tree.addTopLevelItem(item)

    # ── Выбор ────────────────────────────────────────────────────────────────

    @property
    def selected_books(self) -> list[Book]:
        return list(self._preselected_cache.values())

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        book = item.data(0, Qt.ItemDataRole.UserRole)
        if book is None:
            return
        if item.checkState(0) == Qt.CheckState.Checked:
            self._preselected_ids.add(book.id)
            self._preselected_cache[book.id] = book
        else:
            self._preselected_ids.discard(book.id)
            self._preselected_cache.pop(book.id, None)
