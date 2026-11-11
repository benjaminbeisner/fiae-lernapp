def farbthema(request):
    """Farbthema, Level und Lernserie für die Kopfzeile auf jeder Seite."""
    if not request.user.is_authenticated:
        return {"farbthema": "standard"}
    from lernen.belohnung import level_aus_xp
    from lernen.logik import lernserie

    from .models import Profil

    profil, _ = Profil.objects.get_or_create(user=request.user)
    return {
        "farbthema": profil.farbthema,
        "kopf_level": level_aus_xp(profil.xp)[0],
        "kopf_serie": lernserie(request.user),
    }
