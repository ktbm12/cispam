from django.conf import settings
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # path("api/v1/", include("licenses.api.urls")),  # Phase 2
    # path("", include("dashboard.urls")),             # Phase 3
]
