import unittest

from src.utils.normalize import normalize_name, normalize_tag, normalize_title


class TestNormalizeName(unittest.TestCase):

    def test_lowercase_input(self):
        self.assertEqual(normalize_name('лев'), 'Лев')

    def test_uppercase_input(self):
        self.assertEqual(normalize_name('ЛЕВ'), 'Лев')

    def test_mixed_case_input(self):
        self.assertEqual(normalize_name('лЕв'), 'Лев')

    def test_two_words(self):
        self.assertEqual(normalize_name('лев толстой'), 'Лев Толстой')

    def test_three_words(self):
        self.assertEqual(normalize_name('лев николаевич толстой'), 'Лев Николаевич Толстой')

    def test_already_normalized(self):
        self.assertEqual(normalize_name('Толстой'), 'Толстой')

    def test_strips_whitespace(self):
        self.assertEqual(normalize_name('  лев  '), 'Лев')

    def test_extra_spaces_between_words(self):
        self.assertEqual(normalize_name('лев   толстой'), 'Лев Толстой')

    def test_latin_input(self):
        self.assertEqual(normalize_name('stephen king'), 'Stephen King')

    # ── апостроф ─────────────────────────────────────────────────────────────

    def test_apostrophe_straight(self):
        self.assertEqual(normalize_name("о'герни"), "О'Герни")

    def test_apostrophe_curly(self):
        self.assertEqual(normalize_name('о’герни'), 'О’Герни')

    def test_apostrophe_uppercase_input(self):
        self.assertEqual(normalize_name("О'ФЛИНН"), "О'Флинн")

    def test_apostrophe_already_correct(self):
        self.assertEqual(normalize_name("О'Флинн"), "О'Флинн")

    # ── дефис ────────────────────────────────────────────────────────────────

    def test_hyphen(self):
        self.assertEqual(normalize_name('лебедев-кумач'), 'Лебедев-Кумач')

    def test_hyphen_uppercase_input(self):
        self.assertEqual(normalize_name('ЛЕБЕДЕВ-КУМАЧ'), 'Лебедев-Кумач')

    def test_hyphen_already_correct(self):
        self.assertEqual(normalize_name('Лебедев-Кумач'), 'Лебедев-Кумач')

    def test_hyphen_and_space(self):
        self.assertEqual(normalize_name('жан-поль сартр'), 'Жан-Поль Сартр')


class TestNormalizeTitle(unittest.TestCase):

    def test_lowercase_input(self):
        self.assertEqual(normalize_title('война и мир'), 'Война и мир')

    def test_uppercase_input(self):
        self.assertEqual(normalize_title('ВОЙНА И МИР'), 'Война и мир')

    def test_mixed_case_input(self):
        self.assertEqual(normalize_title('воЙнА И МиР'), 'Война и мир')

    def test_already_normalized(self):
        self.assertEqual(normalize_title('Война и мир'), 'Война и мир')

    def test_single_word(self):
        self.assertEqual(normalize_title('дюна'), 'Дюна')

    def test_strips_whitespace(self):
        self.assertEqual(normalize_title('  война и мир  '), 'Война и мир')

    def test_only_first_word_capitalized(self):
        result = normalize_title('преступление и наказание')
        self.assertTrue(result.startswith('Преступление'))
        self.assertIn(' и ', result)
        self.assertIn(' наказание', result)

    def test_latin_input(self):
        self.assertEqual(normalize_title('the dark tower'), 'The dark tower')


class TestNormalizeTag(unittest.TestCase):

    def test_single_word_lowercase(self):
        self.assertEqual(normalize_tag('фэнтези'), '#Фэнтези')

    def test_two_words_lowercase(self):
        self.assertEqual(normalize_tag('научная фантастика'), '#НаучнаяФантастика')

    def test_three_words(self):
        self.assertEqual(normalize_tag('городское фэнтези россия'), '#ГородскоеФэнтезиРоссия')

    def test_already_has_hash(self):
        self.assertEqual(normalize_tag('#фэнтези'), '#Фэнтези')

    def test_already_pascal_case_with_hash(self):
        # Есть заглавные → повторная нормализация не ломает тег
        self.assertEqual(normalize_tag('#НаучнаяФантастика'), '#НаучнаяФантастика')

    def test_all_uppercase_word_preserved(self):
        # Слово не является всё-строчным → регистр сохраняется (аббревиатура или caps-lock)
        self.assertEqual(normalize_tag('ФЭНТЕЗИ'), '#ФЭНТЕЗИ')

    def test_lowercase_normalized_uppercase_preserved(self):
        # Строчное → capitalize, заглавное → сохраняется: одна фраза, разные слова
        self.assertEqual(normalize_tag('микросервисы API'), '#МикросервисыAPI')

    def test_mixed_case_word_preserved(self):
        # Есть заглавные внутри — регистр сохраняется, только первая буква поднимается
        self.assertEqual(normalize_tag('devOps фантастика'), '#DevOpsФантастика')

    def test_lowercase_same_as_titlecase(self):
        # Строчный ввод и «правильный» ввод дают одинаковый тег
        self.assertEqual(normalize_tag('active directory'), normalize_tag('Active Directory'))

    def test_strips_whitespace(self):
        self.assertEqual(normalize_tag('  фэнтези  '), '#Фэнтези')

    def test_extra_spaces_between_words(self):
        self.assertEqual(normalize_tag('научная   фантастика'), '#НаучнаяФантастика')

    def test_latin_input(self):
        self.assertEqual(normalize_tag('science fiction'), '#ScienceFiction')

    # ── аббревиатуры ─────────────────────────────────────────────────────────

    def test_acronym_all_caps(self):
        # Аббревиатура: не всё строчное → регистр сохраняется
        self.assertEqual(normalize_tag('DDD'), '#DDD')

    def test_acronym_camelcase(self):
        self.assertEqual(normalize_tag('DevOps'), '#DevOps')

    def test_acronym_with_slash(self):
        self.assertEqual(normalize_tag('CI/CD'), '#CI/CD')

    def test_acronym_mixed_word(self):
        self.assertEqual(normalize_tag('GoF'), '#GoF')

    def test_acronym_in_phrase(self):
        self.assertEqual(normalize_tag('API безопасность'), '#APIБезопасность')


if __name__ == '__main__':
    unittest.main()
