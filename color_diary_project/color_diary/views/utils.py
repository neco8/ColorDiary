from urllib.parse import urlparse
from django.urls import reverse


def get_previous_url(request):
    referer = request.META.get('HTTP_REFERER')
    if referer is None:
        return reverse('color_diary:diary-index')

    parse = urlparse(referer)
    if parse.netloc == request.META.get('HTTP_HOST'): # 前のページが自分のサイトなら返す
        return parse.path
    return reverse('color_diary:diary-index')
