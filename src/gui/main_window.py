from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog, QMainWindow, QMenuBar, QMessageBox,
    QTabWidget, QToolBar, QVBoxLayout, QWidget,
)

from src.gui.stats_bar import StatsBar
from src.settings import Settings


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Домашняя библиотека')
        self.setMinimumSize(800, 600)

        self._settings = Settings()

        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()
        self._set_db_active(self._settings.db_path is not None)

    # ── Меню ─────────────────────────────────────────────────────────────────

    def _setup_menu(self):
        menubar = self.menuBar()

        # Настройка
        settings_menu = menubar.addMenu('Настройка')

        db_settings_menu = settings_menu.addMenu('Настройка БД')
        db_settings_menu.addAction(self._action('Создать', self._on_db_create))
        db_settings_menu.addAction(self._action('Открыть', self._on_db_open))
        db_settings_menu.addSeparator()
        db_settings_menu.addAction(self._action('Удалить', self._on_db_delete))

        settings_menu.addAction(self._action('Настройка приложений', self._on_app_settings))

        # База данных
        self._db_menu = menubar.addMenu('База данных')

        shelves_menu = self._db_menu.addMenu('Полки')
        shelves_menu.addAction(self._action('Добавить полку',      self._on_shelf_add))
        shelves_menu.addAction(self._action('Переименовать полку', self._on_shelf_rename))
        shelves_menu.addAction(self._action('Удалить полку',       self._on_shelf_delete))

        books_menu = self._db_menu.addMenu('Книги')
        books_menu.addAction(self._action('Добавить книгу',      self._on_book_add))
        books_menu.addAction(self._action('Редактировать книгу', self._on_book_edit))
        books_menu.addAction(self._action('Удалить книгу',       self._on_book_delete))
        books_menu.addSeparator()
        books_menu.addAction(self._action('Поиск книги', self._on_book_search))

        authors_menu = self._db_menu.addMenu('Авторы')
        authors_menu.addAction(self._action('Добавить автора',      self._on_author_add))
        authors_menu.addAction(self._action('Редактировать автора', self._on_author_edit))
        authors_menu.addAction(self._action('Удалить автора',       self._on_author_delete))

        tags_menu = self._db_menu.addMenu('Теги')
        tags_menu.addAction(self._action('Добавить тег', self._on_tag_add))
        tags_menu.addAction(self._action('Удалить тег',  self._on_tag_delete))

        # О приложении — правый угол
        corner_bar = QMenuBar(self)
        about_menu = corner_bar.addMenu('О приложении')
        about_menu.addAction(self._action('О программе', self._on_about))
        menubar.setCornerWidget(corner_bar, Qt.Corner.TopRightCorner)

        self._apply_menubar_style(menubar, corner_bar,
                                  titles=('Настройка', 'База данных', 'О приложении'))

    # ── Панель инструментов ───────────────────────────────────────────────────

    def _setup_toolbar(self):
        self._toolbar = QToolBar('Основная панель')
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)

        self._toolbar.addAction(self._action('Добавить книгу', self._on_book_add))
        self._toolbar.addAction(self._action('Поиск',          self._on_book_search))
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action('Добавить полку', self._on_shelf_add))

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

    def _set_db_active(self, active: bool) -> None:
        """Показывает или скрывает элементы, зависящие от наличия открытой БД."""
        self._db_menu.setEnabled(active)
        self._toolbar.setVisible(active)
        self.stats_bar.setVisible(active)

    def _apply_menubar_style(self, *menubars: QMenuBar, titles: tuple[str, ...]) -> None:
        fm = self.menuBar().fontMetrics()
        padding_h = 24
        min_width = max(fm.horizontalAdvance(t) for t in titles) + padding_h
        style = f'QMenuBar::item {{ min-width: {min_width}px; padding: 4px 12px; }}'
        for bar in menubars:
            bar.setStyleSheet(style)

    def _action(self, title: str, slot) -> QAction:
        action = QAction(title, self)
        action.triggered.connect(slot)
        return action

    def add_shelf_tab(self, name: str, widget: QWidget) -> None:
        index = self.shelf_tabs.addTab(widget, name)
        self.shelf_tabs.setCurrentIndex(index)

    # ── Слоты: настройка БД ───────────────────────────────────────────────────

    def _on_db_create(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Создать базу данных', '', 'SQLite Database (*.db)'
        )
        if not path:
            return
        if not path.endswith('.db'):
            path += '.db'
        db_path = Path(path)
        db_path.touch()
        self._settings.db_path = db_path
        self._set_db_active(True)

    def _on_db_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Открыть базу данных', '', 'SQLite Database (*.db)'
        )
        if not path:
            return
        self._settings.db_path = Path(path)
        self._set_db_active(True)

    def _on_db_delete(self):
        db_path = self._settings.db_path
        if not db_path:
            return
        reply = QMessageBox.question(
            self,
            'Удаление базы данных',
            f'Удалить файл базы данных?\n\n{db_path}',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            db_path.unlink()
        except FileNotFoundError:
            pass
        self._settings.db_path = None
        self._set_db_active(False)

    # ── Слоты (заглушки) ──────────────────────────────────────────────────────

    def _on_app_settings(self):      pass
    def _on_shelf_add(self):         pass
    def _on_shelf_rename(self):      pass
    def _on_shelf_delete(self):      pass
    def _on_tab_close_requested(self, index: int): pass
    def _on_book_add(self):          pass
    def _on_book_edit(self):         pass
    def _on_book_delete(self):       pass
    def _on_book_search(self):       pass
    def _on_author_add(self):        pass
    def _on_author_edit(self):       pass
    def _on_author_delete(self):     pass
    def _on_tag_add(self):           pass
    def _on_tag_delete(self):        pass
    def _on_about(self):             pass
