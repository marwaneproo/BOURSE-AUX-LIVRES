from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.orders.serializers import CommandeSerializer
from apps.books.models import Livre
from apps.orders.models import Commande, StatutCommande
from .models import Profile
from .serializers import CustomTokenObtainPairSerializer, ProfileSerializer, ProfileUpdateSerializer, RegistrationSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # ── Vérification du bannissement avant d'émettre un token ──
        username = request.data.get('username', '')
        try:
            user = User.objects.get(username=username)
            profile = user.profile
            if profile.est_banni:
                return Response(
                    {'detail': 'Votre compte a été suspendu. Contactez l\'administrateur.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except (User.DoesNotExist, Profile.DoesNotExist):
            pass  # Laisse le parent gérer l'erreur d'authentification standard
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = authenticate(
                request,
                username=request.data.get('username', ''),
                password=request.data.get('password', ''),
            )
            if user is not None:
                login(request, user)
        return response

class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'me']:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        profile = request.user.profile
        if request.method == 'GET':
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(ProfileSerializer(profile, context={'request': request}).data)
            return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'])
    def public(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        try:
            profile = Profile.objects.get(user_id=user_id)
            return Response(ProfileSerializer(profile, context={'request': request}).data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profil introuvable'}, status=404)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Statistiques de l'utilisateur connecté pour le mini-dashboard."""
        user = request.user
        nb_livres_publies = Livre.objects.filter(vendeur=user).count()
        nb_ventes = Commande.objects.filter(
            livre__vendeur=user,
            statut__in=[StatutCommande.CONFIRMEE, StatutCommande.EN_COURS_DE_LIVRAISON, StatutCommande.LIVREE]
        ).count()
        nb_achats = Commande.objects.filter(
            acheteur=user,
            statut__in=[StatutCommande.CONFIRMEE, StatutCommande.EN_COURS_DE_LIVRAISON, StatutCommande.LIVREE]
        ).count()
        return Response({
            'nb_livres_publies': nb_livres_publies,
            'nb_ventes': nb_ventes,
            'nb_achats': nb_achats,
        })
class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class   = RegistrationSerializer


class AdminTokenObtainPairView(CustomTokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user = authenticate(
            request,
            username=request.data.get('username', ''),
            password=request.data.get('password', ''),
        )
        if user is None:
            return Response({'detail': 'Identifiants incorrects.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            is_admin = user.is_staff or user.profile.est_administrateur
        except Profile.DoesNotExist:
            is_admin = user.is_staff
        if not is_admin:
            return Response(
                {'detail': "Ce compte n'a pas les droits administrateur."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().post(request, *args, **kwargs)
