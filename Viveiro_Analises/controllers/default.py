

if 0 == 1:
    from gluon import (db, current, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
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
def wiki(): #Menu
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



def Processos(): #Menu
    
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    tem_laudo =  db(db.Laudos.Protocolo == processo).select()

    if f=='editar':
        formprocess = SQLFORM(db.Requerimentos, processo ) # type: ignore
    elif f=='ver':
        formprocess = SQLFORM(db.Requerimentos, processo, readonly=True,
                              formstyle='table3cols') # type: ignore
    else:
        formprocess = SQLFORM(db.Requerimentos)

    if formprocess.process().accepted:
        session.flash = f'Dados do protocolo atualizados' if processo else 'Protocolo Registrado'
        redirect(URL('default', 'Processos', args=[formprocess.vars.Protocolo], vars={'f':'ver'})) # type: ignore

    elif formprocess.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    db.Requerimentos.especie_ret2.show_if = (db.Requerimentos.especie_poda1!=None)
 
    
    list_fields= [db.Requerimentos.Protocolo, db.Requerimentos.Requerente,
                  db.Requerimentos.Endereco, db.Requerimentos.data_do_laudo, db.Requerimentos.telefone1,
                  db.Requerimentos.Supressoes, db.Requerimentos.Podas, db.Requerimentos.Despacho,
                  db.Requerimentos.local_arvore, db.Requerimentos.tipo_imovel
                  ]
    
    formbusca = buscador('Requerimentos',  # type: ignore
                         Protocolo={'label': 'Protocolo'},
                         data_do_laudo={'type': 'date' ,'label': 'Data'},
                         Requerente={'label': 'Requerente' },
                         Endereco1={'name':'Endereco1', 'label':'Endereço'},
                         cep= {'type':'integer',  'label':'cep'}, list_fields=list_fields )
        
    return response.render(dict(formprocess=formprocess, processo=processo, formbusca=formbusca, tem_laudo=tem_laudo))


def Registrar_Laudo():
    protoc = request.args(0)

    db.Laudos.validate_and_insert(Protocolo = protoc)

    session.edit_laudo = True

    redirect(URL('default','Processos.html', args=[protoc], vars={'reg': True} )) # type: ignore
    

def Laudos(): #Menu
    
    laudo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    
    if f=='editar':
        form = SQLFORM(db.Laudos, laudo, showid=True, formstyle='table3cols')
    elif f=='ver':
        form = SQLFORM(db.Laudos, laudo, readonly=True, formstyle='table3cols')
    else:
        form = SQLFORM(db.Laudos, laudo)
        
    if form.process().accepted:
        response.flash = f'Dados do Laudo atualizados' if laudo else 'Laudo Registrado'
        redirect(URL('default', 'Laudos', args=[form.vars.Protocolo], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass

    return response.render(dict(form=form, laudo=laudo))


def Lista_de_Registros():
    import re
    
    REGEX = re.compile('^(\w+).(\w+).(\w+)\=\=(\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error')) # type: ignore

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=session.controller, f=table, args=row.Protocolo, vars={'f': 'ver'})))] # type: ignore

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False, deletable=False, create=False,csv=False,
    represent_none='', maxtextlength = 120, _class="table"), table=table)


def Despachar_Processos(): #Menu
    from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2 # type: ignore
    from despachos import Despacho_Poda_Particular  # type: ignore

    processo = int(request.vars.processo)
    
    query = db(db.Requerimentos.Protocolo == processo).select().render(0).as_dict()
    #query_obra = db.Obras(db.Obras.id == query.get('Id'))
    texto_despacho = Despacho_Poda_Particular(query)

    markdowner = Markdown2(html4tags=True, tab_width=4, )
    texto_md = markdowner.convert(texto_despacho) or None


    return dict(conteudo = XML(texto_md)) # type: ignore