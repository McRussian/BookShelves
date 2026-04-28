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
        self._list.currentItemChanged.connect(self._update_buttons)
        self._list.itemDoubleClicked.connect(self._on_edit)
        layout.addWidget(self._list, stretch=1)

        self._add_btn = QPushButton('Добавить')
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
        current_id = None
        if current := self._list.currentItem():
            if pub := current.data(Qt.ItemDataRole.UserRole):
                current_id = pub.id

        self._list.clear()
        for pub in publishers:
            item = QListWidgetItem(pub.name)
            item.setData(Qt.ItemDataRole.UserRole, pub)
            if pub.comment:
                item.setToolTip(pub.comment)
            self._list.addItem(item)
            if pub.id == current_id:
                self._list.setCurrentItem(item)

        self._update_buttons()

    def _update_buttons(self) -> None:
        has = self._list.currentItem() is not None
        self._edit_btn.setEnabled(has)
        self._delete_btn.setEnabled(has)

    # ── Действия ─────────────────────────────────────────────────────────────

    def _on_add(self) -> None:
        dlg = PublisherDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload()

    def _on_edit(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        publisher = item.data(Qt.ItemDataRole.UserRole)
        dlg = PublisherDialog(publisher, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._reload()

    def _on_delete(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        publisher = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, 'Удаление',
            f'Удалить издательство «{publisher.name}»?\n\nСвязанные книги сохранятся.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        publisher.delete_instance()
        app_signals.db_changed.emit()
        self._reload()
