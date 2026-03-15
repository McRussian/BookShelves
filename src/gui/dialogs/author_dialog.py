from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout,
)

from src.database.models.author import Author, AuthorAlias


class AuthorDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Новый автор')
        self.setMinimumWidth(420)
        self._author: Author | None = None
        self._aliases: list[str] = []

        layout = QVBoxLayout(self)

        # ── Основные поля ─────────────────────────────────────────────────────
        form = QFormLayout()

        self._firstname = QLineEdit()
        self._firstname.setPlaceholderText('обязательно')
        form.addRow('Имя *:', self._firstname)

        self._lastname = QLineEdit()
        form.addRow('Фамилия:', self._lastname)

        self._surname = QLineEdit()
        form.addRow('Отчество:', self._surname)

        self._comment = QTextEdit()
        self._comment.setPlaceholderText('необязательно')
        self._comment.setFixedHeight(64)
        form.addRow('Комментарий:', self._comment)

        layout.addLayout(form)

        # ── Псевдонимы ────────────────────────────────────────────────────────
        layout.addWidget(QLabel('Псевдонимы:'))

        self._aliases_list = QListWidget()
        self._aliases_list.setFixedHeight(90)
        layout.addWidget(self._aliases_list)

        alias_row = QHBoxLayout()
        self._alias_edit = QLineEdit()
        self._alias_edit.setPlaceholderText('Введите псевдоним...')
        self._alias_edit.returnPressed.connect(self._on_add_alias)

        add_btn = QPushButton('Добавить')
        add_btn.clicked.connect(self._on_add_alias)

        remove_btn = QPushButton('Удалить')
        remove_btn.clicked.connect(self._on_remove_alias)

        alias_row.addWidget(self._alias_edit, stretch=1)
        alias_row.addWidget(add_btn)
        alias_row.addWidget(remove_btn)
        layout.addLayout(alias_row)

        # ── Кнопки ────────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def author(self) -> Author | None:
        return self._author

    # ── Слоты ────────────────────────────────────────────────────────────────

    def _on_add_alias(self) -> None:
        alias = self._alias_edit.text().strip()
        if not alias:
            return
        if alias in self._aliases:
            QMessageBox.warning(self, 'Ошибка', f'Псевдоним «{alias}» уже добавлен.')
            return
        self._aliases.append(alias)
        self._aliases_list.addItem(alias)
        self._alias_edit.clear()

    def _on_remove_alias(self) -> None:
        row = self._aliases_list.currentRow()
        if row >= 0:
            self._aliases.pop(row)
            self._aliases_list.takeItem(row)

    def _on_accept(self) -> None:
        firstname = self._firstname.text().strip()
        if not firstname:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя автора.')
            return

        self._author = Author.create(
            firstname=firstname,
            lastname=self._lastname.text().strip() or None,
            surname=self._surname.text().strip() or None,
            comment=self._comment.toPlainText().strip() or None,
        )
        for alias in self._aliases:
            AuthorAlias.create(author=self._author, alias=alias)

        self.accept()
