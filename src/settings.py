from pathlib import Path

from PyQt6.QtCore import QSettings


class Settings:
    _ORG = 'BookShelves'
    _APP = 'BookShelves'

    _KEY_DB_PATH = 'database/path'
    _KEY_FILE_READERS = 'readers/list'
    _KEY_LAST_USER_ID = 'user/last_id'

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

    # ── Пользователь ─────────────────────────────────────────────────────────

    @property
    def last_user_id(self) -> int | None:
        value = self._qs.value(self._KEY_LAST_USER_ID)
        return int(value) if value is not None else None

    @last_user_id.setter
    def last_user_id(self, user_id: int | None) -> None:
        if user_id is None:
            self._qs.remove(self._KEY_LAST_USER_ID)
        else:
            self._qs.setValue(self._KEY_LAST_USER_ID, user_id)

    # ── Ридеры ────────────────────────────────────────────────────────────────

    @property
    def file_readers(self) -> list[dict]:
        """Список словарей вида {'extension': 'epub', 'command': '/usr/bin/foliate %f'}."""
        return self._qs.value(self._KEY_FILE_READERS) or []

    @file_readers.setter
    def file_readers(self, readers: list[dict]) -> None:
        self._qs.setValue(self._KEY_FILE_READERS, readers)

    def reader_command(self, extension: str) -> str | None:
        """Команда для расширения или None если не настроено."""
        ext = extension.lower().lstrip('.')
        for r in self.file_readers:
            if r.get('extension', '').lower() == ext:
                return r.get('command') or None
        return None
