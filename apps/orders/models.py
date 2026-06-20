from django.conf import settings
from django.db import models


class StatutCommande(models.TextChoices):
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    CONFIRMEE = 'CONFIRMEE', 'Confirmée'
    REFUSEE = 'REFUSEE', 'Refusée'
    EN_COURS_DE_LIVRAISON = 'EN_COURS_DE_LIVRAISON', 'En cours de livraison'
    LIVREE = 'LIVREE', 'Livrée'
    ANNULEE = 'ANNULEE', 'Annulée'


class TypeLivraison(models.TextChoices):
    REMISE_EN_MAIN_PROPRE = 'REMISE_EN_MAIN_PROPRE', 'Remise en main propre'
    LIVRAISON_DOMICILE = 'LIVRAISON_DOMICILE', 'Livraison à domicile'


class Commande(models.Model):
    acheteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commandes')
    livre = models.ForeignKey('books.Livre', on_delete=models.PROTECT, related_name='commandes_associees')
    nom_acheteur = models.CharField(max_length=100)
    prenom_acheteur = models.CharField(max_length=100)
    adresse_livraison = models.TextField()
    telephone = models.CharField(max_length=20)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=30, choices=StatutCommande.choices, default=StatutCommande.EN_ATTENTE)

    class Meta:
        db_table = 'marketplace_commande'

    def __str__(self):
        return f'Commande #{self.id} - {self.livre.titre}'


class Livraison(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='livraison')
    type_livraison = models.CharField(max_length=30, choices=TypeLivraison.choices)
    statut = models.CharField(max_length=50)
    numero_suivi = models.CharField(max_length=100, blank=True, null=True)
    date_estimee = models.DateField(blank=True, null=True)
    date_livraison_effective = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'marketplace_livraison'
