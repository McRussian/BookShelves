from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
)

from src.database.models.author import Author
from src.gui.dialogs.author_dialog import AuthorDialog


class AuthorSearchDialog(QDialog):
    """Диалог выбора авторов с группировкой по алфавиту и поиском."""

    def __init__(self, preselected: list[Author], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор авторов')
        self.setMinimumSize(420, 480)

        self._preselected_ids = {a.id for a in preselected}
        self._selected: list[Author] = []

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по ФИО или псевдониму...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        layout.addWidget(self._tree, stretch=1)

        new_btn = QPushButton('+ Создать нового автора')
        new_btn.clicked.connect(self._on_create_author)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(new_btn)
        bottom.addStretch()
        bottom.addWidget(buttons)
        layout.addLayout(bottom)

        self._populate_grouped(Author.select().order_by(Author.lastname, Author.firstname))

    @property
    def selected_authors(self) -> list[Author]:
        return self._selected

    # ── Заполнение дерева ─────────────────────────────────────────────────────

    def _populate_grouped(self, authors) -> None:
        """Группировка по первой букве фамилии (или имени)."""
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
                group_item.setExpanded(True)
                groups[letter] = group_item
            self._add_author_item(groups[letter], author)

    def _populate_flat(self, authors) -> None:
        """Плоский список без группировки — для режима поиска."""
        self._tree.clear()
        for author in authors:
            self._add_author_item(self._tree.invisibleRootItem(), author)

    def _add_author_item(self, parent: QTreeWidgetItem, author: Author) -> None:
        item = QTreeWidgetItem(parent, [author.display_name])
        item.setData(0, Qt.ItemDataRole.UserRole, author)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(
            0,
            Qt.CheckState.Checked
            if author.id in self._preselected_ids
            else Qt.CheckState.Unchecked,
        )

    # ── Слоты ────────────────────────────────────────────────────────────────

    def _on_search(self, text: str) -> None:
        text = text.strip()
        if text:
            self._populate_flat(Author.search(text))
        else:
            self._populate_grouped(Author.select().order_by(Author.lastname, Author.firstname))

    def _on_create_author(self) -> None:
        dlg = AuthorDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_author = dlg.author
            self._preselected_ids.add(new_author.id)
            self._on_search(self._search.text())

    def _on_accept(self) -> None:
        self._selected = []
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            author = top.data(0, Qt.ItemDataRole.UserRole)
            if author is not None:
                # Плоский режим: авторы прямо под корнем
                if top.checkState(0) == Qt.CheckState.Checked:
                    self._selected.append(author)
            else:
                # Сгруппированный режим: авторы — дети группы
                for j in range(top.childCount()):
                    child = top.child(j)
                    if child.checkState(0) == Qt.CheckState.Checked:
                        self._selected.append(child.data(0, Qt.ItemDataRole.UserRole))
        self.accept()
