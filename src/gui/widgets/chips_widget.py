from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)


class _Chip(QFrame):
    """Один чип: текст + кнопка ×."""

    removed = pyqtSignal()

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 2, 2)
        layout.setSpacing(2)

        layout.addWidget(QLabel(label))

        btn = QToolButton()
        btn.setText('×')
        btn.setFixedSize(16, 16)
        btn.setAutoRaise(True)
        btn.clicked.connect(self.removed)
        layout.addWidget(btn)

        self.adjustSize()


class _PopupFrame(QFrame):
    """Попап со всеми чипами. Закрывается по клику вне окна."""

    item_removed = pyqtSignal(object)

    def __init__(self, items: list[tuple[str, object]], width: int, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(width)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(4)

        # Раскладываем чипы по строкам
        row = QHBoxLayout()
        row.setSpacing(4)
        row_w = 0
        available = width - 12  # margins

        for label, data in items:
            chip = _Chip(label)
            chip_w = chip.sizeHint().width() + 4

            if row_w > 0 and row_w + chip_w > available:
                row.addStretch()
                outer.addLayout(row)
                row = QHBoxLayout()
                row.setSpacing(4)
                row_w = 0

            chip.removed.connect(lambda d=data: self._on_remove(d))
            row.addWidget(chip)
            row_w += chip_w

        row.addStretch()
        outer.addLayout(row)
        self.adjustSize()

    def _on_remove(self, data: object) -> None:
        self.item_removed.emit(data)
        self.close()


class ChipsWidget(QWidget):
    """
    Виджет с чипами (теги, жанры, и т.п.).
    Показывает не более 2 строк. Если элементов больше —
    в конце второй строки появляется кнопка +N, открывающая попап со всеми чипами.
    """

    item_removed = pyqtSignal(object)

    _SPACING = 4
    _PLUS_BTN_W = 38

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[tuple[str, object]] = []
        self._plus_btn: QPushButton | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(self._SPACING)

        self._row1 = QHBoxLayout()
        self._row1.setSpacing(self._SPACING)
        self._row2 = QHBoxLayout()
        self._row2.setSpacing(self._SPACING)

        outer.addLayout(self._row1)
        outer.addLayout(self._row2)

        chip_h = QFontMetrics(self.font()).height() + 12
        self.setFixedHeight(chip_h * 2 + self._SPACING)

    # ── Публичный API ─────────────────────────────────────────────────────────

    def add_item(self, label: str, data: object) -> None:
        """Добавить элемент."""
        self._items.append((label, data))
        self._rebuild()

    def remove_item(self, data: object) -> None:
        """Удалить элемент по объекту данных."""
        self._items = [(l, d) for l, d in self._items if d is not data]
        self._rebuild()

    def set_items(self, items: list[tuple[str, object]]) -> None:
        """Установить список элементов целиком (для режима редактирования)."""
        self._items = list(items)
        self._rebuild()

    def all_data(self) -> list[object]:
        """Вернуть все объекты данных."""
        return [d for _, d in self._items]

    # ── Внутренняя логика ─────────────────────────────────────────────────────

    def _clear_row(self, row: QHBoxLayout) -> None:
        while row.count():
            item = row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _fill_row(
        self,
        chips: list[tuple[_Chip, int, object]],
        available: int,
        reserve: int = 0,
    ) -> tuple[list, list]:
        """Жадно заполняет строку. Возвращает (влезло, остаток)."""
        row, w = [], 0
        for item in chips:
            _, cw, _ = item
            if w + cw <= available - reserve:
                row.append(item)
                w += cw
            else:
                break
        return row, chips[len(row):]

    def _rebuild(self) -> None:
        self._clear_row(self._row1)
        self._clear_row(self._row2)
        self._plus_btn = None

        if not self._items:
            self._row1.addStretch()
            self._row2.addStretch()
            return

        available = max(self.width() - 4, 100)
        s = self._SPACING
        plus_reserve = self._PLUS_BTN_W + s

        # Создаём все чипы
        all_chips: list[tuple[_Chip, int, object]] = []
        for label, data in self._items:
            chip = _Chip(label)
            chip.removed.connect(lambda d=data: self._on_chip_remove(d))
            all_chips.append((chip, chip.sizeHint().width() + s, data))

        # Строка 1: жадно
        row1, rest = self._fill_row(all_chips, available)

        if not rest:
            # Всё влезло в строку 1
            for chip, _, _ in row1:
                self._row1.addWidget(chip)
            self._row1.addStretch()
            self._row2.addStretch()
            return

        # Строка 2: сначала пробуем без +N
        row2, overflow = self._fill_row(rest, available)

        if overflow:
            # Не всё влезло — перебираем строку 2 с резервом под +N
            row2, overflow = self._fill_row(rest, available, reserve=plus_reserve)

        # Удаляем чипы которые уйдут в попап (они не нужны в layout)
        shown = {id(c) for c, _, _ in row1 + row2}
        for chip, _, _ in all_chips:
            if id(chip) not in shown:
                chip.deleteLater()

        # Строка 1
        for chip, _, _ in row1:
            self._row1.addWidget(chip)
        self._row1.addStretch()

        # Строка 2
        for chip, _, _ in row2:
            self._row2.addWidget(chip)

        # Кнопка +N
        if overflow:
            self._plus_btn = QPushButton(f'+{len(overflow)}')
            self._plus_btn.setFixedWidth(self._PLUS_BTN_W)
            self._plus_btn.clicked.connect(self._show_popup)
            self._row2.addWidget(self._plus_btn)

        self._row2.addStretch()

    def _on_chip_remove(self, data: object) -> None:
        self.remove_item(data)
        self.item_removed.emit(data)

    def _show_popup(self) -> None:
        popup = _PopupFrame(self._items, self.width(), self)
        popup.item_removed.connect(self._on_popup_remove)

        anchor = self._plus_btn if self._plus_btn else self
        pos = anchor.mapToGlobal(QPoint(0, anchor.height() + 2))
        popup.move(pos)
        popup.show()

    def _on_popup_remove(self, data: object) -> None:
        self.remove_item(data)
        self.item_removed.emit(data)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rebuild()
