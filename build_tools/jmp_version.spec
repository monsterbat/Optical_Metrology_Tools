# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for JMP Version (without Python Only)
# 打包指令: pyinstaller jmp_version.spec

a = Analysis(
    ['app/main_JMP.py'],  # ← 指向 JMP 版本的主程式
    pathex=[],
    binaries=[],
    datas=[
        # JMP 相關的 JSL 腳本
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
        ('docs/Data Analysis Tools SOP.pdf', 'docs'),
        ],
    hiddenimports=[
        'modules.core.file_operations', 
        'modules.core.jsl_parser',
        'modules.core.spec_setup',
        'modules.ui.components',
        'modules.ui.box_plot_ui',
        'modules.ui.quick_report_ui',
        'modules.utils.path_helper',
        'modules.utils.version',
        'modules.utils.ui_launcher',
        'modules.utils.constants',
        # Python PC 相關的模組已移除，因為 JMP 版本不需要
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
    name='DataAnalysisTools_JMP',  # ← 應用程式名稱
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
    name='Data Analysis Tools (JMP).app',
    icon=None,
    bundle_identifier='com.yourcompany.dataanalysistools.jmp',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.3',
        'CFBundleDisplayName': 'Data Analysis Tools - JMP Edition',
    },
)

