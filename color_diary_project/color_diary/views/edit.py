from django.http import HttpResponse
from django.urls import reverse


CREATE = 0


def edit_diary(request, diary_hash_id):
    #diary_hash_stringを戻した時0だったらcreate
    # todo: choose_colorから送られてきた色idと色レベルを受け取る
    return HttpResponse(f'ここで既存の日記を編集したり、作成します<a href={reverse("color_diary:diary-index")}>リンク</a>')


# todo: choose_colorから来た場合にはchoose_colorに戻してあげる
def edit_color(request, color_hash_id):
    #diary_hash_stringを戻した時0だったらcreate
    return HttpResponse(f'ここで既存の色を編集したり、新しく色を作ります<a href={reverse("color_diary:diary-index")}>リンク</a>')
