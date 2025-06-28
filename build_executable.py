#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# Note: GUI entry point has been removed from setup.py
# This script builds a standalone executable without the GUI entry point
Build script for TikTok-Sayer
This script creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller using pip"""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n=== Building TikTok-Sayer Executable ===\n")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller is not installed. Installing now...")
        install_pyinstaller()
    
    # Create the spec file
    spec_content = f"""\
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_dir / 'tiktok_sayer.py'}'],
    pathex=['{script_dir}'],
    binaries=[],
    datas=[("{script_dir / 'assets'}", 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
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
    name='TikTok-Sayer',
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
    icon='{script_dir / 'assets' / 'icon.ico'}',
)
"""
    
    # Write the spec file
    spec_path = script_dir / "TikTok-Sayer.spec"
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    # Check if icon.ico exists, if not, try to convert from svg
    icon_path = script_dir / "assets" / "icon.ico"
    svg_path = script_dir / "assets" / "icon.svg"
    
    if not icon_path.exists() and svg_path.exists():
        try:
            from cairosvg import svg2png
            from PIL import Image
            import io
            
            print("Converting SVG to ICO...")
            # Convert SVG to PNG
            png_data = svg2png(url=str(svg_path), output_width=256, output_height=256)
            
            # Convert PNG to ICO
            img = Image.open(io.BytesIO(png_data))
            img.save(icon_path)
            print(f"Created icon at {icon_path}")
        except ImportError:
            print("Warning: cairosvg or PIL not installed. Skipping icon conversion.")
            print("You can manually convert the SVG to ICO or install the required packages:")
            print("pip install cairosvg pillow")
    
    # Build the executable
    print("Building executable with PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", str(spec_path), "--clean"])
    
    # Check if build was successful
    exe_path = script_dir / "dist" / "TikTok-Sayer.exe"
    if exe_path.exists():
        print(f"\n✅ Build successful! Executable created at: {exe_path}")
        
        # Create a zip file for distribution
        try:
            import zipfile
            
            zip_path = script_dir / "TikTok-Sayer-Windows.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, "TikTok-Sayer.exe")
                zipf.write(script_dir / "README.md", "README.md")
                zipf.write(script_dir / "LICENSE", "LICENSE")
            
            print(f"✅ Created distribution zip at: {zip_path}")
        except Exception as e:
            print(f"Warning: Failed to create zip file: {str(e)}")
    else:
        print("❌ Build failed! Executable not found.")
        return False
    
    return True


def main():
    """Main function"""
    # Check if all required files exist
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "tiktok_sayer.py"
    
    if not main_script.exists():
        print(f"❌ Main script not found at {main_script}")
        return False
    
    # Create assets directory if it doesn't exist
    assets_dir = script_dir / "assets"
    if not assets_dir.exists():
        os.makedirs(assets_dir)
        print(f"Created assets directory at {assets_dir}")
    
    # Build the executable
    return build_executable()


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)