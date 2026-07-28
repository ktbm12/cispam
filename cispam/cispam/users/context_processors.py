from django.conf import settings


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }


def etablissement_processor(request):
    """Expose la configuration de l'établissement à tous les templates."""
    from cispam.users.models import ConfigurationEtablissement
    
    # Pour éviter les crashs si la table n'existe pas encore (migrations)
    try:
        etablissement = ConfigurationEtablissement.get_solo()
    except Exception:
        etablissement = None
        
    return {
        "etablissement": etablissement
    }
