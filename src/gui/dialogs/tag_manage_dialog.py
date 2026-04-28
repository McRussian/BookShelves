from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from src.gui.widgets.tag_manage_widget import TagManageWidget


class TagManageDialog(QDialog):
    """Диалог управления тегами: просмотр, создание, удаление."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Управление тегами')
        self.setMinimumSize(440, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(TagManageWidget(self), stretch=1)

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)
