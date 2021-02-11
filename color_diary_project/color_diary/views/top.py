from django.shortcuts import render, redirect


def top(request):
    if request.user.is_authenticated:
        return redirect('color_diary:diary-index')
    else:
        return render(request, 'color_diary/welcome.html')