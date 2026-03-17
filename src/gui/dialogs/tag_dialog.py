from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QMessageBox, QVBoxLayout,
)

from src.database.models.tag import Tag
from src.gui.app_signals import app_signals
from src.utils.normalize import normalize_tag


class TagDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Новый тег')
        self.setMinimumWidth(300)
        self._tag: Tag | None = None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText('Название тега...')
        form.addRow('Название *:', self._name_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def tag(self) -> Tag | None:
        return self._tag

    def _on_accept(self) -> None:
        raw = self._name_edit.text().strip()
        if not raw:
            QMessageBox.warning(self, 'Ошибка', 'Введите название тега.')
            return
        name = normalize_tag(raw)
        if Tag.get_or_none(Tag.name == name):
            QMessageBox.warning(self, 'Ошибка', f'Тег «{name}» уже существует.')
            return
        self._tag = Tag.create(name=name)
        app_signals.db_changed.emit()
        self.accept()
