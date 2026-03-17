from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit,
    QMessageBox, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
)

from src.database.models.author import Author
from src.gui.app_signals import app_signals
from src.gui.dialogs.author_dialog import AuthorDialog


class AuthorSearchDialog(QDialog):
    """Диалог выбора авторов с группировкой по алфавиту и поиском."""

    def __init__(self, preselected: list[Author], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор авторов')
        self.setMinimumSize(450, 480)

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
        self._tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._tree, stretch=1)

        new_btn = QPushButton('+ Создать нового автора')
        new_btn.clicked.connect(self._on_create_author)

        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(new_btn)
        bottom.addWidget(self._delete_btn)
        bottom.addStretch()
        bottom.addWidget(buttons)
        layout.addLayout(bottom)

        self._populate_grouped(Author.select().order_by(Author.lastname, Author.firstname))

    @property
    def selected_authors(self) -> list[Author]:
        return self._selected

    # ── Заполнение дерева ─────────────────────────────────────────────────────

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
                group_item.setExpanded(True)
                groups[letter] = group_item
            self._add_author_item(groups[letter], author)

        self._tree.blockSignals(False)
        self._update_delete_btn()

    def _populate_flat(self, authors) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        for author in authors:
            self._add_author_item(self._tree.invisibleRootItem(), author)
        self._tree.blockSignals(False)
        self._update_delete_btn()

    def _add_author_item(self, parent: QTreeWidgetItem, author: Author) -> None:
        item = QTreeWidgetItem(parent, [author.display_name])
        item.setData(0, Qt.ItemDataRole.UserRole, author)
        item.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsUserCheckable
        )
        item.setCheckState(
            0,
            Qt.CheckState.Checked
            if author.id in self._preselected_ids
            else Qt.CheckState.Unchecked,
        )

    def _checked_authors(self) -> list[Author]:
        """Все авторы с установленной галочкой."""
        result = []
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            author = top.data(0, Qt.ItemDataRole.UserRole)
            if author is not None:
                if top.checkState(0) == Qt.CheckState.Checked:
                    result.append(author)
            else:
                for j in range(top.childCount()):
                    child = top.child(j)
                    if child.checkState(0) == Qt.CheckState.Checked:
                        result.append(child.data(0, Qt.ItemDataRole.UserRole))
        return result

    # ── Слоты ────────────────────────────────────────────────────────────────

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column == 0 and item.data(0, Qt.ItemDataRole.UserRole) is not None:
            self._update_delete_btn()

    def _update_delete_btn(self) -> None:
        self._delete_btn.setEnabled(bool(self._checked_authors()))

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

    def _on_delete(self) -> None:
        authors = self._checked_authors()
        if not authors:
            return
        names = '\n'.join(a.display_name for a in authors)
        reply = QMessageBox.question(
            self, 'Удаление',
            f'Удалить из базы данных?\n\n{names}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for author in authors:
            self._preselected_ids.discard(author.id)
            author.delete_instance()
        app_signals.db_changed.emit()
        self._on_search(self._search.text())

    def _on_accept(self) -> None:
        self._selected = self._checked_authors()
        self.accept()
