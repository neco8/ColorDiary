from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
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
            form = ChooseColorForm(login_user=request.user)
        else: # 編集
            try:
                diary = Diary.objects.get(id=diary_id, user=request.user)
            except Diary.DoesNotExist:
                return HttpResponseNotFound(_('不正なIDです。'))

            form = ChooseColorForm(login_user=request.user, initial={
                'color': diary.color.pk,
                'color_level': diary.color_level
            })

        # fixme: color_choosed_diary_id は、現在開いている日記が色を選択しているかどうかを確認するためにやむなく設定した値。SPAにした後、choose_colorのviewを廃止すればこのような事は避けられる。
        if request.session.get('color_choosed_diary_id') != diary_id:
            return render(request, 'color_diary/choose_color.html', {
                'form': form,
                'CREATE': CREATE,
            })

        if 'color_id' in request.session:
            form.initial['color'] = int(request.session.get('color_id'))
        if 'color_level' in request.session:
            form.initial['color_level'] = int(request.session.get('color_level'))

        return render(request, 'color_diary/choose_color.html', {
            'form': form,
            'CREATE': CREATE,
        })

    def post(self, request, *args, **kwargs):
        try:
            diary_id = get_hashids().decode(kwargs.get('diary_hash_id'))[0]
        except:
            return HttpResponseNotFound(_('不正なURLです。'))
        form = ChooseColorForm(login_user=request.user, data=request.POST)

        if form.is_valid():
            request.session['color_id'] = form.cleaned_data['color'].pk
            request.session['color_level'] = form.cleaned_data['color_level']
            request.session['color_choosed_diary_id'] = diary_id
            return redirect('color_diary:edit-diary', diary_hash_id=kwargs.get('diary_hash_id'))
        return render(request, 'color_diary/choose_color.html', {
            'form': form,
            'CREATE': CREATE,
        })
