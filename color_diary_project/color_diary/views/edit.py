from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse, reverse_lazy, resolve
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from ..utils import get_hashids
from ..forms import DiaryModelForm, ColorModelForm
from ..models import Diary, Color
from .utils import get_previous_url


CREATE = 0


class EditDiaryView(LoginRequiredMixin, View):
    login_url = '/color-diary/login/'

    def get(self, request, *args, **kwargs):
        if 'color_id' not in request.session or 'color_level' not in request.session:
            return redirect(reverse('color_diary:choose-color', kwargs={'diary_hash_id': kwargs['diary_hash_id']}))

        try:
            diary_id = get_hashids().decode(kwargs['diary_hash_id'])[0]
        except:
            return HttpResponseNotFound('そのURLは存在しません。')

        if diary_id == CREATE:
            self.form = DiaryModelForm(user=request.user)
        else: # 編集
            try:
                diary = Diary.objects.get(user=request.user, id=diary_id)
            except Diary.DoesNotExist:
                # todo: 404画面を作る
                return HttpResponseNotFound('そのような日記は存在しません。')
            self.form = DiaryModelForm(user=request.user, instance=diary)
        return render(request, 'color_diary/edit_diary.html', {'form': self.form})

    def post(self, request, *args, **kwargs):
        color = Color.objects.get(users=request.user, id=int(request.session.pop('color_id')))
        color_level = int(request.session.pop('color_level'))

        try:
            diary_id = get_hashids().decode(kwargs['diary_hash_id'])[0]
        except:
            return HttpResponseNotFound('そのURLは存在しません。')

        if diary_id == CREATE:
            self.form = DiaryModelForm(
                user=request.user,
                color=color,
                color_level=color_level,
                data=request.POST,
            )
        else: # 編集
            try:
                diary = Diary.objects.get(user=request.user, id=diary_id)
            except Diary.DoesNotExist:
                return HttpResponseNotFound('そのような日記は存在しません。')
            self.form = DiaryModelForm(
                user=request.user,
                color=color,
                color_level=color_level,
                instance=diary,
                data=request.POST,
            )
        if self.form.is_valid():
            self.form.save()
            return redirect('color_diary:diary-index')
        return render(request, 'color_diary/edit_diary.html', {'form': self.form})


class EditColorView(LoginRequiredMixin, View):
    login_url = reverse_lazy('color_diary:login')

    def get(self, request, *args, **kwargs):
        try:
            color_id = get_hashids().decode(kwargs['color_hash_id'])[0]
        except:
            return HttpResponseNotFound('不正なURLです。')

        if color_id == CREATE:
            self.form = ColorModelForm(user=request.user, initial={'hex_color': '000000'})
        elif color_id == Color.get_default_color().pk:
            return HttpResponseNotFound('編集する事はできません。')
        else: # 編集
            try:
                color = Color.objects.get(users=request.user, id=color_id)
            except Color.DoesNotExist:
                return HttpResponseNotFound('不正なIDです。')

            self.form = ColorModelForm(user=request.user, instance=color)
        return render(request, 'color_diary/edit_color.html', {'form': self.form})

    def post(self, request, *args, **kwargs):
        try:
            color_id = get_hashids().decode(kwargs['color_hash_id'])[0]
        except:
            return HttpResponseNotFound('不正なURLです。')

        if color_id == CREATE:
            self.form = ColorModelForm(user=request.user, data=request.POST)
        elif color_id == Color.get_default_color().pk:
            return HttpResponseNotFound('編集する事はできません。')
        else: # 編集
            try:
                color = Color.objects.get(users=request.user, id=color_id)
            except Color.DoesNotExist:
                return HttpResponseNotFound('不正なIDです。')
            self.form = ColorModelForm(user=request.user, instance=color, data=request.POST)

        if self.form.is_valid():
            self.form.save()
            previous_url = get_previous_url(request)
            if resolve(previous_url).url_name == 'color_diary:choose-color':
                return redirect(previous_url)
            return redirect('color_diary:color-index')

        return render(request, 'color_diary/edit_color.html', {'form': self.form})