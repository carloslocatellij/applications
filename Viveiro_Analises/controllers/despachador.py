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
    
    
@auth.requires_membership('admin')
def Gerenciar_templates(): #Menu
    """
    Controller para gerenciar templates de despacho
    """
    # Form para template
    template_form = SQLFORM(db.despacho_template)
    
    if template_form.accepts(request.vars, session):
        response.flash = 'Template salvo com sucesso'
        redirect(URL('gerenciar_templates'))
    
    # Grid para visualizar/editar templates existentes
    grid = SQLFORM.grid(db.despacho_template,
                       fields=[db.despacho_template.nome,
                              db.despacho_template.tipo,
                              db.despacho_template.descricao],
                       maxtextlength=50,
                       create=False,
                       searchable=True,
                       details=True)
    
    return dict(form=template_form, grid=grid)


@auth.requires_membership('admin')
def Gerenciar_variaveis(): 
    """
    Controller para gerenciar variáveis dos templates
    """
    template_id = request.args(0)
    
    if not template_id:
        redirect(URL('gerenciar_templates'))
    
    # Form para variáveis
    db.despacho_variaveis.template_id.default = template_id
    var_form = SQLFORM(db.despacho_variaveis)
    
    if var_form.accepts(request.vars, session):
        response.flash = 'Variável salva com sucesso'
        redirect(URL('gerenciar_variaveis', args=[template_id]))
    
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