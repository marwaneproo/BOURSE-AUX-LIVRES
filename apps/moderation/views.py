from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.serializers import UserSerializer
from apps.books.serializers import LivreSerializer
from apps.accounts.models import Profile
from apps.books.models import EtatLivre, Livre, StatutAnnonce
from apps.notifications.models import Notification, TypeNotification
from apps.orders.models import Commande
from .models import Signalement, StatutSignalement
from .permissions import IsAdminProfile
from .serializers import SignalementSerializer


def log_admin_action(user, obj, action_flag, message):
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=str(obj.pk),
        object_repr=str(obj)[:200],
        action_flag=action_flag,
        change_message=message,
    )


def paginated_data(queryset, request, prefix, serializer):
    search = request.query_params.get(f"{prefix}_q", "").strip()
    page_number = request.query_params.get(f"{prefix}_page", 1)
    if prefix == "users" and search:
        queryset = queryset.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )
    elif prefix == "books" and search:
        queryset = queryset.filter(
            Q(titre__icontains=search)
            | Q(auteur__icontains=search)
            | Q(matiere__icontains=search)
            | Q(vendeur__username__icontains=search)
        )
    elif prefix == "reports" and search:
        queryset = queryset.filter(
            Q(raison__icontains=search)
            | Q(signaleur__username__icontains=search)
        )

    status_value = request.query_params.get(f"{prefix}_status", "").strip()
    if status_value:
        if prefix == "users":
            queryset = queryset.filter(profile__est_banni=status_value == "banned")
        elif prefix == "books":
            queryset = queryset.filter(statut=status_value)
        elif prefix == "reports":
            queryset = queryset.filter(statut=status_value)

    page = Paginator(queryset, 10).get_page(page_number)
    return {
        "results": serializer(page.object_list),
        "page": page.number,
        "pages": page.paginator.num_pages,
        "count": page.paginator.count,
        "has_previous": page.has_previous(),
        "has_next": page.has_next(),
    }


class SignalementViewSet(viewsets.ModelViewSet):
    serializer_class   = SignalementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or (
            getattr(self.request.user, 'profile', None) and
            self.request.user.profile.est_administrateur
        ):
            return Signalement.objects.all().order_by('-date_signalement')
        return Signalement.objects.filter(signaleur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(signaleur=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminProfile])
    def accepter(self, request, pk=None):
        """Accepte le signalement, retire le livre et notifie les parties."""
        try:
            sig = Signalement.objects.select_related(
                "signaleur",
                "livre_signale__vendeur",
            ).get(pk=pk)
        except Signalement.DoesNotExist:
            return Response({"error": "Signalement introuvable"}, status=404)

        if sig.statut != StatutSignalement.PENDING:
            return Response({"error": "Ce signalement a deja ete traite."}, status=400)
        livre = sig.livre_signale
        vendeur = livre.vendeur if livre else None
        titre = livre.titre if livre else None

        with transaction.atomic():
            if livre:
                livre.statut = StatutAnnonce.ARCHIVEE
                livre.save(update_fields=["statut"])

            sig.statut = StatutSignalement.ACCEPTED
            sig.traite_par = request.user
            sig.date_traitement = timezone.now()
            sig.save(update_fields=["statut", "traite_par", "date_traitement"])

            notifications = [
                Notification(
                    utilisateur=sig.signaleur,
                    contenu=(
                        f"Votre signalement a ete accepte. Le livre {titre} "
                        "a ete retire du catalogue."
                        if livre else
                        "Votre signalement a ete accepte et traite par un administrateur."
                    ),
                    type_notification=TypeNotification.SIGNALEMENT_ACCEPTE,
                )
            ]
            if vendeur:
                notifications.append(Notification(
                    utilisateur=vendeur,
                    contenu=(
                        f"Votre annonce {titre} a ete retiree du catalogue "
                        "par un administrateur apres validation du signalement."
                    ),
                    type_notification=TypeNotification.ALERTE_SYSTEME,
                ))
            Notification.objects.bulk_create(notifications)
            log_admin_action(
                request.user, sig, CHANGE,
                "Signalement accepté et annonce retirée." if livre else "Signalement accepté.",
            )

        return Response(SignalementSerializer(sig).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminProfile])
    def refuser(self, request, pk=None):
        """Admin refuse le signalement avec message explicatif."""
        try:
            sig = Signalement.objects.get(pk=pk)
        except Signalement.DoesNotExist:
            return Response({'error': 'Signalement introuvable'}, status=404)

        if sig.statut != StatutSignalement.PENDING:
            return Response({'error': 'Ce signalement a déjà été traité.'}, status=400)

        message_admin = request.data.get('message', '').strip()
        if not message_admin:
            return Response({'error': 'Un message explicatif est requis pour refuser un signalement.'}, status=400)

        sig.statut          = StatutSignalement.REJECTED
        sig.traite_par      = request.user
        sig.message_admin   = message_admin
        sig.date_traitement = timezone.now()
        sig.save()

        # Notification avec message de l'admin
        Notification.objects.create(
            utilisateur=sig.signaleur,
            contenu=f"Votre signalement a été refusé. Message administrateur : {message_admin}",
            type_notification=TypeNotification.SIGNALEMENT_REFUSE,
            lien="",
        )
        log_admin_action(request.user, sig, CHANGE, "Signalement refusé.")

        return Response(SignalementSerializer(sig).data)


class AdminStatsView(generics.GenericAPIView):
    permission_classes = [IsAdminProfile]

    def get(self, request):
        users = User.objects.filter(
            is_staff=False,
            profile__est_administrateur=False,
        ).order_by("-date_joined")
        livres = Livre.objects.order_by("-date_creation")
        signalements = Signalement.objects.order_by("-date_signalement")
        stats = {
            'nb_utilisateurs' : users.count(),
            'nb_neuf'          : Livre.objects.filter(etat=EtatLivre.NEUF).count(),
            'nb_bon'           : Livre.objects.filter(etat=EtatLivre.BON).count(),
            'nb_usage'         : Livre.objects.filter(etat=EtatLivre.USAGE).count(),
            'nb_livres'       : Livre.objects.count(),
            'nb_disponibles'  : Livre.objects.filter(statut=StatutAnnonce.DISPONIBLE).count(),
            'nb_vendus'       : Livre.objects.filter(statut=StatutAnnonce.VENDU).count(),
            'nb_commandes'    : Commande.objects.count(),
            'nb_signalements' : Signalement.objects.filter(statut=StatutSignalement.PENDING).count(),
            'nb_notifications': Notification.objects.count(),
            "derniers_users": UserSerializer(users[:10], many=True).data,
            'derniers_livres' : LivreSerializer(
                livres[:10],
                many=True, context={'request': request}
            ).data,
            'derniers_signalements': SignalementSerializer(
                signalements[:20], many=True
            ).data,
            "users_page": paginated_data(
                users, request, "users",
                lambda items: UserSerializer(items, many=True).data,
            ),
            "books_page": paginated_data(
                livres, request, "books",
                lambda items: LivreSerializer(
                    items, many=True, context={"request": request}
                ).data,
            ),
            "reports_page": paginated_data(
                signalements, request, "reports",
                lambda items: SignalementSerializer(items, many=True).data,
            ),
            "notification_recipients": UserSerializer(users, many=True).data,
            "notification_history": [
                {
                    "id": item.id,
                    "recipient": item.utilisateur.username,
                    "content": item.contenu,
                    "created_at": item.date_creation,
                }
                for item in Notification.objects.filter(
                    type_notification=TypeNotification.ADMIN_MESSAGE
                ).select_related("utilisateur")[:30]
            ],
            "activity_log": [
                {
                    "id": entry.id,
                    "admin": entry.user.username,
                    "object": entry.object_repr,
                    "message": entry.change_message,
                    "action": entry.action_flag,
                    "created_at": entry.action_time,
                }
                for entry in LogEntry.objects.select_related("user")[:30]
            ],
        }
        return Response(stats)


class AdminNotifView(generics.CreateAPIView):
    permission_classes = [IsAdminProfile]

    def post(self, request):
        user_id = request.data.get('user_id')
        contenu = str(request.data.get("contenu", "")).strip()
        if not contenu:
            return Response({'error': 'contenu requis'}, status=400)

        if user_id == 'all':
            users = User.objects.filter(is_staff=False, profile__est_administrateur=False)
        else:
            try:
                users = [User.objects.get(
                    pk=user_id,
                    is_staff=False,
                    profile__est_administrateur=False,
                )]
            except (User.DoesNotExist, ValueError, TypeError):
                return Response({'error': 'Utilisateur introuvable'}, status=404)

        notifications = [
            Notification(
                utilisateur=u,
                contenu=contenu,
                type_notification=TypeNotification.ADMIN_MESSAGE,
            )
            for u in users
        ]
        Notification.objects.bulk_create(notifications)
        log_admin_action(
            request.user, request.user, ADDITION,
            f"Notification admin envoyée à {len(notifications)} utilisateur(s).",
        )
        return Response({"detail": f"Notification envoyée à {len(notifications)} utilisateur(s)."})


class AdminBanView(generics.UpdateAPIView):
    permission_classes = [IsAdminProfile]

    def patch(self, request, user_id):
        try:
            profile = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({'error': 'Profil introuvable'}, status=404)
        if profile.user.is_staff or profile.est_administrateur:
            return Response({'error': 'Un compte administrateur ne peut pas être banni.'}, status=400)
        raw_banni = request.data.get('est_banni', True)
        banni = raw_banni if isinstance(raw_banni, bool) else str(raw_banni).lower() in ('1', 'true', 'yes')
        profile.est_banni = banni
        profile.save()
        log_admin_action(
            request.user, profile, CHANGE,
            "Utilisateur banni." if banni else "Utilisateur débanni.",
        )
        return Response({'detail': f"Utilisateur {'banni' if banni else 'débanni'}."})


class AdminLivreDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminProfile]
    queryset = Livre.objects.all()

    def destroy(self, request, *args, **kwargs):
        livre = self.get_object()
        try:
            response = super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"error": "Ce livre est lié à une commande et ne peut pas être supprimé."}, status=status.HTTP_409_CONFLICT)
        log_admin_action(request.user, livre, DELETION, "Livre supprimé.")
        return response


class AdminSignalementView(generics.UpdateAPIView):
    permission_classes = [IsAdminProfile]

    def patch(self, request, pk):
        try:
            sig = Signalement.objects.get(pk=pk)
        except Signalement.DoesNotExist:
            return Response({'error': 'Signalement introuvable'}, status=404)
        sig.statut     = request.data.get('statut', StatutSignalement.ACCEPTED)
        sig.traite_par = request.user
        sig.save()
        return Response({'detail': 'Signalement mis à jour.'})


class AdminUserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminProfile]
    queryset = User.objects.filter(is_staff=False, profile__est_administrateur=False)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            response = super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"error": "Cet utilisateur possède des données liées à des commandes et ne peut pas être supprimé."}, status=status.HTTP_409_CONFLICT)
        log_admin_action(request.user, user, DELETION, "Utilisateur supprimé.")
        return response

