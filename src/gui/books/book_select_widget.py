from src.database.models.book import Book
from src.gui.books.book_checkable_widget import BookCheckableWidget


class BookSelectWidget(BookCheckableWidget):

    def __init__(self, preselected: list[Book] = (), parent=None):
        super().__init__(preselected=preselected, parent=parent)
