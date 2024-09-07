@echo off
setlocal

REM Define o caminho do jogo (ajuste conforme necessário)
set "game_path=G:\SteamLibrary\steamapps\common\mfdx\MF2\MF2.exe"

REM Nome do programa de monitoramento
set "monitoring_program=LifeSpanMF2.exe"

REM Caminho da pasta onde o script .bat está localizado
set "base_path=%~dp0"

REM Caminho completo para o programa de monitoramento
set "monitoring_program_path=%base_path%%monitoring_program%"

REM Inicia o jogo
start "" "%game_path%"

REM Aguarda alguns segundos para garantir que o jogo tenha tempo de iniciar
timeout /t 20 /nobreak >nul

REM Verifica se o programa de monitoramento existe
if exist "%monitoring_program_path%" (
    REM Aguarda o processo do jogo estar em execução
    set "game_running=false"
    for /f "tokens=1,2" %%a in ('tasklist /FI "IMAGENAME eq MF2.exe" /FO CSV /NH') do (
        if "%%b"=="MF2.exe" (
            set "game_running=true"
        )
    )

    REM Se o jogo estiver em execução, inicia o programa de monitoramento
    if "%game_running%"=="true" (
        start "" "%monitoring_program_path%"
        REM Fecha o script .bat
        exit /b 0
    ) else (
        REM Exibe uma mensagem de erro se o jogo não estiver em execução
        echo Erro: O jogo "%game_path%" nao esta em execucao.
        pause
        exit /b 1
    )
) else (
    REM Exibe uma mensagem de erro se o programa de monitoramento nao for encontrado
    echo Erro: O programa de monitoramento "%monitoring_program%" nao foi encontrado na mesma pasta que o script.
    pause
    exit /b 1
)
