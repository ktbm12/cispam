# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Dossier du projet
base_dir = Path('.').resolve()

# ============================================================================
# DATA FILES — everything that is NOT Python code but needed at runtime
# ============================================================================
added_files = [
    # App templates & static assets
    ('cispam/templates', 'cispam/templates'),
    ('cispam/static', 'cispam/static'),
    ('staticfiles', 'staticfiles'),
    ('locale', 'locale'),

    # ---- Django Migration files (loaded dynamically by Django's migration loader) ----
    # These are .py files but Django imports them via importlib at runtime,
    # so PyInstaller cannot trace them. We include them as DATA files AND
    # as hidden imports below.
    ('cispam/contrib', 'cispam/contrib'),
    ('cispam/users/migrations', 'cispam/users/migrations'),
]

# Collect data files from third-party packages that bundle non-.py resources
added_files += collect_data_files('fido2')
added_files += collect_data_files('allauth')
added_files += collect_data_files('crispy_forms')
added_files += collect_data_files('crispy_bootstrap5')
added_files += collect_data_files('django')
added_files += collect_data_files('django_celery_beat')
added_files += collect_data_files('environ')

# ============================================================================
# HIDDEN IMPORTS — Python modules that are imported dynamically at runtime
# ============================================================================
hidden_imports = [
    # --- Our app ---
    'cispam',
    'cispam.contrib',
    'cispam.contrib.sites',
    'cispam.contrib.sites.migrations',
    'cispam.contrib.sites.migrations.0001_initial',
    'cispam.contrib.sites.migrations.0002_alter_domain_unique',
    'cispam.contrib.sites.migrations.0003_set_site_domain_and_name',
    'cispam.contrib.sites.migrations.0004_alter_options_ordering_domain',
    'cispam.users',
    'cispam.users.apps',
    'cispam.users.urls',
    'cispam.users.core_urls',
    'cispam.users.models',
    'cispam.users.views',
    'cispam.users.admin',
    'cispam.users.forms',
    'cispam.users.context_processors',
    'cispam.users.adapters',
    'cispam.users.managers',
    'cispam.users.tasks',
    'cispam.users.migrations',
    'cispam.users.migrations.0001_initial',
    'cispam.users.migrations.0002_utilisateur_name',
    'cispam.users.migrations.0003_configurationetablissement',

    # --- Config ---
    'config',
    'config.settings',
    'config.settings.base',
    'config.settings.desktop',
    'config.wsgi',

    # --- Core Django ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'django.templatetags.static',
    'django.templatetags.i18n',

    # --- Third party ---
    'whitenoise',
    'whitenoise.middleware',
    'whitenoise.runserver_nostatic',
    'environ',

    # --- Celery ---
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

    # --- PyWebView ---
    'webview',

    # --- Argon2 password hashing ---
    'argon2',
    'argon2._password_hasher',
]

# Collect ALL submodules for packages that heavily rely on dynamic imports
hidden_imports += collect_submodules('cispam')
hidden_imports += collect_submodules('config')
hidden_imports += collect_submodules('allauth')
hidden_imports += collect_submodules('crispy_forms')
hidden_imports += collect_submodules('crispy_bootstrap5')
hidden_imports += collect_submodules('webview')
hidden_imports += collect_submodules('openpyxl')
hidden_imports += collect_submodules('django.contrib')
hidden_imports += collect_submodules('django_celery_beat')
hidden_imports += collect_submodules('environ')
hidden_imports += collect_submodules('argon2')

# De-duplicate
hidden_imports = list(set(hidden_imports))

# ============================================================================
# ANALYSIS
# ============================================================================
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
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='cispam/static/images/favicons/favicon.ico',
)
