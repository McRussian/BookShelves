from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from src.database.models.author import Author


def build_author_results(query: str, preselected_cache: dict) -> list:
    """DB search + preselected authors always included even when not matching."""
    matched = list(Author.search(query))
    matched_ids = {a.id for a in matched}
    extra = [a for a in preselected_cache.values() if a.id not in matched_ids]
    return extra + matched


class AuthorListWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_query: str = ''

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по ФИО или псевдониму...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        layout.addWidget(self._tree, stretch=1)

        self._populate_grouped(Author.select().order_by(Author.lastname, Author.firstname))

    # ── Заполнение ────────────────────────────────────────────────────────────

    def _populate_grouped(self, authors) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        groups: dict[str, QTreeWidgetItem] = {}
        bold = QFont()
        bold.setBold(True)

        for author in authors:
            letter = (author.lastname or author.firstname or '?')[0].upper()
            if letter not in groups:
                group_item = QTreeWidgetItem(self._tree, [letter])
                group_item.setFont(0, bold)
                group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                group_item.setExpanded(False)
                groups[letter] = group_item
            self._add_author_item(groups[letter], author)

        self._tree.blockSignals(False)

    def _populate_flat(self, authors) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        for author in authors:
            self._add_author_item(self._tree.invisibleRootItem(), author)
        self._tree.blockSignals(False)

    def _add_author_item(self, parent: QTreeWidgetItem, author: Author) -> None:
        item = QTreeWidgetItem(parent, [author.display_name])
        item.setData(0, Qt.ItemDataRole.UserRole, author)

    def _on_search(self, text: str) -> None:
        self._current_query = text.strip()
        if self._current_query:
            self._populate_flat(self._get_search_results(self._current_query))
        else:
            self._populate_grouped(Author.select().order_by(Author.lastname, Author.firstname))

    def _get_search_results(self, query: str):
        return Author.search(query)

    # ── Обновление после изменений в БД ──────────────────────────────────────

    def _cache_add(self, author: Author) -> None:
        self._reload()

    def _cache_remove(self, authors: list[Author]) -> None:
        self._reload()

    def _reload(self) -> None:
        self._on_search(self._current_query)
