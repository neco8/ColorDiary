from django.views.generic import View, CreateView
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME, get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from ..admin import UserCreationForm
from ..forms import UserLoginForm
from ..models import User


class LoginView(View):
    template_name = 'color_diary/login.html'

    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        return render(request, 'color_diary/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(self.get_redirect_url())

        return render(request, 'color_diary/login.html', {
            'form': UserLoginForm(initial={'email': email}),
            'error_message': 'invalid login.'
        })

    def get_redirect_url(self):
        url = self.request.GET.get(REDIRECT_FIELD_NAME, reverse('color_diary:diary-index'))
        return url


def logout_view(request):
    logout(request)
    return redirect('color_diary:top')


class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    success_url = reverse_lazy('color_diary:diary-index')
    template_name = 'color_diary/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, email=email, password=password)
        login(self.request, user=user)

        return response