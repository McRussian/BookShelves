from src.database.models.tag import Tag
from src.gui.widgets.tag_checkable_widget import TagCheckableWidget


class TagSelectWidget(TagCheckableWidget):
    """Виджет выбора тегов: новый тег сразу отмечается, preselected поддерживается."""

    def __init__(self, preselected: list[Tag], parent=None):
        super().__init__(preselected=preselected, auto_select_new=True, parent=parent)
