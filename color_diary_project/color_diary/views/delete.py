from django.views.generic import View
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..utils import get_hashids
from .utils import get_previous_url
from ..models import Diary, Color


class DeleteDiaryView(LoginRequiredMixin, View):
    # todo: 詳細画面に戻る時、入力していた内容を保持しておきたい。フォームの入力保持。これはvue.jsの自動保存にしよう。vue.jsで、削除ボタンが押された時に保存をサーバーへ移す。
    # todo: キャンセルボタンのテスト。複数の場所から行って戻る時はしっかりもとの所に戻れるかどうか
    login_url = '/color-diary/login/'

    def get(self, request, *args, **kwargs):
        previous_url = get_previous_url(request)
        return render(request, 'color_diary/delete_diary.html', {'previous_url': previous_url})

    def post(self, request, *args, **kwargs):
        diary_hash_id = kwargs['diary_hash_id']

        try:
            diary_id = get_hashids().decode(diary_hash_id)[0]
        except:
            raise ValueError(_('invalid diary hash id.'))

        try:
            diary = Diary.objects.get(id=diary_id, user=request.user)
        except Diary.DoesNotExist:
            return redirect('color_diary:diary-index')

        diary.delete()
        return redirect('color_diary:diary-index')


class DeleteColorView(LoginRequiredMixin, View):
    login_url = '/color-diary/login/'

    def get(self, request, *args, **kwargs):
        previous_url = get_previous_url(request)
        return render(request, 'color_diary/delete_color.html', {'previous_url': previous_url})

    def post(self, request, *args, **kwargs):
        try:
            color_id = get_hashids().decode(kwargs['color_hash_id'])[0]
        except:
            raise ValueError(_('invalid color hash id.'))

        try:
            color = Color.objects.get(users=request.user, id=color_id)
        except Color.DoesNotExist:
            return redirect(reverse('color_diary:color-index'))

        color.users.remove(request.user)
        return redirect(reverse('color_diary:color-index'))