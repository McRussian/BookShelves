from PyQt6.QtCore import QObject, pyqtSignal


class _AppSignals(QObject):
    db_changed = pyqtSignal()


app_signals = _AppSignals()
