from django.test import TestCase

from ..fields import is_hex, parse_hex_color, HexColor, HexColorField


class IsHexTests(TestCase):
    def test_is_hex_with_hex(self):
        self.assertTrue(is_hex('FFFFFF'))

    def test_is_not_hex_with_not_hex(self):
        self.assertFalse(is_hex('kljgi:;'))

    def test_is_not_hex_with_empty(self):
        self.assertFalse(is_hex(''))


class HexColorTests(TestCase):
    def test_init_red_with_not_hex(self):
        with self.assertRaises(ValueError, msg='RGB must be hex.'):
            HexColor('zz', 'ff', 'ff')

    def test_init_green_with_not_hex(self):
        with self.assertRaises(ValueError, msg='RGB must be hex.'):
            HexColor('ff', 'zz', 'ff')

    def test_init_blue_with_not_hex(self):
        with self.assertRaises(ValueError, msg='RGB must be hex.'):
            HexColor('ff', 'ff', 'zz')

    def test_init_red_with_wrong_length(self):
        with self.assertRaises(ValueError, msg='each of RGB must be 2 length.'):
            HexColor('fff', 'ff', 'ff')

    def test_init_green_with_wrong_length(self):
        with self.assertRaises(ValueError, msg='each of RGB must be 2 length.'):
            HexColor('ff', 'fff', 'ff')

    def test_init_blue_with_wrong_length(self):
        with self.assertRaises(ValueError, msg='each of RGB must be 2 length.'):
            HexColor('ff', 'ff', 'fff')

    def test_init_alpha_with_string(self):
        with self.assertRaises(ValueError, msg='Could not convert string to float: \'string\''):
            HexColor('ff', 'ff', 'ff', 'string')

    def test_init_alpha_with_0(self):
        hex_color = HexColor('ff', 'ff', 'ff', 0)
        self.assertEqual(hex_color.red, 'FF')
        self.assertEqual(hex_color.green, 'FF')
        self.assertEqual(hex_color.blue, 'FF')
        self.assertEqual(hex_color.alpha, 0.0)

    def test_init_alpha_with_1(self):
        hex_color = HexColor('ff', 'ff', 'ff', 1)
        self.assertEqual(hex_color.red, 'FF')
        self.assertEqual(hex_color.green, 'FF')
        self.assertEqual(hex_color.blue, 'FF')
        self.assertEqual(hex_color.alpha, 1.0)

    def test_init_alpha_with_minus_1(self):
        with self.assertRaises(ValueError, msg='0 <= alpha <= 1.'):
            hex_color = HexColor('ff', 'ff', 'ff', -1)

    def test_init_alpha_with_2(self):
        with self.assertRaises(ValueError, msg='0 <= alpha <= 1.'):
            hex_color = HexColor('ff', 'ff', 'ff', 2)

    def test_str(self):
        hex_color = HexColor('ff', 'ff', 'ff')
        self.assertEqual(str(hex_color), '#FFFFFF-1.0')


class ParseHexColorTests(TestCase):
    def test_red_with_string(self):
        with self.assertRaises(ValueError, msg='RGB must be hex.'):
            parse_hex_color('zzffff1.0')

    def test_alpha_with_string(self):
        with self.assertRaises(ValueError, msg='alpha must be float.(0 <= alpha <= 1)'):
            parse_hex_color('ffffffk')

    def test_alpha_with_0(self):
        hex_color = parse_hex_color('ffffff0')
        self.assertEqual(hex_color.red, 'FF')
        self.assertEqual(hex_color.green, 'FF')
        self.assertEqual(hex_color.blue, 'FF')
        self.assertEqual(hex_color.alpha, 0.0)

    def test_alpha_with_1(self):
        hex_color = parse_hex_color('ffffff1')
        self.assertEqual(hex_color.red, 'FF')
        self.assertEqual(hex_color.green, 'FF')
        self.assertEqual(hex_color.blue, 'FF')
        self.assertEqual(hex_color.alpha, 1.0)

    def test_alpha_with_minus_1(self):
        with self.assertRaises(ValueError, msg=''):
            parse_hex_color('ffffff-1')

    def test_with_low_count_of_string(self):
        with self.assertRaises(ValueError, msg='each of RGB must be 2 length.'):
            parse_hex_color('fff1')


class HexColorFieldTests(TestCase):
    def test_that_db_type_returns_char(self):
        self.assertEqual(HexColorField().db_type(connection=None), 'CHAR(10)')

    def test_from_db_value_with_none(self):
        self.assertIsNone(HexColorField().from_db_value(value=None, expression=None, connection=None))

    def test_from_db_value_with_ffffff(self):
        white = HexColor('ff', 'ff', 'ff')
        self.assertEqual(HexColorField().from_db_value(value='ffffff1.0', expression=None, connection=None), white)

    def test_that_get_prep_value_with_ffffff(self):
        white = HexColor('ff', 'ff', 'ff')
        self.assertEqual(HexColorField().get_prep_value(white), 'FFFFFF1.0')

    def test_to_python_with_none(self):
        self.assertIsNone(HexColorField().to_python(None))

    def test_that_to_python_with_hex_color(self):
        white = HexColor('ff', 'ff', 'ff')
        self.assertEqual(HexColorField().to_python(white), HexColor('ff', 'ff', 'ff'))
        self.assertNotEqual(HexColorField().to_python(white), HexColor('3f', 'ff', 'ff'))

    def test_that_to_python_with_string(self):
        white_string = 'ffffff'
        self.assertEqual(HexColorField().to_python(white_string), HexColor('ff', 'ff', 'ff'))
