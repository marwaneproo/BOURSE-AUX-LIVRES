from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Profile


class PageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        Profile.objects.create(user=self.user, est_acheteur=True, est_vendeur=True)
        self.admin = User.objects.create_user(username='manager', password='password123', is_staff=True)
        Profile.objects.create(user=self.admin, est_administrateur=True)

    def test_public_pages_render_for_guests(self):
        for name in ['home', 'login', 'register', 'books', 'book-detail', 'admin-panel']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(f'web:{name}')).status_code, 200)

    def test_member_pages_redirect_guests_to_login(self):
        for name in ['dashboard', 'sell', 'profile', 'orders', 'messaging']:
            with self.subTest(name=name):
                response = self.client.get(reverse(f'web:{name}'))
                self.assertRedirects(
                    response,
                    f"{reverse('web:login')}?next={reverse(f'web:{name}')}",
                    fetch_redirect_response=False,
                )

    def test_regular_user_pages_render_with_session(self):
        self.client.force_login(self.user)
        for name in ['dashboard', 'books', 'book-detail', 'sell', 'profile', 'orders', 'messaging']:
            with self.subTest(name=name):
                response = self.client.get(reverse(f'web:{name}'))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'django-user-data')

    def test_home_redirects_authenticated_user_once(self):
        self.client.force_login(self.user)
        self.assertRedirects(
            self.client.get(reverse('web:home')),
            reverse('web:dashboard'),
            fetch_redirect_response=False,
        )

    def test_admin_portal_uses_its_own_login_page(self):
        response = self.client.get(reverse('web:admin-panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connexion Admin")
        self.assertIn("csrftoken", response.cookies)

    def test_catalogue_templates_include_owner_aware_controls(self):
        catalogue = self.client.get(reverse("web:books"))
        detail = self.client.get(reverse("web:book-detail"))
        self.assertContains(catalogue, "const isOwner")
        self.assertContains(catalogue, "favoriteButton")
        self.assertContains(detail, "btn-contacter\").style.display = \"none")

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse('web:logout')), reverse('web:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_legacy_catalog_url_redirects(self):
        response = self.client.get('/livres/?q=python')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, f"{reverse('web:books')}?q=python")
