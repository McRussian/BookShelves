from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QTextEdit, QVBoxLayout,
)

from src.database.models.publisher import Publisher
from src.gui.app_signals import app_signals


class PublisherDialog(QDialog):

    def __init__(self, publisher: Publisher | None = None, parent=None):
        super().__init__(parent)
        self._publisher = publisher
        self.setWindowTitle('Редактировать издательство' if publisher else 'Новое издательство')
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._name = QLineEdit(publisher.name if publisher else '')
        self._name.setPlaceholderText('обязательно')
        form.addRow('Название *:', self._name)

        self._comment = QTextEdit(publisher.comment or '' if publisher else '')
        self._comment.setPlaceholderText('необязательно')
        self._comment.setFixedHeight(80)
        form.addRow('Комментарий:', self._comment)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def publisher(self) -> Publisher | None:
        return self._publisher

    def _on_accept(self) -> None:
        name = self._name.text().strip()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название издательства.')
            return

        existing = Publisher.get_or_none(Publisher.name == name)
        if existing and (self._publisher is None or existing.id != self._publisher.id):
            QMessageBox.warning(self, 'Дубликат', f'Издательство «{name}» уже существует.')
            return

        comment = self._comment.toPlainText().strip() or None

        if self._publisher:
            self._publisher.name = name
            self._publisher.comment = comment
            self._publisher.save()
        else:
            self._publisher = Publisher.create(name=name, comment=comment)

        app_signals.db_changed.emit()
        self.accept()
