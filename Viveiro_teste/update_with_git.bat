Title "Instalador - Sistema SMMAURB - (c) Carlos A. Locatelli"
@echo off
setlocal

:: Define a URL do seu repositório Git aqui
set "REPO_URL=https://github.com/carloslocatellij/applications.git"


echo Verificando e instalando o Git via WinGet...
git --version >nul 2>&1
if %errorlevel%==0 (
    echo O Git está instalado no seu computador.
    git --version
) else (
    echo O Git NÃO está instalado ou não foi encontrado no PATH.
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
)

:: 0 - Configurar Proxy
set /p "PROXY_USER=Digite seu usuario: "
set /p "PROXY_PASS=Digite sua_senha: "
set PROXY_HOST=10.17.0.60
set PROXY_PORT=3128

:: Configura o Gerenciador de Credenciais do Windows
echo Configurando o Git Credential Manager...
git config --global credential.helper manager

:: Configura o Proxy HTTP e HTTPS com autenticação
echo Configurando o Proxy do Git...
git config --global http.proxy http://%PROXY_USER%:%PROXY_PASS%@%PROXY_HOST%:%PROXY_PORT%
git config --global https.proxy https://%PROXY_USER%:%PROXY_PASS%@%PROXY_HOST%:%PROXY_PORT%

:: Verifica se as configurações foram aplicadas
echo.
echo === Configuracoes Atuais do Git ===
git config --global --list | findstr /I "proxy credential"

echo url=https://github.com | git credential approve

:: 1. Define os caminhos das pastas e do arquivo JSON
set "pasta_documentos=%USERPROFILE%\Documents"
if not exist "%pasta_documentos%" ( 
    set "pasta_documentos=%USERPROFILE%\Documentos"
) 

set "pasta_viveiro=%pasta_documentos%\Viveiro_Analises"
set "pasta_app_viveiro=%pasta_viveiro%\applications\Viveiro_Analises"
set "arquivo_json=%pasta_app_viveiro%\private\appconfig.json"

:: Atualiza as variáveis de ambiente na sessão atual do CMD
call refreshenv >nul 2>&1
echo Adicionando caminhos do Git se necessario...
set "PATH=%PATH%;C:\Program Files\Git\cmd;C:\Program Files\Git\bin"



:: 2. Verifica se a pasta 'Viveiro_Analises' existe
if exist "%pasta_viveiro%" (
       


    powershell -Command ^
        "$json = Get-Content '%arquivo_json%' | ConvertFrom-Json;" ^
        "if ([version]$json.version -gt [version]'1.3.6') { exit 0 } else { exit 1 }"

        :: 5. Captura o resultado do PowerShell (0 = Maior, 1 = Menor ou Igual)
    if %errorlevel% equ 0 (
        echo Versao eh maior que 1.3.6. Executando git pull...
      
        :: Entra na pasta do repositório para rodar o Git
        cd /d "%pasta_viveiro%"

        if exist "%pasta_viveiro%\.git" (
            git pull
        ) else (
            echo Clonando o repositorio web2py...
            git clone https://github.com/web2py/web2py.git "%pasta_documentos%\web2py"
            ren "%pasta_documentos%\web2py" "Viveiro_Analises"
            cd /d %pasta_viveiro%
        )

        rmdir /s /q "%pasta_viveiro%\binaries" >nul 2>&1

        if exist "%pasta_viveiro%\applications\.git" (
            cd /d "%pasta_viveiro%\applications"
            git pull
        ) else (
            rmdir /s /q "%pasta_viveiro%\applications"
            echo Clonando o repositorio da app...
            git clone %REPO_URL% "%pasta_viveiro%\applications"
        )


    ) else (

        echo A versao nao eh maior que 1.3.6.

        rmdir /s /q "%pasta_viveiro%"

        cd "%pasta_documentos%"

        git clone https://github.com/web2py/web2py.git "%pasta_documentos%\web2py"
        ren "%pasta_documentos%\web2py" "Viveiro_Analises"
        cd /d "%pasta_viveiro%"

        rmdir /s /q "%pasta_viveiro%\binaries" >nul 2>&1
        rmdir /s /q "%pasta_viveiro%\applications" >nul 2>&1

        echo Clonando o repositorio da app...
        git clone %REPO_URL% "%pasta_viveiro%\applications"
    )


    robocopy "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\private" "%pasta_app_viveiro%\private" appconfig.json /XO
    robocopy  "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\site-packages" "%pasta_viveiro%\site-packages"  /E /XO

    set /p "senha=Digite a sua senha: "
    
    :: 3. Executa o PowerShell para substituir o padrao pela senha
    powershell -Command "(Get-Content '%arquivo_json%') -replace '----------', '%senha%' | Set-Content '%arquivo_json%'"
    :: Atualiza requerimentos
    cd /d "%pasta_app_viveiro%"
    python -m pip install --upgrade pip
    pip install -r "%pasta_app_viveiro%\requirements.txt"




) else (

    echo A pasta 'Viveiro_Analises' nao foi encontrada em Documentos.
    echo Primeira Instalação.
   
    git clone https://github.com/web2py/web2py.git "%pasta_documentos%\web2py"

    ren "%pasta_documentos%\web2py" "Viveiro_Analises"

    cd /d "%pasta_viveiro%"

    rmdir /s /q "%pasta_viveiro%\binaries" >nul 2>&1
    rmdir /s /q "%pasta_viveiro%\applications" >nul 2>&1

    echo Clonando o repositorio...
    git clone %REPO_URL% "%pasta_viveiro%\applications"


    cd /d %pasta_viveiro%

    robocopy "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\private" "%pasta_viveiro%\applications\Viveiro_Analises\private" appconfig.json /XO
    robocopy  "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\site-packages" "%pasta_viveiro%\site-packages"  /E /XO
    set /p "senha=Digite a sua senha: "
    
    :: 3. Executa o PowerShell para substituir o padrao pela senha
    powershell -Command "(Get-Content '%arquivo_json%') -replace '----------', '%senha%' | Set-Content '%arquivo_json%'"


    cd /d "%pasta_app_viveiro%"
    python -m pip install --upgrade pip
    pip install -r "%pasta_app_viveiro%\requirements.txt"

    mklink "%userprofile%\Desktop\Viveiro_Analises.lnk" "%pasta_viveiro%\web2py.exe"

)


echo Processo concluido com sucesso!
pause   
endlocal
