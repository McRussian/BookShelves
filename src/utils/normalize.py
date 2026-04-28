_NAME_SEPS = "-'’"  # дефис, прямой и типографский апостроф


def normalize_name(text: str) -> str:
    """Каждое слово с заглавной буквы; апостроф и дефис — тоже разделители.

    'лев николаевич' → 'Лев Николаевич'
    'о'генри'        → 'О'Генри'
    'лебедев-кумач'  → 'Лебедев-Кумач'
    """
    def _cap_word(word: str) -> str:
        result = []
        cap_next = True
        for ch in word:
            if ch in _NAME_SEPS:
                result.append(ch)
                cap_next = True
            elif cap_next:
                result.append(ch.upper())
                cap_next = False
            else:
                result.append(ch.lower())
        return ''.join(result)

    return ' '.join(_cap_word(w) for w in text.strip().split())


def normalize_title(text: str) -> str:
    """Только первая буква заглавная: 'война и мир' → 'Война и мир'."""
    text = text.strip().lower()
    return text[0].upper() + text[1:] if text else text


def normalize_tag(text: str) -> str:
    """PascalCase с префиксом #.

    Стратегия для каждого слова:
    - всё строчное → capitalize() («микросервисы» → «Микросервисы»,
                                    «active directory» → «#ActiveDirectory»)
    - есть хоть одна заглавная → только поднять первую, остальное не трогать
      («DDD» → «DDD», «DevOps» → «DevOps», «CI/CD» → «CI/CD»)

    Это позволяет вводить аббревиатуры в верхнем регистре и не бояться,
    что строчной ввод даст неожиданный результат.
    """
    def _tag_word(word: str) -> str:
        if not word:
            return word
        return word.capitalize() if word == word.lower() else word[0].upper() + word[1:]

    text = text.strip().lstrip('#')
    pascal = ''.join(_tag_word(w) for w in text.split())
    return f'#{pascal}'
