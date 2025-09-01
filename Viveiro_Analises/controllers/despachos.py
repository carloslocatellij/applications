from ast import alias


if 0 == 1:
    from gluon import (db, current, redirect, URL, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, BUTTON, TD, TABLE, TR,
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE,
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC, buscador) # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore
    
    
@auth.requires_login()
def Gerenciar_templates(): #Menu
    """
    Controller para gerenciar templates de despacho
    """
    # Form para template
    table = 'despacho_template'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, ) 
    else:
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        
    
    if form.process().accepted:
        session.flash = f'Dados atualizados' if registro else 'Registrado'
        redirect(URL(request.controller, request.function , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    formbusca = buscador('despacho_template', 
                        nome={'label': 'Nome'},
                        texto={'label': 'Texto'},
                        descricao={'label': 'Descrição'})
    links = [
    dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=request.controller , f= request.function, # type: ignore
     args=row.id, vars={'f': 'ver'}))),
    dict(header='Editar', body=lambda row: A('Editar', _href=URL(c=request.controller , f= request.function, # type: ignore
     args=row.id, vars={'f': 'editar'})))
     ]
    
    grid_despachos = SQLFORM.grid(db.despacho_template, links=links,user_signature=False, editable=False, searchable=True, details=False,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left')

    return dict(form=form, formbusca=grid_despachos, registro=registro)



def form_condicoes():
    
    list_campos = []
    table1fields = list(db.Requerimentos.keys())[26:]
    for field in table1fields:
        if not field.startswith('_') and not field[-1].isdigit() and not 'especie_' in field and not'ALL' in field:
            list_campos.append(field)
            
    table2fields = list(db.Laudos.keys())[26:]
    for field in table2fields:
        if (not field.startswith('_')  and not 'especie_' in field and not'ALL' in field 
            and not field[-1].isdigit() and not field in list_campos):
            list_campos.append(field)
            
    key_operators = ["=", "!=", "<", ">", "<=", ">=", "contêm", "não contem"]
    operators = ["é igual a", "é diferente de", "é menor que", "é maior que", "é menor ou igual a", "é maior ou igual a", "contêm", "não contem"]
    dict_operador = dict(zip(key_operators, operators))
    
    form_condicoes = SQLFORM.factory(
    Field('campo', requires=IS_IN_SET(list_campos)),
    Field('operador', requires=IS_IN_SET(dict_operador)),
    Field('valor'), buttons=[BUTTON('Inserir Condição', type='button', 
                    _onclick=f'''
                        var campo = jQuery('#no_table_campo').val();
                        var operador = jQuery('#no_table_operador').val();
                        var valor = jQuery('#no_table_valor').val();
                        var textarea = jQuery('#despacho_template_condicoes')[0];
                        var startPos = textarea.selectionStart;
                        var endPos = textarea.selectionEnd;
                        var text = textarea.value;
                        var fstring =  "{{" + '"campo": ' + '"' + campo + '"' + ', ' + '"operador": ' + '"' + operador + '"' + ', ' + '"valor": ' + '"' + valor + '"' + "}}"
                        if (textarea.value.length > 0 && textarea.value[0] == '[' && textarea.value[textarea.value.length - 1] == ']') {{{{
                            textarea.value = text.substring(0, startPos) + fstring + "," + '\\n' + text.substring(endPos);
                        }}}} else {{{{
                            textarea.value = '[' + text.substring(0, startPos) + fstring + "," + '\\n' + text.substring(endPos) + ']';
                        }}}}
                        textarea.focus();
                        textarea.selectionEnd = endPos - 2;
                        return false;
                    ''', _class='btn btn-info' )], fromstyle= 'inline'
                                )
    
        # Modified buttons with AJAX functionality
    #tables = [table  for table in db.tables() ]
    

        
    
    return dict(form_condicoes=form_condicoes)


def form_variaveis():
    btns_vars = []
    for_tabelas = SQLFORM.factory(
        Field('tabelas', 'list:string', multiple=True, requires=IS_IN_SET(['Requerimentos', 'Laudos'])) )
    list_campos = []
    table1fields = list(db.Requerimentos.keys())[28:]
    for field in table1fields:
        if not field.startswith('_') and not field[-1].isdigit() and not 'especie_' in field and not'ALL' in field:
            list_campos.append(field)
            
    table2fields = list(db.Laudos.keys())[28:]
    for field in table2fields:
        if (not field.startswith('_')  and not 'especie_' in field and not'ALL' in field 
            and not field[-1].isdigit() and not field in list_campos):
            list_campos.append(field)
    
    for field in list_campos:
        btn = BUTTON(field.replace('_', ' ').capitalize()  , type='button',
                    _onclick=f'''
                        var textarea = jQuery('#despacho_template_texto')[0];
                        var startPos = textarea.selectionStart;
                        var endPos = textarea.selectionEnd;
                        var text = textarea.value;
                        textarea.value = text.substring(0, startPos) + ' {{{field}}} ' + text.substring(endPos);
                        textarea.focus();
                        textarea.selectionStart = startPos + {len(field) + 4};
                        textarea.selectionEnd = startPos + {len(field) + 4};
                        return false;
                    ''', _class='btn btn-info')
        btns_vars.append(TD(btn))
    
    if for_tabelas.process().accepted:
        redirect(URL(request.controller, request.function, extension='', vars={'tabs': for_tabelas.vars.tabelas}))
    
    table_buttons = TABLE()
    for itens_linha in range(len(list_campos)//8):     
        table_buttons.append(TR(btns_vars[itens_linha  * 8: (itens_linha + 1) * 8]))
        
    return dict(for_tabelas=for_tabelas, btns_vars=table_buttons)