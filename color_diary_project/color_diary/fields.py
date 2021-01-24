from django.db import models
from django.utils.translation import gettext_lazy as _

import re
import math


def is_hex(string: str):
    return bool(re.fullmatch(r'[0-9a-fA-F]+', string))


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
        return f'#{self.red}{self.green}{self.blue}-{self.alpha}'

    def __eq__(self, other):
        if not isinstance(other, HexColor):
            try:
                other = parse_hex_color(other)
            except:
                return False

        return self.red == other.red \
               and self.green == other.green \
               and self.blue == other.blue\
               and self.alpha == other.alpha

    def __gt__(self, other):
        if self.hue > other.hue:
            return True
        if self.saturation > other.saturation:
            return True
        return self.value < other.value

    def __lt__(self, other):
        if self.hue < other.hue:
            return True
        if self.saturation < other.saturation:
            return True
        return self.value > other.value

    def _calc_color(self):
        calc_red = int(self.red, 16) / 255
        calc_green = int(self.green, 16) / 255
        calc_blue = int(self.blue, 16) / 255

        cmax = max(calc_red, calc_green, calc_blue)
        cmin = min(calc_red, calc_green, calc_blue)
        return calc_red, calc_green, calc_blue, cmax, cmin

    @property
    def hue(self):
        calc_red, calc_green, calc_blue, cmax, cmin = self._calc_color()

        hue = -1
        if cmax == cmin:
            return hue
        elif calc_blue == cmax:
            hue = (60 * (calc_green - calc_red) / (cmax - cmin) + 60) % 360
        elif calc_red == cmax:
            hue = (60 * (calc_blue - calc_green) / (cmax - cmin) + 120) % 360
        else:
            hue = (60 * (calc_red - calc_blue) / (cmax - cmin) + 240) % 360

        return hue

    @property
    def saturation(self):
        calc_red, calc_green, calc_blue, cmax, cmin = self._calc_color()
        return cmax - cmin

    @property
    def value(self):
        calc_red, calc_green, calc_blue, cmax, cmin = self._calc_color()
        return cmax

# note: カラーコードからHexColorへ変換する動作はHexColorField内にしかないからHexColorField内へ移動した。いや、将来文字列から変換するなんて色々使えるだろう。だから外にするべきだ
def parse_hex_color(hex_color_code: str):
    # カラーコードは'FFFFFF'や'FFFFFF1.0'など
    # カラーコードをHexColorに変換する

    # 記号を取り除いておく
    hex_color_code = re.sub(r'[^a-zA-Z0-9.]', '', hex_color_code)

    # fixme: もっといいリストを作る実装あるよね、多分
    match = re.fullmatch(r'(\w{2})(\w{2})(\w{2})([0-9.]+)?', hex_color_code)
    if match is None:
        raise ValueError(_('hex_color_code is wrong.'))
    rgb_list = [match.group(1), match.group(2), match.group(3)]
    alpha = match.group(4) or 1.0

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

    floored_alpha = math.floor(alpha * 100) / 100

    return HexColor(*rgb_list, floored_alpha)


class HexColorField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length'] # 既に最大長は指定したため、ここでは読みやすさのために最大長は省く
        return name, path, args, kwargs

    def db_type(self, connection):
        return 'CHAR(10)'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return parse_hex_color(value)

    def get_prep_value(self, value):
        return f'{value.red}{value.green}{value.blue}{value.alpha}' # データベースの為めに文字列に変換する処理はHexColorクラスではなくこのクラスに入れるのか！

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, HexColor):
            return value

        return parse_hex_color(value)
