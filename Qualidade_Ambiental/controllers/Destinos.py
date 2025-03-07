
if 0==1:
    from gluon import *


    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, IS_CHKBOX01, IS_CPF_OR_CNPJ, UnidadeDestino, Pessoas, IS_DATE, EntradaATT, Unid_Destino_represent
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T

session.forget(response)

from datetime import date

UnidadeDestino = db.define_table('UnidadeDestino',
    Field ('Id', 'id'),
    Field ('IdEmpreendedor', 'reference Pessoas',  requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format)),
    Field ('IdEndereco', 'reference Enderecos'),
    Field ('Tipo', 'text'),
    Field ('Atividade', 'text'),
    Field ('Coordenadas', 'text'),
    Field ('Matricula', 'text'),
    Field ('Area', 'decimal(8,2)'),
    auth.signature,
    format = '%(Atividade)s',
    fake_migrate=True,
    )

def Unid_Destino_represent(row):
	Unid_Destino = db((db.UnidadeDestino.Id == row.id) & (db.Pessoas.Id == db.UnidadeDestino.IdEmpreendedor)).select(db.Pessoas.Nome, cache=(cache.ram, 3600), cacheable=True).first()
	if Unid_Destino:
		destino = Unid_Destino.Nome
		return destino
	else:
		return ''

veiculos = [(1, 'Carro'), (2, 'CARROCA'), (3, 'PICKUP'), (4, 'CARRETA_P'), (5, 'CARRETA_G'), (6, 'OUTRO')]


EntradaPonto = db.define_table('EntradaPonto',
    Field ('Id', 'id'),
    Field ('Placa',  'string', length='9', required=True, requires = IS_MATCH('[ABCDEFGHIJKLMNOPQRSTUVWXYZ#]{3}', error_message='Não é Placa')),
    Field ('TipoVeic', 'integer', requires = IS_IN_SET(veiculos)),
    Field ('Data', 'date', required=True, requires=IS_DATE(format=T(f'%d/%m/%Y'),error_message='deve ser no formato Dia/Mês/Ano!')),
    Field ('Volume', 'decimal(3,2)', default=1.0 ,requires=IS_IN_SET([1.0, 2.0 ]), widget=SQLFORM.widgets.radio.widget ),
    Field ('Sofa', 'integer',default=0 ,requires=IS_IN_SET([0, 1, 2, 3, 4 ]), widget=SQLFORM.widgets.radio.widget),
    Field ('Colchao' , 'integer', default=0 ,requires=IS_IN_SET([0, 1, 2, 3, 4 ]), widget=SQLFORM.widgets.radio.widget, rname='Colchão'),
    Field ('Poda', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Moveis', 'integer',requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Ferro', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Entulho', 'integer',  requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('PlastPapel', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Eletron', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Outros', 'string'),
    Field ('IdPonto', 'reference UnidadeDestino', requires=IS_IN_DB(db(db.UnidadeDestino.Tipo=='Ponto de Apoio'), 'UnidadeDestino.Id', \
        db.UnidadeDestino._format, cache=(cache.ram, 1800))),
    auth.signature,
    fake_migrate=True,
    )




Transportadores = db.define_table('Transportadores',
    Field('Id', 'id'),
    Field('IdPessoa', 'reference Pessoas', label='Pessoa'),
    Field('NomeFantasia',  'string', length='128', requires = IS_UPPER(),notnull=True, label='Nome Fantasia'),
    Field('RazaoSocial',  'string', length='128', requires = IS_UPPER(),notnull=True, label='Razão Social'),
    Field('CNPJ', 'string'),
    Field('IM', 'integer', label='Inscrição Municipal'),
    Field('Cadastro', 'integer', label='Nº de Cadastro de CTR'),
    Field('Tipo'),
    Field('Tel','string', label='Telefone'),
    Field('email', 'string'),
    auth.signature,
    #primarykey=['Id'],
    format ='%(RazaoSocial)s',
    #fake_migrate=True,
 )

db.define_table('TransportadorStatus',
    Field('Transportador', 'reference Transportadores'),
    Field('Status', 'string', requires=IS_IN_SET(['Validado', 'Não Validado', 'Pendente']), default='Pendente', label='Situação'),
    Field('StatusData', 'date', default=datetime.date.today(), requires=IS_DATE(format=T(f'%d/%m/%Y')), readable=False, label='Data de Registro da Situação'),
    Field('Protocolo', 'reference Processos',  requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('Doc_talao', 'upload', label='Documento do Talão de CTR'),
    #auth.signature,
    #fake_migrate=True,
)


EntradaATT = db.define_table('EntradaATT',
    Field('CTR', 'integer'),
    Field('Unid_Destino', 'reference UnidadeDestino', requires=IS_EMPTY_OR(IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent)) ),
    Field('Transportador', 'reference Transportadores' ),
    Field('Data', 'date' ),
    Field('Veiculo_tipo', 'string'),
    Field('Classe_Residuo', 'string', requires=IS_IN_SET(['A - CONCRETO / ALVENARIA', 'B - METAL/ PLASTICO/ PAPEL', 'PODA / VOLUMOSOS', 'A 80% / B 20% *', 'A 65% / B 35% *',
    'A 50% / B 50% *', 'A 35% / B 65% *', 'A 20% / B 80% *', 'MADEIRA', 'GESSO' ,'D * NECESSITA CADRI', 'REJEITO']
    )),
    Field('Volume', 'decimal(7,2)', notnull=True ),
    auth.signature,
#format= '%(CTR)s'
#fake_migrate=True,
)



Licencas = db.define_table('Licenca',
    Field('Num', 'string', ),
    Field('Tipo', 'string', requires=IS_IN_SET(['L. Instalação', 'L. Operação', 'L. Renovação'])),
    Field('Protocolo', 'reference Processos', requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('Anterior', 'string',),
    Field('IdEmpresa', 'reference Pessoas'),
    Field('Unid_Destino','reference UnidadeDestino', requires=IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent), label="ATT"),
    Field('Data', 'date', requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!')),
    Field('IdEndereco', 'reference Enderecos'),
    Field('Exigencias', 'text'),
    Field('validade', 'date',  requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!') ),
    Field('Status', 'boolean'),
    #auth.signature,
    format= '%(Num)s',
    #fake_migrate=True,
)


mensagem_contrução = "Em Contrução! 🛠"
UnidadeDestino = db.UnidadeDestino
Pessoas = db.Pessoas
EntradaATT = db.EntradaATT

def Destinos():
    return dict(msg = DIV(mensagem_contrução, _class="jumbotron"))


def Cadastro_de_Destino(): #Menu
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formdest = SQLFORM(db.UnidadeDestino, reg, showid=True)
    elif f=='ver':
        formdest = SQLFORM(db.UnidadeDestino, reg, readonly=True , showid=True, linkto=URL(c='default', f='Lista_de_Registros', args='db' ),
        labels={})
    else:
        formdest = SQLFORM(db.UnidadeDestino)


    if formdest.process().accepted:
        response.flash = f'Destino Atualizado' if reg else f'Destino Registrado'
        redirect(URL(c='Destinos', f='Cadastro_de_Destino', args=[formdest.vars.id], vars={'f': 'ver'}),)
    elif formdest.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass

    b = buscador('UnidadeDestino', Tipo={'label':'Tipo'},
                                    Matricula= {'label':'Matricula', },
    )

    return dict(formdest=formdest, b=b)

def Registro_de_Licencas(): #Menu

    hoje = date.today()
    este_ano = date.today().year

    def num_licenca():
        return db(db.Licenca.Data > date(este_ano, 1, 1)).count()+1

    db.Licenca.Num.default= lambda: f'{este_ano}-{num_licenca()}'
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formlicenca = SQLFORM(db.Licenca, reg)
    elif f=='ver':
        formlicenca = SQLFORM(db.Licenca, reg, readonly=True,  )
    else:
        formlicenca = SQLFORM(db.Licenca)


    if formlicenca.process().accepted:
        response.flash = f'Licença Atualizada' if reg else f'Licença Registrada'
        redirect(URL(c='Destinos', f='Registro_de_Licencas', args=[formlicenca.vars.id], vars={'f': 'ver'}),)
    elif formlicenca.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass



    return dict(formlicenca=formlicenca, )


def lista_areas_licenciadas(): #Menu

    lstatts = db((db.UnidadeDestino.IdEmpreendedor == db.Pessoas.Id) &(db.UnidadeDestino.id  == db.Licenca.Unid_Destino) &(db.Licenca.Status == True) & (db.Licenca.validade >= date.today() )).select(
                UnidadeDestino.IdEmpreendedor, UnidadeDestino.Tipo,
                UnidadeDestino.Coordenadas, Pessoas.Telefone, Pessoas.Email,db.Licenca.Num, db.Licenca.validade, db.Licenca.Protocolo )

    lstatts = SQLTABLE(lstatts, headers='fieldname:capitalize',
            truncate=100,
            upload=URL('download'), _class="web2py_grid",
            _border='1px    ')

    return dict(lstatts=lstatts, )

def relatorio_entradas_atts(): #Menu

    consulta = SQLFORM.factory(
            Field('Ctr'),
            Field('Unidade',requires=IS_EMPTY_OR(IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent))),
            Field('Transportador', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Transportadores.Id', db.Transportadores._format))),
            Field('DataIni', label='Data Inicial', type='date', requires= IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
            Field('DataFim', label='Data Final', type='date', requires= IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
            Field('Classe',  requires=IS_IN_SET(['', 'A - CONCRETO / ALVENARIA', 'B - METAL/ PLASTICO/ PAPEL',
                'PODA / VOLUMOSOS', 'A 80% / B 20% *', 'A 65% / B 35% *',
'A 50% / B 50% *', 'A 35% / B 65% *', 'A 20% / B 80% *', 'MADEIRA','GESSO', 'D * NECESSITA CADRI', 'REJEITO'])),
            table_name='EntrAtt', formstyle='table3cols', formname='consulta'
    )


    DataIni = DataFim = Unidade = Transportador = Classe = Ctr = None
    if consulta.process().accepted:
        session.Ctr = Ctr = consulta.vars.Ctr
        session.Unidade = Unidade = consulta.vars.Unidade
        session.Transportador = Transportador = consulta.vars.Transportador
        session.DataIni = DataIni = consulta.vars.DataIni
        session.DataFim = DataFim =consulta.vars.DataFim
        session.Classe = Classe = consulta.vars.Classe
        response.flash = 'Exibindo dados para: ',str(session.Unidade) if str(session.Unidade) else '' , str(session.Transportador) ,str(session.DataIni),str(session.DataFim) ,str(session.Classe)
    elif consulta.errors:
        response.flash = 'Erro no formulário'

    if DataIni or DataFim or Unidade or Transportador or Classe or Ctr:
        query = db(((EntradaATT.Data>=DataIni) if DataIni else (EntradaATT.Data>='2018-01-01')) &\
                    ((EntradaATT.Data<=DataFim) if DataFim else (EntradaATT.Data<= date.today() ) ) &\
                    ((EntradaATT.CTR == Ctr) if Ctr else (EntradaATT.CTR != None))      &\
                    ((EntradaATT.Unid_Destino == Unidade) if Unidade else (EntradaATT.Unid_Destino != None)) &\
                    ((EntradaATT.Transportador == Transportador) if Transportador else (EntradaATT.Transportador != None)) &\
                    ((EntradaATT.Classe_Residuo == Classe) if Classe else (EntradaATT.Classe_Residuo != None))
                    )
    else:
        query = db((EntradaATT.Data>='2018-01-01') & (EntradaATT.Data<=date.today()))

    #soma = db(db.EntradaATT.Transportador, db.EntradaATT.Volume)

    response.query = SQLFORM.grid(query, searchable=False, deletable=False, editable=False, create=False, paginate=50,
            fields=(db.EntradaATT.CTR, db.Pessoas.Nome,
                db.EntradaATT.Transportador, db.EntradaATT.Data,
                db.EntradaATT.Classe_Residuo, db.EntradaATT.Volume),\

            field_id=db.EntradaATT.id,\
                left=db.EntradaATT.on((EntradaATT.Unid_Destino == UnidadeDestino.Id) & (db.UnidadeDestino.IdEmpreendedor == db.Pessoas.Id)),\
                exportclasses=dict(csv=True, csv_with_hidden_cols=False , html=False, xml=False ,tsv_with_hidden_cols=False, tsv=False),
                maxtextlength = 120, _class="web2py_grid"
                )

    #tabela = SQLTABLE(query.select(),paginate=50 )

#TODO: erro - objeto bool is not callable - qnd exporta p csv

    return dict(consulta=consulta, query= response.query)
