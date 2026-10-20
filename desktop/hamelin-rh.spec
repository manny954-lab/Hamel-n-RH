# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

PROJECT_ROOT = Path("/home/Emmanuel/Documentos/OPENCODE")
desktop_dir = PROJECT_ROOT / "desktop"
app_dir = desktop_dir / "app"

a = Analysis(
    [str(app_dir / "main.py")],
    pathex=[str(desktop_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "PySide6",
        "shiboken6",
        "app.api_client",
        "app.models",
        "app.ui.theme",
        "app.components.componentes",
        "app.views.login_view",
        "app.views.dashboard_view",
        "app.views.empleados_view",
        "app.views.asistencia_view",
        "app.views.incidencias_view",
        "app.views.justificantes_view",
        "app.views.nomina_view",
        "app.views.reportes_view",
        "app.views.auditoria_view",
        "app.views.usuarios_view",
        "app.main_window",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="hamelin-rh",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
