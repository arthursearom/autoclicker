@echo off
setlocal
title AutoClicker - Gerar EXE
where py >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Instale Python 3 para Windows.
    echo Marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)
echo [1/3] Instalando dependencias...
py -m pip install --upgrade pip
if errorlevel 1 goto erro
py -m pip install -r requirements.txt
if errorlevel 1 goto erro
echo [2/3] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [3/3] Gerando AutoClicker.exe...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name AutoClicker --collect-all customtkinter autoclick.py
if errorlevel 1 goto erro
echo.
echo CONCLUIDO! Executavel em dist\\AutoClicker.exe
pause
exit /b 0
:erro
echo Ocorreu um erro durante a compilacao. Leia as mensagens acima.
pause
exit /b 1
