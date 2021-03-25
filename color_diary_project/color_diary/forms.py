from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import IntegerField, Case, When, Value

from .models import Diary, Color, User
from .fields import parse_hex_color


DEFAULT_COLOR_LEVEL = 10


class ChooseColorForm(forms.Form):
    color = forms.ModelChoiceField(widget=forms.RadioSelect, initial=Color.get_default_color(), queryset=None)
    color_level = forms.IntegerField(
        initial=DEFAULT_COLOR_LEVEL,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'step': '1',
            'min': '1',
            'max': '10',
            'value': f'{DEFAULT_COLOR_LEVEL}'
        }))

    def __init__(self, login_user=None, *args, **kwargs):
        self.login_user = login_user

        if self.login_user is None:
            raise ValueError(_('the user argument is not given.'))

        super().__init__(*args, **kwargs)

        # querysetをHexColorオブジェクトでソートする
        queryset = Color.objects.filter(users__id=self.login_user.pk)
        sorted_list = sorted(queryset, key=lambda color: color.hex_color)

        cases = []
        for hex_color_order, color in enumerate(sorted_list):
            cases.append(When(id=color.pk, then=Value(hex_color_order)))

        self.fields["color"].queryset =  queryset.annotate(
            hex_color_order=Case(
                *cases,
                output_field=IntegerField()
            )
        ).order_by('hex_color_order')



class ColorModelForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['hex_color',]

    def __init__(self, user=None, *args, **kwargs):
        self.user = user

        super().__init__(*args, **kwargs)

        if self.instance.hex_color:
            hex_color = self.instance.hex_color
            self.initial['hex_color'] = f'{hex_color.red}{hex_color.green}{hex_color.blue}'
        else:
            self.initial['hex_color'] = '000000'

        if self.instance.hex_color == parse_hex_color('ffffff0'):
            self.fields['hex_color'].disabled = True

        self.fields['hex_color'].widget.attrs['placeholder'] = 'Color Code:'

    def clean_hex_color(self):
        cleaned_data = self.cleaned_data['hex_color']
        if len(cleaned_data) > 6:
            raise ValidationError(_('Color code is too long.'))
        try:
            parse_hex_color(cleaned_data)
        except ValueError as err:
            raise ValidationError(_(str(err)))
        return cleaned_data

    def clean(self):
        if self.user is None:
            raise ValidationError(_('the user argument is required.'))

    def save(self, commit=True):
        # Colorは変更する事ができない。Colorのhex_colorを変更した時は新たにオブジェクトを作るか
        # 既存のオブジェクトをとってきて、現在ログインしているユーザーと関連付ける。
        # また、変更以前の色を使っていた日記は、新しい色に新たに関連付けられる。

        hex_color = parse_hex_color(self.cleaned_data['hex_color'])
        new_color = Color.objects.create(hex_color=hex_color)
        new_color.users.add(self.user)

        if self.instance.pk:
            previous_color = Color.objects.get(id=self.instance.pk)
            Diary.objects.filter(user=self.user, color=previous_color).update(color=new_color)
            previous_color.users.remove(self.user)

            if previous_color.users.all().count() == 0:
                previous_color.delete()


class DiaryModelForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['context', 'created_at', 'color', 'color_level']

    def __init__(self, user=None, color=None, color_level=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.instance.user = user
        if color:
            self.instance.color = color
        if color_level:
            self.instance.color_level = color_level

        # hiddenにしたフィールドに関しては、値が入っていない
        self.fields['created_at'].widget = forms.HiddenInput()
        try:
            self.initial['color'] = self.instance.color.pk
        except self.instance._meta.model.color.RelatedObjectDoesNotExist:
            self.initial['color'] = None
        self.fields['color'].widget = forms.HiddenInput()
        if self.instance.color_level:
            self.initial['color_level'] = self.instance.color_level
        self.fields['color_level'].widget = forms.HiddenInput()

    def clean(self):
        if self.instance.user is None:
            raise ValidationError(_('the user argument is required.'))

        if self.instance.color.users.filter(id=self.instance.user.pk).count() == 0:
            raise ValidationError(_("this is invalid color. you don't have this color."))

    def save(self, commit=True):
        # 自身で変更できるのは作成日時だけ。更新日時は変更できない。日記一覧では作成日時のみを表示する。
        now = timezone.now()
        if self.instance.created_at == '':
            self.instance.created_at = now

        if commit:
            super().save(commit)
        return self.instance


class UserLoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password:'}))

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email:'
