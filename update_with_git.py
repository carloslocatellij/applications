#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador / Atualizador - Sistema SMMAURB
(c) Carlos A. Locatelli
Convertido de update_with_git.bat para Python.
"""

import sys
import os
import shutil
import subprocess
import json
import re
import urllib.parse
from pathlib import Path


REPO_URL = "https://github.com/carloslocatellij/applications.git"
WEB2PY_REPO = "https://github.com/web2py/web2py.git"
PROXY_HOST = "10.17.0.60"
PROXY_PORT = "3128"


def set_console_title(title: str):
    """Define o título do console no Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except Exception:
            os.system(f'title "{title}"')


def run_cmd(cmd, cwd=None, check=False, capture_output=False):
    """Executa um comando no terminal."""
    shell = isinstance(cmd, str)
    return subprocess.run(
        cmd,
        cwd=cwd,
        shell=shell,
        check=check,
        capture_output=capture_output,
        text=True
    )


def check_json_version(json_path: Path, target_version: str = "1.3.6") -> bool:
    """Verifica se a versão no appconfig.json é maior que target_version."""
    if not json_path.exists():
        return False
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        version_str = data.get("version", "0.0.0")

        def parse_v(v):
            return [int(x) for x in re.findall(r'\d+', str(v))]

        return parse_v(version_str) > parse_v(target_version)
    except Exception as e:
        print(f"Aviso ao ler versão do JSON ({e}). Considerando versão menor ou igual.")
        return False


def remove_dir_safely(path: Path):
    """Remove um diretório se existir."""
    if path.exists():
        try:
            shutil.rmtree(path)
        except Exception:
            run_cmd(f'rmdir /s /q "{path}"')


def clone_web2py(target_dir: Path):
    """Clona o web2py sem recursão e remove as pastas 'binaries' e 'applications'."""
    web2py_temp = target_dir.parent / "web2py"
    if web2py_temp.exists():
        remove_dir_safely(web2py_temp)

    print("Clonando o repositorio web2py...")
    run_cmd(f'git clone {WEB2PY_REPO} "{web2py_temp}"')
    if web2py_temp.exists():
        if target_dir.exists():
            remove_dir_safely(target_dir)
        web2py_temp.rename(target_dir)

    # Remove pasta binaries e pasta applications padrão do web2py
    remove_dir_safely(target_dir / "binaries")
    remove_dir_safely(target_dir / "applications")


def clone_app(pasta_viveiro: Path):
    """Clona a aplicação (carloslocatellij/applications) diretamente na pasta 'applications' do web2py."""
    pasta_app = pasta_viveiro / "applications"
    remove_dir_safely(pasta_app)
    print("Clonando o repositorio da app em 'applications'...")
    run_cmd(f'git clone {REPO_URL} "{pasta_app}"')


def run_robocopy(src: str, dst: str, extra_args=None):
    """Executa robocopy tratando os códigos de retorno do Windows (0 a 7 indicam sucesso)."""
    if extra_args is None:
        extra_args = []
    cmd = ["robocopy", src, dst] + extra_args
    res = subprocess.run(cmd, shell=True)
    if res.returncode >= 8:
        print(f"Aviso/Erro no Robocopy: código {res.returncode}")


def create_desktop_shortcut(target_path: Path, shortcut_name: str = "Viveiro_Analises.lnk"):
    """Cria um atalho na Área de Trabalho do usuário."""
    desktop = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
    if not desktop.exists():
        desktop = Path(os.environ.get("USERPROFILE", Path.home())) / "Área de Trabalho"

    shortcut_path = desktop / shortcut_name

    ps_cmd = (
        f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}'); "
        f"$s.TargetPath = '{target_path}'; $s.Save()"
    )
    res = run_cmd(["powershell", "-Command", ps_cmd])
    if res.returncode != 0:
        run_cmd(f'cmd /c mklink "{shortcut_path}" "{target_path}"')


def find_python_executable(pasta_viveiro: Path) -> str:
    """Retorna o executável do Python correto a ser usado para pip (detecta venv se existir)."""
    possible_venvs = [
        pasta_viveiro / ".venv" / "Scripts" / "python.exe",
        pasta_viveiro / "venv" / "Scripts" / "python.exe",
        pasta_viveiro.parent / ".venv" / "Scripts" / "python.exe",
    ]
    for venv_py in possible_venvs:
        if venv_py.exists():
            print(f"Ambiente virtual detectado: {venv_py}")
            return str(venv_py)
    return sys.executable


def install_requirements(pasta_viveiro: Path):
    """Instala todas as dependências encontradas em arquivos requirements.txt e garante o legacy-cgi."""
    python_exe = find_python_executable(pasta_viveiro)
    print(f"Instalando requerimentos usando Python: {python_exe}")

    # Atualiza o pip
    run_cmd(f'"{python_exe}" -m pip install --upgrade pip')

    # Se estiver em Python >= 3.13, garante a instalação de legacy-cgi
    if sys.version_info >= (3, 13):
        print("Python >= 3.13 detectado. Garantindo instalacao do 'legacy-cgi'...")
        run_cmd(f'"{python_exe}" -m pip install legacy-cgi')

    # Procura por todos os arquivos requirements.txt dentro de pasta_viveiro/applications
    pasta_applications = pasta_viveiro / "applications"
    req_files = list(pasta_applications.rglob("requirements.txt")) if pasta_applications.exists() else []

    if not req_files:
        # Fallback para o arquivo principal se a busca rglob não encontrar
        fallback_req = pasta_viveiro / "applications" / "Viveiro_Analises" / "requirements.txt"
        if fallback_req.exists():
            req_files.append(fallback_req)

    for req_file in req_files:
        print(f"Instalando dependencias de: {req_file}")
        run_cmd(f'"{python_exe}" -m pip install -r "{req_file}"', cwd=req_file.parent)


def main():
    set_console_title("Instalador - Sistema SMMAURB - (c) Carlos A. Locatelli")

    # Verificando e instalando o Git
    print("Verificando e instalando o Git via WinGet...")
    git_check = run_cmd("git --version", capture_output=True)
    if git_check.returncode == 0:
        print("O Git está instalado no seu computador.")
        if git_check.stdout:
            print(git_check.stdout.strip())
    else:
        print("O Git NÃO está instalado ou não foi encontrado no PATH.")
        run_cmd("winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements")

    # Adicionando caminhos padrão do Git ao PATH da sessão atual
    git_paths = [r"C:\Program Files\Git\cmd", r"C:\Program Files\Git\bin"]
    for p in git_paths:
        if os.path.exists(p) and p not in os.environ.get("PATH", ""):
            os.environ["PATH"] += os.pathsep + p

    # 0 - Configurar Proxy
    proxy_user = input("Digite seu usuario: ").strip()
    proxy_pass = input("Digite sua_senha: ").strip()

    print("Configurando o Git Credential Manager...")
    run_cmd("git config --global credential.helper manager")

    print("Configurando o Proxy do Git...")
    user_enc = urllib.parse.quote(proxy_user, safe='')
    pass_enc = urllib.parse.quote(proxy_pass, safe='')
    http_proxy = f"http://{user_enc}:{pass_enc}@{PROXY_HOST}:{PROXY_PORT}"
    https_proxy = f"https://{user_enc}:{pass_enc}@{PROXY_HOST}:{PROXY_PORT}"

    run_cmd(f'git config --global http.proxy {http_proxy}')
    run_cmd(f'git config --global https.proxy {https_proxy}')

    print("\n=== Configuracoes Atuais do Git ===")
    run_cmd('git config --global --list | findstr /I "proxy credential"')

    # Aprovar credencial para github.com
    try:
        p = subprocess.Popen(["git", "credential", "approve"], stdin=subprocess.PIPE, text=True)
        p.communicate("url=https://github.com\n")
    except Exception as e:
        print(f"Aviso ao aprovar credencial: {e}")

    # 1. Caminhos das pastas e arquivo JSON
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    pasta_documentos = user_profile / "Documents"
    if not pasta_documentos.exists():
        pasta_documentos = user_profile / "Documentos"

    pasta_viveiro = pasta_documentos / "Viveiro_Analises"
    pasta_app_viveiro = pasta_viveiro / "applications" / "Viveiro_Analises"
    arquivo_json = pasta_app_viveiro / "private" / "appconfig.json"

    # 2. Verifica se a pasta 'Viveiro_Analises' existe
    if pasta_viveiro.exists():
        if check_json_version(arquivo_json, "1.3.6"):
            print("Versao eh maior que 1.3.6. Executando git pull...")

            if (pasta_viveiro / ".git").exists():
                run_cmd("git pull", cwd=pasta_viveiro)
            else:
                clone_web2py(pasta_viveiro)

            remove_dir_safely(pasta_viveiro / "binaries")

            pasta_app = pasta_viveiro / "applications"
            if (pasta_app / ".git").exists():
                print("Atualizando repositorio da app...")
                run_cmd("git pull", cwd=pasta_app)
            else:
                clone_app(pasta_viveiro)
        else:
            print("A versao nao eh maior que 1.3.6.")
            remove_dir_safely(pasta_viveiro)
            clone_web2py(pasta_viveiro)
            clone_app(pasta_viveiro)

    else:
        print("A pasta 'Viveiro_Analises' nao foi encontrada em Documentos.")
        print("Primeira Instalação.")
        clone_web2py(pasta_viveiro)
        clone_app(pasta_viveiro)

    # Cópia e atualizações finais
    run_robocopy(
        r"F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\private",
        str(pasta_app_viveiro / "private"),
        ["appconfig.json", "/XO"]
    )
    run_robocopy(
        r"F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\site-packages",
        str(pasta_viveiro / "site-packages"),
        ["/E", "/XO"]
    )

    senha = input("Digite a sua senha: ")

    if arquivo_json.exists():
        try:
            content = arquivo_json.read_text(encoding="utf-8", errors="ignore")
            content = content.replace("----------", senha)
            arquivo_json.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"Erro ao atualizar {arquivo_json}: {e}")

    # Instala/Atualiza requerimentos
    install_requirements(pasta_viveiro)

    if not (user_profile / "Desktop" / "Viveiro_Analises.lnk").exists():
        create_desktop_shortcut(pasta_viveiro / "web2py.exe", "Viveiro_Analises.lnk")

    print("\nProcesso concluido com sucesso!")
    input("Pressione ENTER para fechar...")


if __name__ == "__main__":
    main()
