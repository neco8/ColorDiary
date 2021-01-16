from django.db import models
from django.utils.translation import gettext_lazy as _

import re


def is_hex(string: str):
    string = string.upper()
    return bool(re.fullmatch('[0-9A-F]+', string))


class HexColor:
    """Hex Color Code"""

    def __init__(self, red: str, green: str, blue: str, alpha=1.0):
        # RGB入力値は16進数で00~FF
        # alphaは0以上1以下のfloat型

        # fixme: このようなバリデーション処理はどこへ書けばいいのだろうか？
        if not (is_hex(red) and is_hex(green) and is_hex(blue)):
            raise ValueError(_('RGB must be hex.'))
        if not (
                len(red) == 2
                and len(green) == 2
                and len(blue) == 2
        ):
            raise ValueError(_('each of RGB must be 2 length.'))

        if alpha:
            alpha = float(alpha) # ここで文字列を通さないはず
        if alpha < 0 or alpha > 1:
            raise ValueError(_('0 <= alpha <= 1.'))

        self.red = red.upper()
        self.green = green.upper()
        self.blue = blue.upper()
        self.alpha = alpha

    def __str__(self):
        return ''.join(['#', self.red, self.green, self.blue, '-', str(self.alpha)])

    def __eq__(self, other):
        return self.red == other.red \
               and self.green == other.green \
               and self.blue == other.blue\
               and self.alpha == other.alpha

# note: カラーコードからHexColorへ変換する動作はHexColorField内にしかないからHexColorField内へ移動した。いや、将来文字列から変換するなんて色々使えるだろう。だから外にするべきだ
def parse_hex_color(hex_color_code):
    # カラーコードは'FFFFFF'や'FFFFFF1.0'など
    # カラーコードをHexColorに変換する

    if len(hex_color_code) < 6:
        raise ValueError(_('each of RGB must be 2 length.'))

    # fixme: もっといいリストを作る実装あるよね、多分
    rgb_list = [hex_color_code[:2], hex_color_code[2:4], hex_color_code[4:6]]
    alpha = 1.0
    if len(hex_color_code) > 6:
        alpha = hex_color_code[6:]

    for color in rgb_list:
        if not is_hex(color):
            raise ValueError(_('RGB must be hex.'))

    try:
        alpha = float(alpha)
    except:
        raise ValueError(_('alpha must be float.(0 <= alpha <= 1)'))
    else:
        if alpha < 0 or alpha > 1:
            raise ValueError(_('0 <= alpha <= 1.'))

    return HexColor(*rgb_list, alpha)


class HexColorField(models.Field):
    def db_type(self, connection):
        return 'CHAR'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return parse_hex_color(value)

    def get_prep_value(self, value):
        return ''.join([value.red, value.green, value.blue, str(value.alpha)]) # データベースの為めに文字列に変換する処理はHexColorクラスではなくこのクラスに入れるのか！

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, HexColor):
            return value

        return parse_hex_color(value)
