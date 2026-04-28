from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QMessageBox, QVBoxLayout,
)

from src.database.models.user import User
from src.utils.normalize import normalize_name


class UserDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Новый пользователь')
        self.setMinimumWidth(360)
        self._user: User | None = None

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._login = QLineEdit()
        self._login.setPlaceholderText('обязательно, уникальный')
        form.addRow('Логин *:', self._login)

        self._firstname = QLineEdit()
        self._firstname.setPlaceholderText('обязательно')
        form.addRow('Имя *:', self._firstname)

        self._lastname = QLineEdit()
        form.addRow('Фамилия:', self._lastname)

        self._surname = QLineEdit()
        form.addRow('Отчество:', self._surname)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def user(self) -> User | None:
        return self._user

    def _on_accept(self) -> None:
        login = self._login.text().strip().lower()
        if not login:
            QMessageBox.warning(self, 'Ошибка', 'Введите логин.')
            return

        firstname = self._firstname.text().strip()
        if not firstname:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя.')
            return

        if User.get_or_none(User.login == login):
            QMessageBox.warning(self, 'Ошибка', f'Логин «{login}» уже занят.')
            return

        self._user = User.create(
            login=login,
            firstname=normalize_name(firstname),
            lastname=normalize_name(self._lastname.text()) or None,
            surname=normalize_name(self._surname.text()) or None,
        )
        self.accept()
