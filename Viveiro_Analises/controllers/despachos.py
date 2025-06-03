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
        db[table].id.requires = IS_NOT_IN_DB(db, f'{table}.id', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        
     
    # Modified buttons with AJAX functionality
    btns_vars = []
    for field in list(db.Requerimentos.keys())[26:]:
        if not field.startswith('_') and not 'qtd_' in field and not 'especie_' in field and not'ALL' in field:
            btn = BUTTON(field, type='button',
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

    return dict(form=form, formbusca=formbusca, registro=registro, btns_vars=TABLE(TR(btns_vars[:11]), TR(btns_vars[11:22]), TR(btns_vars[22:])))



def form_condicoes():
    form_condicoes = SQLFORM.factory(
    Field('campo', requires=IS_IN_SET([campo for campo in db.Requerimentos.fields])),
    Field('operador', requires=IS_IN_SET(["=", "!=", "<", ">", "<=", ">=", "contêm", "está entre", "não está entre", ])),
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
                        textarea.value = text.substring(0, startPos) + fstring + "," + '\\n' + text.substring(endPos);
                        textarea.focus();
                        return false;
                    ''', _class='btn btn-info' )], fromstyle= 'bootstrap3_stacked'
                                )
    return dict(form_condicoes=form_condicoes)