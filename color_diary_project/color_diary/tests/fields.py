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
    def assertHexColor(self, hex_color, red, green, blue, alpha):
        self.assertEqual(hex_color.red, red)
        self.assertEqual(hex_color.green, green)
        self.assertEqual(hex_color.blue, blue)
        self.assertEqual(hex_color.alpha, alpha)

    def test_init_red_with_not_hex(self):
        with self.assertRaisesMessage(ValueError, expected_message='RGB must be hex.'):
            HexColor('zz', 'ff', 'ff')

    def test_init_green_with_not_hex(self):
        with self.assertRaisesMessage(ValueError, expected_message='RGB must be hex.'):
            HexColor('ff', 'zz', 'ff')

    def test_init_blue_with_not_hex(self):
        with self.assertRaisesMessage(ValueError, expected_message='RGB must be hex.'):
            HexColor('ff', 'ff', 'zz')

    def test_init_red_with_wrong_length(self):
        with self.assertRaisesMessage(ValueError, expected_message='each of RGB must be 2 length.'):
            HexColor('fff', 'ff', 'ff')

    def test_init_green_with_wrong_length(self):
        with self.assertRaisesMessage(ValueError, expected_message='each of RGB must be 2 length.'):
            HexColor('ff', 'fff', 'ff')

    def test_init_blue_with_wrong_length(self):
        with self.assertRaisesMessage(ValueError, expected_message='each of RGB must be 2 length.'):
            HexColor('ff', 'ff', 'fff')

    def test_init_alpha_with_string(self):
        with self.assertRaisesMessage(ValueError, expected_message='could not convert string to float: \'string\''):
            HexColor('ff', 'ff', 'ff', 'string')

    def test_init_alpha_with_0(self):
        hex_color = HexColor('ff', 'ff', 'ff', 0)
        self.assertHexColor(hex_color, 'FF', 'FF', 'FF', 0.0)

    def test_init_alpha_with_1(self):
        hex_color = HexColor('ff', 'ff', 'ff', 1)
        self.assertHexColor(hex_color, 'FF', 'FF', 'FF', 1.0)

    def test_init_alpha_with_minus_1(self):
        with self.assertRaisesMessage(ValueError, expected_message='0 <= alpha <= 1.'):
            hex_color = HexColor('ff', 'ff', 'ff', -1)

    def test_init_alpha_with_2(self):
        with self.assertRaisesMessage(ValueError, expected_message='0 <= alpha <= 1.'):
            hex_color = HexColor('ff', 'ff', 'ff', 2)

    def test_str(self):
        hex_color = HexColor('ff', 'ff', 'ff')
        self.assertEqual(str(hex_color), '#FFFFFF-1.0')


class ParseHexColorTests(TestCase):
    def test_red_with_string(self):
        with self.assertRaisesMessage(ValueError, expected_message='RGB must be hex.'):
            print(parse_hex_color('zzffff1.0'))

    def test_alpha_with_string(self):
        with self.assertRaisesMessage(ValueError, expected_message='hex_color_code is wrong.'):
            print(parse_hex_color('ffffffk'))

    def test_parse_hex_color_with_symbol(self):
        hex_color = parse_hex_color('#ffffff-----$%$"&"&"$%"$%"&"----0')
        HexColorTests().assertHexColor(hex_color, 'FF', 'FF', 'FF', 0.0)

    def test_alpha_with_0(self):
        hex_color = parse_hex_color('ffffff0')
        HexColorTests().assertHexColor(hex_color, 'FF', 'FF', 'FF', 0.0)

    def test_alpha_with_1(self):
        hex_color = parse_hex_color('ffffff1')
        HexColorTests().assertHexColor(hex_color, 'FF', 'FF', 'FF', 1.0)

    def test_alpha_with_2(self):
        with self.assertRaisesMessage(ValueError, expected_message=''):
            parse_hex_color('ffffff2')

    def test_with_low_count_of_string(self):
        with self.assertRaisesMessage(ValueError, expected_message='hex_color_code is wrong.'):
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
