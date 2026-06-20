from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.books.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.messaging.urls')),
    path('api/', include('apps.notifications.urls')),
    path('api/', include('apps.moderation.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('apps.web.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
