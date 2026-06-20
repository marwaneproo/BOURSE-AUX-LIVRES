from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EtatLivre(models.TextChoices):
    NEUF = 'NEUF', 'Neuf'
    BON = 'BON', 'Bon état'
    USAGE = 'USAGE', 'Usagé'


class StatutAnnonce(models.TextChoices):
    DISPONIBLE = 'DISPONIBLE', 'Disponible'
    VENDU = 'VENDU', 'Vendu'
    ARCHIVEE = 'ARCHIVEE', 'Archivée'


class TypeAnnonce(models.TextChoices):
    VENTE = 'VENTE', 'Vente'
    DON = 'DON', 'Don'
    ECHANGE = 'ECHANGE', 'Échange'


class Livre(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    auteur = models.CharField(max_length=255)
    matiere = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_livre = models.CharField(max_length=100, default='Manuel Scolaire')
    type_annonce = models.CharField(max_length=20, choices=TypeAnnonce.choices, default=TypeAnnonce.VENTE)
    date_publication = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=StatutAnnonce.choices, default=StatutAnnonce.DISPONIBLE)
    etat = models.CharField(max_length=20, choices=EtatLivre.choices)
    vendeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='livres_a_vendre')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_livre'
        ordering = ['-date_creation']

    def __str__(self):
        return self.titre


class ImageLivre(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='livres/images/')
    est_principale = models.BooleanField(default=False)
    date_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_imagelivre'


class Favori(models.Model):
    acheteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoris')
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='favorises_par')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_favori'
        unique_together = ('acheteur', 'livre')


class Evaluation(models.Model):
    evaluateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations_donnees')
    evalue = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations_recues')
    commande = models.ForeignKey('orders.Commande', on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations')
    note = models.IntegerField()
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marketplace_evaluation'
        unique_together = ('evaluateur', 'commande')

    def clean(self):
        if not 1 <= self.note <= 5:
            raise ValidationError('La note doit être entre 1 et 5.')
