from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import InviteCode, Profil


class RegistrierungsForm(UserCreationForm):
    einladungscode = forms.CharField(label="Einladungscode", max_length=20)
    email = forms.EmailField(label="E-Mail", required=True)
    first_name = forms.CharField(label="Vorname", max_length=50, required=True)

    class Meta:
        model = User
        fields = ("einladungscode", "username", "first_name", "email")
        labels = {"username": "Benutzername"}

    def clean_einladungscode(self):
        code = self.cleaned_data["einladungscode"].strip().upper()
        try:
            invite = InviteCode.objects.get(code=code)
        except InviteCode.DoesNotExist:
            raise forms.ValidationError("Diesen Einladungscode gibt es nicht.")
        if not invite.ist_gueltig():
            raise forms.ValidationError("Dieser Einladungscode ist abgelaufen oder schon verbraucht.")
        self.invite = invite
        return code

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Mit dieser E-Mail gibt es schon ein Konto.")
        return email


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ("anzeigename", "in_rangliste", "tagesziel_minuten", "farbthema")
        help_texts = {"anzeigename": "Leer lassen = dein Vorname", "tagesziel_minuten": "Empfehlung: 20 bis 60 Minuten"}

    def __init__(self, *args, level=1, **kwargs):
        from lernen.belohnung import FARBTHEMEN
        super().__init__(*args, **kwargs)
        self.fields["farbthema"] = forms.ChoiceField(
            label="Farbthema", choices=[(k, n) for k, n, ab in FARBTHEMEN if level >= ab],
            help_text="Weitere Farbthemen schaltest du mit höheren Leveln frei.")
        self.fields["tagesziel_minuten"].widget.attrs.update(min=5, max=240)

    def clean_tagesziel_minuten(self):
        return min(max(self.cleaned_data["tagesziel_minuten"], 5), 240)
