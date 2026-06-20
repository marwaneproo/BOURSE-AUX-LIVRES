from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import resolve, reverse

from apps.notifications.models import Notification, TypeNotification
from .models import Profile


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        Profile.objects.create(user=self.user)
        self.admin = User.objects.create_user(username='manager', password='password123', is_staff=True)
        Profile.objects.create(user=self.admin, est_administrateur=False)

    def test_login_api_creates_django_session(self):
        response = self.client.post(
            reverse('auth-login'),
            {'username': 'student', 'password': 'password123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_admin_login_rejects_regular_users(self):
        response = self.client.post(
            reverse('auth-admin-login'),
            {'username': 'student', 'password': 'password123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_login_accepts_admin_users(self):
        response = self.client.post(
            reverse('auth-admin-login'),
            {'username': 'manager', 'password': 'password123'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin.id)
        self.assertTrue(response.json()['user']['est_administrateur'])

    def test_admin_stats_returns_dashboard_contract(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin-stats'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('nb_commandes', response.json())
        self.assertIn('derniers_users', response.json())
        users = response.json()['derniers_users']
        self.assertTrue(users)
        self.assertIn('est_administrateur', users[0])
        self.assertIn("est_banni", users[0])
        self.assertIn("users_page", response.json())
        self.assertIn("books_page", response.json())
        self.assertIn("reports_page", response.json())
        self.assertIn("notification_history", response.json())
        self.assertIn("activity_log", response.json())

    def test_admin_notification_works_with_session_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        page = client.get(reverse("web:admin-panel"))
        csrf_token = page.cookies["csrftoken"].value

        response = client.post(
            reverse("admin-notify"),
            {"user_id": self.user.id, "contenu": "  Message de test  "},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.get(utilisateur=self.user)
        self.assertEqual(notification.contenu, "Message de test")
        self.assertEqual(notification.type_notification, TypeNotification.ADMIN_MESSAGE)
        stats = client.get(reverse("admin-stats")).json()
        self.assertTrue(stats["notification_history"])
        self.assertTrue(stats["activity_log"])

    def test_admin_notification_rejects_missing_csrf_for_session(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)

        response = client.post(
            reverse("admin-notify"),
            {"user_id": self.user.id, "contenu": "Message de test"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_stats_search_and_pagination(self):
        for index in range(11):
            user = User.objects.create_user(
                username=f"student{index}",
                email=f"student{index}@example.com",
                password="password123",
            )
            Profile.objects.create(user=user, est_banni=index == 0)
        self.client.force_login(self.admin)

        page = self.client.get(reverse("admin-stats"), {"users_page": 1}).json()["users_page"]
        banned = self.client.get(
            reverse("admin-stats"),
            {"users_status": "banned", "users_q": "student0"},
        ).json()["users_page"]

        self.assertEqual(len(page["results"]), 10)
        self.assertGreaterEqual(page["pages"], 2)
        self.assertEqual(banned["count"], 1)
        self.assertTrue(banned["results"][0]["est_banni"])

    def test_admin_stats_rejects_regular_users(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('admin-stats')).status_code, 403)

    def test_domain_routes_resolve(self):
        routes = [
            '/api/auth/login/',
            '/api/auth/admin/login/',
            '/api/profiles/me/',
            '/api/livres/',
            '/api/commandes/',
            '/api/messages/',
            '/api/notifications/',
            '/api/signalements/',
            '/api/admin-panel/stats/',
        ]
        for route in routes:
            with self.subTest(route=route):
                self.assertIsNotNone(resolve(route))
