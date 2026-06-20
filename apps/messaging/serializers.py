from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    expediteur_details  = UserSerializer(source='expediteur', read_only=True)
    destinataire_details= UserSerializer(source='destinataire', read_only=True)

    class Meta:
        model  = Message
        fields = [
            'id', 'expediteur', 'expediteur_details', 'destinataire',
            'destinataire_details', 'contenu', 'date_envoi', 'est_lu'
        ]
        read_only_fields = ['expediteur', 'date_envoi', 'est_lu']


