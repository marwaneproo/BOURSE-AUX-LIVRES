from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommandeViewSet, LivraisonViewSet

router = DefaultRouter()
router.register('commandes', CommandeViewSet, basename='commande')
router.register('livraisons', LivraisonViewSet, basename='livraison')

urlpatterns = [path('', include(router.urls))]
