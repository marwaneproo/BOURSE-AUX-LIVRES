from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from .models import Signalement

class SignalementSerializer(serializers.ModelSerializer):
    signaleur  = UserSerializer(read_only=True)
    traite_par = UserSerializer(read_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        livre = attrs.get("livre_signale")
        utilisateur = attrs.get("utilisateur_signale")
        if request and livre and livre.vendeur_id == request.user.id:
            raise serializers.ValidationError({
                "livre_signale": "Vous ne pouvez pas signaler votre propre annonce."
            })
        if request and utilisateur and utilisateur.id == request.user.id:
            raise serializers.ValidationError({
                "utilisateur_signale": "Vous ne pouvez pas vous signaler vous-même."
            })
        return attrs

    class Meta:
        model  = Signalement
        fields = [
            'id', 'signaleur', 'livre_signale', 'utilisateur_signale',
            'raison', 'date_signalement', 'statut', 'traite_par',
            'message_admin', 'date_traitement'
        ]
        read_only_fields = ['signaleur', 'statut', 'traite_par', 'message_admin', 'date_traitement']
