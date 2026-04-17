@echo off
title Nora de Nexora - MyJNexoraVisual
echo Lanzando Orquestador de Conciencia (Rutas Dinámicas)...
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"
"%PROJECT_DIR%env\Scripts\streamlit" run "%PROJECT_DIR%Scripts\ia_app.py"
pause
