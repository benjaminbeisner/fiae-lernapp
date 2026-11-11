#!/usr/bin/env bash
# Neue Version vom GitHub-Repo holen und einspielen.  Aufruf: sudo bash /opt/fiae-lernapp/app/deploy/update.sh
set -euo pipefail
BASE=/opt/fiae-lernapp; APP=$BASE/app
cd "$APP"
sudo -u lernapp git pull --ff-only
sudo -u lernapp "$BASE/venv/bin/pip" install -q -r requirements.txt
sudo -u lernapp "$BASE/venv/bin/python" manage.py migrate --noinput
sudo -u lernapp "$BASE/venv/bin/python" manage.py collectstatic --noinput -v0
sudo -u lernapp "$BASE/venv/bin/python" manage.py fragen_laden
systemctl restart fiae-lernapp
echo "Update fertig."
