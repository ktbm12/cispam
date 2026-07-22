from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from cispam.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("dashboard")


user_redirect_view = UserRedirectView.as_view()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum
        from cispam.users.models import AnneeScolaire, Eleve, Inscription, Paiement

        try:
            annee = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            annee = None

        total_eleves = Eleve.objects.filter(is_deleted=False).count()
        total_inscriptions = Inscription.objects.filter(is_deleted=False).count()

        paiements = Paiement.objects.filter(is_deleted=False)
        total_paye = paiements.aggregate(total=Sum("montant"))["total"] or 0

        inscriptions = Inscription.objects.filter(is_deleted=False)
        total_frais = inscriptions.aggregate(total=Sum("frais_total"))["total"] or 0
        total_solde = total_frais - total_paye

        taux_recouvrement = round((total_paye / total_frais * 100), 1) if total_frais > 0 else 0

        context.update({
            "annee_active": annee,
            "total_eleves": total_eleves,
            "total_inscriptions": total_inscriptions,
            "total_frais": total_frais,
            "total_paye": total_paye,
            "total_solde": total_solde,
            "taux_recouvrement": taux_recouvrement,
            "derniers_paiements": paiements.select_related("inscription__eleve", "inscription__classe")[:5],
            "derniere_inscriptions": inscriptions.select_related("eleve", "classe")[:5],
        })
        return context


dashboard_view = DashboardView.as_view()


class AnneeScolaireListView(LoginRequiredMixin, TemplateView):
    template_name = "annees/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db import models
        from cispam.users.models import AnneeScolaire

        annees = AnneeScolaire.objects.filter(is_deleted=False).annotate(
            nb_inscriptions=models.Count("inscriptions", filter=models.Q(inscriptions__is_deleted=False)),
        )

        context["annees"] = annees
        try:
            context["annee_active"] = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            context["annee_active"] = None
        return context


class AnneeScolaireActivateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import get_object_or_404, redirect
        from cispam.users.models import AnneeScolaire

        pk = kwargs.get("pk")
        annee = get_object_or_404(AnneeScolaire, pk=pk)
        annee.est_active = True
        annee.save()
        messages.success(request, f"L'année scolaire {annee.libelle} est désormais l'année active du système.")
        return redirect(request.META.get("HTTP_REFERER", "annees_list"))


class AnneeScolaireCreateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect
        from cispam.users.models import AnneeScolaire

        libelle = request.POST.get("libelle", "").strip()
        date_debut = request.POST.get("date_debut")
        date_fin = request.POST.get("date_fin")
        est_active = request.POST.get("est_active") == "on"

        if not libelle or not date_debut or not date_fin:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect(request.META.get("HTTP_REFERER", "annees_list"))

        try:
            annee = AnneeScolaire.objects.create(
                libelle=libelle,
                date_debut=date_debut,
                date_fin=date_fin,
                est_active=est_active,
            )
            messages.success(request, f"Année scolaire {annee.libelle} créée avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {e}")

        return redirect(request.META.get("HTTP_REFERER", "annees_list"))


annees_list_view = AnneeScolaireListView.as_view()
annees_activate_view = AnneeScolaireActivateView.as_view()
annees_create_view = AnneeScolaireCreateView.as_view()


# ==============================================================================
# VUES — CLASSES & NIVEAUX
# ==============================================================================

class ClasseListView(LoginRequiredMixin, TemplateView):
    template_name = "classes/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from cispam.users.models import AnneeScolaire, Classe, Niveau, NiveauScolaireEnum

        if not Niveau.objects.exists():
            Niveau.objects.get_or_create(nom=NiveauScolaireEnum.MATERNELLE, defaults={"ordre": 1, "description": "Cycle Maternelle"})
            Niveau.objects.get_or_create(nom=NiveauScolaireEnum.PRIMAIRE, defaults={"ordre": 2, "description": "Cycle Primaire"})

        classes = Classe.objects.filter(is_deleted=False).select_related("niveau")
        niveaux = Niveau.objects.filter(is_deleted=False)

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            annee_active = None

        context.update({
            "classes": classes,
            "niveaux": niveaux,
            "annee_active": annee_active,
        })
        return context


class ClasseCreateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import get_object_or_404, redirect
        from cispam.users.models import Classe, Niveau

        nom = request.POST.get("nom", "").strip()
        niveau_id = request.POST.get("niveau")
        capacite_max = request.POST.get("capacite_max", 30)
        description = request.POST.get("description", "").strip()

        if not nom or not niveau_id:
            messages.error(request, "Veuillez fournir le nom et le niveau de la classe.")
            return redirect(request.META.get("HTTP_REFERER", "classes_list"))

        niveau = get_object_or_404(Niveau, pk=niveau_id)
        try:
            classe = Classe.objects.create(
                nom=nom,
                niveau=niveau,
                capacite_max=int(capacite_max),
                description=description,
            )
            messages.success(request, f"La classe {classe.nom} ({niveau.get_nom_display()}) a été créée avec succès !")
        except Exception as e:
            messages.error(request, f"Impossible de créer la classe : {e}")

        return redirect(request.META.get("HTTP_REFERER", "classes_list"))


classes_list_view = ClasseListView.as_view()
classes_create_view = ClasseCreateView.as_view()


# ==============================================================================
# VUES — GRILLE DES FRAIS DE SCOLARITÉ
# ==============================================================================

class FraisScolariteListView(LoginRequiredMixin, TemplateView):
    template_name = "frais/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from cispam.users.models import AnneeScolaire, Classe, FraisScolarite

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
            frais_list = FraisScolarite.objects.filter(annee_scolaire=annee_active, is_deleted=False).select_related("classe", "annee_scolaire")
        except AnneeScolaire.DoesNotExist:
            annee_active = None
            frais_list = FraisScolarite.objects.none()

        classes = Classe.objects.filter(is_deleted=False).select_related("niveau")

        context.update({
            "frais_list": frais_list,
            "classes": classes,
            "annee_active": annee_active,
        })
        return context


class FraisScolariteCreateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import get_object_or_404, redirect
        from cispam.users.models import AnneeScolaire, Classe, FraisScolarite

        classe_id = request.POST.get("classe")
        montant_total = request.POST.get("montant_total", 0)
        montant_tranche_1 = request.POST.get("montant_tranche_1", 0)
        montant_tranche_2 = request.POST.get("montant_tranche_2", 0)
        montant_tranche_3 = request.POST.get("montant_tranche_3", 0)

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            messages.error(request, "Aucune année scolaire active n'a été définie.")
            return redirect(request.META.get("HTTP_REFERER", "frais_list"))

        classe = get_object_or_404(Classe, pk=classe_id)
        libelle = f"Frais {classe.nom} — {annee_active.libelle}"

        try:
            frais, created = FraisScolarite.objects.update_or_create(
                classe=classe,
                annee_scolaire=annee_active,
                defaults={
                    "libelle": libelle,
                    "montant_total": montant_total,
                    "nombre_tranches": 3,
                    "montant_tranche_1": montant_tranche_1,
                    "montant_tranche_2": montant_tranche_2,
                    "montant_tranche_3": montant_tranche_3,
                },
            )
            action_text = "définie" if created else "mise à jour"
            messages.success(request, f"La grille tarifaire de la classe {classe.nom} a été {action_text} avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement des frais : {e}")

        return redirect(request.META.get("HTTP_REFERER", "frais_list"))


frais_list_view = FraisScolariteListView.as_view()
frais_create_view = FraisScolariteCreateView.as_view()


# ==============================================================================
# VUES — INSCRIPTIONS DES ÉCOLIERS
# ==============================================================================

class InscriptionListView(LoginRequiredMixin, TemplateView):
    template_name = "inscriptions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from cispam.users.models import AnneeScolaire, Classe, Inscription, ModePaiementEnum, TrancheEnum

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
            inscriptions = Inscription.objects.filter(annee_scolaire=annee_active, is_deleted=False).select_related(
                "eleve", "classe", "annee_scolaire"
            ).prefetch_related("eleve__parents", "paiements")
        except AnneeScolaire.DoesNotExist:
            annee_active = None
            inscriptions = Inscription.objects.none()

        classes = Classe.objects.filter(is_deleted=False).select_related("niveau")

        context.update({
            "inscriptions": inscriptions,
            "classes": classes,
            "annee_active": annee_active,
            "modes_paiement": ModePaiementEnum.choices,
            "tranches": TrancheEnum.choices,
        })
        return context


class InscriptionCreateView(LoginRequiredMixin, TemplateView):
    template_name = "inscriptions/nouveau.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from cispam.users.models import AnneeScolaire, Classe, LienParenteEnum, SexeEnum, TypeInscriptionEnum

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            annee_active = None

        classes = Classe.objects.filter(is_deleted=False).select_related("niveau")

        context.update({
            "annee_active": annee_active,
            "classes": classes,
            "sexes": SexeEnum.choices,
            "liens_parente": LienParenteEnum.choices,
            "types_inscription": TypeInscriptionEnum.choices,
        })
        return context

    def post(self, request, *args, **kwargs):
        from datetime import date
        from django.contrib import messages
        from django.shortcuts import get_object_or_404, redirect
        from cispam.users.models import AnneeScolaire, Classe, Eleve, FraisScolarite, Inscription, Parent

        try:
            annee_active = AnneeScolaire.objects.get(est_active=True)
        except AnneeScolaire.DoesNotExist:
            messages.error(request, "Veuillez d'abord définir une année scolaire active.")
            return redirect("annees_list")

        # Extraction des données du formulaire
        nom = request.POST.get("nom", "").strip()
        prenom = request.POST.get("prenom", "").strip()
        sexe = request.POST.get("sexe", "M")
        date_naissance = request.POST.get("date_naissance")
        lieu_naissance = request.POST.get("lieu_naissance", "").strip()
        adresse = request.POST.get("adresse", "").strip()
        classe_id = request.POST.get("classe")
        type_inscription = request.POST.get("type_inscription", "NOUVELLE")

        # Infos du parent
        parent_nom = request.POST.get("parent_nom", "").strip()
        parent_prenom = request.POST.get("parent_prenom", "").strip()
        parent_telephone = request.POST.get("parent_telephone", "").strip()
        parent_lien = request.POST.get("parent_lien", "PERE")

        if not nom or not prenom or not date_naissance or not classe_id:
            messages.error(request, "Veuillez remplir tous les champs obligatoires (*).")
            return redirect("inscriptions_create")

        classe = get_object_or_404(Classe, pk=classe_id)

        # Génération matricule automatique : ECO-AAAA-xxxxx
        annee_str = date.today().year
        count_eleves = Eleve.objects.count() + 1
        matricule = f"ECO-{annee_str}-{count_eleves:05d}"

        try:
            # 1. Création de l'élève
            eleve = Eleve.objects.create(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                sexe=sexe,
                date_naissance=date_naissance,
                lieu_naissance=lieu_naissance,
                adresse=adresse,
            )

            # 2. Création du parent si renseigné
            if parent_nom and parent_prenom:
                Parent.objects.create(
                    eleve=eleve,
                    nom=parent_nom,
                    prenom=parent_prenom,
                    telephone=parent_telephone,
                    lien_parente=parent_lien,
                    est_contact_principal=True,
                )

            # 3. Récupération des frais de scolarité rattachés à la classe
            try:
                frais_config = FraisScolarite.objects.get(classe=classe, annee_scolaire=annee_active)
                frais_total = frais_config.montant_total
            except FraisScolarite.DoesNotExist:
                frais_total = 0

            # 4. Inscription de l'élève
            inscription = Inscription.objects.create(
                eleve=eleve,
                classe=classe,
                annee_scolaire=annee_active,
                type_inscription=type_inscription,
                frais_total=frais_total,
            )

            messages.success(
                request,
                f"L'élève {eleve.nom_complet} (Matricule: {eleve.matricule}) a été inscrit en classe de {classe.nom} avec succès !"
            )
            return redirect("inscriptions_list")

        except Exception as e:
            messages.error(request, f"Erreur lors de l'inscription : {e}")
            return redirect("inscriptions_create")


inscriptions_list_view = InscriptionListView.as_view()
inscriptions_create_view = InscriptionCreateView.as_view()


# ==============================================================================
# VUES — PAIEMENTS & CAISSE
# ==============================================================================

class PaiementCreateView(LoginRequiredMixin, RedirectView):
    permanent = False

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import get_object_or_404, redirect
        from cispam.users.models import Inscription, ModePaiementEnum, Paiement, Recu, StatutRecuEnum, TrancheEnum

        inscription_id = request.POST.get("inscription_id")
        montant = request.POST.get("montant")
        mode_paiement = request.POST.get("mode_paiement", ModePaiementEnum.ESPECES)
        tranche = request.POST.get("tranche", TrancheEnum.TRANCHE_1)
        reference_transaction = request.POST.get("reference_transaction", "").strip()

        if not inscription_id or not montant:
            messages.error(request, "Veuillez préciser l'inscription et le montant du paiement.")
            return redirect(request.META.get("HTTP_REFERER", "inscriptions_list"))

        inscription = get_object_or_404(Inscription, pk=inscription_id)

        try:
            montant_num = float(montant)
            if montant_num <= 0:
                messages.error(request, "Le montant doit être supérieur à 0 FCFA.")
                return redirect(request.META.get("HTTP_REFERER", "inscriptions_list"))

            # 1. Création du paiement
            paiement = Paiement.objects.create(
                inscription=inscription,
                montant=montant_num,
                mode_paiement=mode_paiement,
                tranche=tranche,
                reference_transaction=reference_transaction,
                operateur=request.user.name or request.user.username,
            )

            # 2. Génération automatique du reçu
            annee = inscription.annee_scolaire.libelle.split('-')[0] if inscription.annee_scolaire else '0000'
            count_recus = Recu.objects.count() + 1
            num_recu = f"REC-{annee}-{count_recus:05d}"

            recu = Recu.objects.create(
                paiement=paiement,
                numero_recu=num_recu,
                statut=StatutRecuEnum.GENERE,
            )

            messages.success(
                request,
                f"Encaissement de {montant_num:,.0f} FCFA enregistré avec succès ! Reçu N° {recu.numero_recu} généré."
            )

        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement du paiement : {e}")

        return redirect(request.META.get("HTTP_REFERER", "inscriptions_list"))


paiements_create_view = PaiementCreateView.as_view()



