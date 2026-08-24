
def atualizar(): #Menu
    import subprocess
    import os
    import urllib
    import getpass
    from pathlib import Path
    from update_with_git import (
        REPO_URL, WEB2PY_REPO, PROXY_HOST, PROXY_PORT, install_requirements, run_cmd)
    # 0 - Configurar Proxy
    proxy_user = input("Digite seu usuario: ").strip()
    proxy_pass = getpass.getpass("Digite sua_senha: ").strip()

    print("Configurando o Git Credential Manager...")
    run_cmd("git config --global credential.helper manager")

    print("Configurando o Proxy do Git...")
    user_enc = urllib.parse.quote(proxy_user, safe='')
    pass_enc = urllib.parse.quote(proxy_pass, safe='')
    http_proxy = f"http://{user_enc}:{pass_enc}@{PROXY_HOST}:{PROXY_PORT}"
    https_proxy = f"https://{user_enc}:{pass_enc}@{PROXY_HOST}:{PROXY_PORT}"

    run_cmd(f'git config --global http.proxy {http_proxy}')
    run_cmd(f'git config --global https.proxy {https_proxy}')
    run_cmd('cls')

    print("\n=== Configuracoes Atuais do Git ===")
    run_cmd('git config --global --list | findstr /I "proxy credential"')
    # Aprovar credencial para github.com
    try:
        p = subprocess.Popen(["git", "credential", "approve"], stdin=subprocess.PIPE, text=True)
        p.communicate("url=https://github.com\n")
    except Exception as e:
        print(f"Aviso ao aprovar credencial: {e}")
    
    # Caminho para o seu arquivo .bat
    #caminho_arquivo_bat = Path(Path.home(), 'Documents', 'Viveiro_Analises', 'site-packages',  'update_with_git.py')
   
    # 1. Caminhos das pastas e arquivo JSON
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    pasta_documentos = user_profile / "Documents"
    if not pasta_documentos.exists():
        pasta_documentos = user_profile / "Documentos"

    pasta_viveiro = pasta_documentos / "Viveiro_Analises"

    try:
        # Executa o arquivo .bat
        # O argumento shell=True pode ser necessário em alguns casos para executar arquivos .bat,
        # mas é preciso ter cuidado com a segurança, usando-o apenas com caminhos de confiança.
        # Em vez disso, é mais seguro passar o caminho completo para o executável do cmd.exe
        # e o caminho para o arquivo .bat como um argumento, ou simplesmente chamar o arquivo .bat
        # diretamente se ele estiver no PATH ou no diretório atual.
        # Opção 1: Chamar diretamente (se o .bat estiver no PATH ou diretório atual)
        #print(caminho_arquivo_bat)
        #subprocess.run(caminho_arquivo_bat, shell=True, check=True)
        # Opção 2: Usar cmd.exe e Call (mais explícito, se necessário)
        #subprocess.run(f"call {caminho_arquivo_bat}", shell=True, check=True)
        
        if (pasta_viveiro / ".git").exists():
            run_cmd("git pull", cwd=pasta_viveiro)
        pasta_app = pasta_viveiro / "applications"
        if (pasta_app / ".git").exists():
            print("Atualizando repositorio da app...")
            run_cmd("git pull", cwd=pasta_app)
            
        # Instala/Atualiza requerimentos
        install_requirements(pasta_viveiro)

        session.flash = f"Arquivo .bat executado com sucesso!"
        return dict(mensagem="O sistema está sendo atualizado. Clique em voltar e aguarde.")
    except subprocess.CalledProcessError as e:
        session.flash = f"Erro ao executar comando: {e}"
    except Exception as e:
        session.flash = f"Erro ao atualizar: {e}"
    finally:
        session.flash = f"Atualizando... Atualize a página."
        redirect(URL('default','index', extension=''), client_side=True)
        return 'Atualizando...'


