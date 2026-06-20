from django.db.models import Avg, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.models import Profile
from apps.orders.models import StatutCommande
from .models import EtatLivre, Evaluation, Favori, ImageLivre, Livre, StatutAnnonce
from .serializers import EvaluationSerializer, FavoriSerializer, LivreSerializer

class LivreViewSet(viewsets.ModelViewSet):
    queryset           = Livre.objects.all()
    serializer_class   = LivreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if self.action == 'retrieve':
            queryset = Livre.objects.all()
        elif self.action in ['mes_livres']:
            queryset = Livre.objects.filter(vendeur=self.request.user)
        else:
            queryset = Livre.objects.filter(statut=StatutAnnonce.DISPONIBLE)

        matiere  = self.request.query_params.get('matiere')
        niveau   = self.request.query_params.get('niveau')
        max_prix = self.request.query_params.get('max_prix')
        q        = self.request.query_params.get('q')
        vendeur  = self.request.query_params.get('vendeur')

        if matiere:  queryset = queryset.filter(matiere__icontains=matiere)
        if niveau:   queryset = queryset.filter(niveau__iexact=niveau)
        if max_prix: queryset = queryset.filter(prix__lte=max_prix)
        if q:        queryset = queryset.filter(
            Q(titre__icontains=q) | Q(auteur__icontains=q) | Q(matiere__icontains=q)
        )
        if vendeur:  queryset = queryset.filter(vendeur_id=vendeur)
        return queryset

    def create(self, request, *args, **kwargs):
        data = {}
        for key in request.data:
            if hasattr(request.data, 'getlist'):
                vals = request.data.getlist(key)
                data[key] = vals[0] if len(vals) == 1 else vals
            else:
                data[key] = request.data[key]

        if 'prix' in data and data['prix'] in ('', None, 'null'):
            data['prix'] = None
        if not data.get('type_livre'):
            data['type_livre'] = 'Manuel Scolaire'

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        livre = serializer.save(vendeur=self.request.user)
        images = []
        if 'image' in self.request.FILES:
            images.append(self.request.FILES['image'])
        images.extend(self.request.FILES.getlist('images'))
        for i, img in enumerate(images):
            ImageLivre.objects.create(livre=livre, image=img, est_principale=(i == 0))

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mes_livres(self, request):
        livres = Livre.objects.filter(vendeur=request.user)
        serializer = self.get_serializer(livres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def archiver(self, request, pk=None):
        livre = self.get_object()
        if livre.vendeur != request.user:
            raise PermissionDenied("Vous n'êtes pas le vendeur de ce livre.")
        livre.statut = StatutAnnonce.ARCHIVEE
        livre.save()
        return Response({'statut': livre.statut})

    def update(self, request, *args, **kwargs):
        livre = self.get_object()
        if livre.vendeur != request.user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres livres.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        livre = self.get_object()
        if livre.vendeur != request.user and not request.user.is_staff:
            try:
                if not request.user.profile.est_administrateur:
                    raise PermissionDenied()
            except Profile.DoesNotExist:
                raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)

class FavoriViewSet(viewsets.ModelViewSet):
    serializer_class   = FavoriSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favori.objects.filter(acheteur=self.request.user).select_related('livre')

    def perform_create(self, serializer):
        serializer.save(acheteur=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        livre_id = request.data.get('livre')
        if not livre_id:
            return Response({'error': 'livre requis'}, status=400)
        try:
            livre = Livre.objects.get(pk=livre_id)
        except Livre.DoesNotExist:
            return Response({'error': 'Livre introuvable'}, status=404)

        if livre.vendeur_id == request.user.id:
            return Response({"error": "Vous ne pouvez pas ajouter votre propre livre aux favoris."}, status=400)

        favori, created = Favori.objects.get_or_create(acheteur=request.user, livre=livre)
        if not created:
            favori.delete()
            return Response({'est_favori': False, 'message': 'Retiré des favoris'})
        return Response({'est_favori': True, 'message': 'Ajouté aux favoris'})


# ─── ÉVALUATIONS ──────────────────────────────────────────────────────────────

class EvaluationViewSet(viewsets.ModelViewSet):
    serializer_class   = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        evalue_id = self.request.query_params.get('evalue')
        if evalue_id:
            return Evaluation.objects.filter(evalue_id=evalue_id)
        return Evaluation.objects.filter(
            Q(evaluateur=self.request.user) | Q(evalue=self.request.user)
        )

    def perform_create(self, serializer):
        commande = serializer.validated_data.get('commande')

        if commande:
            # Vérification participation
            if commande.acheteur != self.request.user and commande.livre.vendeur != self.request.user:
                raise ValidationError({'commande': "Vous n'avez pas participé à cette commande."})

            # ── Bug fix: l'évaluation n'est possible que sur une commande LIVREE ──
            if commande.statut != StatutCommande.LIVREE:
                raise ValidationError({'commande': "Vous ne pouvez évaluer qu'une commande livrée."})

            # Anti-spam
            if Evaluation.objects.filter(evaluateur=self.request.user, commande=commande).exists():
                raise ValidationError({'commande': 'Vous avez déjà évalué pour cette commande.'})

        serializer.save(evaluateur=self.request.user)

    @action(detail=False, methods=['get'])
    def profil(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requis'}, status=400)
        evals = Evaluation.objects.filter(evalue_id=user_id)
        avg   = evals.aggregate(avg=Avg('note'))['avg'] or 0
        return Response({
            'evaluations' : EvaluationSerializer(evals, many=True).data,
            'note_moyenne': round(avg, 1),
            'nb_evaluations': evals.count()
        })


