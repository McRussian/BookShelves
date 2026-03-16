from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout,
)

from src.database.models.genre import Genre


class GenreSearchDialog(QDialog):
    """Диалог выбора жанров. Без поиска — иерархия из БД, при поиске — плоский список."""

    def __init__(self, preselected: list[Genre], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор жанров')
        self.setMinimumSize(380, 480)

        self._preselected_ids = {g.id for g in preselected}
        self._selected: list[Genre] = []

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по названию жанра...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        layout.addWidget(self._tree, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_tree()

    @property
    def selected_genres(self) -> list[Genre]:
        return self._selected

    # ── Заполнение дерева ─────────────────────────────────────────────────────

    def _populate_tree(self) -> None:
        """Иерархическое дерево из БД."""
        self._tree.clear()
        bold = QFont()
        bold.setBold(True)

        roots = Genre.select().where(Genre.parent.is_null()).order_by(Genre.name)
        for root in roots:
            root_item = QTreeWidgetItem(self._tree, [root.name])
            root_item.setFont(0, bold)
            root_item.setData(0, Qt.ItemDataRole.UserRole, root)
            root_item.setFlags(root_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            root_item.setCheckState(
                0,
                Qt.CheckState.Checked if root.id in self._preselected_ids
                else Qt.CheckState.Unchecked,
            )
            root_item.setExpanded(True)
            self._add_children(root_item, root)

    def _add_children(self, parent_item: QTreeWidgetItem, parent_genre: Genre) -> None:
        children = Genre.select().where(Genre.parent == parent_genre).order_by(Genre.name)
        for genre in children:
            item = QTreeWidgetItem(parent_item, [genre.name])
            item.setData(0, Qt.ItemDataRole.UserRole, genre)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                0,
                Qt.CheckState.Checked if genre.id in self._preselected_ids
                else Qt.CheckState.Unchecked,
            )
            item.setExpanded(True)
            self._add_children(item, genre)

    def _populate_flat(self, genres) -> None:
        """Плоский список — для режима поиска."""
        self._tree.clear()
        for genre in genres:
            item = QTreeWidgetItem(self._tree.invisibleRootItem(), [genre.name])
            item.setData(0, Qt.ItemDataRole.UserRole, genre)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                0,
                Qt.CheckState.Checked if genre.id in self._preselected_ids
                else Qt.CheckState.Unchecked,
            )

    # ── Сбор отмеченных элементов (рекурсивно) ────────────────────────────────

    def _collect_checked(self, parent: QTreeWidgetItem) -> None:
        for i in range(parent.childCount()):
            item = parent.child(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                genre = item.data(0, Qt.ItemDataRole.UserRole)
                if genre is not None:
                    self._selected.append(genre)
            self._collect_checked(item)

    # ── Слоты ────────────────────────────────────────────────────────────────

    def _on_search(self, text: str) -> None:
        text = text.strip()
        if text:
            self._populate_flat(Genre.search(text))
        else:
            self._populate_tree()

    def _on_accept(self) -> None:
        self._selected = []
        self._collect_checked(self._tree.invisibleRootItem())
        self.accept()
