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
