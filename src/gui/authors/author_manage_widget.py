from src.gui.authors.author_checkable_widget import AuthorCheckableWidget


class AuthorManageWidget(AuthorCheckableWidget):

    def __init__(self, parent=None):
        super().__init__(auto_select_new=False, parent=parent)
