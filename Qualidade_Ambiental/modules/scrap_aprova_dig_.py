#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================#
#---    SCRIPT DE WEBSCRAP      ---#
#---      APROVA DIGITAL        ---#
#==================================#

from bs4 import BeautifulSoup
import os
import re
import urllib.request
import csv # Objetivo: Automatizar geração de planilha com dados necessários do Aprova Digital
#import asyncio - TODO - Converter em assincrono



def intro():
    '''Apenas uma introdução em modo texto'''

    print('''#==================================#
#---    SCRIPT DE WEBSCRAP      ---#
#---      APROVA DIGITAL        ---#
#==================================#''')
    print('')
    return ''


def pega_numeracao_da_pasta():
    '''Função para achar o próximo número de pasta numerada na raiz indicada no caminho abaixo'''

    caminho_pasta_hab = 'F:\Qualidade Ambiental\HABITE-SE 2022 - Digital'
    pastas_de_hab = []
    pattern = '^\d+'
    for dir in os.listdir(caminho_pasta_hab):
        if os.path.isdir(os.path.join(caminho_pasta_hab,dir)):
            for d in os.listdir(os.path.join(caminho_pasta_hab,dir)):
                if os.path.isdir(os.path.join(caminho_pasta_hab,dir, d)):
                    pastas_de_hab.append(int(re.findall(pattern,d)[0] ) if len(re.findall(pattern,d)) > 0 else 0)

    return str(max(pastas_de_hab)+1)



    '''
    Modulo de raspagem

Infelizmente, devido ao proxy da empro bloquear o requests ou urllib de acessar a web, 
o scrap deve ser feito em página.html salva no computador local (a ser passada para o servidor processar)
Portanto, as funcionalidades acamba sendo limitadas. No entanto o código ainda pode automatizar diversos processo de obtenção de dados.

urlexemplo =  str(input('digite o caminho e nome do arquivo html do dof: ')) #"file:///C:/Users/clocatelli/Documents/DOFS/consulta_dof.php.htm"
raspa_aprova(urlexemplo)

return ['dados do proprietário da obra e dados da obra']
'''

def raspa_aprova(url):
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
        except TypeError:
            print ('Não é o tipo de arquivo correto')
            print('')
        except Exception as e:
            print (f'Erro:: {e}')
            print('')
    
    dados = {}
        
    try:
        protocolo = soup.find(mattooltip="Este é o código de identificação deste processo")
        try:
            protocolo = protocolo.getText()
        except AttributeError as ae:
            print (f'Protocolo não encontrado na página fornecida: {ae}')
            print('')

        try:
            Nome= soup.find(text=re.compile('Nome do Proprietário'))
            CPF = soup.find(text=re.compile('^CPF$'))
            CNPJ = soup.find(text=re.compile('^CNPJ$'))
            email = soup.find(text=re.compile('E-mail do Proprietário'))
            tel = soup.find(text=re.compile('Telefone Fixo ou Celular do Proprietário'))

            dados_gerador = dict(
                        Nome = Nome.parent.parent.next_sibling.get_text() if Nome == 'Nome do Proprietário' else '-',
                        CPF = CPF.parent.parent.next_sibling.get_text() if CPF == 'CPF' else '',
                        CNPJ = CNPJ.parent.parent.next_sibling.get_text() if CNPJ == 'CNPJ' else '',
                        email = email.parent.parent.next_sibling.get_text() if email else '-',
                        tel = ''.join(re.findall('\d+', tel.parent.parent.next_sibling.get_text())) if tel else '-'
            )
        except AttributeError as ae:
            print (f'Erro ao atribuir dados do Gerador: {ae}')
            print('')

        try:

            CadMunicipal = soup.find(text=re.compile(r'^Cadastro Imobiliário$'))
            Logradouro = soup.find(text=re.compile(r'^Logradouro da Obra$'))
            Lote = soup.find(text=re.compile(r'^Lote/Data da Obra$'))
            Quadra = soup.find(text=re.compile(r'^Quadra/Quarteirão da Obra$'))
            Num = soup.find(text=re.compile(r'^Número Predial Principal da Obra$'))
            Compl =  soup.find(text=re.compile(r'^Endereço Complementar da Obra$'))
            Bairro = soup.find(text=re.compile(r'^Loteamento/Bairro da Obra$'))
            Cep = soup.find(text=re.compile(r'^CEP da Obra$'))
            endereco_obra = dict(
                CadMunicipal = CadMunicipal.parent.parent.next_sibling.get_text().replace('.','').replace('/','') if CadMunicipal else print('sem Cad. Municipal'),
                Logradouro = Logradouro.parent.parent.next_sibling.get_text() if Logradouro else print('sem Logradouro'),
                Lote = re.sub('(?![A-z])(?!\d)(?! )(?!,)', '', Lote.parent.parent.next_sibling.get_text().strip().replace(' ',',')) if Lote else '',
                Quadra = re.sub('(?![A-z])(?!\d)(?! )(?!,)', '',Quadra.parent.parent.next_sibling.get_text().strip().replace(' ','')) if Quadra else '',
                Num = ''.join(re.findall('\d+',Num.parent.parent.next_sibling.get_text().replace('-','0'))) if Num else '0',
                Compl = Compl.parent.parent.next_sibling.get_text() if Compl else '',
                Bairro = Bairro.parent.parent.next_sibling.get_text() if Bairro else print('sem Bairro'),
                Cep = Cep.parent.parent.next_sibling.get_text().replace('-','') if Cep else print('sem Cep.'))

        except AttributeError as ae:
            print ('Erro ao atribuir dados do endereço da obra: {ae}')
            print('')
        
        try:
            area_do_terreno = soup.find(text=re.compile(r'^Área do Terreno$'))
            area_existente = soup.find(text=re.compile(r'Total de Área Existente \(Aprovada com Alvará e Habite-se\)'))
            area_construida_final = soup.find(text=re.compile(r'^Área Total Final da Edificação$'))
            area_demolir = soup.find(text=re.compile(r'^Total de Área a Demolir$'))
            finalidade = soup.find(text=re.compile(r'^Tipo de Uso$'))
            pavimentos_sup = soup.find(text=re.compile(r'^Quantidade de Pavimentos$'))
            pavimentos_sub = soup.find(text=re.compile(r'^Quantidade de Subsolos$'))
            alvara= soup.find(text=re.compile(r'^Número do Alvará aprovado no modo físico'))
            data_alvara = soup.find(text=re.compile(r'^Data de Expedição do Alvará$'))
            data_alvara = data_alvara.parent.parent.next_sibling.get_text()
            data_alvara = data_alvara if re.match('\d{8}', data_alvara.replace('/','').replace('-','')) else ''

            dados_obra = dict(
            alvara = ''.join(re.findall('\d+',alvara.parent.parent.next_sibling.get_text())) if alvara else '',
            data_alvara = data_alvara,
            area_do_terreno = area_do_terreno.parent.parent.next_sibling.get_text().replace(u'm²','').replace(',','.').replace(' ','') if area_do_terreno else '',
            area_existente = area_existente.parent.parent.next_sibling.get_text().replace(u'm²','').replace(',','.').replace(' ','') if area_existente else '',
            area_construida_final = area_construida_final.parent.parent.next_sibling.get_text().replace(u'm²','').replace(',','.').replace(' ','') if area_construida_final else '',
            area_demolir = area_demolir.parent.parent.next_sibling.get_text().replace(u'm²','').replace(',','.').replace(' ','') if area_demolir else '',
            finalidade = finalidade.parent.parent.next_sibling.get_text().upper() if finalidade else print('sem finalidade.'),
            pavimentos_sup = pavimentos_sup.parent.parent.next_sibling.get_text().replace(u'Unidade(s)','') if pavimentos_sup else print('sem pavimentos_sup.'),
            pavimentos_sub = pavimentos_sub.parent.parent.next_sibling.get_text().replace(u'Unidade(s)','') if pavimentos_sub else print('sem pavimentos_sub.'),)

        except AttributeError as ae:
            print (f'Erro ao atribuir dados de área da obra::   {ae}')
            print('')

        try:
            exigencia = soup.find(text=re.compile('Consta exigência, no alvará, da utilização de madeira legalizada\?'))
            material_cobertura = soup.find(text=re.compile(r'^Material utilizado:$'))
            declara = soup.find(text=re.compile(r'Declaro,\r\n para fins de Habite-se'))
            cobertura = dict(
            exigencia = exigencia.parent.parent.next_sibling.getText() if exigencia else print('sem dado da exigência de DOF.'),
            material_cobertura = material_cobertura.parent.parent.next_sibling.get_text() if material_cobertura else print('sem dado de material_cobertura.'),
            declara = declara.parent.get_text() if declara else 'Sem declaração',
            declarou = declara.parent.parent.next_sibling.get_text() if declara else ''
            )
        
        except AttributeError as ae:
            print (f'Erro ao atribuir dados da cobertura da obra {ae}')
            print('')

        dados = {'protocolo': protocolo, 'dados_gerador': dados_gerador, 'endereco_obra':endereco_obra, 'dados_obra':dados_obra, 'cobertura':cobertura}


    except IndexError: # Interrompe o script
        return 'Arquivo não encontrado'
    except AttributeError:
        return 'Tag Html não encontrada' # Interrompe o script
    else:
        return 'Ocorreu um erro' # Interrompe o script

    finally: # Continua o script - tudo certo aqui
        print('-'*50)
        print(dados)
        print('-'*50)
        print('')
        #breakpoint()
        return dados

def criar_pasta_compartilhada(dados):
    dados_gerador = dados['dados_gerador']
    protocolo = dados['protocolo']
    caminho_pasta_hab = 'F:\Qualidade Ambiental\HABITE-SE 2022 - Digital'

    protocolo_existe = False
    for dir in os.listdir(caminho_pasta_hab):
        if os.path.isdir(os.path.join(caminho_pasta_hab,dir)):
            for d in os.listdir(os.path.join(caminho_pasta_hab,dir)):
                if protocolo in str(d):
                    protocolo_existe = True     
                

    if __name__ == "__main__": 
        op_criar_pasta = str(input('Deseja criar a pasta: Digite(s/n): '))
        if op_criar_pasta == 's':
            if protocolo_existe:
                print(f'Já existe pasta para o protocolo {protocolo}')
            else:
                try:
                    os.mkdir('F:\Qualidade Ambiental\HABITE-SE 2022 - Digital\A - RECEPÇÃO - AVALIAÇÃO\{}_{}_{}'.format(pega_numeracao_da_pasta(),str(dados_gerador['Nome'].replace('/','-')).upper(), protocolo))
                    print('Pasta criada! {}_{} '.format(str(dados_gerador['Nome']).upper(), protocolo))
                except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
    else:
        if protocolo_existe:
                print (f'Já existe pasta para este protocolo:: {protocolo}')
                return 'Já existe pasta para este protocolo!'
        else:
            try:
                os.mkdir('F:\Qualidade Ambiental\HABITE-SE 2022 - Digital\A - RECEPÇÃO - AVALIAÇÃO\{}_{}_{}'.format(pega_numeracao_da_pasta(),str(dados_gerador['Nome'].replace('/','-')).upper(), protocolo))
                print('Pasta criada! {}_{} '.format(str(dados_gerador['Nome']).upper(), protocolo))
            except Exception as e:
                    print (f'Ocorreu um erro ao criar a pasta:: {e}')
                    return e               


def criar_atualizar_arq_de_dados(dados):
    pasta_do_proc = ''
    caminho_pasta_hab = 'F:\Qualidade Ambiental\HABITE-SE 2022 - Digital'


    for dir in os.listdir(caminho_pasta_hab):
        if os.path.isdir(os.path.join(caminho_pasta_hab,dir)):
            for d in os.listdir(os.path.join(caminho_pasta_hab,dir)):
                if dados['protocolo'] in str(d):
                    pasta_do_proc = os.path.join(dir, str(d)) 
    
    try:
        with open('F:\Qualidade Ambiental\HABITE-SE 2022 - Digital\{}\dados.csv'.format(pasta_do_proc), 'w', newline='') as f:
            writer = csv.writer(f)
            for k, v in dados.items():
                if k != 'protocolo':
                    writer.writerow(v.keys())
                    writer.writerow(v.values())
            f.close()

    except Exception as e:
        print(f'Erro ao criar/atualizar arquivo de dados:: {e}') # Arquivo de dados não criado aqui   


if __name__ == "__main__":
    print(intro())

    while True:

        opt = str(input('continuar: Digite(s/n): '))
        
        url = str(input('digite o caminho e nome do arquivo html do dof: '))    
        if opt == 'n': break

        dados = raspa_aprova(url)
        criar_pasta_compartilhada(dados)
        criar_atualizar_arq_de_dados(dados)
 

