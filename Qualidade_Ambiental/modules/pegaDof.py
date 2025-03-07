
#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---            DOF           -----#
#==================================#
'''
    "(C)" Carlos Augusto Locatelli Júnior 2022
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA; Consulte <https://www.gnu.org/licenses/>.

'''


import unicodedata
import urllib
from bs4 import BeautifulSoup
import re


#urlexemplo =  "file:///C:\\Users\\clocatelli\\Downloads\\dof\\Documento de Origem Florestal - Ibama.htm"

def intro():
    print('''#=============================#

#--           DOF            -#

#=============================#''')

def pegaquali(url):
    #req = urllib2.Request(url)
    html = urllib.request.urlopen(url)
    html = html.read()
    soup = BeautifulSoup(html, 'html.parser')
    def ndof():
        try:
            cod = soup.find(id='codigo_controle').attrs.get('value')
            if not ' ' in cod:
                return f'{str(cod[0:4])} {str(cod[4:8])} {str(cod[8:12])} {str(cod[12:])}'
            else:
                return cod

        except Exception as e:
            print('Erro: {e}')

    try:
        #dados = soup.find('table', id='produtos').find_all('td')
        dados = soup.find('table', id='produtos').find('table', border='1').find_all('span')
        blinkdof = ndof()
    except IndexError:
        return 'Não encontrado'
    finally:
        itens = [str(x).replace('<span>','').replace('</span>','') for x in dados]
        listDof = []
        itensDof = {}
        Dofitens =  []
        for i in range(int(len(itens)/7)):
            itensDof['Nº'] = itens[i*7]
            itensDof['Espécie'] = itens[1+(i*7)]
            itensDof['Nome Popular'] = itens[2+(i*7)]
            itensDof['Produto'] = itens[3+(i*7)]
            itensDof['Quantidade'] = itens[4+(i*7)]
            itensDof['Unidade'] = itens[5+(i*7)]
            itensDof['Valor Item'] = itens[6+(i*7)]
            Dofitens.append(itensDof)
            itensDof = {}


        print(blinkdof)
        #print(Dofitens)

        return (Dofitens , blinkdof)

if __name__ == "__main__":
    print(intro())

    while True:
        opt = str(input('continuar: Digite(s/n): '))
        if opt == 'n': break
        url = str(input('digite o caminho e nome do arquivo html do dof: '))
        print(pegaquali(url))
