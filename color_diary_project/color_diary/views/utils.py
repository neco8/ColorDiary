from django.urls import reverse


def get_previous_url(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and str(referer).startswith(reverse('')): # 前のページが自分のサイトなら返す
        return referer
    return reverse('color_diary:diary-index')
