# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Python Only Version (Python 3.12)
# 打包指令: python3.12 -m PyInstaller build_tools/python_version_new.spec

import os
import sys

spec_root = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(spec_root, 'app', 'main_python.py')],
    pathex=[spec_root],
    binaries=[],
    datas=[
        # Config 資料夾
        (os.path.join(spec_root, 'config'), 'config'),
    ],
    hiddenimports=[
        # ===== src.ui 模組 =====
        'src.ui.python_pc_ui',
        'src.ui.pc_preview_dialog',
        'src.ui.box_plot_dialog',
        'src.ui.correlation_dialog',
        'src.ui.spec_setup_dialog',
        
        # ===== src.core 模組 =====
        'src.core.data_processor',
        'src.core.pc_calculator',
        'src.core.distribution_fitter',
        'src.core.aicc_calculator',
        'src.core.box_plot_analyzer',
        'src.core.correlation_analyzer',
        
        # ===== src.io 模組 =====
        'src.io.file_operations',
        
        # ===== src.utils 模組 =====
        'src.utils.paths',
        'src.utils.version',
        'src.utils.constants',
        'src.utils.jmptools',
        
        # ===== 第三方套件 =====
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        
        'pandas',
        'numpy',
        'scipy',
        'scipy.stats',
        'scipy.optimize',
        'scipy.special',
        'scipy.sparse',
        'scipy._lib',
        'scipy._cyutility',
        
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'matplotlib.patches',
        
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        
        'seaborn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不需要的模組
        'src.core.jsl_handler',
        'src.ui.jmp_ui',
        'src.ui.quick_report_ui',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Optical Data Analysis Tools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Optical Data Analysis Tools',
)

app = BUNDLE(
    coll,
    name='Optical Data Analysis Tools.app',
    icon=None,
    bundle_identifier='com.yourcompany.opticaldataanalysis',
    info_plist={
        'CFBundleName': 'Optical Data Analysis Tools',
        'CFBundleDisplayName': 'Optical Data Analysis Tools',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
    },
)

