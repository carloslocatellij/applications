if 0 == 1:
    from gluon import (db, current, redirect, URL, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01,
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE,
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC) # type: ignore
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
    
    # Modified buttons with AJAX functionality
    btns_vars = []
    for field in list(db.Requerimentos.keys())[26:]:
        if not field.startswith('_') and not 'qtd_' in field and not 'especie_' in field and not'ALL' in field:
            btn = BUTTON(field, 
                        _onclick=f'''jQuery('#despacho_template_texto').val(jQuery('#despacho_template_texto').val() + ' {{{field}}} '); return false;''')
            btns_vars.append(TD(btn))

    return dict(form=form, formbusca=formbusca, registro=registro, btns_vars=TABLE(TR(btns_vars[:11]), TR(btns_vars[11:22]), TR(btns_vars[22:])))


@auth.requires_login()
def Gerenciar_variaveis(): 
    """
    Controller para gerenciar variáveis dos templates
    """
    template_id = request.args(0)
    
    if not template_id:
        redirect(URL('Gerenciar_templates'))
    
    # Form para variáveis
    db.despacho_variaveis.template_id.default = template_id
    var_form = SQLFORM(db.despacho_variaveis)
    
    if var_form.accepts(request.vars, session):
        response.flash = 'Variável salva com sucesso'
        redirect(URL(c='despachos',f='gerenciar_variaveis', args=[template_id]))
    
    # Grid para visualizar/editar variáveis do template
    query = db.despacho_variaveis.template_id == template_id
    grid = SQLFORM.grid(query,
                       fields=[db.despacho_variaveis.nome_variavel,
                              db.despacho_variaveis.descricao,
                              db.despacho_variaveis.fonte_dados],
                       maxtextlength=50,
                       create=False,
                       searchable=True)
    
    return dict(form=var_form, grid=grid)