from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from ..utils import get_hashids
from ..forms import DiaryModelForm
from ..models import Diary, Color


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


# todo: choose_colorから来た場合にはchoose_colorに戻してあげる
def edit_color(request, color_hash_id):
    #diary_hash_stringを戻した時0だったらcreate
    return HttpResponse(f'ここで既存の色を編集したり、新しく色を作ります<a href={reverse("color_diary:diary-index")}>リンク</a>')
