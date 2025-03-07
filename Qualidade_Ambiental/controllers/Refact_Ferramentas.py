if 0==1:  # Este namespace serve apenas para a IDE enchergar e trabalhar com os itens abaixo
    from gluon import *
    from gluon import db, SQLFORM, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, redirect, URL, FORM_CPF
    from gluon import XML, a_db, db, auth, Auth, Field, buscador, analise_de_residuos_projedatos, geradocspy, scrap_aprova_dig_
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T

from os import remove, path
from re import sub
from datetime import datetime
from gluon.contrib.pymysql.err import IntegrityError
from pathlib import Path
from openpyxl import load_workbook # type: ignore
from scrap_aprova_dig_ import raspa_aprova # type: ignore
from folder_maker import criar_pasta_compartilhada # type: ignore
from gluon import SQLFORM

def processar_arquivo_html(arquivo):
    try:
        dados_do_processo = raspa_aprova('file:///{}/{}'.format(str(path.join(request.folder, 'uploads')), arquivo))
        print('Dados obtidos apartir do arquivo!')
        return dados_do_processo
    except Exception as e:
        session.flash = f'Erro ao processar o arquivo enviado: {e}'
        return None


def remover_arquivo(arquivo):
    try:
        remove('{}/{}'.format(str(path.join(request.folder, 'uploads')), arquivo))
        print('Arquivo removido da memória.')
    except OSError as e:
        session.flash = f"Erro na remoção do arquivo do server: Error: {e.strerror} : \
        {path.join(request.folder, 'uploads')} : {arquivo}"


def atualizar_planilha_control(dados_do_processo):
    planilha_control = Path(pasta_qualidade, 'DOCUMENTOS', 'Controle de Processos.xlsx') # type: ignore
    print('Planilha encontrada')
    wb = load_workbook(planilha_control, rich_text=True)
    print('Planilha aberta')
    ws = wb.active
    print('Planilha ativada')
    hj = datetime.today()
    ws.append([hj.strftime('%d/%m/%Y') , dados_do_processo['protocolo'], dados_do_processo['dados_gerador']['Nome'], 1,
                1 if float(dados_do_processo['dados_obra']['area_construida_final']) > 400.00 else 0, 0,
                        dados_do_processo['dados_obra']['area_construida_final']])
    try:
        print('Dados inseridos')
        wb.save(planilha_control)
    except PermissionError as pe:
        print('Planilha bloqueada')
        response.flash = 'Planilha de controle aberta. Feche e repita o procedimento.'
        redirect(URL(c='static', f='423.html' ))
    print('Planilha de processos atualizada.')


def buscar_ou_inserir_pessoa(dados_gerador):
    cnpj = dados_gerador.get('CNPJ')
    cpf = dados_gerador.get('CPF') or dados_gerador.get('cpf')
    nome = dados_gerador.get('Nome') or dados_gerador.get('nome')
    telefone = dados_gerador.get('tel') or ''
    email = dados_gerador.get('email') or ''

    if cnpj:
        pessoa = db.executesql(f"SELECT Id, Nome FROM Pessoas WHERE Pessoas.CNPJ = '{cnpj}' LIMIT 1;") or \
        db.executesql(f"SELECT Id, Nome FROM Pessoas WHERE Pessoas.CNPJ = '{cnpj.replace('.','').replace('/','').replace('-','')}' LIMIT 1;") or \
        db.executesql(f"SELECT Id, Nome FROM Pessoas WHERE Pessoas.CNPJ = '{'{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}'.format(*cnpj)}' LIMIT 1;")
    elif cpf:
        pessoa = db.executesql(f"SELECT Id, Nome FROM Pessoas WHERE Pessoas.CPF = '{cpf}' LIMIT 1;")
    else:
        pessoa = None

    if pessoa:
        print(f'Pessoa ::{pessoa[0][1]}:: encontrada no banco de dados!')
        return pessoa[0][0]
    else:
        pessoa = db.Pessoas.validate_and_insert(Nome=nome, CNPJ=cnpj,
                                                CPF=cpf.replace('.','').replace('-','')if cpf else None, Telefone=telefone,
                                                Email=email)
        db.commit()

        print(f'Pessoa :::{pessoa.id}: inserida no banco de dados!')
        return pessoa.id

def buscar_ou_inserir_processo(protocolo, id_pessoa):
    processo = db.executesql(f"SELECT Id FROM Processos WHERE Processos.protocolo = '{protocolo}' LIMIT 1 ;")
    if processo:
        print(f'Processo ::{protocolo}:: encontrado no banco de dados!')
        return processo[0][0]
    else:
        processo = db.Processos.validate_and_insert(Protocolo=protocolo,
                                                    IdPessoa=id_pessoa,
                                                    IdDpto='1024412',
                                                    IdTipo=3)
        db.commit()
        print(f'Processo ::{protocolo}:: inserido no banco de dados!')
        return processo.id

def buscar_ou_inserir_logradouro(endereco_obra):
    logradouro = db.executesql(f"SELECT Id, Logradouro FROM Logradouros WHERE Logradouros.Cep = '{endereco_obra['Cep']}' LIMIT 1 ;")
    if logradouro:
        print(f'Logradouro ::{logradouro[0][1]}:: encontrado no banco de dados!')
        return logradouro[0][0]
    else:
        nomebairro = sub(' - .*$', '' , endereco_obra['Bairro'])
        palavra_chave_bairro = ' '.join(nomebairro.split()[ int(len(nomebairro.split())//2): int(len(nomebairro.split())/2+2) ])
        try:
            idbairro = db.executesql(f"SELECT Bairros.Id, Bairros.Bairro FROM Bairros WHERE Bairros.Bairro LIKE '%{palavra_chave_bairro}%';")
            idbairro[0][0]
            if idbairro:
                print(f'Bairro ::{idbairro[0][0]}:: encontrado no banco de dados!')
            else:
                print("Bairro não encontrado")
                bairro_id = db.Bairros.validade_and_insert(
                    Bairro = endereco_obra['Bairro'],
                    Cor = '', IdCidade= 9999
                    )

        except Exception as e:
                    session.flash = "Erro ao cadastrar Bairro"
                    print(e)
                    print('Redirecionando para form de Logradouros')
                    redirect(URL('default', 'Logradouros'))
        denom = endereco_obra['Logradouro'].split()
        if denom == 'R' or denom[0] == 'r':
            denomin = 'RUA'
        elif denom == "AV" or denom == 'Av' or denom == 'av':
            denomin = 'AVENIDA'
        else:
            denomin = '-'
        try:
            logradouro = db.Logradouros.validate_and_insert(
                            Logradouro = ' '.join(endereco_obra['Logradouro'].split()[1:]),
                            Cep = endereco_obra['Cep'],
                            Denominacao = denomin,
                            Prefixo='-',
                            IdBairro=idbairro[0][0] if idbairro else bairro_id,
                            IdCidade=9999)
            print(f'Logradouro ::{logradouro}:: inserido no banco de dados!')

            db.commit()
            return logradouro.id
        except Exception as e:
                    session.flash = f"Erro ao cadastrar Logradouro: {e}"
                    print(logradouro.errors)
                    redirect(URL('default', 'Logradouros'))



def buscar_ou_inserir_endereco(id_logradouro, endereco_obra):
    idendereco = db.Enderecos((db.Enderecos.IdLogradouro == id_logradouro) &
                        (db.Enderecos.Quadra == endereco_obra['Quadra'] ) \
                        & (db.Enderecos.Lote == endereco_obra['Lote'] )) or db.Enderecos((db.Enderecos.IdLogradouro == id_logradouro) &
                        (db.Enderecos.Quadra == '0' + endereco_obra['Quadra'] ) \
                        & (db.Enderecos.Lote == endereco_obra['Lote'] ))
    if idendereco:
        print(f'Endereço ::{idendereco.IdLogradouro}:: encontrado no banco de dados!')
        return idendereco.id
    elif db.Enderecos((db.Enderecos.IdLogradouro == id_logradouro) &
                        (db.Enderecos.Num == endereco_obra['Num'] )) and endereco_obra['Num'] != '0' :
        idendereco = db.Enderecos((db.Enderecos.IdLogradouro == id_logradouro) & (db.Enderecos.Num == endereco_obra['Num'] ))
        print(f'Endereço ::{idendereco.IdLogradouro}:: encontrado no banco de dados!')
        return idendereco.id
    else:
        try:
            idendereco = db.Enderecos.validate_and_insert(IdLogradouro = id_logradouro,
                Num= int(endereco_obra['Num']) or 0,
                Quadra=endereco_obra['Quadra'],
                Lote=endereco_obra['Lote'],
                Complemento=endereco_obra['Compl'],)
            db.commit()
            print(f'Endereço ::{idendereco}:: inserido no banco de dados!')
            return idendereco.id
        except IntegrityError as ie:
            session.flash = f'Este Endereço já está Registrado. Erro: {ie.args}'
        except Exception as e:
            session.flash = f'{e}'
            redirect(URL('default', 'Enderecos'))


def buscar_ou_inserir_obra(id_pessoa, id_processo, id_endereco, dados_obra, CadMunicipal):
    obra = db.executesql(f'''SELECT Id FROM Obras WHERE Obras.Protocolo = '{id_processo}' OR
                                Obras.CadMunicipal = '{CadMunicipal}' OR
                                Obras.IdEndereco = '{id_endereco}' LIMIT 1 ;''')
    if obra: # Se a obra já existir, retorne o ID dessa obra
        session.flash = f'Obra existente encontrada, id: {obra}'
        print(f'Obra ::{obra[0][0]}:: encontrada no banco de dados!')
        return obra[0][0]
    else: # Caso contrário, prepare os dados para inserção
        dados_inserir = {
            'Protocolo': id_processo,
            'CadMunicipal': CadMunicipal,
            'Alvara': dados_obra['alvara'],
            'DataAlvara': dados_obra['data_alvara'],
            'IdGerador': id_pessoa,
            'IdEndereco': id_endereco,
            'Finalidade': dados_obra['finalidade'],
            'AreaTerreno': dados_obra['area_do_terreno'],
            'AreaConstrExist': dados_obra['area_existente'],
            'AreaConstrDemolir': dados_obra['area_demolir'],
            'AreaConstrExecutar': dados_obra['area_construida_final'],
            'PavtosSubS': dados_obra['pavimentos_sub'],
            'PavtosSobreS': dados_obra['pavimentos_sup']
        }

        try:
            id_obra = db.Obras.validate_and_insert(**dados_inserir)
            print(f'Obra ::{id_obra}:: inserida no banco de dados!')
            db.commit()
            return id_obra.id
        except Exception as e:
            # Em caso de erro, registre o erro e redirecione para a página de obras
            print(f"Erro ao registrar obra: {e}")
            session.flash = f"Erro ao registrar obra: {e}"
            redirect(URL('default', 'Obras'))


def preparar_dados(dados_do_processo):
    caminho = Path(pasta_qualidade_habite_se) # type: ignore
    criar_pasta_compartilhada(dados_do_processo, caminho, list(pastas_aprova), numerar=True) # type: ignore
    id_pessoa = buscar_ou_inserir_pessoa(dados_do_processo['dados_gerador'])
    id_processo = buscar_ou_inserir_processo(dados_do_processo['protocolo'], id_pessoa)
    id_logradouro = buscar_ou_inserir_logradouro(dados_do_processo['endereco_obra'])
    id_endereco = buscar_ou_inserir_endereco(id_logradouro, dados_do_processo['endereco_obra'])

    return (id_pessoa, id_processo, id_endereco)


def importar_processos_online(): #Menu
    from scrap_sigm_gest import pega_conteudo_html, captura_dados_de_processos # type: ignore

    form_arquivo = SQLFORM.factory(
        Field('Arq_mod', type='upload', required=True, uploadfolder=Path(request.folder, 'static/temp'),
              requires=IS_EMPTY_OR(IS_UPLOAD_FILENAME(extension='htm')), label='Anexar Pagina'),
        Field('Aba', type='string', requires=IS_IN_SET(['Pendentes', 'Meus', 'Todos'])))



    attributo_id_das_tables = {'Pendentes':'tablePendentes', 'Meus': 'tableRecebidos', 'Todos': 'tableTodos'}
    dict_processos_obtidos = {}

    if form_arquivo.process().accepted:
        arquivo = Path(request.folder, 'static/temp', form_arquivo.vars.Arq_mod)
        table_selecionada = attributo_id_das_tables[form_arquivo.vars.Aba]
        caminho_a = 'file:///{}'.format(arquivo.absolute())


        dados_do_processo = processar_arquivo_html(arquivo) # Process the HTML file
        if not dados_do_processo:
            session.flash = 'Erro ao processar o arquivo.'
            return dict(form=form_arquivo)

        remover_arquivo(arquivo)  # Remove the uploaded file

        id_pessoa, id_processo, id_endereco = preparar_dados(dados_do_processo) # Prepare data
        id_obra = buscar_ou_inserir_obra(id_pessoa, id_processo, id_endereco, # Insert or update the process
                                         dados_do_processo['dados_obra'],
                                         dados_do_processo['endereco_obra']['CadMunicipal'])

        atualizar_planilha_control(dados_do_processo) # Update the control spreadsheet  # Redirect to the edited process page


    if 'processos_obtidos' in locals():
        return response.render(form=form_arquivo, texto=BEAUTIFY(TABLE(*[ (TR(TD(k), TD(BEAUTIFY(TABLE(v)))) for (k, v) in dict_processos_obtidos.items() )] ) ) )
    else:
        return dict(form=form_arquivo)
