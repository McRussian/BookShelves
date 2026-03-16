from pathlib import Path

from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QMessageBox, QPushButton, QSpinBox,
    QTextEdit, QVBoxLayout,
)

from src.database.models.author import Author
from src.database.models.book import Book, BookAuthor, BookGenre, BookTag
from src.database.models.book_format import BookFormat
from src.database.models.edition import Edition
from src.database.models.publisher import Publisher
from src.gui.dialogs.author_search_dialog import AuthorSearchDialog
from src.gui.dialogs.tag_search_dialog import TagSearchDialog
from src.gui.widgets.chips_widget import ChipsWidget


class BookDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Новая книга')
        self.setMinimumWidth(600)
        self._book: Book | None = None
        self._authors: list[Author] = []

        layout = QVBoxLayout(self)

        # ── Основные поля ─────────────────────────────────────────────────────
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._title = QLineEdit()
        self._title.setPlaceholderText('обязательно')
        form.addRow('Название *:', self._title)

        file_row = QHBoxLayout()
        self._file_path = QLineEdit()
        self._file_path.setReadOnly(True)
        self._file_path.setPlaceholderText('выберите файл...')
        browse_btn = QPushButton('Обзор...')
        browse_btn.clicked.connect(self._on_browse)
        file_row.addWidget(self._file_path, stretch=1)
        file_row.addWidget(browse_btn)
        form.addRow('Файл *:', file_row)

        # Страниц и год — в одну строку
        pages_year_row = QHBoxLayout()
        self._pages = QSpinBox()
        self._pages.setRange(0, 99999)
        self._pages.setSpecialValueText('—')
        self._year = QSpinBox()
        self._year.setRange(0, 2100)
        self._year.setSpecialValueText('—')
        pages_year_row.addWidget(QLabel('Страниц:'))
        pages_year_row.addWidget(self._pages)
        pages_year_row.addSpacing(16)
        pages_year_row.addWidget(QLabel('Год:'))
        pages_year_row.addWidget(self._year)
        pages_year_row.addStretch()
        form.addRow('', pages_year_row)

        # Издание и издательство — в одну строку
        ed_pub_row = QHBoxLayout()
        self._edition_combo = QComboBox()
        self._fill_combo(self._edition_combo, Edition.select(), 'name')
        self._publisher_combo = QComboBox()
        self._fill_combo(self._publisher_combo, Publisher.select(), 'name')
        ed_pub_row.addWidget(QLabel('Издание:'))
        ed_pub_row.addWidget(self._edition_combo, stretch=1)
        ed_pub_row.addSpacing(16)
        ed_pub_row.addWidget(QLabel('Издательство:'))
        ed_pub_row.addWidget(self._publisher_combo, stretch=2)
        form.addRow('', ed_pub_row)

        self._comment = QTextEdit()
        self._comment.setPlaceholderText('необязательно')
        self._comment.setFixedHeight(64)
        form.addRow('Комментарий:', self._comment)

        layout.addLayout(form)

        # ── Авторы ────────────────────────────────────────────────────────────
        layout.addWidget(QLabel('Авторы:'))

        self._authors_list = QListWidget()
        self._authors_list.setFixedHeight(80)
        layout.addWidget(self._authors_list)

        authors_row = QHBoxLayout()
        select_authors_btn = QPushButton('Выбрать авторов...')
        select_authors_btn.clicked.connect(self._on_select_authors)
        authors_row.addWidget(select_authors_btn)
        authors_row.addStretch()
        layout.addLayout(authors_row)

        # ── Теги и жанры — в две колонки ──────────────────────────────────────
        tags_genres_row = QHBoxLayout()

        tags_col = QVBoxLayout()
        tags_col.addWidget(QLabel('Теги:'))
        self._tags_chips = ChipsWidget()
        tags_col.addWidget(self._tags_chips)
        select_tags_btn = QPushButton('Выбрать теги...')
        select_tags_btn.clicked.connect(self._on_select_tags)
        tags_col.addWidget(select_tags_btn)

        genres_col = QVBoxLayout()
        genres_col.addWidget(QLabel('Жанры:'))
        self._genres_chips = ChipsWidget()
        genres_col.addWidget(self._genres_chips)
        add_genre_btn = QPushButton('+ Добавить жанр')
        add_genre_btn.clicked.connect(self._on_add_genre)
        genres_col.addWidget(add_genre_btn)

        tags_genres_row.addLayout(tags_col)
        tags_genres_row.addLayout(genres_col)
        layout.addLayout(tags_genres_row)

        # ── Кнопки ────────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @property
    def book(self) -> Book | None:
        return self._book

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def _fill_combo(self, combo: QComboBox, query, field: str) -> None:
        combo.addItem('—', None)
        for item in query:
            combo.addItem(getattr(item, field), item)

    # ── Слоты ────────────────────────────────────────────────────────────────

    def _on_browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, 'Выбрать файл книги', '',
            'Книги (*.epub *.fb2 *.pdf *.mobi *.djvu);;Все файлы (*)',
        )
        if path:
            self._file_path.setText(path)

    def _on_select_authors(self) -> None:
        dlg = AuthorSearchDialog(self._authors, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._authors = dlg.selected_authors
            self._authors_list.clear()
            for author in self._authors:
                self._authors_list.addItem(author.display_name)

    def _on_select_tags(self) -> None:
        current = self._tags_chips.all_data()
        dlg = TagSearchDialog(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._tags_chips.set_items([(t.name, t) for t in dlg.selected_tags])

    def _on_add_genre(self) -> None:
        pass  # будет реализовано: диалог поиска/выбора жанра

    def _on_accept(self) -> None:
        title = self._title.text().strip()
        if not title:
            QMessageBox.warning(self, 'Ошибка', 'Введите название книги.')
            return

        file_path = self._file_path.text()
        if not file_path:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл книги.')
            return

        p = Path(file_path)
        file_size = p.stat().st_size if p.exists() else None

        ext = p.suffix.lower().lstrip('.')
        fmt, _ = BookFormat.get_or_create(name=ext) if ext else (None, None)

        self._book = Book.create(
            title=title,
            file_path=file_path,
            file_size=file_size,
            pages=self._pages.value() or None,
            year=self._year.value() or None,
            format=fmt,
            edition=self._edition_combo.currentData(),
            publisher=self._publisher_combo.currentData(),
            comment=self._comment.toPlainText().strip() or None,
        )

        for author in self._authors:
            BookAuthor.create(book=self._book, author=author)

        for tag in self._tags_chips.all_data():
            BookTag.create(book=self._book, tag=tag)

        for genre in self._genres_chips.all_data():
            BookGenre.create(book=self._book, genre=genre)

        self.accept()
