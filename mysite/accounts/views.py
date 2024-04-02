from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.decorators import login_required

from .models import Profile
from django.views.generic import TemplateView, CreateView

from .forms import UserForm, ProfileForm


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


class UpdateProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_update_form.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:login')

        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

        return render(request, self.template_name, context)


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
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileForm(self.request.POST)
        else:
            context['profile_form'] = ProfileForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']

        self.object = form.save()

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:login')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'message': 'Hello', 'foo': 'bar', 'spam': 'eggs'})
