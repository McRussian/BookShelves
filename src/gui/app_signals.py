from PyQt6.QtCore import QObject, pyqtSignal


class _AppSignals(QObject):
    db_changed = pyqtSignal()

    # Эмитируется после смены пользователя; аргумент — новый объект User
    user_changed = pyqtSignal(object)


app_signals = _AppSignals()
