from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.models import Notification, TypeNotification
from .models import Favori, Livre, StatutAnnonce


@receiver(post_save, sender=Livre)
def notifier_changement_statut(sender, instance, created, **kwargs):
    if not created and instance.statut == StatutAnnonce.DISPONIBLE:
        for favori in Favori.objects.filter(livre=instance):
            Notification.objects.create(
                utilisateur=favori.acheteur,
                contenu=f"Bonne nouvelle ! Le livre '{instance.titre}' est de nouveau disponible.",
                type_notification=TypeNotification.FAVORI_DEVENU_DISPONIBLE,
                lien=f'/catalogue/detail/?id={instance.id}',
            )
