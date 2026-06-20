from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MessagerieViewSet

router = DefaultRouter()
router.register('messages', MessagerieViewSet, basename='message')

urlpatterns = [path('', include(router.urls))]
