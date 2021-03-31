from django.http import HttpResponseNotFound
from django.urls import reverse_lazy, resolve
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from ..utils import get_hashids
from ..forms import DiaryModelForm, ColorModelForm
from ..models import Diary, Color
from .utils import get_previous_url


CREATE = 0


class EditDiaryView(LoginRequiredMixin, View):
    login_url = reverse_lazy('color_diary:login')

    def get(self, request, *args, **kwargs):
        # colorかcolor_levelがNoneのとき、このview関数後html描画時に色選択に遷移する。クライアント側で保存しておいた値を考慮して、edit_diary.htmlに実装

        try:
            diary_id = get_hashids().decode(kwargs['diary_hash_id'])[0]
        except:
            return HttpResponseNotFound('そのURLは存在しません。')

        if diary_id == CREATE:
            # colorかcolor_levelがNoneのときでも、このviewを実行する可能性があるのでこの安全策は必要
            color_id = int(request.session.get('color_id', 0))
            color_level = int(request.session.get('color_level')) if 'color_level' in request.session else None
            try:
                color = Color.objects.get(pk=color_id)
            except Color.DoesNotExist:
                color = None
            form = DiaryModelForm(color=color, color_level=color_level, user=request.user)

            return render(request, 'color_diary/edit_diary.html', {
                'form': form,
            })

        # 日記編集
        try:
            diary = Diary.objects.get(user=request.user, id=diary_id)
        except Diary.DoesNotExist:
            # todo: 404画面を作る
            return HttpResponseNotFound()

        if request.session.get('color_choosed_diary_id') != diary_id:
            form = DiaryModelForm(user=request.user, instance=diary)
            return render(request, 'color_diary/edit_diary.html', {
                'form': form,
            })

        color_id = int(request.session.get('color_id', diary.color.pk))
        color_level = int(request.session.get('color_level', diary.color_level))
        form = DiaryModelForm(color=Color.objects.get(pk=color_id), color_level=color_level, user=request.user, instance=diary)
        return render(request, 'color_diary/edit_diary.html', {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        color = Color.objects.get(users=request.user, id=int(request.POST.get('color')))
        color_level = int(request.POST.get('color_level'))

        try:
            diary_id = get_hashids().decode(kwargs['diary_hash_id'])[0]
        except:
            return HttpResponseNotFound()

        if diary_id == CREATE:
            form = DiaryModelForm(
                user=request.user,
                color=color,
                color_level=color_level,
                data=request.POST,
            )
        else: # 編集
            try:
                diary = Diary.objects.get(user=request.user, id=diary_id)
            except Diary.DoesNotExist:
                return HttpResponseNotFound()
            form = DiaryModelForm(
                user=request.user,
                color=color,
                color_level=color_level,
                instance=diary,
                data=request.POST,
            )
        if form.is_valid():
            form.save()
            if 'color_id' in request.session:
                del request.session['color_id']
            if 'color_level' in request.session:
                del request.session['color_level']
            if 'color_choosed_diary_id' in request.session:
                del request.session['color_choosed_diary_id']

            return redirect('color_diary:diary-index')
        return render(request, 'color_diary/edit_diary.html', {'form': self.form})


class EditColorView(LoginRequiredMixin, View):
    login_url = reverse_lazy('color_diary:login')

    def get(self, request, *args, **kwargs):
        try:
            color_id = get_hashids().decode(kwargs['color_hash_id'])[0]
        except:
            return HttpResponseNotFound()

        if color_id == CREATE:
            self.form = ColorModelForm(user=request.user, initial={'hex_color': '000000'})
        elif color_id == Color.get_default_color().pk:
            return HttpResponseNotFound()
        else: # 編集
            try:
                color = Color.objects.get(users=request.user, id=color_id)
            except Color.DoesNotExist:
                return HttpResponseNotFound()

            self.form = ColorModelForm(user=request.user, instance=color)
        request.session['previous_url'] = get_previous_url(request)
        return render(request, 'color_diary/edit_color.html', {'form': self.form})

    def post(self, request, *args, **kwargs):
        try:
            color_id = get_hashids().decode(kwargs['color_hash_id'])[0]
        except:
            return HttpResponseNotFound()

        if color_id == CREATE:
            self.form = ColorModelForm(user=request.user, data=request.POST)
        elif color_id == Color.get_default_color().pk:
            return HttpResponseNotFound()
        else: # 編集
            try:
                color = Color.objects.get(users=request.user, id=color_id)
            except Color.DoesNotExist:
                return HttpResponseNotFound()
            self.form = ColorModelForm(user=request.user, instance=color, data=request.POST)

        if self.form.is_valid():
            self.form.save()
            previous_url = request.session.pop('previous_url')
            if resolve(previous_url).url_name == 'choose-color':
                return redirect(previous_url)
            return redirect('color_diary:color-index')

        return render(request, 'color_diary/edit_color.html', {'form': self.form})