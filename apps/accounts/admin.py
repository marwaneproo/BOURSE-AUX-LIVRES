from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'est_actif', 'est_banni', 'est_administrateur', 'date_inscription')
    list_filter = ('est_actif', 'est_banni', 'est_administrateur')
    search_fields = ('user__username', 'user__email')
