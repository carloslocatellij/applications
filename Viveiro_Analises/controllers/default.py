
from datetime import datetime

if 0 == 1:
    from gluon import * # type: ignore
    from gluon import (db, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01,
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE,
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC) # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})



def index():
    response.flash = ("Seja Bem Vindo")
    session.counter = (session.counter or 0) + 1
    return dict(message=T('Sistema de Dados da Secretaria Municipal de Meio Ambiente - São José do Rio Preto'), counter=session.counter)


# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)


# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    expõe:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    para decorar funções que precisam de controle de acesso
    Observe também que há http: //..../ [app] / appadmin / manage / auth para permitir que o administrador gerencie usuários"""
    return dict(form=auth())

# ---- ação ao conteúdo estático enviado pelo servidor (required) ---
@cache.action()
def download():
    """
    permite o download de arquivos enviados
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def Processos():
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    
    if f=='editar':
        formprocess = SQLFORM(db.Requerimento, processo, showid=True )
    elif f=='ver':
        formprocess = SQLFORM(db.Requerimento, processo, readonly=True, formstyle='table3cols')
    else:
        formprocess = SQLFORM(db.Requerimento)

    if formprocess.process().accepted:
        response.flash = f'Dados do protocolo atualizados' if processo else 'Protocolo Registrado'
        redirect(URL('default', 'Processos', args=[formprocess.vars.Protocolo], vars={'f':'ver'}))

    elif formprocess.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass

    formbusca = SQLFORM.factory(
        Field('Requerente'),
        Field('Protocolo')
        , formstyle='table3cols', formname='formbusca')
        #Field('Tipo', 'integer', requires = IS_IN_SET(servicos))

    if formbusca.process().accepted:
        session.buscaPessoa =  formbusca.vars.Requerente
        session.buscaProtocolo  = formbusca.vars.Protocolo
        response.flash = 'Exibindo dados para: ',str(session.vars) 
    
    if session.buscaPessoa:
        busca = db(db.Requerimento.Requerente.contains(session.buscaPessoa)) 
        session.buscaPessoa = None
    elif session.buscaProtocolo:
        busca = db(db.Requerimento.Protocolo.contains(session.buscaProtocolo))
        session.buscaProtocolo = None
    else:
        busca = db(db.Requerimento.Protocolo != '')

    fields_grd= [db.Requerimento.Protocolo, db.Requerimento.Requerente, db.Requerimento.telefone1 , db.Requerimento.Endereco1]

    links= [
        dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Processos', args=row.Protocolo, vars={'f':'ver'})))] 


    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links, editable=False, searchable=True, deletable=False, create=False, details=False, csv=False,  maxtextlength = 120, _class="table", user_signature=False,)
        
    return response.render(dict(formprocess=formprocess, processo=processo, formbusca=formbusca, grade=grade))
