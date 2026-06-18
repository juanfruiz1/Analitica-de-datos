@echo off
cd /d "%~dp0"
echo Iniciando chat con OpenAI...
echo Se abrira el navegador en http://localhost:8501
echo Para cerrar: Ctrl+C en esta ventana.
echo.
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m streamlit run src\chat_openai.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run src\chat_openai.py
) else (
    python -m streamlit run src\chat_openai.py
)
pause
