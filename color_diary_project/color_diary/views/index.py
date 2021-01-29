from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .edit import DIARY_CREATE
from ..models import Diary


class DiaryIndexView(LoginRequiredMixin, ListView):
    # todo: フィルタ機能をつける
    login_url = '/color-diary/login/'
    template_name = 'color_diary/diary_index.html'
    context_object_name = 'diary_list'

    def get_queryset(self):
        return Diary.objects.all(user=self.request.user).order_by('-created_at')


def color_index(request):
    return HttpResponse(f'色の一覧を表示します<a href={reverse("color_diary:diary-index")}>リンク</a>')
