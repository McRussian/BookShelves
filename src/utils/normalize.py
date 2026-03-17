def normalize_name(text: str) -> str:
    """Каждое слово с заглавной буквы: 'лев николаевич' → 'Лев Николаевич'."""
    return ' '.join(w.capitalize() for w in text.strip().split())


def normalize_title(text: str) -> str:
    """Только первая буква заглавная: 'война и мир' → 'Война и мир'."""
    text = text.strip().lower()
    return text[0].upper() + text[1:] if text else text


def normalize_tag(text: str) -> str:
    """PascalCase с префиксом #: 'научная фантастика' → '#НаучнаяФантастика'."""
    # Убрать возможный #, который пользователь мог ввести сам
    text = text.strip().lstrip('#')
    pascal = ''.join(w.capitalize() for w in text.split())
    return f'#{pascal}'
