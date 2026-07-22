"""
================================================================================
ECOLE GESTION — Modèles complets (Application unique : users)
================================================================================
Architecture :
  - OngBaseModel     : UUID PK, timestamps, soft-delete, metadata JSON
  - AutoSlugMixin    : génération auto de slug unique
  - OngManager       : exclut les objets soft-deleted par défaut
  - Enums centralisés : dans ce fichier
  - Tous les modèles métier dans une seule app Django : users
================================================================================
"""

import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


# ==============================================================================
# ENUMS
# ==============================================================================

class SexeEnum(models.TextChoices):
    """Sexe de l'élève."""
    MASCULIN = 'M', _('Masculin')
    FEMININ = 'F', _('Féminin')


class LienParenteEnum(models.TextChoices):
    """Lien de parenté avec l'élève."""
    PERE = 'pere', _('Père')
    MERE = 'mere', _('Mère')
    TUTEUR = 'tuteur', _('Tuteur')
    ONCLE = 'oncle', _('Oncle')
    TANTE = 'tante', _('Tante')
    GRAND_PARENT = 'grand_parent', _('Grand-parent')
    AUTRE = 'autre', _('Autre')


class TypeInscriptionEnum(models.TextChoices):
    """Type d'inscription."""
    NOUVELLE = 'nouvelle', _('Nouvelle inscription')
    REINSCRIPTION = 'reinscription', _('Réinscription')
    TRANSFERT = 'transfert', _('Transfert')


class StatutInscriptionEnum(models.TextChoices):
    """Statut d'une inscription."""
    EN_COURS = 'en_cours', _('En cours')
    TERMINEE = 'terminee', _('Terminée')
    ABANDONNEE = 'abandonnee', _('Abandonnée')
    SUSPENDUE = 'suspendue', _('Suspendue')


class ModePaiementEnum(models.TextChoices):
    """Mode de paiement accepté."""
    ESPECES = 'especes', _('Espèces')
    CHEQUE = 'cheque', _('Chèque')
    VIREMENT = 'virement', _('Virement bancaire')
    MOBILE_MONEY = 'mobile_money', _('Mobile Money')
    CARTE_BANCAIRE = 'carte_bancaire', _('Carte bancaire')


class TrancheEnum(models.TextChoices):
    """Tranche de paiement des frais de scolarité."""
    TRANCHE_1 = 'tranche_1', _('Tranche 1 (Inscription)')
    TRANCHE_2 = 'tranche_2', _('Tranche 2')
    TRANCHE_3 = 'tranche_3', _('Tranche 3')
    ACOMPTE = 'acompte', _('Acompte')
    SOLDE = 'solde', _('Solde final')


class StatutPaiementEnum(models.TextChoices):
    """Statut global du paiement d'un élève."""
    PAYE = 'paye', _('Payé')
    PARTIEL = 'partiel', _('Partiel')
    IMPAYE = 'impaye', _('Impayé')


class RoleUtilisateurEnum(models.TextChoices):
    """Rôles des utilisateurs du système."""
    DIRECTEUR = 'directeur', _('Directeur / Directrice')
    COMPTABLE = 'comptable', _('Comptable')
    SECRETAIRE = 'secretaire', _('Secrétaire')
    CAISSIER = 'caissier', _('Caissier')
    ENSEIGNANT = 'enseignant', _('Enseignant')
    SURVEILLANT = 'surveillant', _('Surveillant')


class NiveauScolaireEnum(models.TextChoices):
    """Niveaux scolaires disponibles."""
    MATERNELLE = 'maternelle', _('Maternelle')
    PRIMAIRE = 'primaire', _('Primaire')


class StatutRecuEnum(models.TextChoices):
    """Statut d'un reçu."""
    GENERE = 'genere', _('Généré')
    IMPRIME = 'imprime', _('Imprimé')
    ENVOYE = 'envoye', _('Envoyé au parent')
    ANNULE = 'annule', _('Annulé')


# ==============================================================================
# MANAGER
# ==============================================================================

class OngManager(models.Manager):
    """
    Manager par défaut qui exclut les objets supprimés logiquement.
    Utilisez `all_objects` pour accéder à tous les objets.
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def active(self):
        """Retourne uniquement les objets actifs."""
        return self.get_queryset().filter(is_active=True)

    def inactive(self):
        """Retourne les objets inactifs mais non supprimés."""
        return self.get_queryset().filter(is_active=False)


# ==============================================================================
# UTILITAIRE SLUG
# ==============================================================================

def _generate_unique_slug(instance, source_value):
    """Génère un slug unique, en tenant compte des objets supprimés logiquement."""
    base_slug = slugify(source_value) if source_value else str(instance.id)[:8]
    if not base_slug:
        base_slug = str(instance.id)[:8]

    model = instance.__class__
    slug = base_slug
    counter = 1

    manager = getattr(model, 'all_objects', model.objects)

    qs = manager.filter(slug=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    while qs.exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        qs = manager.filter(slug=slug)
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)

    return slug


class AutoSlugMixin:
    """
    Mixin qui génère automatiquement un slug unique lors de la sauvegarde.

    Utilisation :
        class MonModele(AutoSlugMixin, OngBaseModel):
            slug_source_field = 'nom'
            nom = models.CharField(max_length=255)
            slug = models.SlugField(unique=True, max_length=255)
    """

    slug_source_field = 'name'

    def save(self, *args, **kwargs):
        if not self.slug:
            source_value = getattr(self, self.slug_source_field, None)
            self.slug = _generate_unique_slug(self, source_value)
        super().save(*args, **kwargs)


# ==============================================================================
# MODÈLE DE BASE
# ==============================================================================

class OngBaseModel(models.Model):
    """
    Modèle de base pour toute la plateforme :
    - UUID primary key
    - created / modified (auto_now_add / auto_now)
    - is_active
    - soft delete (is_deleted)
    - metadata JSON
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        help_text=_("Identifiant UUID unique."),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("Date de création."),
    )
    modified = models.DateTimeField(
        auto_now=True,
        help_text=_("Date de dernière modification."),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indique si l'objet est actif."),
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Suppression logique (soft delete)."),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Métadonnées additionnelles au format JSON."),
    )

    objects = OngManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created']

    def soft_delete(self, save=True):
        self.is_deleted = True
        if save:
            self.save(update_fields=["is_deleted", "modified"])

    def restore(self, save=True):
        self.is_deleted = False
        if save:
            self.save(update_fields=["is_deleted", "modified"])

    def __str__(self):
        return str(self.id)


# ==============================================================================
# MODÈLES MÉTIER — CONFIGURATION
# ==============================================================================

class AnneeScolaire(AutoSlugMixin, OngBaseModel):
    """
    Représente une année scolaire (ex: 2025-2026).
    Une seule année scolaire peut être active à la fois.
    """

    slug_source_field = 'libelle'

    libelle = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Libellé de l'année scolaire, ex: 2025-2026"),
    )
    date_debut = models.DateField(
        help_text=_("Date de début de l'année scolaire."),
    )
    date_fin = models.DateField(
        help_text=_("Date de fin de l'année scolaire."),
    )
    est_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Indique si c'est l'année scolaire en cours. Une seule active à la fois."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique de l'année scolaire."),
    )

    class Meta:
        verbose_name = _("Année scolaire")
        verbose_name_plural = _("Années scolaires")
        ordering = ['-date_debut']

    def __str__(self):
        return self.libelle

    def save(self, *args, **kwargs):
        if self.est_active:
            AnneeScolaire.objects.filter(est_active=True).exclude(pk=self.pk).update(
                est_active=False
            )
        super().save(*args, **kwargs)


class Niveau(AutoSlugMixin, OngBaseModel):
    """Niveau scolaire : Maternelle ou Primaire."""

    slug_source_field = 'nom'

    nom = models.CharField(
        max_length=50,
        choices=NiveauScolaireEnum.choices,
        unique=True,
        help_text=_("Nom du niveau scolaire."),
    )
    ordre = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Ordre d'affichage (1 = Maternelle, 2 = Primaire)."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description du niveau."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique du niveau."),
    )

    class Meta:
        verbose_name = _("Niveau")
        verbose_name_plural = _("Niveaux")
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.get_nom_display()


class Classe(AutoSlugMixin, OngBaseModel):
    """Classe d'une école (ex: Petite Section, CP, CM2)."""

    slug_source_field = 'nom'

    nom = models.CharField(
        max_length=50,
        help_text=_("Nom de la classe, ex: Petite Section, CP, CM2."),
    )
    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name='classes',
        help_text=_("Niveau scolaire de la classe."),
    )
    capacite_max = models.PositiveSmallIntegerField(
        default=30,
        help_text=_("Capacité maximale d'élèves dans cette classe."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description ou informations complémentaires."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique de la classe."),
    )

    class Meta:
        verbose_name = _("Classe")
        verbose_name_plural = _("Classes")
        ordering = ['niveau__ordre', 'nom']
        unique_together = ['nom', 'niveau']

    def __str__(self):
        return f"{self.nom} ({self.niveau})"

    @property
    def effectif_actuel(self):
        """Nombre d'élèves inscrits dans cette classe pour l'année active."""
        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
            return Inscription.objects.filter(
                classe=self,
                annee_scolaire=annee_active,
                statut=StatutInscriptionEnum.EN_COURS,
            ).count()
        except AnneeScolaire.DoesNotExist:
            return 0

    @property
    def places_restantes(self):
        """Nombre de places restantes."""
        return self.capacite_max - self.effectif_actuel


# ==============================================================================
# MODÈLES MÉTIER — ÉLÈVES & PARENTS
# ==============================================================================

def eleve_photo_path(instance, filename):
    """Chemin de stockage des photos d'élèves."""
    ext = os.path.splitext(filename)[1]
    return f"eleves/photos/{instance.id}{ext}"


class Eleve(AutoSlugMixin, OngBaseModel):
    """
    Dossier complet d'un élève.
    Chaque élève a un matricule unique et un slug unique.
    """

    slug_source_field = 'nom_complet'

    matricule = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_("Matricule unique de l'élève, ex: ECO-2025-00042."),
    )
    nom = models.CharField(
        max_length=100,
        help_text=_("Nom de famille de l'élève."),
    )
    prenom = models.CharField(
        max_length=100,
        help_text=_("Prénom(s) de l'élève."),
    )
    date_naissance = models.DateField(
        help_text=_("Date de naissance de l'élève."),
    )
    sexe = models.CharField(
        max_length=1,
        choices=SexeEnum.choices,
        help_text=_("Sexe de l'élève."),
    )
    lieu_naissance = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Lieu de naissance."),
    )
    nationalite = models.CharField(
        max_length=50,
        default="Ivoirienne",
        blank=True,
        help_text=_("Nationalité de l'élève."),
    )
    photo = models.ImageField(
        upload_to=eleve_photo_path,
        blank=True,
        null=True,
        help_text=_("Photo d'identité de l'élève."),
    )
    adresse = models.TextField(
        blank=True,
        help_text=_("Adresse de résidence de l'élève."),
    )
    date_premiere_inscription = models.DateField(
        auto_now_add=True,
        help_text=_("Date de la première inscription dans l'établissement."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique de l'élève."),
    )

    class Meta:
        verbose_name = _("Élève")
        verbose_name_plural = _("Élèves")
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )

    @property
    def inscription_actuelle(self):
        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
            return Inscription.objects.get(
                eleve=self,
                annee_scolaire=annee_active,
                is_deleted=False,
            )
        except (AnneeScolaire.DoesNotExist, Inscription.DoesNotExist):
            return None

    @property
    def classe_actuelle(self):
        inscription = self.inscription_actuelle
        return inscription.classe if inscription else None

    @property
    def statut_paiement(self):
        inscription = self.inscription_actuelle
        if not inscription:
            return None
        return inscription.statut_paiement


class Parent(AutoSlugMixin, OngBaseModel):
    """
    Parent ou tuteur d'un élève.
    Un élève peut avoir plusieurs parents/tuteurs.
    """

    slug_source_field = 'nom_complet'

    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.CASCADE,
        related_name='parents',
        help_text=_("Élève associé."),
    )
    nom = models.CharField(
        max_length=100,
        help_text=_("Nom du parent/tuteur."),
    )
    prenom = models.CharField(
        max_length=100,
        help_text=_("Prénom(s) du parent/tuteur."),
    )
    telephone = models.CharField(
        max_length=20,
        help_text=_("Numéro de téléphone principal (obligatoire)."),
    )
    telephone_secondaire = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Numéro de téléphone secondaire."),
    )
    email = models.EmailField(
        blank=True,
        help_text=_("Adresse email du parent/tuteur."),
    )
    adresse = models.TextField(
        blank=True,
        help_text=_("Adresse de résidence."),
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Profession du parent/tuteur."),
    )
    lien_parente = models.CharField(
        max_length=20,
        choices=LienParenteEnum.choices,
        help_text=_("Lien de parenté avec l'élève."),
    )
    est_contact_principal = models.BooleanField(
        default=False,
        help_text=_("Indique si c'est le contact principal pour cet élève."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique du parent."),
    )

    class Meta:
        verbose_name = _("Parent / Tuteur")
        verbose_name_plural = _("Parents / Tuteurs")
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_lien_parente_display()})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def save(self, *args, **kwargs):
        # Si ce parent devient contact principal, désactiver les autres
        if self.est_contact_principal:
            Parent.objects.filter(eleve=self.eleve, est_contact_principal=True).exclude(
                pk=self.pk
            ).update(est_contact_principal=False)
        super().save(*args, **kwargs)


# ==============================================================================
# MODÈLES MÉTIER — INSCRIPTION
# ==============================================================================

class Inscription(AutoSlugMixin, OngBaseModel):
    """
    Inscription d'un élève dans une classe pour une année scolaire donnée.
    C'est le pivot central : Eleve × Classe × AnneeScolaire.
    """

    slug_source_field = 'reference'

    eleve = models.ForeignKey(
        Eleve,
        on_delete=models.PROTECT,
        related_name='inscriptions',
        help_text=_("Élève inscrit."),
    )
    classe = models.ForeignKey(
        Classe,
        on_delete=models.PROTECT,
        related_name='inscriptions',
        help_text=_("Classe d'inscription."),
    )
    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.PROTECT,
        related_name='inscriptions',
        help_text=_("Année scolaire de l'inscription."),
    )
    date_inscription = models.DateField(
        auto_now_add=True,
        help_text=_("Date de l'inscription."),
    )
    type_inscription = models.CharField(
        max_length=20,
        choices=TypeInscriptionEnum.choices,
        default=TypeInscriptionEnum.NOUVELLE,
        help_text=_("Type d'inscription."),
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutInscriptionEnum.choices,
        default=StatutInscriptionEnum.EN_COURS,
        help_text=_("Statut actuel de l'inscription."),
    )
    frais_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Montant total des frais de scolarité fixé à l'inscription."),
    )
    remarques = models.TextField(
        blank=True,
        help_text=_("Remarques ou notes sur l'inscription."),
    )
    reference = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        blank=True,
        help_text=_("Référence unique de l'inscription, ex: INS-2025-00001."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique de l'inscription."),
    )

    class Meta:
        verbose_name = _("Inscription")
        verbose_name_plural = _("Inscriptions")
        ordering = ['-date_inscription']
        unique_together = ['eleve', 'annee_scolaire']

    def __str__(self):
        return f"{self.eleve} — {self.classe} ({self.annee_scolaire})"

    def save(self, *args, **kwargs):
        # Génération auto de la référence si vide
        if not self.reference:
            annee = self.annee_scolaire.libelle.split('-')[0] if self.annee_scolaire else '0000'
            count = Inscription.objects.filter(
                annee_scolaire=self.annee_scolaire
            ).count() + 1
            self.reference = f"INS-{annee}-{count:05d}"
        super().save(*args, **kwargs)

    @property
    def montant_paye(self):
        """Montant total payé pour cette inscription."""
        total = Paiement.objects.filter(
            inscription=self,
            is_deleted=False,
        ).aggregate(total=models.Sum('montant'))['total']
        return total or 0

    @property
    def solde(self):
        """Solde restant à payer."""
        return self.frais_total - self.montant_paye

    @property
    def statut_paiement(self):
        """Statut global du paiement."""
        if self.montant_paye >= self.frais_total:
            return StatutPaiementEnum.PAYE
        elif self.montant_paye > 0:
            return StatutPaiementEnum.PARTIEL
        return StatutPaiementEnum.IMPAYE

    @property
    def pourcentage_paye(self):
        """Pourcentage des frais payés."""
        if self.frais_total > 0:
            return round((self.montant_paye / self.frais_total) * 100, 1)
        return 0


# ==============================================================================
# MODÈLES MÉTIER — FRAIS DE SCOLARITÉ
# ==============================================================================

class FraisScolarite(AutoSlugMixin, OngBaseModel):
    """
    Template des frais de scolarité par classe et par année scolaire.
    Définit le montant total et le découpage en tranches.
    """

    slug_source_field = 'libelle'

    classe = models.ForeignKey(
        Classe,
        on_delete=models.PROTECT,
        related_name='frais_scolarite',
        help_text=_("Classe concernée."),
    )
    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.PROTECT,
        related_name='frais_scolarite',
        help_text=_("Année scolaire concernée."),
    )
    libelle = models.CharField(
        max_length=100,
        help_text=_("Libellé des frais, ex: 'Frais scolarité 2025-2026'."),
    )
    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Montant total des frais de scolarité."),
    )
    nombre_tranches = models.PositiveSmallIntegerField(
        default=3,
        help_text=_("Nombre de tranches de paiement (1 à 3)."),
    )
    montant_tranche_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Montant de la tranche 1 (inscription)."),
    )
    date_echeance_1 = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date d'échéance de la tranche 1."),
    )
    montant_tranche_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True,
        help_text=_("Montant de la tranche 2."),
    )
    date_echeance_2 = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date d'échéance de la tranche 2."),
    )
    montant_tranche_3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        blank=True,
        help_text=_("Montant de la tranche 3."),
    )
    date_echeance_3 = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date d'échéance de la tranche 3."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique."),
    )

    class Meta:
        verbose_name = _("Frais de scolarité")
        verbose_name_plural = _("Frais de scolarité")
        ordering = ['annee_scolaire', 'classe']
        unique_together = ['classe', 'annee_scolaire']

    def __str__(self):
        return f"{self.classe} — {self.annee_scolaire} ({self.montant_total} FCFA)"

    def clean(self):
        from django.core.exceptions import ValidationError
        total_tranches = self.montant_tranche_1 + self.montant_tranche_2 + self.montant_tranche_3
        if total_tranches != self.montant_total:
            raise ValidationError(
                _("La somme des tranches ({}) doit être égale au montant total ({}).").format(
                    total_tranches, self.montant_total
                )
            )


# ==============================================================================
# MODÈLES MÉTIER — PAIEMENT
# ==============================================================================

class Paiement(AutoSlugMixin, OngBaseModel):
    """
    Paiement effectué par un parent pour une inscription donnée.
    Chaque paiement génère automatiquement un reçu.
    """

    slug_source_field = 'reference'

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.PROTECT,
        related_name='paiements',
        help_text=_("Inscription concernée par le paiement."),
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Montant versé."),
    )
    date_paiement = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date et heure du paiement."),
    )
    mode_paiement = models.CharField(
        max_length=20,
        choices=ModePaiementEnum.choices,
        default=ModePaiementEnum.ESPECES,
        help_text=_("Mode de paiement utilisé."),
    )
    reference_transaction = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Référence externe : n° chèque, référence virement, ID mobile money..."),
    )
    tranche = models.CharField(
        max_length=20,
        choices=TrancheEnum.choices,
        default=TrancheEnum.TRANCHE_1,
        help_text=_("Tranche concernée par ce paiement."),
    )
    operateur = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Nom de l'utilisateur qui a encaissé le paiement."),
    )
    remarques = models.TextField(
        blank=True,
        help_text=_("Remarques sur le paiement."),
    )
    reference = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        blank=True,
        help_text=_("Référence unique du paiement, ex: PAI-2025-00001."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique du paiement."),
    )

    class Meta:
        verbose_name = _("Paiement")
        verbose_name_plural = _("Paiements")
        ordering = ['-date_paiement']

    def __str__(self):
        return f"{self.reference} — {self.montant} FCFA ({self.inscription.eleve})"

    def save(self, *args, **kwargs):
        # Génération auto de la référence si vide
        if not self.reference:
            annee = self.inscription.annee_scolaire.libelle.split('-')[0] if self.inscription and self.inscription.annee_scolaire else '0000'
            count = Paiement.objects.filter(
                inscription__annee_scolaire=self.inscription.annee_scolaire if self.inscription else None
            ).count() + 1
            self.reference = f"PAI-{annee}-{count:05d}"
        super().save(*args, **kwargs)

    @property
    def solde_apres_paiement(self):
        """Solde restant après ce paiement."""
        return self.inscription.solde if self.inscription else 0


# ==============================================================================
# MODÈLES MÉTIER — REÇU
# ==============================================================================

class Recu(AutoSlugMixin, OngBaseModel):
    """
    Reçu généré automatiquement à chaque paiement.
    Numéroté séquentiellement par année scolaire.
    """

    slug_source_field = 'numero_recu'

    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.PROTECT,
        related_name='recu',
        help_text=_("Paiement associé à ce reçu."),
    )
    numero_recu = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        blank=True,
        help_text=_("Numéro unique du reçu, ex: REC-2025-00123."),
    )
    date_emission = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date et heure d'émission du reçu."),
    )
    montant_lettres = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Montant écrit en toutes lettres."),
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutRecuEnum.choices,
        default=StatutRecuEnum.GENERE,
        help_text=_("Statut actuel du reçu."),
    )
    pdf_path = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Chemin du fichier PDF généré."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Slug unique du reçu."),
    )

    class Meta:
        verbose_name = _("Reçu")
        verbose_name_plural = _("Reçus")
        ordering = ['-date_emission']

    def __str__(self):
        return f"{self.numero_recu} — {self.paiement.montant} FCFA"

    def save(self, *args, **kwargs):
        # Génération auto du numéro de reçu si vide
        if not self.numero_recu:
            annee = self.paiement.inscription.annee_scolaire.libelle.split('-')[0] if self.paiement and self.paiement.inscription and self.paiement.inscription.annee_scolaire else '0000'
            count = Recu.objects.filter(
                paiement__inscription__annee_scolaire=self.paiement.inscription.annee_scolaire if self.paiement and self.paiement.inscription else None
            ).count() + 1
            self.numero_recu = f"REC-{annee}-{count:05d}"
        super().save(*args, **kwargs)

    @property
    def eleve(self):
        """Élève concerné par ce reçu."""
        return self.paiement.inscription.eleve if self.paiement and self.paiement.inscription else None

    @property
    def classe(self):
        """Classe de l'élève au moment du reçu."""
        return self.paiement.inscription.classe if self.paiement and self.paiement.inscription else None

    @property
    def annee_scolaire(self):
        """Année scolaire du reçu."""
        return self.paiement.inscription.annee_scolaire if self.paiement and self.paiement.inscription else None


# ==============================================================================
# MODÈLE UTILISATEUR PERSONNALISÉ
# ==============================================================================

class Utilisateur(AbstractUser):
    """
    Utilisateur du système avec rôle personnalisé.
    Étend AbstractUser de Django (username, password, email, first_name, last_name).
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True,
    )
    name = models.CharField(_("Nom de l'utilisateur"), blank=True, max_length=255)
    role = models.CharField(
        max_length=20,
        choices=RoleUtilisateurEnum.choices,
        default=RoleUtilisateurEnum.SECRETAIRE,
        help_text=_("Rôle de l'utilisateur dans le système."),
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Numéro de téléphone de l'utilisateur."),
    )
    photo = models.ImageField(
        upload_to='utilisateurs/photos/',
        blank=True,
        null=True,
        help_text=_("Photo de profil."),
    )
    est_actif_systeme = models.BooleanField(
        default=True,
        help_text=_("Indique si le compte est actif dans le système."),
    )
    derniere_connexion_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_("Dernière adresse IP de connexion."),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")

    def __str__(self):
        return f"{self.name or self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.pk})

    @property
    def peut_encaisser(self):
        """Vérifie si l'utilisateur peut effectuer des encaissements."""
        return self.role in [
            RoleUtilisateurEnum.DIRECTEUR,
            RoleUtilisateurEnum.COMPTABLE,
            RoleUtilisateurEnum.CAISSIER,
        ]

    @property
    def peut_administrer(self):
        """Vérifie si l'utilisateur a des droits d'administration."""
        return self.role in [
            RoleUtilisateurEnum.DIRECTEUR,
            RoleUtilisateurEnum.COMPTABLE,
        ]


# Alias pour rétrocompatibilité
User = Utilisateur

