"""Erzeugt Einladungscodes auf der Kommandozeile.

Aufruf: python manage.py einladung --anzahl 11 --notiz "Klasse FIAE 2026"
"""

from django.core.management.base import BaseCommand

from accounts.models import InviteCode


class Command(BaseCommand):
    help = "Erzeugt Einladungscodes (je Code eine Registrierung)."

    def add_arguments(self, parser):
        parser.add_argument("--anzahl", type=int, default=1)
        parser.add_argument("--nutzungen", type=int, default=1, help="Wie oft ein Code genutzt werden darf")
        parser.add_argument("--notiz", default="")

    def handle(self, *args, anzahl, nutzungen, notiz, **opts):
        for _ in range(anzahl):
            code = InviteCode.objects.create(max_nutzungen=nutzungen, notiz=notiz)
            self.stdout.write(code.code)
