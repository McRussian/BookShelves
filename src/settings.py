from pathlib import Path

from PyQt6.QtCore import QSettings


class Settings:
    _ORG = 'BookShelves'
    _APP = 'BookShelves'

    _KEY_DB_PATH = 'database/path'
    _KEY_FILE_READERS = 'readers/list'

    def __init__(self):
        self._qs = QSettings(self._ORG, self._APP)

    # ── База данных ───────────────────────────────────────────────────────────

    @property
    def db_path(self) -> Path | None:
        value = self._qs.value(self._KEY_DB_PATH)
        return Path(value) if value else None

    @db_path.setter
    def db_path(self, path: Path | None) -> None:
        if path is None:
            self._qs.remove(self._KEY_DB_PATH)
        else:
            self._qs.setValue(self._KEY_DB_PATH, str(path))

    # ── Ридеры ────────────────────────────────────────────────────────────────

    @property
    def file_readers(self) -> list[dict]:
        """Список словарей вида {'extension': 'epub', 'program': '/usr/bin/foliate'}."""
        return self._qs.value(self._KEY_FILE_READERS) or []

    @file_readers.setter
    def file_readers(self, readers: list[dict]) -> None:
        self._qs.setValue(self._KEY_FILE_READERS, readers)
