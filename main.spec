# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from kivy_deps import sdl2, glew
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

def convert_dep_bins(dep_bins):
    """Filtra binários None"""
    result = []
    for b in dep_bins:
        if isinstance(b, tuple) and b[0] is not None:
            if len(b) == 3:
                result.append((b[0], b[1]))
            else:
                result.append(b)
    return result

# DLLs essenciais
binaries = []
binaries += convert_dep_bins(sdl2.dep_bins)
binaries += convert_dep_bins(glew.dep_bins)

# DLLs ANGLE
angle_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'kivy_deps', 'angle')
if os.path.exists(angle_path):
    for dll in os.listdir(angle_path):
        if dll.endswith('.dll'):
            binaries.append((os.path.join(angle_path, dll), '.'))

hiddenimports = [
    'kivy.core.window',
    'kivy.core.image',
    'kivy.core.text',
    'kivy.graphics.opengl',
    'kivy.uix.*',
    'kivymd.uix.*',
]

# Análise principal
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('controllers/*', 'controllers'),
        ('models/*', 'models'),
        ('views/*', 'views'),
        ('assets/*', 'assets'),
        ('uploads/*', 'uploads'),
        ('downloads/*', 'downloads'),
        ('models_whisper/*', 'models_whisper'),
        ('.env', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='atas-kivy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = sem terminal
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='atas-kivy'
)

# Ajuste para rodar ANGLE no onefile
if getattr(sys, 'frozen', False):
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
