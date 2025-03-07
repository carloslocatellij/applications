#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---    SCRIPT DE WEBSCRAP      ---#
#---      SIGM ONLINE           ---#
#==================================#

'''
    "(C)" Carlos Augusto Locatelli Júnior 2024
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; Consulte <https://www.gnu.org/licenses/>.
'''

from bs4 import BeautifulSoup # type: ignore
import re
import urllib.request
import csv
import folder_maker
from pathlib import Path
from typing import List

def intro():
    '''Apenas uma introdução em modo texto'''

    print('''#==================================#
#---    SCRIPT DE WEBSCRAP      ---#
#---      SIGM AMB GEST MUN     ---#
#=======================+++========#''')
    print('')
    return ''

def pega_conteudo_html(url: str = '' )-> object:
    '''Raspa dados da página web especificada pela URL.

    Parâmetro: url (str): URL da página web a ser raspada.
    Retorna: Objeto BeautifulSoup.
    '''
    dados = None
    try:
        html = urllib.request.urlopen(url)
    except FileNotFoundError:
        print ('Falha ao encontrar o arquivo')
    except Exception as e:
        print (f'Falha ao abrir o arquivo: {e}')
    else:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            dados = soup
        except TypeError:
            print ('Não é o tipo de arquivo correto')
        except Exception as e:
            print (f'Erro:: {e}')

    return dados


def captura_dados_de_processos(obj_dados, idtable='tablePendentes') -> dict:
    '''Recebe um objeto do tipo BeautifulSoup com as tags html preparadas.
    Retorna uma lista com um dicionário de dados para cada processo. Em caso de erro, retorna None  '''
    lista_d_pgrs = []
    try:
        tab_d_pgrs = obj_dados.find_all('table', id=idtable)
    except Exception as e:
        print(f'Erro ao encontrar a tabela: {id} no objeto: {e}')
    try:
        tab_d_pgrs = BeautifulSoup(str(tab_d_pgrs), 'html.parser')
    except Exception as e:
        print(f'Erro ao parsear o html da tabela: {e}')
    finally:
        try:
            tab_d_pgrs.find_all('a', class_= "verConsulta" )
            for a in tab_d_pgrs.find_all('a', class_= "verConsulta" ):
                dict_d_process = {}
                indice_pessoa = -4 if a.findParent().findNextSiblings()[-1].get_text() != '' else -5
                indice_serv = 1
                dados_obs = a.findParent().findNextSiblings()[indice_pessoa - 1].get_text().replace('\r','').split('\n')[4:]
                dict_d_process['protocolo'] = a.get_text()
                dict_d_process['servico'] = a.findParent().findNextSiblings()[indice_serv].get_text()
                dict_d_process['dados_obs'] = {val.split(':')[0].strip() : val.split(':')[1].strip() for val in dados_obs if len(val.split(':')) >1}
                dict_d_process['cpf'] = a.findParent().findNextSiblings()[indice_pessoa].get_text().split(' - ')[0]
                dict_d_process['nome'] = a.findParent().findNextSiblings()[indice_pessoa].get_text().split(' - ')[1]
                dict_d_process['email'] = a.findParent().findNextSiblings()[indice_pessoa].get_text().split(' - ')[2]

                lista_d_pgrs.append(dict_d_process)
        except UnboundLocalError as ue:
            print("Elemento não encontrado.")
        except:
            print('O elemento aparentemente não existe ou não tem a tag <a class="verConsulta>')
        return lista_d_pgrs


def cria_csv_c_dados(lista_de_dados, caminho_para_o_arq_csv):
    '''Recebe: uma lista de dicionários, um por processo, contentdo os dados do respectivo processo.
    Cria um arquivo csv com os dados recebidos'''

# o arquivo csv deve ter o nome com data e hora realizado
    arq_csv = Path(Path.home(), caminho_para_o_arq_csv, 'test_gest.scv')

    with open(arq_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        for process in lista_de_dados:
            for val in process.values():
                writer.writerow(val)
        f.close()
