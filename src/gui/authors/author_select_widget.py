from src.database.models.author import Author
from src.gui.authors.author_checkable_widget import AuthorCheckableWidget


class AuthorSelectWidget(AuthorCheckableWidget):

    def __init__(self, preselected: list[Author] = (), parent=None):
        super().__init__(preselected=preselected, auto_select_new=True, parent=parent)
