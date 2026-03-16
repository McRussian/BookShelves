from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit,
    QMessageBox, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
)

from src.database.models.tag import Tag
from src.gui.dialogs.tag_dialog import TagDialog


class TagSearchDialog(QDialog):
    """Диалог выбора тегов с группировкой по алфавиту и поиском."""

    def __init__(self, preselected: list[Tag], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор тегов')
        self.setMinimumSize(360, 420)

        self._preselected_ids = {t.id for t in preselected}
        self._selected: list[Tag] = []

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по названию...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        self._tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._tree, stretch=1)

        new_btn = QPushButton('+ Создать новый тег')
        new_btn.clicked.connect(self._on_create_tag)

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

        self._populate_grouped(Tag.select().order_by(Tag.name))

    @property
    def selected_tags(self) -> list[Tag]:
        return self._selected

    # ── Заполнение дерева ─────────────────────────────────────────────────────

    def _populate_grouped(self, tags) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        groups: dict[str, QTreeWidgetItem] = {}
        bold = QFont()
        bold.setBold(True)

        for tag in tags:
            letter = (tag.name or '?')[0].upper()
            if letter not in groups:
                group_item = QTreeWidgetItem(self._tree, [letter])
                group_item.setFont(0, bold)
                group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                group_item.setExpanded(True)
                groups[letter] = group_item
            self._add_tag_item(groups[letter], tag)

        self._tree.blockSignals(False)
        self._update_delete_btn()

    def _populate_flat(self, tags) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        for tag in tags:
            self._add_tag_item(self._tree.invisibleRootItem(), tag)
        self._tree.blockSignals(False)
        self._update_delete_btn()

    def _add_tag_item(self, parent: QTreeWidgetItem, tag: Tag) -> None:
        item = QTreeWidgetItem(parent, [tag.name])
        item.setData(0, Qt.ItemDataRole.UserRole, tag)
        item.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsUserCheckable
        )
        item.setCheckState(
            0,
            Qt.CheckState.Checked
            if tag.id in self._preselected_ids
            else Qt.CheckState.Unchecked,
        )

    def _checked_tags(self) -> list[Tag]:
        """Все теги с установленной галочкой."""
        result = []
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            tag = top.data(0, Qt.ItemDataRole.UserRole)
            if tag is not None:
                if top.checkState(0) == Qt.CheckState.Checked:
                    result.append(tag)
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
        self._delete_btn.setEnabled(bool(self._checked_tags()))

    def _on_search(self, text: str) -> None:
        text = text.strip()
        if text:
            self._populate_flat(Tag.search(text))
        else:
            self._populate_grouped(Tag.select().order_by(Tag.name))

    def _on_create_tag(self) -> None:
        dlg = TagDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_tag = dlg.tag
            self._preselected_ids.add(new_tag.id)
            self._on_search(self._search.text())

    def _on_delete(self) -> None:
        tags = self._checked_tags()
        if not tags:
            return
        names = '\n'.join(t.name for t in tags)
        reply = QMessageBox.question(
            self, 'Удаление',
            f'Удалить из базы данных?\n\n{names}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for tag in tags:
            self._preselected_ids.discard(tag.id)
            tag.delete_instance()
        self._on_search(self._search.text())

    def _on_accept(self) -> None:
        self._selected = self._checked_tags()
        self.accept()
