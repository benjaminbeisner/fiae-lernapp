from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import InviteCode
from lernen import logik
from lernen.models import Frage, Karte, Versuch


class FragenTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("fragen_laden", verbosity=0)

    def setUp(self):
        self.user = User.objects.create_user("test", password="geheim-12345")
        self.client.force_login(self.user)

    def test_zahl_lesen(self):
        self.assertEqual(logik.zahl_lesen("1.234,50"), Decimal("1234.50"))
        self.assertEqual(logik.zahl_lesen("950,40 €"), Decimal("950.40"))
        self.assertEqual(logik.zahl_lesen("950.40"), Decimal("950.40"))
        self.assertEqual(logik.zahl_lesen("1.764"), Decimal("1764"))
        self.assertEqual(logik.zahl_lesen("-1"), Decimal("-1"))

    def test_jede_auswahlfrage_hat_richtige_antwort(self):
        for f in Frage.objects.exclude(typ="zahl"):
            self.assertTrue(f.antworten.filter(richtig=True).exists(), f.schluessel)
            if f.typ == "einfach":
                self.assertEqual(f.antworten.filter(richtig=True).count(), 1, f.schluessel)

    def test_pruefe_mehrfach(self):
        f = Frage.objects.get(schluessel="SEC-04")
        richtige = [str(i) for i in f.antworten.filter(richtig=True).values_list("id", flat=True)]
        q = QueryDict(mutable=True)
        q.setlist("antwort", richtige)
        self.assertTrue(logik.pruefe_antwort(f, q)[0])
        q.setlist("antwort", richtige[:1])
        self.assertFalse(logik.pruefe_antwort(f, q)[0])

    def test_leitner(self):
        f = Frage.objects.first()
        k = logik.karte_aktualisieren(self.user, f, True, "taeglich")
        self.assertEqual(k.box, 2)
        self.assertEqual(k.faellig_am, timezone.localdate() + timedelta(days=2))
        k = logik.karte_aktualisieren(self.user, f, False, "taeglich")
        self.assertEqual(k.box, 1)

    def test_einstufung_durchlauf(self):
        self.client.post(reverse("einstufung_start"))
        anzahl = Frage.objects.filter(einstufung=True).count()
        for _ in range(anzahl):
            s = self.client.session["lernsitzung"]
            frage = Frage.objects.get(id=s["ids"][s["pos"]])
            if frage.typ == "zahl":
                daten = {"aktion": "antworten", "zahl": str(frage.loesung_zahl).replace(".", ",")}
            else:
                daten = {"aktion": "antworten", "antwort": [str(i) for i in frage.antworten.filter(richtig=True).values_list("id", flat=True)]}
            self.client.post(reverse("sitzung"), daten)
            self.client.post(reverse("sitzung"), daten)  # doppelt absenden zählt nicht doppelt
            self.client.post(reverse("sitzung"), {"aktion": "weiter"})
        self.assertEqual(Versuch.objects.filter(user=self.user, richtig=True).count(), anzahl)
        r = self.client.get(reverse("sitzung_ende"))
        self.assertContains(r, "100 %")

    def test_tagesfragen(self):
        ids = logik.tagesfragen(self.user)
        self.assertEqual(len(ids), 10)
        f = Frage.objects.get(id=ids[0])
        Karte.objects.create(user=self.user, frage=f, faellig_am=timezone.localdate())
        self.assertIn(f.id, logik.tagesfragen(self.user))

    def test_seiten(self):
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)
        self.assertEqual(self.client.get(reverse("einstufung_start")).status_code, 200)


class RegistrierungTest(TestCase):
    def daten(self, code):
        return {"einladungscode": code, "username": "lena", "first_name": "Lena", "email": "lena@example.org",
                "password1": "Sehr-sicheres-PW-42", "password2": "Sehr-sicheres-PW-42"}

    def test_ohne_gueltigen_code(self):
        r = self.client.post(reverse("registrieren"), self.daten("FALSCH"))
        self.assertContains(r, "gibt es nicht")
        self.assertFalse(User.objects.filter(username="lena").exists())

    def test_mit_code_und_verbraucht(self):
        code = InviteCode.objects.create()
        r = self.client.post(reverse("registrieren"), self.daten(code.code.lower()))
        self.assertRedirects(r, reverse("einstufung_start"))
        code.refresh_from_db()
        self.assertEqual(code.nutzungen, 1)
        self.client.logout()
        d = self.daten(code.code)
        d.update(username="max", email="max@example.org")
        r = self.client.post(reverse("registrieren"), d)
        self.assertContains(r, "verbraucht")

    def test_login_pflicht(self):
        r = self.client.get(reverse("dashboard"))
        self.assertRedirects(r, reverse("login") + "?next=/")
