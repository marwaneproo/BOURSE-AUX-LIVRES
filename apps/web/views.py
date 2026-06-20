from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.views.generic import TemplateView


def frontend_user(user):
    if not user.is_authenticated:
        return None
    profile = getattr(user, 'profile', None)
    photo_url = profile.photo.url if profile and profile.photo else None
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'nom': user.last_name,
        'prenom': user.first_name,
        'est_administrateur': user.is_staff or bool(profile and profile.est_administrateur),
        'est_vendeur': bool(profile and profile.est_vendeur),
        'est_acheteur': bool(profile and profile.est_acheteur),
        'photo_url': photo_url,
    }


class UserContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_token(self.request)
        context["frontend_user"] = frontend_user(self.request.user)
        return context


class HomeView(UserContextMixin, TemplateView):
    template_name = 'web/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or getattr(request.user.profile, 'est_administrateur', False):
                return redirect('web:admin-panel')
            return redirect('web:dashboard')
        return super().dispatch(request, *args, **kwargs)


class GuestPageView(UserContextMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or getattr(request.user.profile, 'est_administrateur', False):
                return redirect('web:admin-panel')
            return redirect('web:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ProtectedPageView(UserContextMixin, LoginRequiredMixin, TemplateView):
    login_url = 'web:login'


class AdminPageView(UserContextMixin, UserPassesTestMixin, TemplateView):
    login_url = 'web:login'

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_staff or getattr(user.profile, 'est_administrateur', False)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url())
        return redirect('web:dashboard')


def logout_view(request):
    logout(request)
    return redirect('web:home')


class PublicPageView(UserContextMixin, TemplateView):
    pass
