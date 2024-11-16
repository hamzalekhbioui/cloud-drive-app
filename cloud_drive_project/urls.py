from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('login/', include('django.contrib.auth.urls')),  # Built-in authentication URLs
    path('register/', include('cloud_drive_app.urls')),  # Custom registration URL
    path('', RedirectView.as_view(url='/login/')),  # Redirect root URL to login page
    path('admin/', admin.site.urls),
    path('', include('cloud_drive_app.urls')),  # Include app URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)