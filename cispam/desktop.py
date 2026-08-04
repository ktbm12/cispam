"""
================================================================================
CISPAM — Lanceur Desktop Windows avec PyWebview
================================================================================
Lance l'application Django en serveur local (Waitress) et ouvre une fenêtre 
bureau native via PyWebview.
================================================================================
"""

import os
import socket
import sys
import threading
from pathlib import Path

import webview
from waitress import serve

# Chemins et environnement Django
# When frozen by PyInstaller, sys._MEIPASS is the temp directory where
# all bundled files (templates, static, migrations, etc.) are extracted.
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "cispam"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.desktop")

import django
django.setup()

from django.core.management import execute_from_command_line
# Run migrations automatically to initialize the empty database if needed
print("Vérification et application des migrations de la base de données...")
execute_from_command_line(["manage.py", "migrate"])

from config.wsgi import application  # noqa: E402


def find_free_port() -> int:
    """Trouve un port TCP disponible sur la machine locale."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(host: str, port: int):
    """Démarre le serveur WSGI Waitress en arrière-plan."""
    serve(application, host=host, port=port, threads=6, _quiet=True)


def main():
    host = "127.0.0.1"
    port = find_free_port()

    # Démarrage du serveur WSGI dans un thread séparé
    server_thread = threading.Thread(
        target=start_server, args=(host, port), daemon=True
    )
    server_thread.start()

    url = f"http://{host}:{port}/"

    # Création de la fenêtre Desktop native PyWebview
    window = webview.create_window(
        title="CISPAM — Gestion Scolaire & Encaissement",
        url=url,
        width=1280,
        height=800,
        min_size=(1024, 700),
        resizable=True,
        text_select=True,
    )

    # Démarrage de la boucle GUI native PyWebview
    webview.start(debug=False)


if __name__ == "__main__":
    main()
