

if 0==1:
    from gluon import * 
    

    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, IS_CHKBOX01, IS_CPF_OR_CNPJ, UnidadeDestino, Pessoas, IS_DATE, EntradaATT, Unid_Destino_represent
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T


def Transportadores():


    
    return locals()

def Cadastro_de_Transportador():
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    db.Transportadores.IdPessoa.default = request.vars['pessoa_id'] or session.pessoa_id or None

    if f=='editar':
        formtransp = SQLFORM(db.Transportadores, reg, showid=True)
    elif f=='ver':      
        formtransp = SQLFORM(db.Transportadores, reg, readonly=True , showid=True, linkto=URL(c='default', f='Lista_de_Registros', args='db' ), 
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



def Lista_de_Transportadores():

    busca = buscador('Transportadores', 'Cadastro_de_Transportador',
                                    RazaoSocial={'label':'Razão Social'}, 
                                    Cadastro= {'label':'CTR','type':'integer' }, 
                                    CNPJ= {'label':'CNPJ', 'type':'string'}
    )
    return busca


def Situacao_do_Transportador():
    reg = request.args(0) or None
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

