@echo off
REM Chemin vers votre installation Miniconda
set CONDAPATH=C:\Users\basti\miniconda3

REM Nom de votre environnement Conda
set ENVNAME=EBR_Visualization

REM Chemin vers votre script Python
set SCRIPTPATH=C:\Users\basti\Documents\ebr-visualisation\Home.py

REM Activer l'environnement Conda
call %CONDAPATH%\Scripts\activate.bat %CONDAPATH%
call conda activate %ENVNAME%

REM Lancer le script Streamlit
streamlit run %SCRIPTPATH%

REM Ouvrir l'URL dans le navigateur
start http://localhost:8501

PAUSE