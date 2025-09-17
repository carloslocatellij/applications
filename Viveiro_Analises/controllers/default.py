# -*- coding: utf-8 -*-


from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2

if 0 == 1:
    from gluon import (db, current, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, BEAUTIFY, BUTTON, SPAN,
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





def avisos():
    registros_de_avisos = db(
    (db.Avisos.id > 0) & (~db.Avisos.recebido_por.belongs([auth.user_id]))).select()
    avisos = [aviso.corpo for aviso in registros_de_avisos] 
    
    for aviso in registros_de_avisos:
        recebidos = aviso.recebido_por or []
        if auth.user_id not in aviso.recebido_por:
            recebidos.append(auth.user_id)
            aviso.update_record(recebido_por=recebidos)
        
    db.commit()
    markdowner = Markdown2(html4tags=True, tab_width=4, )
    
    
    return dict(avisos=XML(markdowner.convert(*avisos))) # type: ignore



def index():
    registros_de_avisos = db(
    (db.Avisos.id > 0) & (~db.Avisos.recebido_por.belongs([auth.user_id]))).select()
    avisos = [aviso for aviso in registros_de_avisos] 

    return dict(mensagem=T('Sistema de Dados da Secretaria Municipal de Meio Ambiente - São José do Rio Preto'), avisos=avisos)




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
    auth.wikimenu() # add the wiki to the menu
#     """ ##
#       [see](web2py.com/examples/static/sphinx/gluon/gluon.contrib.markdown.html)
#       [Markdown see](https://groups.google.com/g/web2py/c/om9aXi3xg3Y/m/jE4t-KwpBQAJ)
#     """
    response.view = 'test_wiki.htmSCRIPT   response.flash = T("Welcome!")'
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
* <input type="checkbox" /> 3 '''

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
    session.registro = processo
    session.function = table
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
    
    db.Requerimentos.especie_ret2.show_if = db.Requerimentos.especie_ret1 == ''
 
    
    list_fields= [db.Requerimentos.Protocolo, db.Requerimentos.Requerente,
                  db.Requerimentos.Endereco, db.Requerimentos.data_do_laudo, db.Requerimentos.telefone1,
                  db.Requerimentos.Supressoes_requeridas, db.Requerimentos.Podas_requeridas, db.Requerimentos.Despacho,
                  db.Requerimentos.local_arvore, db.Requerimentos.tipo_imovel
                  ]
    
    formbusca = buscador('Requerimentos',  # type: ignore
                         Protocolo={'label': 'Protocolo'},
                         data_do_laudo={'type': 'date' ,'label': 'Data', 'requires': IS_EMPTY_OR(
                            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx") )},
                         Requerente={'label': 'Requerente' },
                         Endereco1={'name':'Endereco1', 'label':'Endereço'},
                         Bairro={},
                         cep= {'type':'integer',  'label':'cep'}, list_fields=list_fields )
        
    return dict(formprocess=formprocess, processo=processo, formbusca=formbusca, tem_laudo=tem_laudo)


def editar_laudo():
    protoc = request.args(0)
    session.edit_laudo = True if session.edit_laudo == False else False
    redirect(URL('default','Requerimentos', extension='', args=[protoc], vars={'f':'ver'}), client_side=True) # type: ignore
    

@auth.requires_login()
def Registrar_Laudo():
    
    #TODO: O botão de registrar laudo deve oferecer caixa de confirmação em caso de não ouver supressões no processo.
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
      # type: ignore

    processo= request.vars.processo or ''  
    prime_query= ''
    conteudo= ''
    copybtn= ''
    form=''
    returnbtn = A('Voltar', _href=URL('default', 'Requerimentos', args=[processo], vars={'f':'ver'}), _class='btn btn-primary')# type: ignore
    newbtn = A('Novo', _href=URL('default', 'Requerimentos'), _class='btn btn-primary')# type: ignore
    
    if processo:
        prime_query = db(db.Requerimentos.Protocolo == processo).select().first()
        relation_query = db((db.Requerimentos.Protocolo == processo) & (db.Laudos.Protocolo == processo)).select().first()
        query_protoc_ref = None
        if prime_query.protocolo_anterior:
            if  db(db.Laudos.Protocolo == prime_query.protocolo_anterior).count() > 0:
                query_protoc_ref = db((db.Requerimentos.Protocolo == prime_query.protocolo_anterior) &
                                        (db.Laudos.Protocolo == db.Requerimentos.Protocolo)).select().first()
            else:
                query_protoc_ref = db((db.Requerimentos.Protocolo == prime_query.protocolo_anterior)).select().first()
            
        textos_despacho = Despachar(prime_query, relation_query, query_protoc_ref) #type: ignore
        markdowner = Markdown2(html4tags=True,  )
        
        conteudo= []
        for texto_despacho in textos_despacho:
            texto_md = markdowner.convert(texto_despacho) or None
            texto_md_escaped = texto_md.replace('\n', '\\n').replace('"', r'\\\\"').replace('<p>', '').replace('</p>', '')
            conteudo.append(DIV(XML(texto_md), _class='card', _style="border-color : silver")) # type: ignore
            copybtn = TAG.button('<Copiar>', _class='btn btn-info', _onclick='navigator.clipboard.writeText("{}").then(function(){{alert("Texto copiado!");}})'.format(texto_md_escaped))  # type: ignore
            conteudo.append(copybtn)
            conteudo.append(XML(markdowner.convert('-----'))) #type: ignore
        
        
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
    session.registro = registro
    session.function = table

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}', formname=table + registro if registro else '') # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, formname=table + registro if registro else '') 
    else:
        db[table].id.requires = IS_NOT_IN_DB(db, f'{table}.id', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}', formname=table)
        
    if form.process().accepted:
        session.flash = f'Dados atualizados' if registro else 'Registrado'
        redirect(URL('default', session.function , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
   
  
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.id] , vars={'f': 'ver'})))]
    
    
    grd_especies = SQLFORM.grid(db(db.Especies.id >0), orderby=db.Especies.Nome, links=links, user_signature=False, editable=False, searchable=True,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left')


    return response.render(dict(form=form,  especie=registro, grd_especies=grd_especies))


def fotos():
    table = 'fotos'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    fields = ['titulo', 'foto', 'fonte', 'tipo'] if not f else None
    
    item_em_questao = session.registro or None
    
    
    if session.function:
        vinculo = 'id'+session.function[:-1] if not session.function == 'Requerimentos' else 'idLaudo'
        db.fotos[vinculo].default = item_em_questao 

    db.fotos.tipo.requires = IS_IN_SET(['árvore', 'caule', 'casca', 'copa', 'galho', 'folha', 'flor', 'fruto', 'muda', 'raiz', 'semente', 'tronco', 'outro' ])   
    
    if f=='editar':
        form = SQLFORM(db.fotos, registro, submit_button=f'Alterar dados da {tablename}', fields=fields, formname= table, deletable=True)
    elif f=='ver':
        form = SQLFORM(db.fotos, registro, readonly=True, fields=fields, formname= table, )
    else:
        form = SQLFORM(db.fotos, submit_button=f'Registrar {tablename}', fields=fields, formname= table)
    
    if form.process().accepted:
        session.flash = f'Registrado'
        if item_em_questao:
            redirect(URL('default', session.function , extension='', args=[item_em_questao], vars={'f':'ver'})) # type: ignore
        else:
            redirect(URL('default', 'fotos', args=[request.args(0)], vars={'f':'ver'}))
            
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
        
    
    if session.function:
        fotos_do_item_em_questao = db(db.fotos[vinculo] == item_em_questao)
    
    listagem_fotos = []
    
    if not f:
        for foto in fotos_do_item_em_questao.select(orderby=~db.fotos.tipo).as_list():
            listagem_fotos.append((foto.get('id'), foto.get('foto'), foto.get('titulo'), foto.get('tipo')))
            
        table_fotos = TABLE( _align='center') # type: ignore
        linha_cards_fotos = TR( ) # type: ignore
        num_col = 4
        resto = len(listagem_fotos) % num_col
        
        for item, elemento in enumerate(listagem_fotos): 
            card_foto = TD( B(A(f'Foto: {elemento[2]}',
                                _href=URL(c=request.controller, f='fotos', extension='',
                                          args=[elemento[0]], vars={'f':'ver'} ))),  # type: ignore
                            DIV(  IMG( _src=URL(r=request, f='download', args=elemento[1]), # type: ignore
                                 _alt=f'foto não encontrada', _width='20%', 
                                 _style='display: block;  margin-left: auto; margin-right: auto'),
                                _align='center', _class="card", _style='padding:20px' ), f'tipo: {elemento[3]}',  _width='20%') 
            linha_cards_fotos.append(card_foto)
            
            if len(listagem_fotos) <= num_col and len(linha_cards_fotos) == len(listagem_fotos):          
                table_fotos.append(linha_cards_fotos)               
                linha_cards_fotos = TR() # type: ignore
            
            elif len(table_fotos) >= len(listagem_fotos) // num_col:
                if len(linha_cards_fotos) == resto: 
                    table_fotos.append(linha_cards_fotos)
                    linha_cards_fotos = TR()
            else:
                if len(linha_cards_fotos) == num_col:
                    table_fotos.append(linha_cards_fotos)
                    linha_cards_fotos = TR()
            
                
    return dict(listagem_fotos=listagem_fotos if not f else '',
                table_fotos=table_fotos if not f else '',
                form=form, f=f)



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
        session.flash = f'Dados do {tablename} atualizados' if registro else '{tablename} Registrado'
        redirect(URL('default', table , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    formbusca = buscador(table,  # type: ignore
                         Bairro ={'label': table[:-1]},
                         )

    return response.render(dict(form=form, formbusca=formbusca, registro=registro, tabela=table))




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


