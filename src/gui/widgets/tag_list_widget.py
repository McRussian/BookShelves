from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from src.database.models.tag import Tag


def filter_tags(tags: list, query: str) -> list:
    """Фильтр по подстроке без учёта регистра; работает с кириллицей через str.lower()."""
    q = query.lower()
    return [t for t in tags if q in t.name.lower()]


def build_search_results(tags: list, selected_ids: set, query: str) -> list:
    """Список тегов для отображения при поиске.

    Отмеченные теги показываются первыми, даже если не совпадают с запросом.
    """
    matched = filter_tags(tags, query)
    matched_ids = {t.id for t in matched}
    checked_extra = [t for t in tags if t.id in selected_ids and t.id not in matched_ids]
    return checked_extra + matched


class TagListWidget(QWidget):
    """Базовый виджет: дерево тегов + поиск + in-memory кеш.

    Подклассы переопределяют _add_tag_item и _on_search для специфического поведения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_tags: list[Tag] = list(Tag.select().order_by(Tag.name))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._search = QLineEdit()
        self._search.setPlaceholderText('Поиск по названию...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        layout.addWidget(self._tree, stretch=1)

        self._populate_grouped(self._all_tags)

    # ── Заполнение дерева ─────────────────────────────────────────────────────

    def _populate_grouped(self, tags) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        groups: dict[str, QTreeWidgetItem] = {}
        bold = QFont()
        bold.setBold(True)

        for tag in tags:
            name = tag.name or '?'
            letter = name[1].upper() if name.startswith('#') and len(name) > 1 else name[0].upper()
            if letter not in groups:
                group_item = QTreeWidgetItem(self._tree, [letter])
                group_item.setFont(0, bold)
                group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                group_item.setExpanded(False)
                groups[letter] = group_item
            self._add_tag_item(groups[letter], tag)

        self._tree.blockSignals(False)

    def _populate_flat(self, tags) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()
        for tag in tags:
            self._add_tag_item(self._tree.invisibleRootItem(), tag)
        self._tree.blockSignals(False)

    def _add_tag_item(self, parent: QTreeWidgetItem, tag: Tag) -> None:
        item = QTreeWidgetItem(parent, [tag.name])
        item.setData(0, Qt.ItemDataRole.UserRole, tag)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

    def _on_search(self, text: str) -> None:
        text = text.strip()
        if text:
            self._populate_flat(filter_tags(self._all_tags, text))
        else:
            self._populate_grouped(self._all_tags)

    # ── Кеш ──────────────────────────────────────────────────────────────────

    def _cache_add(self, tag: Tag) -> None:
        self._all_tags.append(tag)
        self._all_tags.sort(key=lambda t: t.name)
        self._on_search(self._search.text())

    def _cache_remove(self, tags: list[Tag]) -> None:
        deleted_ids = {t.id for t in tags}
        self._all_tags = [t for t in self._all_tags if t.id not in deleted_ids]
        self._on_search(self._search.text())
