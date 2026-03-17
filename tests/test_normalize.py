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
        # Слитное слово — capitalize оставляет только первую букву заглавной
        self.assertEqual(normalize_tag('#НаучнаяФантастика'), '#Научнаяфантастика')

    def test_uppercase_input(self):
        self.assertEqual(normalize_tag('ФЭНТЕЗИ'), '#Фэнтези')

    def test_mixed_case_input(self):
        self.assertEqual(normalize_tag('НаУчНаЯ фАнТаСтИкА'), '#НаучнаяФантастика')

    def test_strips_whitespace(self):
        self.assertEqual(normalize_tag('  фэнтези  '), '#Фэнтези')

    def test_extra_spaces_between_words(self):
        self.assertEqual(normalize_tag('научная   фантастика'), '#НаучнаяФантастика')

    def test_latin_input(self):
        self.assertEqual(normalize_tag('science fiction'), '#ScienceFiction')


if __name__ == '__main__':
    unittest.main()
