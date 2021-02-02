from django.shortcuts import render


def welcome(request):
    return render(request, 'color_diary/welcome.html')