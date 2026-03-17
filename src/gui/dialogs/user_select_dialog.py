from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMessageBox,
    QPushButton, QVBoxLayout,
)

from src.database.models.user import User
from src.gui.dialogs.user_dialog import UserDialog


class UserSelectDialog(QDialog):

    def __init__(self, last_user_id: int | None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Выбор пользователя')
        self.setMinimumSize(340, 320)
        self._selected: User | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Выберите пользователя:'))

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_accept)
        layout.addWidget(self._list, stretch=1)

        add_btn = QPushButton('+ Добавить пользователя')
        add_btn.clicked.connect(self._on_add)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        bottom.addWidget(add_btn)
        bottom.addStretch()
        bottom.addWidget(buttons)
        layout.addLayout(bottom)

        self._populate(last_user_id)

    @property
    def selected_user(self) -> User | None:
        return self._selected

    def _populate(self, select_id: int | None) -> None:
        self._list.clear()
        users = list(User.select().order_by(User.lastname, User.firstname))
        for user in users:
            item = QListWidgetItem(user.display_name)
            item.setData(Qt.ItemDataRole.UserRole, user)
            self._list.addItem(item)
            if user.id == select_id:
                self._list.setCurrentItem(item)

        if self._list.currentItem() is None and self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_add(self) -> None:
        dlg = UserDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._populate(dlg.user.id)

    def _on_accept(self) -> None:
        item = self._list.currentItem()
        if item is None:
            QMessageBox.warning(self, 'Ошибка', 'Выберите пользователя.')
            return
        self._selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
