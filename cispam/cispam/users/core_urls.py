from django.urls import path

from cispam.users.views import annees_activate_view
from cispam.users.views import annees_create_view
from cispam.users.views import annees_list_view
from cispam.users.views import classes_create_view
from cispam.users.views import classes_list_view
from cispam.users.views import dashboard_view
from cispam.users.views import etudiants_par_classe_print_view
from cispam.users.views import paiements_par_classe_print_view
from cispam.users.views import export_paiements_excel_view
from cispam.users.views import backup_database_view
from cispam.users.views import frais_create_view
from cispam.users.views import frais_list_view
from cispam.users.views import inscriptions_create_view
from cispam.users.views import inscriptions_list_view
from cispam.users.views import paiements_create_view
from cispam.users.views import recherche_view
from cispam.users.views import recu_detail_view
from cispam.users.views import recu_list_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("dashboard/", dashboard_view, name="dashboard_page"),
    path("annees/", annees_list_view, name="annees_list"),
    path("annees/<uuid:pk>/activer/", annees_activate_view, name="annees_activate"),
    path("annees/creer/", annees_create_view, name="annees_create"),
    path("classes/", classes_list_view, name="classes_list"),
    path("classes/creer/", classes_create_view, name="classes_create"),
    path("classes/etudiants/imprimer/", etudiants_par_classe_print_view, name="classes_etudiants_print"),
    path("classes/paiements/imprimer/", paiements_par_classe_print_view, name="classes_paiements_print"),
    path("classes/paiements/excel/", export_paiements_excel_view, name="classes_paiements_excel"),
    path("frais/", frais_list_view, name="frais_list"),
    path("frais/creer/", frais_create_view, name="frais_create"),
    path("inscriptions/", inscriptions_list_view, name="inscriptions_list"),
    path("inscriptions/nouvelle/", inscriptions_create_view, name="inscriptions_create"),
    path("paiements/creer/", paiements_create_view, name="paiements_create"),
    path("recus/", recu_list_view, name="recu_list"),
    path("recus/<uuid:pk>/", recu_detail_view, name="recu_detail"),
    path("recherche/", recherche_view, name="recherche"),
    path("sauvegarde/", backup_database_view, name="sauvegarde_db"),
]
