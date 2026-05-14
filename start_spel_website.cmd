@echo off
setlocal

cd /d "%~dp0"

for %%I in ("%~dp0.") do set "APP_DIR=%%~fI"
for %%I in ("%APP_DIR%\..\.venv\Scripts\python.exe") do set "PYTHON_EXE=%%~fI"

if not exist "%PYTHON_EXE%" (
    echo Kon Python niet vinden op "%PYTHON_EXE%".
    echo Maak eerst een virtuele omgeving aan of pas dit pad aan in start_spel_website.cmd.
    pause
    exit /b 1
)

echo.
echo AI in Actie-website start op:
echo http://127.0.0.1:8040/
echo.
echo Laat dit venster open terwijl de website draait.
echo Open daarna zelf je browser op het adres hierboven.
echo Stoppen doe je later met Ctrl+C in dit venster.
echo.

"%PYTHON_EXE%" -m uvicorn website_app:app --app-dir "%APP_DIR%" --host 127.0.0.1 --port 8040

echo.
echo De server is gestopt.
pause

endlocal
