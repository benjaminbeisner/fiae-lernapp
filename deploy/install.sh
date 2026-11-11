#!/usr/bin/env bash
# Erstinstallation der FIAE-Lernapp auf Ubuntu 24.04 mit vorhandenem nginx und MariaDB.
# Aufruf:  sudo bash deploy/install.sh lernen.deinedomain.de https://github.com/NAME/fiae-lernapp.git
set -euo pipefail

DOMAIN="${1:?Bitte Subdomain angeben, z. B. lernen.deinedomain.de}"
REPO="${2:?Bitte die GitHub-Adresse des Repos angeben}"
BASE=/opt/fiae-lernapp
APP=$BASE/app
PORT=8002

[[ $EUID -eq 0 ]] || { echo "Bitte mit sudo ausführen."; exit 1; }

if ss -tln | grep -q ":$PORT "; then
  echo "Port $PORT ist schon belegt. Bitte in deploy/fiae-lernapp.service und deploy/nginx.conf.template einen freien Port eintragen."; exit 1
fi

echo "==> Pakete installieren"
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev build-essential pkg-config default-libmysqlclient-dev git certbot python3-certbot-nginx

echo "==> Systembenutzer und Code"
id lernapp &>/dev/null || useradd --system --home-dir "$BASE" --shell /usr/sbin/nologin lernapp
mkdir -p "$BASE"
if [[ -d $APP/.git ]]; then
  sudo -u lernapp git -C "$APP" pull --ff-only
else
  git clone "$REPO" "$APP"
fi
chown -R lernapp:lernapp "$BASE"

echo "==> Datenbank in MariaDB anlegen"
if [[ ! -f $APP/.env ]]; then
  DBPW=$(openssl rand -hex 24)
  SECRET=$(openssl rand -base64 48 | tr -d '\n=/+')
  mysql <<SQL
CREATE DATABASE IF NOT EXISTS fiae_lernapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'fiae_lernapp'@'localhost' IDENTIFIED BY '$DBPW';
ALTER USER 'fiae_lernapp'@'localhost' IDENTIFIED BY '$DBPW';
GRANT ALL PRIVILEGES ON fiae_lernapp.* TO 'fiae_lernapp'@'localhost';
FLUSH PRIVILEGES;
SQL
  sed -e "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=$SECRET|" \
      -e "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$DOMAIN|" \
      -e "s|^DB_PASSWORD=.*|DB_PASSWORD=$DBPW|" "$APP/.env.example" > "$APP/.env"
  chown lernapp:lernapp "$APP/.env"; chmod 600 "$APP/.env"
  echo "    .env mit zufälligem Datenbank-Passwort angelegt."
fi

echo "==> Python-Umgebung"
sudo -u lernapp python3 -m venv "$BASE/venv"
sudo -u lernapp "$BASE/venv/bin/pip" install -q --upgrade pip
sudo -u lernapp "$BASE/venv/bin/pip" install -q -r "$APP/requirements.txt"

echo "==> Datenbank-Tabellen, statische Dateien, Fragen"
cd "$APP"
sudo -u lernapp "$BASE/venv/bin/python" manage.py migrate --noinput
sudo -u lernapp "$BASE/venv/bin/python" manage.py collectstatic --noinput -v0
sudo -u lernapp "$BASE/venv/bin/python" manage.py fragen_laden

echo "==> Dienst starten"
cp "$APP/deploy/fiae-lernapp.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now fiae-lernapp

echo "==> nginx und HTTPS"
sed "s/__DOMAIN__/$DOMAIN/" "$APP/deploy/nginx.conf.template" > /etc/nginx/sites-available/fiae-lernapp
ln -sf /etc/nginx/sites-available/fiae-lernapp /etc/nginx/sites-enabled/fiae-lernapp
nginx -t
systemctl reload nginx
certbot --nginx -d "$DOMAIN" --redirect --non-interactive --agree-tos --register-unsafely-without-email || \
  echo "!! certbot hat nicht geklappt. Zeigt der DNS-Eintrag für $DOMAIN schon auf diesen Server? Danach erneut: sudo certbot --nginx -d $DOMAIN"

echo
echo "Fertig. Jetzt dein Admin-Konto anlegen:"
echo "  cd $APP && sudo -u lernapp $BASE/venv/bin/python manage.py createsuperuser"
echo "Danach: https://$DOMAIN"
