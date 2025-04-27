

from dataclasses import fields
from gluon.http import redirect
from gluon.sqlhtml import represent


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

    
    return dict(message=T('Sistema de Dados da Secretaria Municipal de Meio Ambiente - São José do Rio Preto'),
                )
0

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)


# ---- Embedded wiki (example) ----
@auth.requires_login()
def wiki(): #Menu
    from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2
    from gluon.contrib.markdown import WIKI as markdown
    from gluon.contrib.markmin import markmin2html
    auth.wikimenu() # add the wiki to the menu
#     """ ##
#       [see](web2py.com/examples/static/sphinx/gluon/gluon.contrib.markdown.html)
#       [Markdown see](https://groups.google.com/g/web2py/c/om9aXi3xg3Y/m/jE4t-KwpBQAJ)
#     """
    response.view = 'test_wiki.html'
#     response.flash = T("Welcome!")
#     my_md = '''## Welcome to the cov19cty App!
# ### To generate County Comparison Charts:
# 1. Click Menu >> Gen Chart >> Multi-County Input Form
#   1. Add Your Counties to compare (state, county, typeOfData)
#   2. Define Your Time Series
# 2. Click Menu >> Gen Chart >> Show Multi-County Chart
#     '''
#     my_html = markdown(my_md)
#     # return dict( message=my_html )
#     return my_html mark = XML(meu_mark)

    meu_mark ='''
# Meu Titulo

## Outro Titulo

* <input type="checkbox" checked="checked" /> 1
* <input type="checkbox" checked="checked" /> 2
* <input type="checkbox" /> 3


    '''
    content = authdb(authdb.wiki_page.slug=="instalacao-atualizacao-do-sistema-viveiro-analises").select().first().body # type: ignore
    
    markdowner = Markdown2(html4tags=True, tab_width=4, )
    meu_mark = markdowner.convert(content)


    return dict(wiki = auth.wiki() ,content=XML(meu_mark)) # type: ignore

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
def Requerimentos(): #Menu
    table='Requerimentos'
    tablename = f'{db[table]._tablename[:-1]}'
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    tem_laudo = db(db.Laudos.Protocolo == processo).count() > 0


    if f=='editar':
        formprocess = SQLFORM(db[table], processo, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        formprocess = SQLFORM(db[table], processo, readonly=True, ) 
    else:
        db.Requerimentos.Protocolo.requires = IS_NOT_IN_DB(db, 'Requerimentos.Protocolo', error_message='Já está registrado.')
        formprocess = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        

    if formprocess.process().accepted:
        session.flash = f'Dados do protocolo atualizados' if processo else 'Protocolo Registrado'
        redirect(URL('default', 'Requerimentos', args=[formprocess.vars.Protocolo], vars={'f':'ver'})) # type: ignore

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
                         Bairro={},
                         cep= {'type':'integer',  'label':'cep'}, list_fields=list_fields )
        
    return response.render(dict(formprocess=formprocess, processo=processo, formbusca=formbusca, tem_laudo=tem_laudo))


def editar_laudo():
    protoc = request.args(0)
    session.edit_laudo = True if session.edit_laudo == False else False
    redirect(URL('default','Requerimentos', extension='', args=[protoc], vars={'f':'ver'}), client_side=True) # type: ignore
    

@auth.requires_login()
def Registrar_Laudo():
    
    #TODO: O botão de registrar laudo deve oferecer caixa de confirmação em caso de não haver supressões no processo.
    print('tentado registrar')
    protoc = request.args(0)
    processo = db(db.Requerimentos.Protocolo == protoc).select().first()
    
    # form = SQLFORM.factory()
    # if not any([processo.qtd_ret1, processo.qtd_ret2, processo.qtd_ret3, processo.qtd_ret4]):
    #     my_extra_element = TR(LABEL('Registrar Laudo mesmo sem supressões no Requerimento.'), INPUT(_name='agree', value=True, _type='checkbox')) # type: ignore
    #     form[0].insert(-1, my_extra_element) # type: ignore
    
    # print(processo.Protocolo)
    
    # response.render(BEAUTIFY(Modal('Atenção', form, id='atencao')))
    
    # if form.process().accepted:
    #     if form.vars.agree:  
    
    
    try:
        db.Laudos.validate_and_insert(Protocolo=protoc, proprietario=processo.Requerente, data_do_laudo=processo.data_do_laudo,
                                    Despacho=processo.Despacho, qtd_poda1=processo.qtd_poda1, qtd_poda2=processo.qtd_poda2,
                                    qtd_poda3=processo.qtd_poda3, qtd_poda4=processo.qtd_poda4, especie_poda1=processo.especie_poda1,
                                    especie_poda2=processo.especie_poda2, especie_poda3=processo.especie_poda3, 
                                    especie_poda4=processo.especie_poda4, qtd_ret1=processo.qtd_ret1, qtd_ret2=processo.qtd_ret2, 
                                    qtd_ret3=processo.qtd_ret3, qtd_ret4=processo.qtd_ret4, especie_ret1=processo.especie_ret1,
                                    especie_ret2=processo.especie_ret2, especie_ret3=processo.especie_ret3, especie_ret4=processo.especie_ret4)
        session.edit_laudo = True
    except Exception as e:
        session.flash = f'Erro {e}'
    
    redirect(URL('default','Requerimentos', extension='', args=[protoc], vars={'f':'ver'})) # type: ignore
    
    
@auth.requires_login()
def Laudos():
    table= 'Laudos'
    laudo = request.args(0) or None

    try:
        if session.edit_laudo==True:
            form = SQLFORM(db[table], laudo, submit_button=f'Atualizar {db[table]._tablename[:-1]}', deletable=True)
        else:
            form = SQLFORM(db[table], laudo, readonly=True, represent_none='')

    except Exception as e:
        form = SQLFORM(db[table], submit_button=f'Registrar {db[table]._tablename[:-1]}')
    
        
    if form.process().accepted:
        session.flash = f'Dados do Laudo atualizados' if laudo else 'Laudo Registrado'
        editar_laudo()
        redirect(URL('default','Requerimentos', extension='', args=[laudo], vars={'f':'ver'}), client_side=True) # type: ignore
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
    returnbtn = A('Voltar', _href=URL('default', 'Requerimentos', args=[processo], vars={'f':'ver'}), _class='btn btn-primary')# type: ignore
    newbtn = A('Novo', _href=URL('default', 'Requerimentos'), _class='btn btn-primary')# type: ignore
    if processo:
        prime_query = db(db.Requerimentos.Protocolo == processo).select().render(0).as_dict()
        relation_query = db(db.Laudos.Protocolo == processo)
        query_protoc_ref = ''
        
        if  prime_query.get('protocolo_anterior'):
            
            if db(db.Laudos.Protocolo == prime_query.get('protocolo_anterior')).count() > 0:
                query_protoc_ref = db((db.Requerimentos.Protocolo == prime_query.get('protocolo_anterior')) &
                                      (db.Laudos.Protocolo == db.Requerimentos.Protocolo)).select().render(0).as_dict()
                
            elif db(db.Requerimentos.Protocolo == prime_query.get('protocolo_anterior')):
                    query_protoc_ref = db(db.Requerimentos.Protocolo == prime_query.get('protocolo_anterior')).select().render(0).as_dict()
                    
            
        if relation_query.count() > 0:
            relation_query = relation_query.select().render(0).as_dict()
        else:
            relation_query = None
            
        texto_despacho = Despachar(prime_query, relation_query, query_protoc_ref)

        markdowner = Markdown2(html4tags=True,  )
        
        texto_md = markdowner.convert(texto_despacho) or None
        texto_md_escaped = texto_md.replace('\n', '\\n').replace('"', r'\\\\"').replace('<p>', '').replace('</p>', '')
        copybtn = TAG.button('<Copiar>', _class='btn btn-info', _onclick='navigator.clipboard.writeText("{}").then(function(){{alert("Texto copiado!");}})'.format(texto_md_escaped))  # type: ignore
        
   
        conteudo = XML(texto_md) # type: ignore
    else:
        form = SQLFORM.factory(Field('Protocolo'))
        
    if not processo:  
        if form.process().accepted:
            session.flash = f'Procurando'
            redirect(URL('default', 'Despachar_Processos', vars={'processo' : form.vars.Protocolo}) )# type: ignore


    return dict(returnbtn=returnbtn, newbtn=newbtn, copybtn=copybtn, conteudo = conteudo, form= form) # type: ignore


@auth.requires_login()
def Especies(): #Menu
    table = 'Especies'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, ) 
    else:
        db[table].id.requires = IS_NOT_IN_DB(db, f'{table}.id', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        
    if form.process().accepted:
        session.flash = f'Dados atualizados' if registro else 'Registrado'
        redirect(URL('default', table , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
   
    formbusca = buscador('Especies',  # type: ignore
                         Nome={'label': 'Nome Popular'},
                         Especie={'label': 'Nome Científico'},
                         OutroNome={'label': 'Outros Nomes'}
                         )

    return response.render(dict(form=form, formbusca=formbusca, especie=registro))


@auth.requires_login()
def Bairros(): #Menu
    table = 'Bairros'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, ) 
    else:
        db[table][table[:-1]].requires = IS_NOT_IN_DB(db, f'{table}.{table[:-1]}', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        
    if form.process().accepted:
        session.flash = f'Dados atualizados' if registro else 'Registrado'
        redirect(URL('default', table , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    formbusca = buscador(table,  # type: ignore
                         Bairro ={'label': table[:-1]},
                         )

    return response.render(dict(form=form, formbusca=formbusca, registro=registro))




@auth.requires_login()
def Lista_de_Registros():
    import re
    REGEX = re.compile(r'^(\w+).(\w+).(\w+)\=\=(\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error')) # type: ignore

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [
    dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=request.args(1) , f= table, # type: ignore
     args=row.id, vars={'f': 'ver'}))),
    dict(header='Editar', body=lambda row: A('Editar', _href=URL(c=request.args(1) , f= table, # type: ignore
     args=row.id, vars={'f': 'editar'})))
     ]

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left'), table=table)


