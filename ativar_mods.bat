@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Verificando se as pastas Bin, Data e Launcher existem no diretório atual
if not exist "Bin\" (
    echo ERRO: Pasta 'Bin' nao encontrada.
    goto :error
)
if not exist "Data\" (
    echo ERRO: Pasta 'Data' nao encontrada.
    goto :error
)
if not exist "Launcher\" (
    echo ERRO: Pasta 'Launcher' nao encontrada.
    goto :error
)

:: Verificando se a pasta _fdge existe
if not exist "_fdge\" (
    echo ERRO: Pasta '_fdge' nao encontrada.
    goto :error
)

:: Copiando arquivos de _fdge\_ROOT para o diretório atual
xcopy "_fdge\_ROOT\*" "%~dp0" /E /H /R /Y
if ERRORLEVEL 1 goto :error

:: Criando ou limpando a pasta %LocalAppData%\Larian Studios\Baldur's Gate 3\Mod
if not exist "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods\" (
    mkdir "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods\"
) else (
    del /F /Q "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods\*"
)

:: Copiando arquivos de _fdge\_PAK para %LocalAppData%\Larian Studios\Baldur's Gate 3\Mod
xcopy "_fdge\_PAK\*" "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods\" /E /H /R /Y
if ERRORLEVEL 1 goto :error

goto :success

:error
echo Ocorreu um erro durante a execucao do script.
timeout /t 5 /nobreak > nul
exit /b 1

:success
echo Instalacao concluida com sucesso!
timeout /t 5 /nobreak > nul
exit /b 0
