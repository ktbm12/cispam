from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from cispam.users.views import annees_activate_view
from cispam.users.views import annees_create_view
from cispam.users.views import annees_list_view
from cispam.users.views import classes_create_view
from cispam.users.views import classes_list_view
from cispam.users.views import dashboard_view
from cispam.users.views import frais_create_view
from cispam.users.views import frais_list_view
from cispam.users.views import inscriptions_create_view
from cispam.users.views import inscriptions_list_view
from cispam.users.views import paiements_create_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("dashboard/", dashboard_view, name="dashboard_page"),
    path("annees/", annees_list_view, name="annees_list"),
    path("annees/<uuid:pk>/activer/", annees_activate_view, name="annees_activate"),
    path("annees/creer/", annees_create_view, name="annees_create"),
    path("classes/", classes_list_view, name="classes_list"),
    path("classes/creer/", classes_create_view, name="classes_create"),
    path("frais/", frais_list_view, name="frais_list"),
    path("frais/creer/", frais_create_view, name="frais_create"),
    path("inscriptions/", inscriptions_list_view, name="inscriptions_list"),
    path("inscriptions/nouvelle/", inscriptions_create_view, name="inscriptions_create"),
    path("paiements/creer/", paiements_create_view, name="paiements_create"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("cispam.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
