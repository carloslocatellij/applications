#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---    SCRIPT DE WEBSCRAP      ---#
#---      DOF    DIGITAL        ---#
#==================================#

'''
    "(C)" Carlos Augusto Locatelli Júnior 2024
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; Consulte <https://www.gnu.org/licenses/>.
'''


from bs4 import BeautifulSoup # type: ignore
import os
import re
import urllib.request
from pathlib import Path


def raspa_dof(url):
    try:
        html = urllib.request.urlopen(url)
    except FileNotFoundError:
        print ('Falha ao encontrar o arquivo')
        print('')
    except Exception as e:
        print (f'Falha ao abrir o arquivo: {e}')
        print('')
    else:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except TypeError:
            print ('Não é o tipo de arquivo correto')
            print('')
        except Exception as e:
            print (f'Erro:: {e}')
            print('')

url = Path('Abertura do Protocolo - CIDADÃO.htm')
url = url.absolute().as_uri()

soup = raspa_dof(url)



# dados = soup.find('textarea').get_text()
# dados = dados.replace('\r','').split('\n')[4:]

# dic_dados = {val.split(':')[0].strip() : val.split(':')[1].strip() for val in dados if len(val.split(':')) >1}

# protocolo_pgr = dic_dados['PROTOCOLO DE PGRCC APROVADO']
# gerador = dados.split('\n')[5].split(':')[1].strip()
# resp_tec = dados.split('\n')[6].split(':')[1].strip()
# conselho = dados.split('\n')[7].split(':')[1].strip()
# cad_mun = dados.split('\n')[8].split(':')[1].strip()
# alvara = dados.split('\n')[9].split(':')[1].strip()
# data_alvara = dados.split('\n')[10].split(':')[1].strip()