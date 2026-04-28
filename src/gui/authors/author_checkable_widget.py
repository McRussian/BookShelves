from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QMessageBox, QPushButton, QTreeWidgetItem,
)

from src.database.models.author import Author
from src.gui.app_signals import app_signals
from src.gui.authors.author_dialog import AuthorDialog
from src.gui.authors.author_list_widget import AuthorListWidget, build_author_results


class AuthorCheckableWidget(AuthorListWidget):

    def __init__(self, preselected: list[Author] = (), auto_select_new: bool = False, parent=None):
        self._preselected_ids: set[int] = {a.id for a in preselected}
        self._preselected_cache: dict[int, Author] = {a.id: a for a in preselected}
        self._auto_select_new = auto_select_new
        self._delete_btn = None
        super().__init__(parent)

        self._tree.itemChanged.connect(self._on_item_changed)
        self._expand_checked_groups()

        create_btn = QPushButton('+ Создать нового автора')
        create_btn.clicked.connect(self.create_author)
        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.clicked.connect(self.delete_checked)
        self._update_delete_btn()

        bottom = QHBoxLayout()
        bottom.addWidget(create_btn)
        bottom.addWidget(self._delete_btn)
        bottom.addStretch()
        self.layout().addLayout(bottom)

    # ── Заполнение ────────────────────────────────────────────────────────────

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
            Qt.CheckState.Checked if author.id in self._preselected_ids else Qt.CheckState.Unchecked,
        )

    def _get_search_results(self, query: str):
        return build_author_results(query, self._preselected_cache)

    def _on_search(self, text: str) -> None:
        super()._on_search(text)
        self._expand_checked_groups()
        self._update_delete_btn()

    def _expand_checked_groups(self) -> None:
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            group = root.child(i)
            for j in range(group.childCount()):
                if group.child(j).checkState(0) == Qt.CheckState.Checked:
                    group.setExpanded(True)
                    break

    # ── Выбор ────────────────────────────────────────────────────────────────

    @property
    def selected_authors(self) -> list[Author]:
        return list(self._preselected_cache.values())

    def _checked_authors(self) -> list[Author]:
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

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column == 0 and item.data(0, Qt.ItemDataRole.UserRole) is not None:
            author = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(0) == Qt.CheckState.Checked:
                self._preselected_ids.add(author.id)
                self._preselected_cache[author.id] = author
            else:
                self._preselected_ids.discard(author.id)
                self._preselected_cache.pop(author.id, None)
            self._update_delete_btn()

    def _update_delete_btn(self) -> None:
        if self._delete_btn is not None:
            self._delete_btn.setEnabled(bool(self._checked_authors()))

    # ── Действия ─────────────────────────────────────────────────────────────

    def create_author(self) -> None:
        dlg = AuthorDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_author = dlg.author
            if self._auto_select_new:
                self._preselected_ids.add(new_author.id)
                self._preselected_cache[new_author.id] = new_author
            self._cache_add(new_author)

    def delete_checked(self) -> None:
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
            self._preselected_cache.pop(author.id, None)
            author.delete_instance()
        app_signals.db_changed.emit()
        self._cache_remove(authors)
