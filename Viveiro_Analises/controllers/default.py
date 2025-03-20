

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
    
    return dict(message=T('Sistema de Dados da Secretaria Municipal de Meio Ambiente - São José do Rio Preto'))


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


@auth.requires_login()
def Processos(): #Menu
    table='Requerimentos'
    tablename = f'{db[table]._tablename[:-1]}'
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    tem_laudo = db(db.Laudos.Protocolo == processo).count() > 0

    if f=='editar':
        formprocess = SQLFORM(db[table], processo, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        formprocess = SQLFORM(db[table], processo, readonly=True,  represent_none='',) # type: ignore
    else:
        formprocess = SQLFORM(db[table], submit_button=f'Registrar {tablename}')

    if formprocess.process(keepvalues= True).accepted:
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


def editar_laudo():
    print('chamou editar_laudo')
    protoc = request.args(0)
    session.edit_laudo = True if session.edit_laudo == False else False
    #response.js =  "jQuery('#Laudo').get(0).reload()"
    print(f'editar_laudo = {session.edit_laudo}')
    redirect(URL('default','Processos', extension='', args=[protoc], vars={'f':'ver'}), client_side=True) # type: ignore


@auth.requires_login()
def Registrar_Laudo():
    print('tentado registrar')
    protoc = request.args(0)
    processo = db(db.Requerimentos.Protocolo == protoc).select().first()
    print(processo.Protocolo)
    try:
        db.Laudos.validate_and_insert(Protocolo = protoc, proprietario=processo.Requerente, data_do_laudo = processo.data_do_laudo, Despacho=processo.Despacho)
        session.edit_laudo = True
    except Exception as e:
        session.flash = f'Erro {e}'
    
    redirect(URL('default','Processos', extension='', args=[protoc], vars={'f':'ver'}), client_side=True) # type: ignore
    
    
@auth.requires_login()
def Laudos():
    table= 'Laudos'
    laudo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else 'ver'
    target='Load'

    if f=='editar':
        form = SQLFORM(db[table], laudo, submit_button=f'Atualizar {db[table]._tablename[:-1]}')
    elif f=='ver':
        form = SQLFORM(db[table], laudo, readonly=True, represent_none='')
    else:
        form = SQLFORM(db[table], submit_button=f'Registrar {db[table]._tablename[:-1]}')
        

    if form.process().accepted:
        session.flash = f'Dados do Laudo atualizados' if laudo else 'Laudo Registrado'
        editar_laudo()
        redirect(URL('default','Processos', extension='', args=[laudo], vars={'f':'ver'}), client_side=True) # type: ignore
        
         
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass

    return response.render(dict(form=form, laudo=laudo))


@auth.requires_login()
def Despachar_Processos(): #Menu
    from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2 # type: ignore
    from despachos import Despachar  # type: ignore

    processo= request.vars.processo or ''  
    prime_query= ''
    conteudo= ''
    copybtn= ''
    form=''
    
    if processo:
        prime_query = db(db.Requerimentos.Protocolo == processo).select().render(0).as_dict()
        
        relation_query = db(db.Laudos.Protocolo == processo) 
         
        if relation_query.count() > 0:
            relation_query = relation_query.select().render(0).as_dict()
        else:
            relation_query = None
            
        texto_despacho = Despachar(prime_query, relation_query)

        markdowner = Markdown2(html4tags=True,  )
        
        texto_md = markdowner.convert(texto_despacho) or None
        texto_md_escaped = texto_md.replace('\n', '\\n').replace('"', r'\\\\"').replace('<p>', '').replace('</p>', '')
        copybtn = TAG.button('<Copiar>', _class='btn btn-info', _onclick='navigator.clipboard.writeText("{}").then(function(){{alert("Texto copiado!");}})'.format(texto_md_escaped))  # type: ignore
        returnbtn = A('Voltar', _href=URL('default', 'Processos', args=[processo], vars={'f':'ver'}), _class='btn btn-primary')# type: ignore
        newbtn = A('Novo', _href=URL('default', 'Processos'), _class='btn btn-primary')# type: ignore
   
        conteudo = XML(texto_md) # type: ignore
    else:
        form = SQLFORM.factory(Field('Protocolo'))
        
    if not processo:  
        if form.process().accepted:
            session.flash = f'Procurando'
            redirect(URL('default', 'Despachar_Processos', vars={'processo' : form.vars.Protocolo}) )# type: ignore


    return dict(returnbtn=returnbtn, newbtn=newbtn, copybtn=copybtn, conteudo = conteudo, form= form) # type: ignore


@auth.requires_login()
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