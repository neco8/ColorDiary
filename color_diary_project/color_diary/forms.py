from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Diary, Color, User
from .fields import parse_hex_color


DEFAULT_COLOR_LEVEL = 10


class ChooseColorForm(forms.Form):
    color = forms.ModelChoiceField(widget=forms.RadioSelect, initial=Color.get_default_color(), queryset=None)
    color_level = forms.ChoiceField(choices=Diary.COLOR_LEVELS, initial=DEFAULT_COLOR_LEVEL)

    def __init__(self, *args, **kwargs):
        self.login_user = kwargs.pop('login_user', None)

        if self.login_user is None:
            raise ValueError(_('the user argument is not given.'))

        super().__init__(*args, **kwargs)
        self.fields["color"].queryset = Color.objects.filter(users__id=self.login_user.pk)


class ColorModelForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['hex_color']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if self.instance.hex_color:
            hex_color = self.instance.hex_color
            self.initial['hex_color'] = f'{hex_color.red}{hex_color.green}{hex_color.blue}'

        if self.instance.hex_color == parse_hex_color('ffffff0'):
            self.fields['hex_color'].disabled = True

    def clean_hex_color(self):
        cleaned_data = self.cleaned_data['hex_color']
        if len(cleaned_data) > 6:
            raise ValidationError(_('hex color code is too long.'))
        return cleaned_data

    def clean(self):
        if self.user is None:
            raise ValidationError(_('the user argument is required.'))

    def save(self, commit=True):
        # Colorは基本immutableで、変更する事ができない。Colorのhex_colorを変更した時は新たにオブジェクトを作るか
        # 既存のオブジェクトをとってきて、現在ログインしているユーザーをとってくる。
        if self.instance.pk:
            previous_color = Color.objects.get(id=self.instance.pk)
            previous_color.users.remove(self.user)

            if previous_color.users.all().count() == 0:
                previous_color.delete()

        hex_color = parse_hex_color(self.cleaned_data['hex_color'])
        new_color = Color.objects.create(hex_color=hex_color)
        new_color.users.add(self.user)


class DiaryModelForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['context',]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.color = kwargs.pop('color', None)
        self.color_level = kwargs.pop('color_level', 0)

        super().__init__(*args, **kwargs)

        self.instance.user = self.user
        self.instance.color = self.color
        self.instance.color_level = self.color_level

    def clean(self):
        if self.user is None:
            raise ValidationError(_('the user argument is required.'))
        if self.color is None:
            raise ValidationError(_('the color argument is required.'))
        if self.color_level == 0:
            raise ValidationError(_('the color_level argument is required.'))

        if self.color.users.filter(id=self.user.id).count() == 0:
            raise ValidationError(_("this is invalid color. you don't have this color."))


class UserLoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)