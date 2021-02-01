from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import View
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import Diary
from ..forms import ChooseColorForm
from ..utils import get_hashids
from .edit import CREATE


class ChooseColorView(LoginRequiredMixin, View):
    login_url = reverse_lazy('color_diary:login')

    def get(self, request, *args, **kwargs):
        # 日記新規作成か、日記編集かを調べる。
        # 0なら新規作成
        # 日記編集なら、存在する日記の色とレベルをとってきて初期値として入力
        try:
            diary_id = get_hashids().decode(kwargs.get('diary_hash_id'))[0]
        except:
            return HttpResponseNotFound(_('不正なURLです。'))

        if diary_id == CREATE:
            self.form = ChooseColorForm(login_user=request.user)
        else: # 編集
            try:
                diary = Diary.objects.get(id=diary_id, user=request.user)
            except Diary.DoesNotExist:
                return HttpResponseNotFound(_('不正なIDです。'))

            self.form = ChooseColorForm(login_user=request.user, initial={
                'color': diary.color.pk,
                'color_level': diary.color_level
            })

        return render(request, 'color_diary/choose_color.html', {
            'form': self.form,
        })

    def post(self, request, *args, **kwargs):
        diary_hash_id = kwargs['diary_hash_id']
        self.form = ChooseColorForm(login_user=request.user, data=request.POST)

        if self.form.is_valid():
            request.session['color_id'] = self.form.cleaned_data['color'].pk
            request.session['color_level'] = self.form.cleaned_data['color_level']
            return redirect('color_diary:edit-diary', diary_hash_id=diary_hash_id)
        else:
            return render(request, 'color_diary/choose_color.html', {
                'form': self.form,
            })