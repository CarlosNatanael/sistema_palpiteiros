@echo off
REM Define o diretório do projeto Flask
REM "C:\Pasta Dev\sistema_palpiteiros"
cd /d "C:\Users\SUPORTE 03\Desktop\EU\Eu (Carlos)\Cod_Dev\sistema_palpiteiros"

REM Define a variável de ambiente para o arquivo Flask principal
set FLASK_APP=app.py

REM Define o ambiente como development para habilitar o modo debug
set FLASK_ENV=development

REM Inicia o servidor Flask no IP e porta especificados
flask run --host=0.0.0.0 --port=3000
