from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow, QMenuBar, QWidget, QVBoxLayout, QTabWidget, QToolBar,
)

from src.gui.stats_bar import StatsBar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Домашняя библиотека')
        self.setMinimumSize(800, 600)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()

    # ── Меню ─────────────────────────────────────────────────────────────────

    def _setup_menu(self):
        menubar = self.menuBar()

        # Настройка
        settings_menu = menubar.addMenu('Настройка')
        settings_menu.addAction(self._action('Настройки...', self._on_settings))

        # База данных
        db_menu = menubar.addMenu('База данных')

        shelves_menu = db_menu.addMenu('Полки')
        shelves_menu.addAction(self._action('Добавить полку',      self._on_shelf_add))
        shelves_menu.addAction(self._action('Переименовать полку', self._on_shelf_rename))
        shelves_menu.addAction(self._action('Удалить полку',       self._on_shelf_delete))

        books_menu = db_menu.addMenu('Книги')
        books_menu.addAction(self._action('Добавить книгу',      self._on_book_add))
        books_menu.addAction(self._action('Редактировать книгу', self._on_book_edit))
        books_menu.addAction(self._action('Удалить книгу',       self._on_book_delete))
        books_menu.addSeparator()
        books_menu.addAction(self._action('Поиск книги', self._on_book_search))

        authors_menu = db_menu.addMenu('Авторы')
        authors_menu.addAction(self._action('Добавить автора',      self._on_author_add))
        authors_menu.addAction(self._action('Редактировать автора', self._on_author_edit))
        authors_menu.addAction(self._action('Удалить автора',       self._on_author_delete))

        tags_menu = db_menu.addMenu('Теги')
        tags_menu.addAction(self._action('Добавить тег', self._on_tag_add))
        tags_menu.addAction(self._action('Удалить тег',  self._on_tag_delete))

        # О приложении — правый угол через corner widget
        corner_bar = QMenuBar(self)
        about_menu = corner_bar.addMenu('О приложении')
        about_menu.addAction(self._action('О программе', self._on_about))
        menubar.setCornerWidget(corner_bar, Qt.Corner.TopRightCorner)

        # Одинаковый размер всех пунктов — вычисляем по самому длинному тексту
        self._apply_menubar_style(menubar, corner_bar,
                                  titles=('Настройка', 'База данных', 'О приложении'))

    # ── Панель инструментов ───────────────────────────────────────────────────

    def _setup_toolbar(self):
        toolbar = QToolBar('Основная панель')
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._action('Добавить книгу', self._on_book_add))
        toolbar.addAction(self._action('Поиск',          self._on_book_search))
        toolbar.addSeparator()
        toolbar.addAction(self._action('Добавить полку', self._on_shelf_add))

    # ── Центральная область ───────────────────────────────────────────────────

    def _setup_central(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.shelf_tabs = QTabWidget()
        self.shelf_tabs.setTabsClosable(True)
        self.shelf_tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        layout.addWidget(self.shelf_tabs, stretch=1)

        self.stats_bar = StatsBar()
        layout.addWidget(self.stats_bar)

        self.setCentralWidget(central)

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def _apply_menubar_style(self, *menubars: QMenuBar, titles: tuple[str, ...]) -> None:
        """Задаёт одинаковую ширину всем пунктам меню на основе самого длинного текста."""
        fm = self.menuBar().fontMetrics()
        padding_h = 24  # отступ слева + справа от текста
        min_width = max(fm.horizontalAdvance(t) for t in titles) + padding_h
        style = f'QMenuBar::item {{ min-width: {min_width}px; padding: 4px 12px; }}'
        for bar in menubars:
            bar.setStyleSheet(style)

    def _action(self, title: str, slot) -> QAction:
        action = QAction(title, self)
        action.triggered.connect(slot)
        return action

    def add_shelf_tab(self, name: str, widget: QWidget) -> None:
        """Добавляет новую вкладку полки."""
        index = self.shelf_tabs.addTab(widget, name)
        self.shelf_tabs.setCurrentIndex(index)

    # ── Слоты (заглушки, будут реализованы позже) ─────────────────────────────

    def _on_settings(self):      pass
    def _on_shelf_add(self):     pass
    def _on_shelf_rename(self):  pass
    def _on_shelf_delete(self):  pass
    def _on_tab_close_requested(self, index: int): pass
    def _on_book_add(self):      pass
    def _on_book_edit(self):     pass
    def _on_book_delete(self):   pass
    def _on_book_search(self):   pass
    def _on_author_add(self):    pass
    def _on_author_edit(self):   pass
    def _on_author_delete(self): pass
    def _on_tag_add(self):       pass
    def _on_tag_delete(self):    pass
    def _on_about(self):         pass
