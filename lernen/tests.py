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
from accounts.models import Profil
from lernen import belohnung
from lernen.models import Abzeichen, Frage, Karte, Lektion, LektionGelesen, Lernzeit, Simulation, Versuch


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
            frage = Frage.objects.get(id=s["items"][s["pos"]]["id"])
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

    def test_tagesnugget_mit_lektion(self):
        items, titel = logik.tagesnugget(self.user)
        self.assertEqual(items[0]["t"], "lektion")
        self.assertTrue(titel.startswith("Lernnugget"))
        lektion = Lektion.objects.get(id=items[0]["id"])
        fragen = Frage.objects.filter(id__in=[i["id"] for i in items if i["t"] == "frage"])
        self.assertEqual(fragen.count(), 8)
        # nur Fragen genau zu diesem Abschnitt, jede Vorlage höchstens einmal
        self.assertEqual(set(fragen.values_list("lektion_id", flat=True)), {lektion.id})
        gruppen = [f.gruppe or f.schluessel for f in fragen]
        self.assertEqual(len(gruppen), len(set(gruppen)))

    def test_wiederholung_nur_faellige(self):
        self.assertEqual(logik.wiederholung(self.user), [])
        f = Frage.objects.filter(lektion__isnull=False).first()
        Karte.objects.create(user=self.user, frage=f, faellig_am=timezone.localdate())
        self.assertEqual(logik.wiederholung(self.user), [{"t": "frage", "id": f.id}])

    def test_zahlenfragen_mit_deutscher_eingabe_loesbar(self):
        from lernen.templatetags.lerntext import zahl_de
        for f in Frage.objects.filter(typ="zahl"):
            ok, _ = logik.pruefe_antwort(f, QueryDict(f"zahl={zahl_de(f.loesung_zahl)}"))
            self.assertTrue(ok, f.schluessel)

    def test_genug_fragen_pro_abschnitt(self):
        self.assertGreaterEqual(Frage.objects.filter(aktiv=True).count(), 2400)
        for l in Lektion.objects.filter(aktiv=True):
            self.assertGreaterEqual(l.fragen.filter(aktiv=True).count(), 25, l.schluessel)

    def test_sitzung_mit_lektion_bucht_xp_und_zeit(self):
        self.client.post(reverse("taeglich_start"))
        r = self.client.get(reverse("sitzung"))
        self.assertContains(r, "Lernnugget")
        self.client.post(reverse("sitzung"), {"aktion": "weiter"})
        self.assertEqual(LektionGelesen.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Profil.objects.get(user=self.user).xp, belohnung.XP_LEKTION)
        s = self.client.session["lernsitzung"]
        frage = Frage.objects.get(id=s["items"][s["pos"]]["id"])
        self.client.get(reverse("sitzung"))
        self.client.post(reverse("sitzung"), {"aktion": "antworten", "zahl": "0", "antwort": []})
        self.assertEqual(Versuch.objects.filter(user=self.user).count(), 1)
        r = self.client.get(reverse("sitzung"))
        self.assertEqual(r.status_code, 200)

    def test_niveau(self):
        thema = Frage.objects.first().thema
        self.assertEqual(logik.niveau(self.user, thema), 1)
        for f in thema.fragen.all()[:10]:
            Versuch.objects.create(user=self.user, frage=f, quelle="thema", richtig=True)
        self.assertEqual(logik.niveau(self.user, thema), 3)

    def test_simulation(self):
        self.client.post(reverse("simulation_start"))
        sim = Simulation.objects.get(user=self.user)
        self.assertEqual(len(sim.fragen_ids), 40)
        self.assertEqual(self.client.get(reverse("simulation", args=[sim.pk])).status_code, 200)
        daten = {"aktion": "abgeben"}
        for f in Frage.objects.filter(id__in=sim.fragen_ids):
            if f.typ == "zahl":
                daten[f"f{f.id}-zahl"] = str(f.loesung_zahl).replace(".", ",")
            else:
                daten[f"f{f.id}"] = [str(i) for i in f.antworten.filter(richtig=True).values_list("id", flat=True)]
        self.client.post(reverse("simulation", args=[sim.pk]), daten)
        sim.refresh_from_db()
        self.assertEqual(sim.prozent, 100)
        self.assertEqual(sim.note, 1)
        r = self.client.get(reverse("simulation_ergebnis", args=[sim.pk]))
        self.assertContains(r, "Note 1")
        self.assertTrue(Abzeichen.objects.filter(user=self.user, schluessel="note1").exists())

    def test_rangliste_nur_sichtbare(self):
        andere = User.objects.create_user("anna", first_name="Anna", password="x-geheim-123")
        Profil.objects.create(user=andere, in_rangliste=False)
        Lernzeit.objects.create(user=andere, sekunden=600)
        Lernzeit.objects.create(user=self.user, sekunden=300)
        r = self.client.get(reverse("rangliste"))
        self.assertNotContains(r, "Anna")
        self.assertContains(r, "5</strong> Min")

    def test_level(self):
        self.assertEqual(belohnung.level_aus_xp(0), (1, 0, 100))
        self.assertEqual(belohnung.level_aus_xp(100), (2, 0, 200))
        self.assertEqual(belohnung.level_aus_xp(350), (3, 50, 300))

    def test_lerntext_escaped(self):
        from lernen.templatetags.lerntext import lerntext
        html = lerntext("<script>x</script> **fett**")
        self.assertNotIn("<script>", html)
        self.assertIn("<strong>fett</strong>", html)

    def test_alle_bilder_vorhanden(self):
        from pathlib import Path
        from django.conf import settings
        for pfad in list(Frage.objects.exclude(bild="").values_list("bild", flat=True)) + list(Lektion.objects.exclude(bild="").values_list("bild", flat=True)):
            self.assertTrue((Path(settings.BASE_DIR) / "static" / pfad).exists(), pfad)

    def test_seiten(self):
        for name in ("dashboard", "einstufung_start", "simulation_start", "rangliste", "abzeichen", "profil"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("thema_detail", args=["netzwerk"])).status_code, 200)


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
