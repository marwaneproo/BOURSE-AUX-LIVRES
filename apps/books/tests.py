from django.contrib.auth.models import User
from django.test import TestCase

from apps.accounts.models import Profile
from apps.messaging.models import Message
from apps.moderation.models import Signalement
from apps.notifications.models import Notification, TypeNotification
from apps.orders.models import Commande, Livraison, StatutCommande, TypeLivraison
from .models import Evaluation, Favori, ImageLivre, Livre, StatutAnnonce


class DomainModelOwnershipTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='password123')
        self.buyer = User.objects.create_user(username='buyer', password='password123')
        Profile.objects.create(user=self.seller, est_vendeur=True)
        Profile.objects.create(user=self.buyer, est_acheteur=True)
        self.book = Livre.objects.create(
            titre='Django',
            description='Reference',
            auteur='Auteur',
            matiere='Informatique',
            niveau='1ère année',
            prix=100,
            etat='BON',
            vendeur=self.seller,
        )

    def test_models_keep_legacy_tables_under_domain_apps(self):
        expected = {
            Profile: ('accounts.Profile', 'marketplace_profile'),
            Livre: ('books.Livre', 'marketplace_livre'),
            ImageLivre: ('books.ImageLivre', 'marketplace_imagelivre'),
            Favori: ('books.Favori', 'marketplace_favori'),
            Evaluation: ('books.Evaluation', 'marketplace_evaluation'),
            Commande: ('orders.Commande', 'marketplace_commande'),
            Livraison: ('orders.Livraison', 'marketplace_livraison'),
            Message: ('messaging.Message', 'marketplace_message'),
            Signalement: ('moderation.Signalement', 'marketplace_signalement'),
            Notification: ('notifications.Notification', 'marketplace_notification'),
        }
        for model, (label, table) in expected.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(model._meta.label, label)
                self.assertEqual(model._meta.db_table, table)

    def test_favorite_toggle_adds_and_removes(self):
        self.client.force_login(self.buyer)
        url = '/api/favoris/toggle/'
        response = self.client.post(url, {'livre': self.book.id}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['est_favori'])
        response = self.client.post(url, {'livre': self.book.id}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['est_favori'])

    def test_seller_cannot_favorite_or_report_own_listing(self):
        self.client.force_login(self.seller)
        favorite_response = self.client.post(
            "/api/favoris/toggle/",
            {"livre": self.book.id},
            content_type="application/json",
        )
        report_response = self.client.post(
            "/api/signalements/",
            {"livre_signale": self.book.id, "raison": "Test"},
            content_type="application/json",
        )
        self.assertEqual(favorite_response.status_code, 400)
        self.assertEqual(report_response.status_code, 400)
        self.assertFalse(Favori.objects.filter(acheteur=self.seller).exists())
        self.assertFalse(Signalement.objects.filter(signaleur=self.seller).exists())

    def test_accepting_book_report_archives_listing_and_notifies_seller(self):
        admin = User.objects.create_user(
            username="admin",
            password="password123",
            is_staff=True,
        )
        Profile.objects.create(user=admin, est_administrateur=True)
        report = Signalement.objects.create(
            signaleur=self.buyer,
            livre_signale=self.book,
            raison="Annonce non conforme",
        )
        self.client.force_login(admin)

        response = self.client.post(
            f"/api/signalements/{report.id}/accepter/",
            {},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        report.refresh_from_db()
        self.assertEqual(self.book.statut, StatutAnnonce.ARCHIVEE)
        self.assertEqual(report.statut, "ACCEPTED")
        self.assertFalse(
            Livre.objects.filter(
                pk=self.book.pk,
                statut=StatutAnnonce.DISPONIBLE,
            ).exists()
        )

        reporter_notification = Notification.objects.get(
            utilisateur=self.buyer,
            type_notification=TypeNotification.SIGNALEMENT_ACCEPTE,
        )
        seller_notification = Notification.objects.get(
            utilisateur=self.seller,
            type_notification=TypeNotification.ALERTE_SYSTEME,
        )
        self.assertIn(self.book.titre, reporter_notification.contenu)
        self.assertIn(self.book.titre, seller_notification.contenu)

    def test_cross_app_relationships_and_signal(self):
        Favori.objects.create(acheteur=self.buyer, livre=self.book)
        commande = Commande.objects.create(
            acheteur=self.buyer,
            livre=self.book,
            nom_acheteur='Buyer',
            prenom_acheteur='Student',
            adresse_livraison='EMSI',
            telephone='0600000000',
            statut=StatutCommande.LIVREE,
        )
        Livraison.objects.create(
            commande=commande,
            type_livraison=TypeLivraison.REMISE_EN_MAIN_PROPRE,
            statut='Livrée',
        )
        Evaluation.objects.create(
            evaluateur=self.buyer,
            evalue=self.seller,
            commande=commande,
            note=5,
        )
        Message.objects.create(expediteur=self.buyer, destinataire=self.seller, contenu='Disponible ?')
        Signalement.objects.create(signaleur=self.buyer, livre_signale=self.book, raison='Test')
        self.book.statut = StatutAnnonce.DISPONIBLE
        self.book.save()

        notification = Notification.objects.get(utilisateur=self.buyer)
        self.assertEqual(notification.type_notification, TypeNotification.FAVORI_DEVENU_DISPONIBLE)
        self.assertEqual(commande.livraison.statut, 'Livrée')
        self.assertEqual(self.seller.evaluations_recues.get().note, 5)
