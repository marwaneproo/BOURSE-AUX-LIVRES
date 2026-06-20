from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EvaluationViewSet, FavoriViewSet, LivreViewSet

router = DefaultRouter()
router.register('livres', LivreViewSet, basename='livre')
router.register('favoris', FavoriViewSet, basename='favori')
router.register('evaluations', EvaluationViewSet, basename='evaluation')

urlpatterns = [path('', include(router.urls))]
