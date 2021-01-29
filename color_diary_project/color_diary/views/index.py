from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
import datetime

from .edit import DIARY_CREATE


# loginが必要
# generic viewが使えそう
def diary_index(request):
    referer = request.META.get('HTTP_REFERER')
    dat = datetime.datetime.now()
    return HttpResponse(f'日記の一覧を表示します{referer=} {request=} {dat=}')


def color_index(request):
    return HttpResponse(f'色の一覧を表示します<a href={reverse("color_diary:diary-index")}>リンク</a>')
