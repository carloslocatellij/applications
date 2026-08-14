# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
from pathlib import Path
from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2 # type: ignore
from gluon.sqlhtml import ExporterCSV # type: ignore

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
    
# ---- example index page ----
def index():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})


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
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


from my_validador import myAutocomplete # type: ignore
from gluon.html import INPUT, XML # type: ignore


def buscaCep():
    return Busca_CEP()(request.args(0)).get('logradouro') # type: ignore

def get_inserted_or_updated_pessoa(dict_person: dict[str, str]) -> int:
    Nome = dict_person.get('Nome')
    CPF = dict_person.get('CPF')
    id = db.Pessoas.validate_and_insert(
                Nome= Nome,
                CPF= CPF)
    db.commit()
    return id.id
    
def get_inserted_or_updated_logradouro(dict_logradouro: dict[str, str]) -> int:
    Logradouro = dict_logradouro.get('Logradouro')
    id = db.Logradouros.validate_and_insert(Logradouro=Logradouro)
    db.commit()
    return id.id


def get_inserted_or_updated_endereco(dict_logradouro: dict[str, str]) -> int:
    ...
    


def Requerimentos(): #Menu
    tables= ['Requerimentos', 'Pessoas', 'Endereços']
    
    table1name = f'{db[tables[0]]._tablename[:-1]}'
    
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    
    session.registro = processo
    session.function = tables[0]

    fields = [
        Field('Nome', requires=IS_IN_DB(db, db.Pessoas.id),  widget=myAutocomplete(
            request=request, field=db.Pessoas.Nome, id_field=db.Pessoas.id, limitby=(0, 7), min_length=4)),
        Field('Protocolo', ),
        
        Field('Cep'),
        Field('Logradouro', widget=SQLFORM.widgets.autocomplete(
            request, db.Logradouros.Logradouro, db.Logradouros.id, limitby=(0, 7), min_length=3), label='Endereço'),
        Field('Numero'),
    ]
        
    if f == 'editar':
        reg_processo = db(db.Processos.id == processo)
        
        
    elif f=='ver':
        reg_processo = db(db.Processos.id == processo)
        
    
    else:
        db.Requerimentos.IdProcesso.requires = IS_NOT_IN_DB(db, 'Processos.id', error_message='Já está registrado.')
        
        
    if session.preencher_cpf:
        fields.append(Field('CPF', ))
        #session.preencher_cpf = False
    formprocessos = SQLFORM.factory(*fields, submit_button=f'Atualizar')
        
        

    
    query = None

    if formprocessos.process(keepvalues= True).accepted:
        idpessoa = None
        if not formprocessos.vars['Nome'].isdigit() and not request.vars['CPF']: 
            session.preencher_cpf = True
            session.flash = f'Registre o CPF: {formprocessos.vars}'
            redirect(URL('default', tables[0], args=[formprocessos.vars.id], vars={'f':'ver'})) # type: ignore
            
        elif not formprocessos.vars['Nome'].isdigit() and request.vars['CPF']:
            idpessoa = get_inserted_or_updated_pessoa(
                dict(Nome= request.vars['Nome'],
                     CPF= request.vars['CPF']))
                 
        
        if not query:
            idprocesso = db.Processos.validate_and_update_or_insert(query,
                Protocolo = request.vars['Protocolo'],
                IdPessoa= idpessoa or request.vars['Nome'],
                IdDpto= 31509)
               
            if idprocesso:
                idrequerimento = db.Requerimentos.validate_and_update_or_insert(query,
                    IdProcesso = idprocesso.id,
                    IdEndereco = 29                                               
                                )
        
        
        
        session.flash = f'Dados do {formprocessos.vars} atualizados => pessoa: {idpessoa} => idprocesso: {idprocesso}' if processo else f'{table1name} Registrado pessoa: {idpessoa}'
        redirect(URL('default', tables[0], args=[formprocessos.vars.id], vars={'f':'ver'})) # type: ignore

    elif formprocessos.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    
    
    list_fields= [db.Requerimentos.IdProcesso, db.Requerimentos.IdEndereco,
                  db.Requerimentos.IdProtocolo_de_Ref, db.Requerimentos.Status, db.Requerimentos.Obs
                  ]
    
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.id] , vars={'f': 'ver'})))]
    
    formbusca = SQLFORM.grid(db(db.Requerimentos.IdProcesso > 0), orderby=~db.Requerimentos.created_on, represent_none='',
                         editable=False, searchable=True, deletable=False, links=links, create=False, details=False, paginate=30,
                         maxtextlength = 120, _class="table", exportclasses=dict(csv=False, tsv=False, tsv_with_hidden_cols=False,
                         json=False, xml=False, html=False, csv_with_hidden_cols=(ExporterCSV, 'CSV' )), user_signature=False, # type: ignore
                         fields=list_fields, links_placement = 'left',)
    
        
    return dict(formprocessos=formprocessos, processo=processo, formbusca=formbusca, nome=formprocessos.vars)