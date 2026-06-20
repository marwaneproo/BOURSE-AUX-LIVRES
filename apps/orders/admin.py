from django.contrib import admin

from .models import Commande, Livraison


class LivraisonInline(admin.StackedInline):
    model = Livraison
    can_delete = False


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'acheteur', 'livre', 'date_commande', 'statut')
    list_filter = ('statut', 'date_commande')
    search_fields = ('nom_acheteur', 'prenom_acheteur', 'telephone', 'acheteur__username')
    inlines = [LivraisonInline]
