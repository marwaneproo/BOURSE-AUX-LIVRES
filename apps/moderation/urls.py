from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminBanView, AdminLivreDeleteView, AdminNotifView, AdminSignalementView, AdminStatsView, AdminUserDeleteView, SignalementViewSet

router = DefaultRouter()
router.register('signalements', SignalementViewSet, basename='signalement')

urlpatterns = [
    path('', include(router.urls)),
    path('admin-panel/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin-panel/notifier/', AdminNotifView.as_view(), name='admin-notify'),
    path('admin-panel/ban/<int:user_id>/', AdminBanView.as_view(), name='admin-ban'),
    path('admin-panel/livre/<int:pk>/supprimer/', AdminLivreDeleteView.as_view(), name='admin-book-delete'),
    path('admin-panel/signalement/<int:pk>/', AdminSignalementView.as_view(), name='admin-report'),
    path('admin-panel/user/<int:pk>/supprimer/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
]
