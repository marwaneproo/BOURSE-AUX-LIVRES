from django.urls import path
from django.views.generic import RedirectView

from .views import GuestPageView, HomeView, ProtectedPageView, PublicPageView, logout_view

app_name = 'web'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('accueil/', ProtectedPageView.as_view(template_name='web/dashboard.html'), name='dashboard'),
    path('catalogue/', PublicPageView.as_view(template_name='web/livres.html'), name='books'),
    path('catalogue/detail/', PublicPageView.as_view(template_name='web/detail-livre.html'), name='book-detail'),
    path('connexion/', GuestPageView.as_view(template_name='web/login.html'), name='login'),
    path('inscription/', GuestPageView.as_view(template_name='web/register.html'), name='register'),
    path('deconnexion/', logout_view, name='logout'),
    path('vendre/', ProtectedPageView.as_view(template_name='web/vendre.html'), name='sell'),
    path('profil/', ProtectedPageView.as_view(template_name='web/profil.html'), name='profile'),
    path('commandes/', ProtectedPageView.as_view(template_name='web/commandes.html'), name='orders'),
    path('messagerie/', ProtectedPageView.as_view(template_name='web/messagerie.html'), name='messaging'),
    path('admin-panel/', PublicPageView.as_view(template_name='web/admin-panel.html'), name='admin-panel'),
    path('livres/', RedirectView.as_view(pattern_name='web:books', permanent=True, query_string=True)),
    path('livres/detail/', RedirectView.as_view(pattern_name='web:book-detail', permanent=True, query_string=True)),
    path('index.html', RedirectView.as_view(pattern_name='web:home', permanent=True)),
    path('livres.html', RedirectView.as_view(pattern_name='web:books', permanent=True, query_string=True)),
    path('detail-livre.html', RedirectView.as_view(pattern_name='web:book-detail', permanent=True, query_string=True)),
    path('login.html', RedirectView.as_view(pattern_name='web:login', permanent=True)),
    path('register.html', RedirectView.as_view(pattern_name='web:register', permanent=True)),
    path('vendre.html', RedirectView.as_view(pattern_name='web:sell', permanent=True)),
    path('profil.html', RedirectView.as_view(pattern_name='web:profile', permanent=True)),
    path('commandes.html', RedirectView.as_view(pattern_name='web:orders', permanent=True)),
    path('messagerie.html', RedirectView.as_view(pattern_name='web:messaging', permanent=True)),
    path('admin-panel.html', RedirectView.as_view(pattern_name='web:admin-panel', permanent=True)),
]
