import shlex
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from src.settings import Settings

POPULAR_FORMATS = [
    'epub', 'pdf', 'fb2', 'mobi', 'djvu',
    'azw3', 'cbz', 'cbr', 'doc', 'docx', 'txt',
]


class AppSettingsDialog(QDialog):
    """Настройка приложений для открытия файлов по формату."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Настройка приложений')
        self.setMinimumWidth(560)
        self._settings = Settings()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            'Укажите команду для каждого формата. '
            'Используйте <b>%f</b> как путь к файлу.'
        ))

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Формат', 'Команда'])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton('+ Добавить')
        add_btn.clicked.connect(self._on_add)
        self._del_btn = QPushButton('Удалить')
        self._del_btn.clicked.connect(self._on_delete)
        self._del_btn.setEnabled(False)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(self._del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.accept)
        layout.addWidget(close)

        self._table.itemSelectionChanged.connect(
            lambda: self._del_btn.setEnabled(bool(self._table.selectedItems()))
        )

        self._load()

    def _load(self) -> None:
        for r in self._settings.file_readers:
            self._add_row(r.get('extension', ''), r.get('command', ''))

    def _add_row(self, ext: str, cmd: str) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(ext))
        self._table.setItem(row, 1, QTableWidgetItem(cmd))

    def _on_add(self) -> None:
        dlg = _AddReaderDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._add_row(dlg.extension, dlg.command)
            self._save()

    def _on_delete(self) -> None:
        rows = sorted({i.row() for i in self._table.selectedItems()}, reverse=True)
        for row in rows:
            self._table.removeRow(row)
        self._save()

    def _save(self) -> None:
        readers = []
        for row in range(self._table.rowCount()):
            ext = (self._table.item(row, 0) or QTableWidgetItem()).text().strip()
            cmd = (self._table.item(row, 1) or QTableWidgetItem()).text().strip()
            if ext and cmd:
                readers.append({'extension': ext, 'command': cmd})
        self._settings.file_readers = readers

    def closeEvent(self, event):
        self._save()
        super().closeEvent(event)


class _AddReaderDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить формат')
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        form_ext = QHBoxLayout()
        form_ext.addWidget(QLabel('Формат:'))
        self._ext_combo = QComboBox()
        self._ext_combo.setEditable(True)
        self._ext_combo.addItems(POPULAR_FORMATS)
        self._ext_combo.setCurrentText('')
        form_ext.addWidget(self._ext_combo, stretch=1)
        layout.addLayout(form_ext)

        form_cmd = QHBoxLayout()
        form_cmd.addWidget(QLabel('Команда:'))
        self._cmd_edit = QLineEdit()
        self._cmd_edit.setPlaceholderText('/usr/bin/foliate %f')
        form_cmd.addWidget(self._cmd_edit, stretch=1)
        browse_btn = QPushButton('…')
        browse_btn.setFixedWidth(28)
        browse_btn.clicked.connect(self._browse)
        form_cmd.addWidget(browse_btn)
        layout.addLayout(form_cmd)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, 'Выбрать приложение', '/usr/bin')
        if path:
            self._cmd_edit.setText(f'{path} %f')

    @property
    def extension(self) -> str:
        return self._ext_combo.currentText().strip().lower().lstrip('.')

    @property
    def command(self) -> str:
        return self._cmd_edit.text().strip()
