# FIAE-Lernapp

Lern-Web-App für die Umschulung Fachinformatiker/in Anwendungsentwicklung: Einstufungstest, tägliches Lernen mit verteilter Wiederholung (Leitner-System) und Themen-Training. Konten gibt es nur mit Einladungscode.

Technik: Python 3.12+, Django 5.2, MariaDB (oder SQLite lokal), Gunicorn hinter nginx.

## Lokal ausprobieren

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install Django whitenoise          # mysqlclient wird lokal nicht gebraucht
export DJANGO_DEBUG=1                  # nutzt SQLite und einen Entwicklungs-Schlüssel
python manage.py migrate
python manage.py fragen_laden
python manage.py createsuperuser
python manage.py einladung --anzahl 3
python manage.py runserver
```

Dann http://127.0.0.1:8000 öffnen. Die Verwaltung liegt unter `/verwaltung/`.

## Installation auf dem Server (Ubuntu 24.04, nginx und MariaDB schon vorhanden)

1. **DNS bei Hetzner:** In der DNS-Konsole einen A-Eintrag anlegen, Name `lernen`, Wert = IP-Adresse des Contabo-Servers. Ein paar Minuten warten.
2. **Installieren:** Per SSH auf dem Server:
   ```bash
   git clone https://github.com/NAME/fiae-lernapp.git /tmp/fiae-lernapp
   sudo bash /tmp/fiae-lernapp/deploy/install.sh lernen.deinedomain.de https://github.com/NAME/fiae-lernapp.git
   ```
   Das Skript installiert die nötigen Pakete, legt einen eigenen Systembenutzer `lernapp`, eine eigene Datenbank mit zufälligem Passwort, den Dienst auf Port 8002 und einen nginx-Eintrag mit HTTPS-Zertifikat an. Die anderen Anwendungen auf dem Server werden nicht verändert.
3. **Admin-Konto anlegen:**
   ```bash
   cd /opt/fiae-lernapp/app && sudo -u lernapp /opt/fiae-lernapp/venv/bin/python manage.py createsuperuser
   ```
4. **Einladungscodes erzeugen:** in der App unter Verwaltung → Einladungscodes, oder per Befehl:
   ```bash
   sudo -u lernapp /opt/fiae-lernapp/venv/bin/python manage.py einladung --anzahl 11 --notiz "Klasse"
   ```
   Jeder Code gilt für eine Registrierung. Link zum Weitergeben: `https://lernen.deinedomain.de/konto/registrieren/?code=CODE`

Ist das Repo privat, braucht der Server zum Klonen einen Zugang (z. B. einen Deploy-Key). Bei einem öffentlichen Repo entfällt das. Die Zugangsdaten stehen nur in `.env` auf dem Server, nicht im Repo.

**Updates einspielen:** `sudo bash /opt/fiae-lernapp/app/deploy/update.sh`

**Logs ansehen:** `sudo journalctl -u fiae-lernapp -f`

## Fragen bearbeiten

Die Fragen liegen als JSON in `fragen/`. Jede Frage hat einen festen `schluessel`. `python manage.py fragen_laden` legt neue Fragen an und aktualisiert vorhandene, der Lernstand bleibt erhalten. Fragetypen:

- `einfach`: eine richtige Antwort
- `mehrfach`: mehrere richtige Antworten
- `zahl`: Rechenaufgabe mit `loesung`, `toleranz` und `einheit`

`"einstufung": true` nimmt eine Frage in den Einstufungstest auf.

Alle Fragen sind selbst geschrieben, im Stil der IHK-Prüfungen. Original-Prüfungsaufgaben sind urheberrechtlich geschützt und gehören nicht in dieses Repo.

## Tests

```bash
DJANGO_DEBUG=1 python manage.py test
```
