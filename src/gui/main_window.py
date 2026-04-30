from pathlib import Path

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QFileDialog, QInputDialog, QLineEdit, QMainWindow, QMenuBar, QMessageBox,
    QSizePolicy, QTabWidget, QToolBar, QToolButton, QVBoxLayout, QWidget,
)
from peewee import fn

from src.database.database import create_db, database_proxy, init_db
from src.database.migrations import run_migrations
from src.database.models import ALL_MODELS
from src.database.models.author import Author
from src.database.models.book import Book
from src.database.models.shelf import Shelf
from src.database.models.user import User
from src.database.seed import seed_reference_data
from src.gui.app_signals import app_signals
from src.gui.authors.author_dialog import AuthorDialog
from src.gui.authors.author_manage_dialog import AuthorManageDialog
from src.gui.settings.app_settings_dialog import AppSettingsDialog
from src.gui.shelves.shelf_manage_dialog import ShelfManageDialog
from src.gui.shelves.shelf_widget import ShelfWidget
from src.gui.books.book_dialog import BookDialog
from src.gui.books.book_manage_dialog import BookManageDialog
from src.gui.publishers.publisher_dialog import PublisherDialog
from src.gui.publishers.publisher_manage_dialog import PublisherManageDialog
from src.gui.tags.tag_dialog import TagDialog
from src.gui.tags.tag_manage_dialog import TagManageDialog
from src.gui.users.user_dialog import UserDialog
from src.gui.users.user_select_dialog import UserSelectDialog
from src.gui.widgets.stats_bar import StatsBar
from src.settings import Settings


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Домашняя библиотека')
        self.setMinimumSize(800, 600)

        self._settings = Settings()
        self._current_user: User | None = None

        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()

        db_path = self._settings.db_path
        if db_path and db_path.exists():
            self._open_db(db_path)
        else:
            self._settings.db_path = None
            self._set_db_active(False)

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
        shelves_menu.addAction(self._action('Добавить полку',    self._on_shelf_add))
        shelves_menu.addAction(self._action('Управление полками', self._on_shelf_manage))

        books_menu = self._db_menu.addMenu('Книги')
        books_menu.addAction(self._action('Добавить книгу', self._on_book_add))
        books_menu.addAction(self._action('Поиск книги',   self._on_book_search))

        authors_menu = self._db_menu.addMenu('Авторы')
        authors_menu.addAction(self._action('Добавить автора', self._on_author_add))
        authors_menu.addAction(self._action('Поиск авторов',  self._on_author_search))

        publishers_menu = self._db_menu.addMenu('Издательства')
        publishers_menu.addAction(self._action('Добавить издательство', self._on_publisher_add))
        publishers_menu.addAction(self._action('Поиск издательств',     self._on_publisher_search))

        tags_menu = self._db_menu.addMenu('Теги')
        tags_menu.addAction(self._action('Добавить тег',  self._on_tag_add))
        tags_menu.addAction(self._action('Поиск тегов',  self._on_tag_search))

        # Пользователи
        self._users_menu = menubar.addMenu('Пользователи')
        self._users_menu.addAction(self._action('Добавить пользователя', self._on_user_add))
        self._users_menu.addAction(self._action('Удалить пользователя',  self._on_user_delete))
        self._users_menu.addAction(self._action('Статистика',            self._on_user_stats))
        self._users_menu.addSeparator()
        self._users_menu.addAction(self._action('Сменить пользователя',  self._on_user_switch))

        # О приложении — правый угол
        corner_bar = QMenuBar(self)
        about_menu = corner_bar.addMenu('О приложении')
        about_menu.addAction(self._action('О программе', self._on_about))
        menubar.setCornerWidget(corner_bar, Qt.Corner.TopRightCorner)

        self._apply_menubar_style(
            menubar, corner_bar,
            titles=('Настройка', 'База данных', 'Пользователи', 'О приложении'),
        )

    # ── Панель инструментов ───────────────────────────────────────────────────

    def _setup_toolbar(self):
        self._toolbar = QToolBar('Основная панель')
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)

        self._toolbar.addAction(self._action('Добавить книгу', self._on_book_add))
        self._toolbar.addAction(self._action('Поиск',          self._on_book_search))
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action('Добавить полку', self._on_shelf_add))
        self._toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._toolbar.addWidget(spacer)

        self._user_btn = QToolButton()
        self._user_btn.setIcon(QIcon.fromTheme(
            'system-log-out',
            self.style().standardIcon(self.style().StandardPixmap.SP_DialogCloseButton),
        ))
        self._user_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._user_btn.clicked.connect(self._on_user_switch)
        self._toolbar.addWidget(self._user_btn)

    # ── Центральная область ───────────────────────────────────────────────────

    def _setup_central(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.shelf_tabs = QTabWidget()
        self.shelf_tabs.setTabsClosable(True)
        self.shelf_tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        self.shelf_tabs.tabBar().installEventFilter(self)
        layout.addWidget(self.shelf_tabs, stretch=1)

        self.stats_bar = StatsBar()
        layout.addWidget(self.stats_bar)

        self.setCentralWidget(central)

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        self._close_db()
        super().closeEvent(event)

    def _set_db_active(self, active: bool) -> None:
        self._db_menu.setEnabled(active)
        self._users_menu.setEnabled(active)
        self._toolbar.setVisible(active)
        self.stats_bar.setVisible(active)

    def eventFilter(self, obj, event) -> bool:
        if obj is self.shelf_tabs.tabBar() and event.type() == QEvent.Type.MouseButtonDblClick:
            index = self.shelf_tabs.tabBar().tabAt(event.pos())
            if index >= 0 and isinstance(self.shelf_tabs.widget(index), ShelfWidget):
                self._start_tab_rename(index)
                return True
        return super().eventFilter(obj, event)

    def _start_tab_rename(self, index: int) -> None:
        tab_bar = self.shelf_tabs.tabBar()
        rect = tab_bar.tabRect(index)
        editor = QLineEdit(tab_bar)
        editor.setText(self.shelf_tabs.tabText(index))
        editor.setGeometry(rect)
        editor.selectAll()
        editor.show()
        editor.setFocus()
        self._tab_editor = editor

        committed = [False]

        def commit():
            if committed[0]:
                return
            committed[0] = True
            name = editor.text().strip()
            editor.deleteLater()
            self._tab_editor = None
            if not name:
                return
            w = self.shelf_tabs.widget(index)
            if not isinstance(w, ShelfWidget) or name == w.shelf.name:
                return
            try:
                w.shelf.name = name
                w.shelf.save()
                self.shelf_tabs.setTabText(index, name)
            except Exception:
                w.shelf = Shelf.get_by_id(w.shelf.id)
                QMessageBox.warning(self, 'Ошибка', f'Полка «{name}» уже существует.')

        editor.returnPressed.connect(commit)
        editor.editingFinished.connect(commit)

    def _logout(self) -> None:
        """Очистить UI текущего пользователя."""
        self._current_user = None
        self._user_btn.setText('')
        self.shelf_tabs.clear()

    def _login(self, user: User) -> None:
        """Загрузить UI для выбранного пользователя."""
        self._current_user = user
        self._settings.last_user_id = user.id
        self._user_btn.setText(f'  {user.login}')
        app_signals.user_changed.emit(user)
        for shelf in Shelf.for_user(user):
            if shelf.is_active:
                self._open_shelf_tab(shelf)

    def _open_shelf_tab(self, shelf: Shelf) -> None:
        shelf.is_active = True
        shelf.save()
        widget = ShelfWidget(shelf)
        self.shelf_tabs.addTab(widget, shelf.name)
        self.shelf_tabs.setCurrentWidget(widget)

    def _open_ids(self) -> set[int]:
        ids = set()
        for i in range(self.shelf_tabs.count()):
            w = self.shelf_tabs.widget(i)
            if isinstance(w, ShelfWidget):
                ids.add(w.shelf.id)
        return ids

    def _current_shelf_widget(self) -> ShelfWidget | None:
        w = self.shelf_tabs.currentWidget()
        return w if isinstance(w, ShelfWidget) else None

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

    # ── Открытие / закрытие БД ────────────────────────────────────────────────

    def _close_db(self) -> None:
        try:
            app_signals.db_changed.disconnect(self._refresh_stats)
        except RuntimeError:
            pass
        db = database_proxy.obj
        if db and not db.is_closed():
            db.close()

    def _open_db(self, db_path: Path) -> None:
        db = init_db(db_path)
        db.create_tables(ALL_MODELS, safe=True)
        run_migrations(db)
        seed_reference_data()
        app_signals.db_changed.connect(self._refresh_stats)
        self._set_db_active(True)
        self._refresh_stats()
        self._select_user_on_open()

    def _select_user_on_open(self) -> None:
        """Показывает диалог выбора пользователя с предвыбранным последним."""
        self._on_user_switch()

    def _refresh_stats(self) -> None:
        books = Book.select().count()
        authors = Author.select().count()
        size = Book.select(fn.SUM(Book.file_size)).scalar() or 0
        self.stats_bar.update_stats(books, authors, size)

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
        self._close_db()
        self._settings.db_path = db_path
        create_db(db_path)
        self._open_db(db_path)

    def _on_db_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Открыть базу данных', '', 'SQLite Database (*.db)'
        )
        if not path:
            return
        self._settings.db_path = Path(path)
        self._close_db()
        self._open_db(Path(path))

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
        self._close_db()
        try:
            db_path.unlink()
        except FileNotFoundError:
            pass
        self._settings.db_path = None
        self._current_user = None
        self._set_db_active(False)

    # ── Слоты: пользователи ───────────────────────────────────────────────────

    def _on_user_add(self):
        dlg = UserDialog(self)
        dlg.exec()

    def _on_user_switch(self):
        self._logout()
        dlg = UserSelectDialog(self._settings.last_user_id, self)
        if dlg.exec() == UserSelectDialog.DialogCode.Accepted:
            self._login(dlg.selected_user)

    def _on_user_delete(self):  pass
    def _on_user_stats(self):   pass

    # ── Слоты (заглушки) ──────────────────────────────────────────────────────

    def _on_app_settings(self):
        AppSettingsDialog(self).exec()
    def _on_shelf_add(self):
        if not self._current_user:
            return
        name, ok = QInputDialog.getText(self, 'Новая полка', 'Название полки:')
        name = name.strip()
        if not ok or not name:
            return
        try:
            shelf = Shelf.create(name=name, user=self._current_user)
        except Exception:
            QMessageBox.warning(self, 'Ошибка', f'Полка «{name}» уже существует.')
            return
        self._open_shelf_tab(shelf)

    def _on_shelf_manage(self):
        if not self._current_user:
            return
        shelves = Shelf.for_user(self._current_user)
        if not shelves:
            QMessageBox.information(self, 'Полки', 'У вас пока нет полок.')
            return
        dlg = ShelfManageDialog(shelves, self._open_ids(), self)
        if dlg.exec() == ShelfManageDialog.DialogCode.Accepted and dlg.opened_shelf:
            self._open_shelf_tab(dlg.opened_shelf)
        else:
            self._sync_tabs_after_manage()

    def _sync_tabs_after_manage(self) -> None:
        """Закрыть табы удалённых в диалоге полок."""
        for i in range(self.shelf_tabs.count() - 1, -1, -1):
            w = self.shelf_tabs.widget(i)
            if isinstance(w, ShelfWidget) and not Shelf.get_or_none(Shelf.id == w.shelf.id):
                self.shelf_tabs.removeTab(i)

    def _on_tab_close_requested(self, index: int):
        w = self.shelf_tabs.widget(index)
        if isinstance(w, ShelfWidget):
            w.shelf.is_active = False
            w.shelf.save()
        self.shelf_tabs.removeTab(index)

    def _on_book_add(self):
        dlg = BookDialog(parent=self)
        dlg.exec()

    def _on_book_search(self):
        dlg = BookManageDialog(self)
        dlg.exec()

    def _on_author_add(self):
        dlg = AuthorDialog(self)
        dlg.exec()

    def _on_author_edit(self):       pass

    def _on_author_search(self):
        dlg = AuthorManageDialog(self)
        dlg.exec()

    def _on_publisher_add(self):
        dlg = PublisherDialog(parent=self)
        dlg.exec()

    def _on_publisher_search(self):
        dlg = PublisherManageDialog(self)
        dlg.exec()

    def _on_tag_add(self):
        dlg = TagDialog(self)
        dlg.exec()

    def _on_tag_search(self):
        dlg = TagManageDialog(self)
        dlg.exec()
    def _on_about(self):             pass
