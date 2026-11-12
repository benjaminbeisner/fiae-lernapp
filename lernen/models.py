from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Pruefung(models.TextChoices):
    AP1 = "AP1", "AP1 (Teil 1)"
    AP2 = "AP2", "AP2 (Teil 2, Fachteil)"
    WISO = "WISO", "Wirtschafts- und Sozialkunde"
    PRAXIS = "PRAXIS", "Berufspraxis"


class Thema(models.Model):
    pruefung = models.CharField("Prüfung", max_length=10, choices=Pruefung.choices, default=Pruefung.AP1)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    gewicht = models.PositiveIntegerField("Ø Punkte pro Prüfung", default=5, help_text="Wie stark das Thema in der Prüfung vorkommt")
    reihenfolge = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Thema"
        verbose_name_plural = "Themen"
        ordering = ["pruefung", "reihenfolge", "name"]

    def __str__(self) -> str:
        return f"{self.get_pruefung_display()}: {self.name}"


class Lektion(models.Model):
    """Ein Lernnugget: kurze Erklärung zu einem Unterthema, danach passende Übungen."""

    schluessel = models.CharField(max_length=50, unique=True)
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name="lektionen")
    titel = models.CharField(max_length=120)
    inhalt = models.TextField(help_text="Erklärung. Erlaubt: **fett**, `code`, Listen mit - , Leerzeile = Absatz")
    merksatz = models.CharField(max_length=300, blank=True)
    bild = models.CharField(max_length=120, blank=True, help_text="Pfad unter static/, z. B. bilder/netzplan.svg")
    stufe = models.PositiveSmallIntegerField(default=1, help_text="1 = Grundlagen, 2 = Aufbau, 3 = Prüfungsniveau")
    reihenfolge = models.PositiveIntegerField(default=0)
    aktiv = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Lektion"
        verbose_name_plural = "Lektionen"
        ordering = ["thema", "stufe", "reihenfolge"]

    def __str__(self) -> str:
        return f"{self.thema.name}: {self.titel}"


class Frage(models.Model):
    class Typ(models.TextChoices):
        EINFACH = "einfach", "Eine richtige Antwort"
        MEHRFACH = "mehrfach", "Mehrere richtige Antworten"
        ZAHL = "zahl", "Zahl eingeben"

    schluessel = models.CharField(max_length=50, unique=True, help_text="Stabile ID aus der Fragendatei")
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name="fragen")
    typ = models.CharField(max_length=10, choices=Typ.choices, default=Typ.EINFACH)
    text = models.TextField("Frage")
    erklaerung = models.TextField("Erklärung", blank=True)
    loesung_zahl = models.DecimalField("Lösung (Zahl)", max_digits=14, decimal_places=4, null=True, blank=True)
    toleranz = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    einheit = models.CharField(max_length=20, blank=True)
    schwierigkeit = models.PositiveSmallIntegerField(default=2, help_text="1 = leicht, 3 = schwer")
    einstufung = models.BooleanField("Im Einstufungstest", default=False)
    lektion = models.ForeignKey(Lektion, null=True, blank=True, on_delete=models.SET_NULL, related_name="fragen")
    bild = models.CharField(max_length=120, blank=True, help_text="Pfad unter static/, z. B. bilder/netzplan.svg")
    gruppe = models.CharField(max_length=60, blank=True, db_index=True,
                              help_text="Varianten derselben Aufgabenvorlage; davon kommt pro Sitzung nur eine")
    punkte = models.PositiveSmallIntegerField(default=0, help_text="Punkte in der Prüfungssimulation (0 = nach Schwierigkeit)")
    aktiv = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"
        ordering = ["thema", "schluessel"]

    def __str__(self) -> str:
        return f"[{self.schluessel}] {self.text[:60]}"


class Antwort(models.Model):
    frage = models.ForeignKey(Frage, on_delete=models.CASCADE, related_name="antworten")
    text = models.CharField(max_length=300)
    richtig = models.BooleanField(default=False)
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Antwortmöglichkeit"
        verbose_name_plural = "Antwortmöglichkeiten"
        ordering = ["reihenfolge", "id"]

    def __str__(self) -> str:
        return self.text


# Leitner-System: Box -> Tage bis zur nächsten Wiederholung
INTERVALLE = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16, 6: 35}
MAX_BOX = max(INTERVALLE)


class Karte(models.Model):
    """Lernstand einer Person zu einer Frage (verteilte Wiederholung)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="karten")
    frage = models.ForeignKey(Frage, on_delete=models.CASCADE, related_name="karten")
    box = models.PositiveSmallIntegerField(default=1)
    faellig_am = models.DateField(default=timezone.localdate)
    richtig_anzahl = models.PositiveIntegerField(default=0)
    falsch_anzahl = models.PositiveIntegerField(default=0)
    zuletzt = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Karte"
        verbose_name_plural = "Karten"
        constraints = [models.UniqueConstraint(fields=["user", "frage"], name="eine_karte_pro_frage")]
        indexes = [models.Index(fields=["user", "faellig_am"])]

    def bewerten(self, richtig: bool) -> None:
        heute = timezone.localdate()
        if richtig:
            self.richtig_anzahl += 1
            self.box = min(self.box + 1, MAX_BOX)
        else:
            self.falsch_anzahl += 1
            self.box = 1
        self.faellig_am = heute + timedelta(days=INTERVALLE[self.box])
        self.zuletzt = timezone.now()


class Versuch(models.Model):
    class Quelle(models.TextChoices):
        EINSTUFUNG = "einstufung", "Einstufungstest"
        TAEGLICH = "taeglich", "Tägliches Lernen"
        THEMA = "thema", "Themen-Training"
        PRUEFUNG = "pruefung", "Prüfungssimulation"
        WIEDERHOLUNG = "wiederholung", "Wiederholung"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="versuche")
    frage = models.ForeignKey(Frage, on_delete=models.CASCADE, related_name="versuche")
    quelle = models.CharField(max_length=14, choices=Quelle.choices)
    richtig = models.BooleanField()
    eingabe = models.CharField(max_length=200, blank=True)
    dauer_sek = models.PositiveIntegerField(default=0)
    zeitpunkt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Versuch"
        verbose_name_plural = "Versuche"
        indexes = [models.Index(fields=["user", "zeitpunkt"])]


class LektionGelesen(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gelesene_lektionen")
    lektion = models.ForeignKey(Lektion, on_delete=models.CASCADE)
    zeitpunkt = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lektion"], name="lektion_einmal_gelesen")]


class Lernzeit(models.Model):
    """Aktive Lernzeit pro Person und Tag (Grundlage der Rangliste)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lernzeiten")
    datum = models.DateField(default=timezone.localdate)
    sekunden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Lernzeit"
        verbose_name_plural = "Lernzeiten"
        constraints = [models.UniqueConstraint(fields=["user", "datum"], name="eine_lernzeit_pro_tag")]


class Abzeichen(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="abzeichen")
    schluessel = models.CharField(max_length=40)
    erhalten_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abzeichen"
        verbose_name_plural = "Abzeichen"
        constraints = [models.UniqueConstraint(fields=["user", "schluessel"], name="abzeichen_einmal")]


class Simulation(models.Model):
    """Eine Prüfungssimulation: feste Fragenliste, Zeitlimit, Auswertung erst am Ende."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="simulationen")
    fragen_ids = models.JSONField()
    antworten = models.JSONField(default=dict)
    start = models.DateTimeField(auto_now_add=True)
    frist = models.DateTimeField()
    abgegeben = models.DateTimeField(null=True, blank=True)
    punkte = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    punkte_max = models.PositiveIntegerField(default=100)

    class Meta:
        verbose_name = "Prüfungssimulation"
        verbose_name_plural = "Prüfungssimulationen"
        ordering = ["-start"]

    @property
    def prozent(self):
        return round(100 * float(self.punkte) / self.punkte_max) if self.punkte is not None else None

    @property
    def note(self):
        p = self.prozent
        if p is None:
            return None
        for grenze, note in ((92, 1), (81, 2), (67, 3), (50, 4), (30, 5)):
            if p >= grenze:
                return note
        return 6
