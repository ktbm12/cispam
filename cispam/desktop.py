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
import traceback
from pathlib import Path

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

if os.name == 'nt':
    LOG_DIR = Path(os.environ.get('APPDATA', str(Path.home()))) / "cispam"
else:
    LOG_DIR = Path.home() / ".cispam"
LOG_DIR.mkdir(parents=True, exist_ok=True)
CRASH_LOG = LOG_DIR / "crash.log"


def report_fatal_error(exc: BaseException):
    """Log the traceback and show a native message box.

    The packaged exe runs without a console window, so an unhandled
    exception must be surfaced some other way instead of vanishing silently.
    """
    CRASH_LOG.write_text(traceback.format_exc(), encoding="utf-8")
    message = f"CISPAM a rencontré une erreur au démarrage :\n\n{exc}\n\nDétails enregistrés dans :\n{CRASH_LOG}"
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, "CISPAM — Erreur", 0x10)
    else:
        print(message, file=sys.stderr)


def find_free_port() -> int:
    """Trouve un port TCP disponible sur la machine locale."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(application, host: str, port: int):
    """Démarre le serveur WSGI Waitress en arrière-plan."""
    from waitress import serve
    serve(application, host=host, port=port, threads=6, _quiet=True)


def bootstrap_django():
    """Initialise Django, applique les migrations et crée l'admin par défaut."""
    import django
    django.setup()

    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "migrate"])

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.exists():
        User.objects.create_superuser(
            email="admin@gmail.com",
            password="admin",
            name="Administrateur",
            role="directeur",
        )

    from config.wsgi import application
    return application


def main():
    application = bootstrap_django()

    host = "127.0.0.1"
    port = find_free_port()

    # Démarrage du serveur WSGI dans un thread séparé
    server_thread = threading.Thread(
        target=start_server, args=(application, host, port), daemon=True
    )
    server_thread.start()

    url = f"http://{host}:{port}/"

    import webview

    # Création de la fenêtre Desktop native PyWebview
    webview.create_window(
        title="CISPAM — Gestion Scolaire & Encaissement",
        url=url,
        width=1280,
        height=800,
        min_size=(1024, 700),
        resizable=True,
        text_select=True,
    )

    # Force the Chromium (WebView2) engine explicitly. Without this, pywebview
    # silently falls back to the legacy Trident/MSHTML (IE11) engine on Windows
    # machines that don't have the WebView2 Runtime installed. That legacy
    # engine cannot render the modern CSS used by the app (Tailwind v4 output:
    # oklch colors, @layer, CSS nesting, etc.), which looks like "the CSS
    # doesn't load" even though the stylesheet is served correctly. Forcing
    # edgechromium turns that silent breakage into a clear, catchable error
    # instead, so we can point the user at installing the WebView2 Runtime.
    gui = 'edgechromium' if os.name == 'nt' else None
    webview.start(gui=gui, debug=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level crash handler
        report_fatal_error(exc)
        sys.exit(1)
