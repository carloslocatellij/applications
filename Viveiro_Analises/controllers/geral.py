
def atualizar(): #Menu
    import subprocess
    from pathlib import Path
    # Caminho para o seu arquivo .bat
    caminho_arquivo_bat = Path(Path.home(), 'Documents', 'Viveiro_Analises', 'site-packages',  'update_with_git.bat')

    try:
        # Executa o arquivo .bat
        # O argumento shell=True pode ser necessário em alguns casos para executar arquivos .bat,
        # mas é preciso ter cuidado com a segurança, usando-o apenas com caminhos de confiança.
        # Em vez disso, é mais seguro passar o caminho completo para o executável do cmd.exe
        # e o caminho para o arquivo .bat como um argumento, ou simplesmente chamar o arquivo .bat
        # diretamente se ele estiver no PATH ou no diretório atual.
        
        # Opção 1: Chamar diretamente (se o .bat estiver no PATH ou diretório atual)
        print(caminho_arquivo_bat)
        
        #subprocess.run(caminho_arquivo_bat, shell=True, check=True)
        
        # Opção 2: Usar cmd.exe e Call (mais explícito, se necessário)
        subprocess.run(f"call {caminho_arquivo_bat}", shell=True, check=True)

        session.flash = f"Arquivo .bat executado com sucesso!"
        return dict(mensagem="O sistema está sendo atualizado. Clique em voltar e aguarde.")
    except subprocess.CalledProcessError as e:
        session.flash = f"Erro ao executar o arquivo .bat: {e}"
    except FileNotFoundError:
        session.flash = f"Arquivo .bat não encontrado em: {caminho_arquivo_bat}"

