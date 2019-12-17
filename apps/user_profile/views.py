from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView

from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from apps.user_profile.forms import UserLoginForm
from apps.user_profile.models import UserProfile


class IndexView(TemplateView):
    template_name = 'user/main.html'


# class UserLoginView(LoginView):
#     template_name = 'user/login.html'
#     form_class = UserLoginForm
#
#
# class UserLogoutView(LogoutView):
#     template_name = 'user/logout.html'


class UserRegisterView(CreateView):
    """
    Creates new user if form is valid and hashes it's password
    """
    model = UserProfile
    template_name = 'user/register.html'
    success_url = reverse_lazy('index')
    fields = (
        'username',
        'email',
        'password',
    )

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'],
                            )
        login(self.request, user)
        return super().form_valid(form)

