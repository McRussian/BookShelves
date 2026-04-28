from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout,
)

from src.database.models.publisher import Publisher
from src.gui.app_signals import app_signals
from src.gui.publishers.publisher_dialog import PublisherDialog


class PublisherManageDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Издательства')
        self.setMinimumSize(420, 460)

        layout = QVBoxLayout(self)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по названию...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._list = QListWidget()
        self._list.itemChanged.connect(self._on_item_changed)
        self._list.itemDoubleClicked.connect(self._on_edit_item)
        layout.addWidget(self._list, stretch=1)

        self._add_btn = QPushButton('+ Добавить')
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn = QPushButton('Редактировать')
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._on_edit)
        self._delete_btn = QPushButton('Удалить')
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(self._add_btn)
        bottom.addWidget(self._edit_btn)
        bottom.addWidget(self._delete_btn)
        bottom.addStretch()
        bottom.addWidget(close_btn)
        layout.addLayout(bottom)

        self._reload()

    # ── Заполнение ────────────────────────────────────────────────────────────

    def _reload(self) -> None:
        self._on_search(self._search.text())

    def _on_search(self, text: str) -> None:
        text = text.strip()
        publishers = Publisher.search(text) if text else Publisher.select().order_by(Publisher.name)
        self._populate(publishers)

    def _populate(self, publishers) -> None:
        self._list.blockSignals(True)
        self._list.clear()
        for pub in publishers:
            item = QListWidgetItem(pub.name)
            item.setData(Qt.ItemDataRole.UserRole, pub)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled |
                Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(Qt.CheckState.Unchecked)
            if pub.comment:
                item.setToolTip(pub.comment)
            self._list.addItem(item)
        self._list.blockSignals(False)
        self._update_buttons()

    # ── Выбор ────────────────────────────────────────────────────────────────

    def _checked_publishers(self) -> list[Publisher]:
        result = []
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                result.append(item.data(Qt.ItemDataRole.UserRole))
        return result

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        self._update_buttons()

    def _update_buttons(self) -> None:
        checked = self._checked_publishers()
        self._delete_btn.setEnabled(bool(checked))
        self._edit_btn.setEnabled(len(checked) == 1)

    # ── Действия ─────────────────────────────────────────────────────────────

    def _on_add(self) -> None:
        dlg = PublisherDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload()

    def _on_edit(self) -> None:
        checked = self._checked_publishers()
        if len(checked) != 1:
            return
        self._open_edit_dialog(checked[0])

    def _on_edit_item(self, item: QListWidgetItem) -> None:
        self._open_edit_dialog(item.data(Qt.ItemDataRole.UserRole))

    def _open_edit_dialog(self, publisher: Publisher) -> None:
        dlg = PublisherDialog(publisher, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload()

    def _on_delete(self) -> None:
        publishers = self._checked_publishers()
        if not publishers:
            return
        names = '\n'.join(p.name for p in publishers)
        reply = QMessageBox.question(
            self, 'Удаление',
            f'Удалить из базы данных?\n\n{names}\n\nСвязанные книги сохранятся.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for pub in publishers:
            pub.delete_instance()
        app_signals.db_changed.emit()
        self._reload()
