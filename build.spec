# -*- mode: python ; coding: utf-8 -*-
"""
跨平台通用打包配置
支持 Windows、macOS 和 Linux

使用方法：
  普通应用：pyinstaller build.spec
  Windows 屏保：pyinstaller build.spec --screensaver
"""

import os
import sys
import pygame

# 检测平台
IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# 检查是否构建屏保版本（通过环境变量或命令行参数）
IS_SCREENSAVER = os.environ.get('BUILD_SCREENSAVER', '0') == '1' or '--screensaver' in sys.argv

# 获取 pygame 路径
pygame_path = os.path.dirname(pygame.__file__)

# 根据模式选择入口文件和输出名称
if IS_SCREENSAVER and IS_WINDOWS:
    entry_script = 'screensaver.py'
    app_name = 'Christmas_Tree_Screensaver'
else:
    entry_script = 'main.py'
    app_name = 'Christmas_Tree'

# 通用隐藏导入
hidden_imports = [
    'pygame',
    'pygame.base',
    'pygame.constants',
    'pygame.rect',
    'pygame.rwobject',
    'pygame.surface',
    'pygame.color',
    'pygame.math',
    'pygame.pkgdata',
]

# Windows 屏保额外需要
if IS_SCREENSAVER and IS_WINDOWS:
    hidden_imports.extend([
        'tkinter',
        'main',
    ])

a = Analysis(
    [entry_script],
    pathex=[],
    binaries=[],
    datas=[
        (pygame_path, 'pygame'),  # 包含整个 pygame 目录
        ('music.mp3', '.'),  # 包含音乐文件到根目录
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Windows 和 Linux 使用 onedir 模式
# macOS 使用 app bundle (内部也是 onedir 结构)
if IS_MACOS and not IS_SCREENSAVER:
    # macOS App Bundle (onedir 内部结构，快速启动)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
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
        name=app_name,
    )

    app = BUNDLE(
        coll,
        name=f'{app_name}.app',
        icon=None,
        bundle_identifier=None,
    )
else:
    # Windows / Linux / Windows 屏保 (onedir)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=app_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # 不显示控制台
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=None,  # 可添加图标：icon='icon.ico'
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=app_name,
    )

print("=" * 60)
print(f"平台: {'Windows' if IS_WINDOWS else 'macOS' if IS_MACOS else 'Linux'}")
print(f"模式: {'屏保' if IS_SCREENSAVER else '普通应用'}")
print(f"入口: {entry_script}")
print(f"输出: {app_name}")
print("=" * 60)
