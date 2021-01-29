from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .edit import DIARY_CREATE
from ..utils import get_hashids
from ..models import Diary


class DiaryIndexView(LoginRequiredMixin, ListView):
    # todo: フィルタ機能をつける
    login_url = '/color-diary/login/'
    template_name = 'color_diary/diary_index.html'
    context_object_name = 'diary_list'

    def get_queryset(self):
        return Diary.objects.all(user=self.request.user).order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['DIARY_CREATE'] = DIARY_CREATE
        return context


def color_index(request):
    return HttpResponse(f'色の一覧を表示します<a href={reverse("color_diary:diary-index")}>リンク</a>')
