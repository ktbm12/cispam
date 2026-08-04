# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Dossier du projet
base_dir = Path('.').resolve()

# Fichiers de données à embarquer dans l'exe
added_files = [
    ('cispam/templates', 'cispam/templates'),
    ('cispam/static', 'cispam/static'),
    ('staticfiles', 'staticfiles'),
    ('locale', 'locale'),
]
added_files += collect_data_files('fido2')
added_files += collect_data_files('allauth')
added_files += collect_data_files('crispy_forms')
added_files += collect_data_files('crispy_bootstrap5')
added_files += collect_data_files('django')

# Imports cachés (Hidden imports) 
hidden_imports = [
    'cispam.users',
    'cispam.users.apps',
    'cispam.users.urls',
    'cispam.users.core_urls',
    'config.settings.desktop',
    'config.wsgi',
    'whitenoise',
    'whitenoise.runserver_nostatic',
    
    # Imports cachés pour Celery
    'celery',
    'celery.fixups.django',
    'celery.loaders.app',
    'celery.backends.database',
    'celery.backends.redis',
    'celery.app.amqp',
    'celery.worker.components',
    'celery.app.events',
    'celery.events.state',
    'kombu.transport.redis',
    'django_celery_beat',
    'django_celery_beat.apps',
]

# Collect all submodules for key packages to prevent runtime MissingModule errors
hidden_imports += collect_submodules('cispam')
hidden_imports += collect_submodules('config')
hidden_imports += collect_submodules('allauth')
hidden_imports += collect_submodules('crispy_forms')
hidden_imports += collect_submodules('crispy_bootstrap5')
hidden_imports += collect_submodules('webview')
hidden_imports += collect_submodules('openpyxl')


a = Analysis(
    ['desktop.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CISPAM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Mettre à True temporairement si besoin de voir les erreurs console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='cispam/static/images/favicons/favicon.ico' # Changez ceci si vous avez une icône (optionnel)
)
