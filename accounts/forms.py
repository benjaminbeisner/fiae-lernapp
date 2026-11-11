from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import InviteCode


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
