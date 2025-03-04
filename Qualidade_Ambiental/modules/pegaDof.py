#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---            DOF           -----#
#==================================#

import unicodedata
import urllib
from bs4 import BeautifulSoup
import re


#urlexemplo =  "file:///C:/Users/clocatelli/Documents/DOFS/consulta_dof.php.htm"


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
        iddof = ''
        for i in range(1,5):
            iddof = iddof + str(soup.find('input', id=f'cod_controle{i}').get('value'))
            iddof = iddof + ' ' if i < 4 else iddof
        return iddof

    try:
        dados = soup.find('table', id='table_gride_itens').find_all('td')

        blinkdof = ndof()
    except IndexError:
        return 'Não encontrado'
    else:
        itens = re.split('<span><center>.</center></span></td>,',str(dados))
        listDof = []
        itensDof = {}
        Dofitens =  []
        for x in itens[1:]:
            pattern_letra_maiuscula = re.compile('[a-z]')
            x = BeautifulSoup(x, 'html.parser').get_text()
            listDof.append(x.encode('utf-8', 'ignore').decode('ascii', 'ignore'))
            for i in listDof:
                
                tem_virg_no_produto = False if re.match(pattern_letra_maiuscula, i.split(',')[1][1]) else True
                itensDof['Nº'] = listDof.index(i)
                itensDof['Produto'] = i.split(',')[0] if tem_virg_no_produto else str(i.split(',')[0] + i.split(',')[1])
                itensDof['Espécie'] = i.split(',')[1] if tem_virg_no_produto else  i.split(',')[2]
                itensDof['Nome Popular'] = i.split(',')[2] if tem_virg_no_produto else  i.split(',')[3]
                qtd = str(i.split(',')[3]+'.'+i.split(',')[4]) if tem_virg_no_produto else  str(i.split(',')[4]+'.'+i.split(',')[5])
                itensDof['Quantidade'] = float(qtd)
                itensDof['Unidade'] = i.split(',')[5].replace('.','').replace(' ','')  if tem_virg_no_produto else  i.split(',')[6]
                itensDof['Valor Item'] = str((i.split(',')[6].replace('.','').replace(' ','')+','+i.split(',')[7].replace(']','')))  if tem_virg_no_produto else  str((i.split(',')[7].replace('.','').replace(' ','')+','+i.split(',')[8].replace(']','')))
            Dofitens.append(itensDof)
            itensDof = {}
        pattern = '\d'
        blinkdof = re.findall(pattern, str(blinkdof))
        iddof = ''
        for c in blinkdof:
            if len(iddof) == 4 or len(iddof) == 9 or  len(iddof) == 14:
                iddof += ' ' + c
            else:
                iddof += c

        #iddof = [c for c in blinkdof if c.isdigit()]
        #iddof = iddof.to_str()
        
        print(iddof)
        #print(Dofitens)
        
        return (Dofitens , iddof)

if __name__ == "__main__":
    print(intro())

    while True:
        opt = str(input('continuar: Digite(s/n): '))
        if opt == 'n': break
        url = str(input('digite o caminho e nome do arquivo html do dof: '))
        print(pegaquali(url))
