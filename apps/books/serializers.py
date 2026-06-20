from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from .models import Evaluation, Favori, ImageLivre, Livre

class ImageLivreSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = ImageLivre
        fields = ['id', 'image', 'image_url', 'est_principale', 'date_upload']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class LivreSerializer(serializers.ModelSerializer):
    vendeur = UserSerializer(read_only=True)
    images  = ImageLivreSerializer(many=True, read_only=True)
    est_favori = serializers.SerializerMethodField()

    class Meta:
        model  = Livre
        fields = [
            'id', 'titre', 'description', 'auteur', 'matiere',
            'niveau', 'prix', 'type_livre', 'type_annonce', 'date_publication',
            'statut', 'etat', 'vendeur', 'images', 'date_creation', 'est_favori'
        ]
        read_only_fields = ['statut', 'vendeur', 'date_creation']

    def get_est_favori(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favori.objects.filter(acheteur=request.user, livre=obj).exists()
        return False


class EvaluationSerializer(serializers.ModelSerializer):
    evaluateur       = UserSerializer(read_only=True)
    evalue_details   = UserSerializer(source='evalue', read_only=True)

    class Meta:
        model  = Evaluation
        fields = ['id', 'evaluateur', 'evalue', 'evalue_details', 'commande', 'note', 'commentaire', 'date_creation']
        read_only_fields = ['evaluateur']

    def validate_note(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError('La note doit être entre 1 et 5.')
        return value


class FavoriSerializer(serializers.ModelSerializer):
    livre_details = LivreSerializer(source='livre', read_only=True)

    class Meta:
        model  = Favori
        fields = ['id', 'acheteur', 'livre', 'livre_details', 'date_ajout']
        read_only_fields = ['acheteur']
