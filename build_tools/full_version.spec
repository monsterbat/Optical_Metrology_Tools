# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Full Version (包含所有功能)
# 打包指令: pyinstaller full_version.spec

a = Analysis(
    ['app/main.py'],  # ← 指向完整版的主程式
    pathex=[],
    binaries=[],
    datas=[
        # 包含所有 JSL 腳本（JMP 功能需要）
        ('scripts/jsl/best_fit_distribution.jsl', 'scripts/jsl'),
        ('scripts/jsl/jmp_pc_report_generate_best_fit.jsl', 'scripts/jsl'),
        ('scripts/jsl/duplicate_process.jsl', 'scripts/jsl'),
        ('scripts/jsl/box_plot_tool.jsl', 'scripts/jsl'),
        ('scripts/jsl/correlation_tool.jsl', 'scripts/jsl'),
        ('scripts/jsl/jmp_pc_report_generate_normal.jsl', 'scripts/jsl'),
        ('scripts/jsl/exclude_fail.jsl', 'scripts/jsl'),
        ('scripts/jsl/explore_outliers.jsl', 'scripts/jsl'),
        ('scripts/jsl/spec_setup.jsl', 'scripts/jsl'),
        ('scripts/jsl/open_file.jsl', 'scripts/jsl'),
        ('scripts/jsl/export_non_excluded_data.jsl', 'scripts/jsl'),
        ('scripts/jsl/aicc_calculate.jsl', 'scripts/jsl'),
        ('docs/Data Analysis Tools SOP.pdf', 'docs'),
        ],
    hiddenimports=[
        # JMP 相關模組
        'modules.core.file_operations', 
        'modules.core.jsl_parser',
        'modules.core.spec_setup',
        'modules.ui.components',
        'modules.ui.box_plot_ui',
        'modules.ui.quick_report_ui',
        # Python PC 相關模組
        'modules.ui.python_pc_ui',
        'modules.ui.pc_preview_dialog',
        'modules.core.python_pc_core',
        'modules.core.python_pc_calculator',
        'modules.core.aicc_calculator',
        # 通用模組
        'modules.utils.path_helper',
        'modules.utils.version',
        'modules.utils.ui_launcher',
        'modules.utils.constants',
        # 數據處理和統計
        'pandas',
        'numpy',
        'scipy',
        'scipy.stats',
        'scipy.optimize',
        'scipy.special',
        # 繪圖
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.patches',
        # Excel
        'openpyxl',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DataAnalysisTools_Full',  # ← 應用程式名稱
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

# macOS App Bundle
app = BUNDLE(
    exe,
    name='Data Analysis Tools.app',
    icon=None,
    bundle_identifier='com.yourcompany.dataanalysistools.full',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.3',
        'CFBundleDisplayName': 'Data Analysis Tools - Full Edition',
    },
)

