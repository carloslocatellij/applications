

if 0==1:
    from gluon import *


    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, IS_CHKBOX01, IS_CPF_OR_CNPJ, UnidadeDestino, Pessoas, IS_DATE, EntradaATT, Unid_Destino_represent
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T

mensagem_contrução = "Em Contrução! 🛠"


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
    auth.signature, #type: ignore
    #primarykey=['Id'],
    format ='%(RazaoSocial)s',
    #fake_migrate=True,
 )

db.define_table('TransportadorStatus',
    Field('Transportador', 'reference Transportadores'),
    Field('Status', 'string', requires=IS_IN_SET(['Validado', 'Não Validado', 'Pendente']), default='Pendente', label='Situação'),
    Field('StatusData', 'date', default=datetime.date.today(), requires=IS_DATE(format=T(f'%d/%m/%Y')), #type: ignore
    readable=False, label='Data de Registro da Situação'),
    Field('Protocolo', 'reference Processos',  requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('Doc_talao', 'upload', label='Documento do Talão de CTR'),
    #auth.signature,
    #fake_migrate=True,
)





def Transportadores():
    return dict(msg = DIV(mensagem_contrução, _class="jumbotron"))

def Cadastro_de_Transportador(): #Menu
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    db.Transportadores.IdPessoa.default = request.vars['pessoa_id'] or session.pessoa_id or None

    if f=='editar':
        formtransp = SQLFORM(db.Transportadores, reg, showid=True)
    elif f=='ver':
        formtransp = SQLFORM(db.Transportadores, reg, readonly=True , showid=True, linkto=URL(c='Trasportadores', f='Lista_de_Registros', args='db' ),
        labels={'TransportadorStatus.Transportador': 'Situações do Transportador', 'EntradaATT.Transportador': 'Entradas em ATTs'})
    else:
        formtransp = SQLFORM(db.Transportadores)


    if formtransp.process().accepted:
        response.flash = f'Transportador Atualizado' if reg else f'Transportador Registrado'
        redirect(URL(c='Transportadores', f='Cadastro_de_Transportador', args=[formtransp.vars.id], vars={'f': 'ver'}),)
    elif formtransp.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass




    formbusca = SQLFORM.factory(
    Field('Nome'),
    Field('CTR', label='Nº de CTR'),
    Field('CNPJ'), formstyle='table3cols', formname='formbusca')

    if formbusca.process().accepted:
        session.buscaNome =  formbusca.vars.Nome
        session.buscaCTR  = formbusca.vars.CTR
        session.buscaCNPJ = formbusca.vars.CNPJ
        response.flash = 'Exibindo dados para: ',str(session.Nome)
    elif formbusca.errors:
        response.flash = 'Erro no formulário'
    else:
        pass

    if session.buscaNome:
        busca = db(db.Transportadores.RazaoSocial.contains(session.buscaNome) )
        session.buscaNome = None
    elif session.buscaCTR:
        busca = db(db.Transportadores.Cadastro == session.buscaCTR)
        session.buscaCTR = None
    elif session.buscaCNPJ:
        busca = db(db.Transportadores.CNPJ == session.buscaCNPJ)
        session.buscaCNPJ = None
    else:
        busca = db(db.Transportadores.RazaoSocial == '')

    #fields_grd= [db.Transportadores.RazaoSocial, db.Pessoas.CPF, db.Pessoas.CNPJ, db.Pessoas.IdEndereco, db.Pessoas.Telefone, db.Pessoas.celular, db.Pessoas.Email, db.Pessoas.Categoria]

    links= [
            #dict(header='Endereço', body=lambda row: A(db.Pessoas.IdEndereco.represent(row.IdEndereco), _href=URL(c='default',f='Enderecos', args=row.IdEndereco, vars={'f':'ver'}))),
            dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='Transportadores', f='Cadastro_de_Transportador', args=row.Id, vars={'f':'ver'})))]

    grade = SQLFORM.grid( busca, represent_none='', links=links, editable=False, searchable=False, deletable=False, create=False, details=False,
                         csv=False,  maxtextlength = 120, _class="table", user_signature=False,)

    return dict(formtransp=formtransp, formbusca=formbusca, grade=grade, reg=reg, f=f)



def Lista_de_Transportadores(): #Menu

    busca = buscador('Transportadores', 'Cadastro_de_Transportador', # type: ignore
                                    RazaoSocial={'label':'Razão Social'},
                                    Cadastro= {'label':'CTR','type':'integer' },
                                    CNPJ= {'label':'CNPJ', 'type':'string'}
    )
    return dict(busca = busca)


def Situacao_do_Transportador(): #Menu
    reg = request.args(0) or request.vars['reg'] or None
    f = request.vars['f'] if request.vars['f']  else None

    db.TransportadorStatus.Transportador.default = request.args(0)

    if f=='editar':
        formsittransp = SQLFORM(db.TransportadorStatus, reg, showid=True)
    elif f=='ver':
        formsittransp = SQLFORM(db.TransportadorStatus, reg, readonly=True , showid=True,)
    else:
        formsittransp = SQLFORM(db.TransportadorStatus)


    if formsittransp.process().accepted:
        response.flash = f'Situação do Transportador Atualizada' if reg else f'Situação do Transportador Registrada'
        redirect(URL(c='Transportadores', f='Situacao_do_Transportador', args=[formsittransp.vars.id], vars={'f': 'ver'}),)
    elif formsittransp.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass

    return dict(formsittransp=formsittransp, )



@auth.requires_login() # type: ignore
def Lista_de_Registros():
    import re
    REGEX = re.compile('^(\\w+).(\\w+).(\\w+)\\=\\=(\\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error'))

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=session.controller, f=table if table.endswith('s') else table+'s',
     args=row.id, vars={'f': 'ver'})))]

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left'), table=table)