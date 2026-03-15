from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame


class StatsBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setFrameShape(QFrame.Shape.StyledPanel) if hasattr(self, 'setFrameShape') else None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)

        self._books_label = QLabel('Книг: —')
        self._authors_label = QLabel('Авторов: —')
        self._size_label = QLabel('Размер: —')

        for label in (self._books_label, self._authors_label, self._size_label):
            layout.addWidget(label)
            if label is not self._size_label:
                sep = QLabel('|')
                layout.addWidget(sep)

        layout.addStretch()

    def update_stats(self, books: int, authors: int, size_bytes: int) -> None:
        self._books_label.setText(f'Книг: {books}')
        self._authors_label.setText(f'Авторов: {authors}')
        self._size_label.setText(f'Размер: {self._format_size(size_bytes)}')

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes >= 1024 ** 3:
            return f'{size_bytes / 1024 ** 3:.1f} ГБ'
        if size_bytes >= 1024 ** 2:
            return f'{size_bytes / 1024 ** 2:.1f} МБ'
        if size_bytes >= 1024:
            return f'{size_bytes / 1024:.1f} КБ'
        return f'{size_bytes} Б'
