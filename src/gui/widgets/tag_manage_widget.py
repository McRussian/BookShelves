from src.gui.widgets.tag_checkable_widget import TagCheckableWidget


class TagManageWidget(TagCheckableWidget):
    """Виджет управления тегами: чекбоксы для массового удаления, новый тег без авто-выбора."""

    def __init__(self, parent=None):
        super().__init__(auto_select_new=False, parent=parent)
