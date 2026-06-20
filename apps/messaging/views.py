from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.serializers import UserSerializer
from .models import Message
from .serializers import MessageSerializer

class MessagerieViewSet(viewsets.ModelViewSet):
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            Q(expediteur=self.request.user) | Q(destinataire=self.request.user)
        ).order_by('date_envoi')

    @action(detail=False, methods=['get'])
    def discussion(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id requis"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            other_user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError, DjangoValidationError):
            return Response({"error": "Utilisateur introuvable"}, status=status.HTTP_404_NOT_FOUND)
        if other_user == request.user:
            return Response({"error": "Conversation invalide"}, status=status.HTTP_400_BAD_REQUEST)
        messages = Message.objects.filter(
            (Q(expediteur=request.user) & Q(destinataire_id=user_id)) |
            (Q(expediteur_id=user_id) & Q(destinataire=request.user))
        ).order_by('date_envoi')
        messages.filter(destinataire=request.user, est_lu=False).update(est_lu=True)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        user = request.user
        msgs = Message.objects.filter(
            Q(expediteur=user) | Q(destinataire=user)
        ).order_by('-date_envoi')
        seen = set()
        result = []
        for m in msgs:
            other = m.destinataire if m.expediteur == user else m.expediteur
            if other.id not in seen:
                seen.add(other.id)
                unread = Message.objects.filter(expediteur=other, destinataire=user, est_lu=False).count()
                result.append({
                    'user': UserSerializer(other).data,
                    'dernier_message': m.contenu,
                    'date': m.date_envoi,
                    'non_lus': unread
                })
        return Response(result)

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)


