"""
Configuration de l'admin Django pour tous les modèles de gestion scolaire.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm, UserAdminCreationForm
from .models import (
    AnneeScolaire,
    Niveau,
    Classe,
    Eleve,
    Parent,
    Inscription,
    FraisScolarite,
    Paiement,
    Recu,
    Utilisateur,
)


# ==============================================================================
# MIXIN ADMIN
# ==============================================================================

class SoftDeleteAdminMixin:
    """
    Mixin pour l'admin qui gère le soft delete :
    - Exclut les objets supprimés de la liste par défaut
    - Ajoute une action pour restaurer
    - Ajoute une action pour supprimer définitivement
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Par défaut, on exclut les supprimés
        return qs.filter(is_deleted=False)

    @admin.action(description=_("Restaurer les objets sélectionnés"))
    def restaurer(self, request, queryset):
        for obj in queryset:
            obj.restore()
        self.message_user(request, _("{} objet(s) restauré(s).").format(queryset.count()))

    @admin.action(description=_("Supprimer définitivement"))
    def supprimer_definitivement(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, _("{} objet(s) supprimé(s) définitivement.").format(count))

    actions = ['restaurer', 'supprimer_definitivement']


# ==============================================================================
# ADMIN — ANNÉE SCOLAIRE
# ==============================================================================

@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['libelle', 'date_debut', 'date_fin', 'est_active', 'created']
    list_filter = ['est_active', 'date_debut']
    search_fields = ['libelle']
    ordering = ['-date_debut']
    readonly_fields = ['slug', 'created', 'modified']
    fieldsets = (
        (None, {
            'fields': ('libelle', 'slug', 'date_debut', 'date_fin', 'est_active')
        }),
        (_("Métadonnées"), {
            'fields': ('is_active', 'is_deleted', 'metadata', 'created', 'modified'),
            'classes': ('collapse',),
        }),
    )


# ==============================================================================
# ADMIN — NIVEAU
# ==============================================================================

@admin.register(Niveau)
class NiveauAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['nom', 'ordre', 'created']
    list_filter = ['nom']
    search_fields = ['nom', 'description']
    ordering = ['ordre']
    readonly_fields = ['slug', 'created', 'modified']


# ==============================================================================
# ADMIN — CLASSE
# ==============================================================================

@admin.register(Classe)
class ClasseAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['nom', 'niveau', 'capacite_max', 'effectif_actuel', 'places_restantes', 'is_active']
    list_filter = ['niveau', 'is_active']
    search_fields = ['nom', 'description']
    ordering = ['niveau__ordre', 'nom']
    readonly_fields = ['slug', 'effectif_actuel', 'places_restantes', 'created', 'modified']
    fieldsets = (
        (None, {
            'fields': ('nom', 'slug', 'niveau', 'capacite_max', 'description')
        }),
        (_("Statistiques"), {
            'fields': ('effectif_actuel', 'places_restantes'),
        }),
        (_("Métadonnées"), {
            'fields': ('is_active', 'is_deleted', 'metadata', 'created', 'modified'),
            'classes': ('collapse',),
        }),
    )


# ==============================================================================
# ADMIN — ÉLÈVE
# ==============================================================================

@admin.register(Eleve)
class EleveAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['matricule', 'nom_complet', 'sexe', 'age', 'classe_actuelle', 'statut_paiement', 'is_active']
    list_filter = ['sexe', 'is_active', 'date_naissance']
    search_fields = ['matricule', 'nom', 'prenom', 'lieu_naissance']
    ordering = ['nom', 'prenom']
    readonly_fields = ['matricule', 'slug', 'age', 'classe_actuelle', 'statut_paiement', 'created', 'modified']
    fieldsets = (
        (_("Identité"), {
            'fields': ('matricule', 'slug', 'nom', 'prenom', 'sexe', 'date_naissance', 'age', 'lieu_naissance', 'nationalite')
        }),
        (_("Contact & Photo"), {
            'fields': ('photo', 'adresse'),
        }),
        (_("Scolarité"), {
            'fields': ('classe_actuelle', 'statut_paiement', 'date_premiere_inscription'),
        }),
        (_("Métadonnées"), {
            'fields': ('is_active', 'is_deleted', 'metadata', 'created', 'modified'),
            'classes': ('collapse',),
        }),
    )


# ==============================================================================
# ADMIN — PARENT
# ==============================================================================

@admin.register(Parent)
class ParentAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['nom_complet', 'eleve', 'lien_parente', 'telephone', 'est_contact_principal', 'is_active']
    list_filter = ['lien_parente', 'est_contact_principal', 'is_active']
    search_fields = ['nom', 'prenom', 'telephone', 'telephone_secondaire', 'email']
    ordering = ['nom', 'prenom']
    readonly_fields = ['slug', 'created', 'modified']


# ==============================================================================
# ADMIN — INSCRIPTION
# ==============================================================================

@admin.register(Inscription)
class InscriptionAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['reference', 'eleve', 'classe', 'annee_scolaire', 'type_inscription', 'statut', 'frais_total', 'montant_paye', 'solde', 'statut_paiement']
    list_filter = ['statut', 'type_inscription', 'annee_scolaire', 'classe']
    search_fields = ['reference', 'eleve__nom', 'eleve__prenom', 'eleve__matricule']
    ordering = ['-date_inscription']
    readonly_fields = ['reference', 'slug', 'montant_paye', 'solde', 'statut_paiement', 'pourcentage_paye', 'created', 'modified']
    fieldsets = (
        (_("Inscription"), {
            'fields': ('reference', 'slug', 'eleve', 'classe', 'annee_scolaire', 'date_inscription')
        }),
        (_("Type & Statut"), {
            'fields': ('type_inscription', 'statut', 'remarques'),
        }),
        (_("Finances"), {
            'fields': ('frais_total', 'montant_paye', 'solde', 'statut_paiement', 'pourcentage_paye'),
        }),
        (_("Métadonnées"), {
            'fields': ('is_active', 'is_deleted', 'metadata', 'created', 'modified'),
            'classes': ('collapse',),
        }),
    )


# ==============================================================================
# ADMIN — FRAIS SCOLARITÉ
# ==============================================================================

@admin.register(FraisScolarite)
class FraisScolariteAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['classe', 'annee_scolaire', 'montant_total', 'nombre_tranches', 'is_active']
    list_filter = ['annee_scolaire', 'classe__niveau']
    search_fields = ['libelle', 'classe__nom']
    ordering = ['annee_scolaire', 'classe']
    readonly_fields = ['slug', 'created', 'modified']


# ==============================================================================
# ADMIN — PAIEMENT
# ==============================================================================

@admin.register(Paiement)
class PaiementAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['reference', 'inscription', 'montant', 'mode_paiement', 'tranche', 'date_paiement', 'operateur']
    list_filter = ['mode_paiement', 'tranche', 'date_paiement']
    search_fields = ['reference', 'inscription__eleve__nom', 'inscription__eleve__prenom', 'reference_transaction']
    ordering = ['-date_paiement']
    readonly_fields = ['reference', 'slug', 'solde_apres_paiement', 'created', 'modified']
    date_hierarchy = 'date_paiement'


# ==============================================================================
# ADMIN — REÇU
# ==============================================================================

@admin.register(Recu)
class RecuAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ['numero_recu', 'eleve', 'classe', 'paiement', 'montant_lettres', 'statut', 'date_emission']
    list_filter = ['statut', 'date_emission']
    search_fields = ['numero_recu', 'paiement__inscription__eleve__nom', 'paiement__inscription__eleve__prenom']
    ordering = ['-date_emission']
    readonly_fields = ['numero_recu', 'slug', 'eleve', 'classe', 'annee_scolaire', 'date_emission', 'created', 'modified']
    date_hierarchy = 'date_emission'


# ==============================================================================
# ADMIN — UTILISATEUR
# ==============================================================================

@admin.register(Utilisateur)
class UtilisateurAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm
    form = UserAdminChangeForm
    list_display = ["username", "email", "name", "role", "is_staff", "is_superuser"]
    search_fields = ["username", "email", "name"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informations personnelles"), {"fields": ("name", "email", "role", "telephone", "photo")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


_original_admin_login = admin.site.login


def _custom_admin_login(request, extra_context=None):
    if getattr(settings, "DJANGO_ADMIN_FORCE_ALLAUTH", False):
        return redirect(f"{reverse(settings.LOGIN_URL)}?next={request.path}")
    return _original_admin_login(request, extra_context)


admin.site.login = _custom_admin_login


