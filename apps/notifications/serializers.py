from rest_framework import serializers

from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'utilisateur', 'contenu', 'lien', 'commande', 'date_creation', 'est_lue', 'type_notification']
        read_only_fields = ['utilisateur', 'date_creation']
