from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View

from .models import Profile
from django.views.generic import TemplateView, CreateView


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'accounts/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin')

    return render(request, 'accounts/login.html', {'error': 'Invalid username or password.'})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('accounts:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


@user_passes_test(lambda u: u.is_superuser)
def set_cookies_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set', content_type='text/plain', charset='utf-8', status=200)
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


def get_cookies_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default_value')
    return HttpResponse(f'Cookie value: fizz={value!r}')


@permission_required('accounts.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Session set!', content_type='text/plain', charset='utf-8', status=200)
    request.session['foobar'] = 'spameggs'
    return response


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default_value')
    return HttpResponse(f'Session value: {value!r}', content_type='text', charset='utf-8', status=200)


class AboutMeView(TemplateView):
    template_name = "accounts/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy('accounts:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        # user authentication:
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password)
        # user login:
        login(self.request, user)
        return response


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'message': 'Hello', 'foo': 'bar', 'spam': 'eggs'})