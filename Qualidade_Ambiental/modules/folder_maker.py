#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---    SCRIPT DE CRIAÇÂO DE    ---#
#---         PASTAS             ---#
#==================================#

'''
    "(C)" Carlos Augusto Locatelli Júnior 2022
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; Consulte <https://www.gnu.org/licenses/>.
'''

from os import mkdir
from pathlib import Path
import re
import time


pattern = r'^\d+_'

def pega_numeracao_da_pasta(caminho_da_pasta, protocolo) -> str:
    '''Função para achar o próximo número de pasta numerada na raiz indicada no caminho'''
    try:
        with open(Path(caminho_da_pasta, 'ultimo_num.txt'), 'r') as ultimonum:
            num = ultimonum.read()
            print(f"Lendo numero da pasta do arquivo: {num}")
            ultimonum.close()
        with open(Path(caminho_da_pasta, 'ultimo_num.txt'), 'w') as proxnum:
            print(f"Tentando atualizar o numero da pasta do arquivo: {int(num)+1}")

            proxnum.write(str(int(num)+1))
            proxnum.close()
        return str(int(num) + 1)

    except:
        numpasta = 0
        num_autal = 0
        ini = time.time()

        for dir in Path(caminho_da_pasta).rglob('*\\'):
            if re.match(pattern, dir.name):
                num_autal = int(re.match(pattern, dir.name).group()[:-1])
                if num_autal > numpasta:
                    numpasta = num_autal

        fim = time.time()
        print(f"tempo p numerar: {fim-ini} s")

    return str(numpasta+1)



def pasta_existe(caminho_da_pasta, protocolo, lista_de_pasta):
    '''Verifica se no caminho informado e um nivel de subpastas a dentro existe uma pasta com o protocolo no nome.'''

    proto_pattern = r'-(\d){2}' if '-' in protocolo else r'^(\d){4}'
    ano_proto = re.search(proto_pattern, protocolo).group()
    ano_proto = ano_proto.replace('-', '20')

    for pasta in lista_de_pasta:
        if pasta[0] in ['B','D']:
            for dir in Path(caminho_da_pasta, pasta, ano_proto).glob('*\\'):
                if protocolo in dir.name:
                    return f"para o protoc. {protocolo} em {dir.absolute()}"
        else:
            for dir in Path(caminho_da_pasta, pasta).glob('*\\'):
                if protocolo in dir.name:
                    return f"para o protoc. {protocolo} em {dir.absolute()}"

    return False



def criar_pasta_compartilhada(dados, caminho_da_pasta, lista_de_pasta ,numerar=False):

    gerador = dados.get('nome') or dados.get('Nome') or dados.get('dados_gerador').get('Nome') or \
     dados.get('dados_gerador').get('nome') or 'Desconhecido'
    protocolo = dados.get('protocolo') or dados.get('Protocolo')

    ini = time.time()
    pasta_existente = pasta_existe(caminho_da_pasta, protocolo, lista_de_pasta)
    fim = time.time()
    print(f"tempo p verificar se existe a pasta: {fim-ini} s")

    if __name__ == "__main__":
        op_criar_pasta = str(input('Deseja criar a pasta: Digite(s/n): '))
        if op_criar_pasta == 's':
            if pasta_existente:
                print(f'Já existe a pasta {pasta_existente}')
            else:
                try:
                    if numerar:
                        mkdir('F:\{}\{}_{}_{}'.format(str(caminho_da_pasta), pega_numeracao_da_pasta(caminho_da_pasta,protocolo),
                                                        str(gerador.replace('/','-')).upper(), protocolo))
                    else:
                        mkdir('F:\{}\{}_{}'.format(str(caminho_da_pasta),str(gerador.replace('/','-')).upper(), protocolo))

                    print('Pasta criada! {}_{} '.format(str(gerador).upper(), protocolo))
                except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
    else:
        if pasta_existente:
            print (f'Já existe a pasta {pasta_existente}')
            return 'Já existe pasta para este protocolo!'
        else:
            try:
                if numerar:
                    mkdir('{}\{}_{}_{}'.format(str(caminho_da_pasta), str(pega_numeracao_da_pasta(str(caminho_da_pasta), protocolo)),
                                                str(gerador.replace('/','-')).upper(), protocolo))
                else:
                    mkdir('{}\{}_{}'.format(str(caminho_da_pasta),str(gerador.replace('/','-')).upper(), protocolo))

                print('Pasta criada! {}_{} '.format(str(gerador).upper(), protocolo))

            except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
                    return e