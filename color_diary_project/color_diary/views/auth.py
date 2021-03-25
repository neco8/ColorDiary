from django.views.generic import View, CreateView, TemplateView
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.signing import dumps, loads, BadSignature, SignatureExpired
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponseBadRequest

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
    template_name = 'color_diary/register.html'

    def form_valid(self, form):
        # validだったら、メールでURLを送る
        # URL行ったら、そこで認証、activeにする
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        site = get_current_site(self.request)
        context = {
            'protocol': self.request.scheme,
            'domain': site.domain,
            'token': dumps(user.pk),
            'user': user
        }
        subject = render_to_string('color_diary/mail/register/subject.txt', context)
        message = render_to_string('color_diary/mail/register/message.txt', context)

        user.email_user(subject, message)
        print()
        return redirect('color_diary:register-done')



class RegisterDoneView(TemplateView):
    template_name = 'color_diary/register_done.html'


class RegisterCompleteView(View):
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 30)

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        except BadSignature:
            return HttpResponseBadRequest()
        except SignatureExpired:
            return HttpResponseBadRequest()

        else:
            try:
                user = get_user_model().objects.get(id=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                user.is_active = True
                user.save()
                login(self.request, user)
                return redirect('color_diary:diary-index')