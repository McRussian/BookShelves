from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QMessageBox, QPushButton, QTreeWidgetItem,
)

from src.database.models.tag import Tag
from src.gui.app_signals import app_signals
from src.gui.tags.tag_dialog import TagDialog
from src.gui.tags.tag_list_widget import TagListWidget, build_search_results


class TagCheckableWidget(TagListWidget):
    """Виджет тегов с чекбоксами и персистентным выделением между поисками.

    auto_select_new=True  — новый созданный тег сразу помечается (для выбора тегов книги).
    auto_select_new=False — новый тег добавляется без галочки (для управления справочником).
    """

    def __init__(self, preselected: list[Tag] = (), auto_select_new: bool = False, parent=None):
        self._preselected_ids: set[int] = {t.id for t in preselected}
        self._auto_select_new = auto_select_new
        self._delete_btn = None
        super().__init__(parent)

        self._tree.itemChanged.connect(self._on_item_changed)
        self._expand_checked_groups()

        create_btn = QPushButton('+ Создать новый тег')
        create_btn.clicked.connect(self.create_tag)
        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.clicked.connect(self.delete_checked)
        self._update_delete_btn()

        bottom = QHBoxLayout()
        bottom.addWidget(create_btn)
        bottom.addWidget(self._delete_btn)
        bottom.addStretch()
        self.layout().addLayout(bottom)

    # ── Заполнение ────────────────────────────────────────────────────────────

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
            Qt.CheckState.Checked if tag.id in self._preselected_ids else Qt.CheckState.Unchecked,
        )

    def _on_search(self, text: str) -> None:
        text = text.strip()
        if text:
            self._populate_flat(build_search_results(self._all_tags, self._preselected_ids, text))
        else:
            self._populate_grouped(self._all_tags)
            self._expand_checked_groups()
        self._update_delete_btn()

    def _expand_checked_groups(self) -> None:
        """Раскрыть группы (буквы), в которых есть отмеченные теги."""
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            group = root.child(i)
            for j in range(group.childCount()):
                if group.child(j).checkState(0) == Qt.CheckState.Checked:
                    group.setExpanded(True)
                    break

    # ── Выбор ────────────────────────────────────────────────────────────────

    @property
    def selected_tags(self) -> list[Tag]:
        return self._checked_tags()

    def _checked_tags(self) -> list[Tag]:
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

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column == 0 and item.data(0, Qt.ItemDataRole.UserRole) is not None:
            tag = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(0) == Qt.CheckState.Checked:
                self._preselected_ids.add(tag.id)
            else:
                self._preselected_ids.discard(tag.id)
            self._update_delete_btn()

    def _update_delete_btn(self) -> None:
        if self._delete_btn is not None:
            self._delete_btn.setEnabled(bool(self._checked_tags()))

    # ── Действия ─────────────────────────────────────────────────────────────

    def create_tag(self) -> None:
        dlg = TagDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_tag = dlg.tag
            if self._auto_select_new:
                self._preselected_ids.add(new_tag.id)
            self._cache_add(new_tag)

    def delete_checked(self) -> None:
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
        app_signals.db_changed.emit()
        self._cache_remove(tags)
