from django.conf import settings
from django.db import models


class TypeNotification(models.TextChoices):
    MESSAGE = 'MESSAGE', 'Message'
    COMMANDE = 'COMMANDE', 'Commande'
    COMMANDE_ACCEPTEE = 'COMMANDE_ACCEPTEE', 'Commande acceptée'
    COMMANDE_REFUSEE = 'COMMANDE_REFUSEE', 'Commande refusée'
    FAVORI_DEVENU_DISPONIBLE = 'FAVORI_DEVENU_DISPONIBLE', 'Favori devenu disponible'
    ALERTE_SYSTEME = 'ALERTE_SYSTEME', 'Alerte système'
    ADMIN_MESSAGE = 'ADMIN_MESSAGE', 'Message admin'
    SIGNALEMENT_ACCEPTE = 'SIGNALEMENT_ACCEPTE', 'Signalement accepté'
    SIGNALEMENT_REFUSE = 'SIGNALEMENT_REFUSE', 'Signalement refusé'


class Notification(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    contenu = models.TextField()
    lien = models.CharField(max_length=255, blank=True, default='')
    commande = models.ForeignKey('orders.Commande', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    date_creation = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)
    type_notification = models.CharField(max_length=30, choices=TypeNotification.choices)

    class Meta:
        db_table = 'marketplace_notification'
        ordering = ['-date_creation']

    def __str__(self):
        return f'Notification pour {self.utilisateur.username}'
