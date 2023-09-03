@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Deletando pastas e arquivos especificados
if exist "Bin\NativeMods" (
    rmdir /S /Q "Bin\NativeMods"
)
if exist "Bin\bg3.exe" (
    del /F /Q "Bin\bg3.exe"
)
if exist "Bin\bg3_dx11.exe" (
    del /F /Q "Bin\bg3_dx11.exe"
)
if exist "Bin\bink2w64.dll" (
    del /F /Q "Bin\bink2w64.dll"
)
if exist "Data\Mods" (
    rmdir /S /Q "Data\Mods"
)
if exist "Data\Public" (
    rmdir /S /Q "Data\Public"
)
if exist "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods" (
    rmdir /S /Q "%LocalAppData%\Larian Studios\Baldur's Gate 3\Mods"
)

:: Movendo arquivos da pasta _fdge/_BKP para Bin
if exist "_fdge\_BKP" (
    xcopy "_fdge\_BKP\*" "Bin\" /E /H /R /Y
    if ERRORLEVEL 1 goto :error
)

:: Renomeando arquivos conforme especificado
if exist "Bin\bink2w64_original.dll" (
    ren "Bin\bink2w64_original.dll" "bink2w64.dll"
)
if exist "Bin\bg3.exe.backup" (
    ren "Bin\bg3.exe.backup" "bg3.exe"
)
if exist "Bin\bg3_dx11.exe.backup" (
    ren "Bin\bg3_dx11.exe.backup" "bg3_dx11.exe"
)

echo Operacao concluida com sucesso!
timeout /t 5 /nobreak > nul
exit /b 0

:error
echo Ocorreu um erro durante a execucao do script.
timeout /t 5 /nobreak > nul
exit /b 1
