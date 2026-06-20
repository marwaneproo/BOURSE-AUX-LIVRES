from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.books.models import StatutAnnonce
from apps.notifications.models import Notification, TypeNotification
from apps.notifications.serializers import NotificationSerializer
from .models import Commande, Livraison, StatutCommande
from .serializers import CommandeSerializer, LivraisonSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    serializer_class   = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Commande.objects.filter(
            Q(acheteur=self.request.user) | Q(livre__vendeur=self.request.user)
        ).select_related('livre', 'acheteur', 'livraison')

    def perform_create(self, serializer):
        livre = serializer.validated_data['livre']
        if livre.statut != StatutAnnonce.DISPONIBLE:
            raise ValidationError({"livre": "Ce livre n'est plus disponible."})
        if livre.vendeur == self.request.user:
            raise ValidationError({"livre": "Vous ne pouvez pas acheter votre propre livre."})

        commande = serializer.save(acheteur=self.request.user)
        livre.statut = StatutAnnonce.VENDU
        livre.save()

        acheteur = self.request.user
        nom_acheteur = f"{acheteur.first_name} {acheteur.last_name}".strip() or acheteur.username
        Notification.objects.create(
            utilisateur      =livre.vendeur,
            contenu          =f"📦 {nom_acheteur} a commandé votre livre « {livre.titre} ». Acceptez ou refusez la commande.",
            type_notification=TypeNotification.COMMANDE,
            commande         =commande,
            lien             ="/commandes/"
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accepter(self, request, pk=None):
        commande = self.get_object()
        if commande.livre.vendeur != request.user:
            raise PermissionDenied("Vous n'êtes pas le vendeur.")
        if commande.statut != StatutCommande.EN_ATTENTE:
            return Response({'error': 'Cette commande ne peut plus être modifiée.'}, status=400)

        commande.statut = StatutCommande.CONFIRMEE
        commande.save()

        # Mettre à jour le statut de livraison
        if hasattr(commande, 'livraison'):
            commande.livraison.statut = 'Confirmée par le vendeur'
            commande.livraison.save()

        Notification.objects.create(
            utilisateur      =commande.acheteur,
            contenu          =f"✅ Votre commande pour « {commande.livre.titre} » a été acceptée par le vendeur !",
            type_notification=TypeNotification.COMMANDE_ACCEPTEE,
            commande         =commande,
            lien             ="/commandes/"
        )
        return Response(CommandeSerializer(commande).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refuser(self, request, pk=None):
        commande = self.get_object()
        if commande.livre.vendeur != request.user:
            raise PermissionDenied("Vous n'êtes pas le vendeur.")
        if commande.statut != StatutCommande.EN_ATTENTE:
            return Response({'error': 'Cette commande ne peut plus être modifiée.'}, status=400)

        commande.statut = StatutCommande.REFUSEE
        commande.save()

        commande.livre.statut = StatutAnnonce.DISPONIBLE
        commande.livre.save()

        Notification.objects.create(
            utilisateur      =commande.acheteur,
            contenu          =f"❌ Votre commande pour « {commande.livre.titre} » a été refusée par le vendeur.",
            type_notification=TypeNotification.COMMANDE_REFUSEE,
            commande         =commande,
            lien             ="/catalogue/"
        )
        return Response(CommandeSerializer(commande).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def marquer_en_livraison(self, request, pk=None):
        """Vendeur marque la commande en cours de livraison."""
        commande = self.get_object()
        if commande.livre.vendeur != request.user:
            raise PermissionDenied("Vous n'êtes pas le vendeur.")
        if commande.statut != StatutCommande.CONFIRMEE:
            return Response({'error': 'La commande doit être confirmée avant la livraison.'}, status=400)

        commande.statut = StatutCommande.EN_COURS_DE_LIVRAISON
        commande.save()

        if hasattr(commande, 'livraison'):
            commande.livraison.statut = 'En cours de livraison'
            commande.livraison.save()

        Notification.objects.create(
            utilisateur      =commande.acheteur,
            contenu          =f"🚚 Votre commande « {commande.livre.titre} » est en cours de livraison !",
            type_notification=TypeNotification.COMMANDE,
            commande         =commande,
            lien             ="/commandes/"
        )
        return Response(CommandeSerializer(commande).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def marquer_livree(self, request, pk=None):
        """Acheteur confirme la réception."""
        commande = self.get_object()
        if commande.acheteur != request.user:
            raise PermissionDenied("Vous n'êtes pas l'acheteur.")
        if commande.statut != StatutCommande.EN_COURS_DE_LIVRAISON:
            return Response({'error': 'La commande doit être en cours de livraison.'}, status=400)

        commande.statut = StatutCommande.LIVREE
        commande.save()

        if hasattr(commande, 'livraison'):
            commande.livraison.statut = 'Livrée'
            commande.livraison.date_livraison_effective = timezone.now()
            commande.livraison.save()

        Notification.objects.create(
            utilisateur      =commande.livre.vendeur,
            contenu          =f"✅ L'acheteur a confirmé la réception du livre « {commande.livre.titre} ».",
            type_notification=TypeNotification.COMMANDE,
            commande         =commande,
            lien             ="/commandes/"
        )
        return Response(CommandeSerializer(commande).data)

    @action(detail=False, methods=['get'])
    def mes_ventes(self, request):
        commandes = Commande.objects.filter(livre__vendeur=request.user)
        serializer = self.get_serializer(commandes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mes_achats(self, request):
        commandes = Commande.objects.filter(acheteur=request.user)
        serializer = self.get_serializer(commandes, many=True)
        return Response(serializer.data)


class LivraisonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = LivraisonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Livraison.objects.filter(
            Q(commande__acheteur=self.request.user) |
            Q(commande__livre__vendeur=self.request.user)
        )

