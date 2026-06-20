from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from apps.books.serializers import LivreSerializer
from .models import Commande, Livraison

class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Livraison
        fields = ['id', 'type_livraison', 'statut', 'numero_suivi', 'date_estimee', 'date_livraison_effective']


class CommandeSerializer(serializers.ModelSerializer):
    acheteur      = UserSerializer(read_only=True)
    livre_details = LivreSerializer(source='livre', read_only=True)
    livraison     = LivraisonSerializer(read_only=True)
    type_livraison= serializers.ChoiceField(
        choices=Livraison._meta.get_field('type_livraison').choices,
        write_only=True
    )

    class Meta:
        model  = Commande
        fields = [
            'id', 'acheteur', 'livre', 'livre_details', 'nom_acheteur',
            'prenom_acheteur', 'adresse_livraison', 'telephone',
            'date_commande', 'statut', 'type_livraison', 'livraison'
        ]
        read_only_fields = ['acheteur', 'statut']

    def create(self, validated_data):
        type_livraison = validated_data.pop('type_livraison')
        commande = Commande.objects.create(**validated_data)
        Livraison.objects.create(
            commande      =commande,
            type_livraison=type_livraison,
            statut        ="En préparation chez le vendeur"
        )
        return commande


