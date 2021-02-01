from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField

from .edit import CREATE
from ..models import Diary, Color


class DiaryIndexView(LoginRequiredMixin, ListView):
    # todo: フィルタ機能をつける
    login_url = reverse_lazy('color_diary:login')
    template_name = 'color_diary/diary_index.html'
    context_object_name = 'diary_list'

    def get_queryset(self):
        return Diary.objects.all(user=self.request.user).order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['CREATE'] = CREATE
        return context


class ColorIndexView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('color_diary:login')
    template_name = 'color_diary/color_index.html'
    context_object_name = 'color_list'

    def get_queryset(self):
        queryset = Color.objects.filter(users=self.request.user)
        sorted_list = sorted(queryset, key=lambda color: color.hex_color)

        cases = []
        for hex_color_order, color in enumerate(sorted_list):
            cases.append(When(id=color.pk, then=Value(hex_color_order)))

        return queryset.annotate(
            hex_color_order=Case(
                *cases,
                output_field=IntegerField()
            )
        ).order_by('hex_color_order')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['CREATE'] = CREATE
        context['default_color'] = Color.get_default_color()
        return context