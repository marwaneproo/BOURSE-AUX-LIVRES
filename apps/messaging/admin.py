from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'destinataire', 'date_envoi', 'est_lu')
    list_filter = ('est_lu',)
    search_fields = ('contenu', 'expediteur__username', 'destinataire__username')
