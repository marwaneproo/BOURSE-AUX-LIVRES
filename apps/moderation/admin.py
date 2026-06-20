from django.contrib import admin

from .models import Signalement


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('id', 'signaleur', 'livre_signale', 'statut', 'date_signalement')
    list_filter = ('statut',)
