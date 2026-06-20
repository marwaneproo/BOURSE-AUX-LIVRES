from django.conf import settings
from django.db import models


class StatutSignalement(models.TextChoices):
    PENDING = 'PENDING', 'En attente'
    ACCEPTED = 'ACCEPTED', 'Accepté'
    REJECTED = 'REJECTED', 'Rejeté'


class Signalement(models.Model):
    signaleur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signalements_faits')
    livre_signale = models.ForeignKey('books.Livre', on_delete=models.CASCADE, null=True, blank=True, related_name='signalements')
    utilisateur_signale = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='accuse_de')
    raison = models.TextField()
    date_signalement = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=30, choices=StatutSignalement.choices, default=StatutSignalement.PENDING)
    traite_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_traites')
    message_admin = models.TextField(blank=True, default='')
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'marketplace_signalement'

    def __str__(self):
        return f'Signalement #{self.id} - {self.statut}'
