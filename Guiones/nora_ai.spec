# Nora AI - PyInstaller Specification
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['ia_app.py'],
             pathex=['D:\\AGENTE_IA\\Scripts'],
             binaries=[],
             datas=[
                 ('../Knowledge/pedagogia_contable.json', 'Knowledge'),
                 ('../Knowledge/persona.txt', 'Knowledge'),
                 ('../.env', '.')
             ],
             hiddenimports=['streamlit', 'google.generativeai', 'supabase', 'PIL', 'psutil'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tkinter', 'unittest', 'email.test'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='NoraAI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='D:\\AGENTE_IA\\tmp\\nora_icon.ico' if os.path.exists('D:\\AGENTE_IA\\tmp\\nora_icon.ico') else None)
