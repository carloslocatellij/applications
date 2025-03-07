#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---          Geradocs          ---#
#---    Gerador de DOCUMENTOS   ---#
#---       AUTOMATIZADO         ---#
#==================================#

# %%
'''
    "(C)" Carlos Augusto Locatelli Júnior 2023
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da
    GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA;
    Consulte <https://www.gnu.org/licenses/>.

'''

# %%
import zipfile
import os
from pathlib import Path
from xml.dom.minidom import parseString
import tempfile
pasta_temporaria = tempfile.mkdtemp(prefix='criaodttmpd') #Cria uma pasta temporária

# %% # para fins de teste
#if __name__ != '__main__':
#   pasta = os.getcwd()
#   arquivo_mod = Path(pasta, Path("modelo2022_1.odt"))# para fins de teste

# %%
def ler_o_arq_modelo(arquivo_mod):
    '''recebe o arquivo de modelo como entrada e retorna o conteúdo do arquivo "content.xml".'''

    with zipfile.ZipFile(arquivo_mod, 'r') as modelo:
        conteudo = modelo.read('content.xml')
    modelo.close()
    return conteudo

# %%
def pegar_campos_do_modelo(conteudo):
    '''recebe o conteúdo do arquivo "content.xml" como entrada e retorna a lista dos campos que
     precisam ser preenchidos.'''

    dom = parseString(conteudo)
    vars = dom.getElementsByTagName('text:variable-set')
    return [val.childNodes[0].data for val in vars]

# %%
def preencher_conteudo(conteudo, entradas_dos_campos):
    '''recebe o conteúdo do arquivo "content.xml" e um dicionário com as informações inseridas pelo usuário e
         retorna o conteúdo do arquivo preenchido.'''
    try:
        conteudot = conteudo.decode('utf-8')
    except Exception as e:
        print('Testo simples')
        conteudot = conteudo

    return f'{conteudot.format(**entradas_dos_campos)}'.replace('&', "&#38;")


# %%
def cria_arquivo_novo(path_arquivo_mod, nome_do_arq='Novo_arquivo'):
    ''' recebe o caminho do diretório onde será criado o novo arquivo e um nome para o novo arquivo, cria um
    arquivo vazio com o nome definido e retorna o caminho completo do arquivo.'''
    arquivo_novo = Path(path_arquivo_mod, nome_do_arq+ '.odt')
    with open(arquivo_novo , 'w') as arq:
        arq.close()
    return arquivo_novo

# %%
def transferencia_de_esqueleto_do_modelo(arquivo_mod, pasta_arq_mod, campo_p_nome):
    '''recebe o arquivo de modelo, o caminho do diretório onde será criado o novo arquivo e o nome do campo que
     identifica o novo arquivo, extrai o conteúdo do arquivo de modelo para uma pasta temporária, cria um novo
     arquivo com o nome definido e transfere o conteúdo da pasta temporária para o novo arquivo, e retorna o
     caminho completo do novo arquivo.'''

    with zipfile.ZipFile(arquivo_mod, 'r') as zip:
        lst_arqvs = zip.infolist()
        for arq in lst_arqvs:
            if arq.filename != 'content.xml':
                zip.extract(arq, pasta_temporaria)
    with zipfile.ZipFile(str(pasta_arq_mod) + f'\\{campo_p_nome}.odt', 'a') as zipfinal:
        for file in Path(pasta_temporaria).iterdir():
            if file.is_dir():
                for root, dirs, files in os.walk(file):
                    for f in files:
                        basedir = os.path.dirname(pasta_temporaria)
                        dirname = root.replace(basedir, '').replace('\\'+Path(pasta_temporaria).name, '')
                        tmpdir = Path(pasta_temporaria).name
                        if Path(f).is_dir():
                            zipfinal.write(Path(pasta_temporaria, f), os.path.join(dirname , f))
                        else:
                            zipfinal.write(Path(root, f), arcname=Path(dirname,f))
            else:
                zipfinal.write(file, file.name)

        zipfinal.close()

    return Path(zipfinal.filename)


# %%
def preencher_arquivo_novo(campo_p_nome: str, conteudo: str, entradas_dos_campos: dict, arquivo_mod: Path) -> None:
    '''Recebe: o Nome do campo que identifica o novo arquivo, o Conteúdo do arquivo preenchido,
     o Dicionário com as informações inseridas pelo usuário e o Caminho completo do arquivo de
     modelo, preenche o arquivo de modelo com as informações inseridas pelo usuário e cria um
     novo arquivo com o nome definido.'''

    path_arquivo_mod = arquivo_mod.parent.absolute()
    arquivo_a_ser_criado = transferencia_de_esqueleto_do_modelo(arquivo_mod, path_arquivo_mod, campo_p_nome)
    with zipfile.ZipFile(arquivo_a_ser_criado, 'a') as arquivo_a_ser_criado:
        #content = zip.getinfo('content.xml')
        #with zip.open( content, 'w') as contentxml:
        arquivo_a_ser_criado.writestr('content.xml' ,preencher_conteudo(conteudo, entradas_dos_campos).encode())

    return arquivo_mod.parts[-1]
