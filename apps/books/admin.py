from django.contrib import admin

from .models import Evaluation, Favori, ImageLivre, Livre


class ImageLivreInline(admin.TabularInline):
    model = ImageLivre
    extra = 1


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'vendeur', 'prix', 'matiere', 'niveau', 'statut', 'etat', 'date_creation')
    list_filter = ('statut', 'etat', 'matiere', 'niveau')
    search_fields = ('titre', 'auteur', 'description', 'vendeur__username')
    inlines = [ImageLivreInline]
    actions = ['marquer_archivee']

    @admin.action(description='Archiver les livres sélectionnés')
    def marquer_archivee(self, request, queryset):
        queryset.update(statut='ARCHIVEE')


admin.site.register(Favori)
admin.site.register(Evaluation)
admin.site.register(ImageLivre)
