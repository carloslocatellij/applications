

if 0 == 1:
    from gluon import *  # type: ignore
    from gluon import (
        db, configuration, IS_IN_SET, IS_UPPER, T, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
        Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db, IS_CHKBOX01, DAL, IS_INT_IN_RANGE, IS_CPF_OR_CNPJ,  MASK_CPF)
 

def Supressões_por_periodo(): #Menu
    response.flash = ("Seja Bem Vindo") # type: ignore
    
    grid = None
    if request.vars.data_ini and request.vars.data_fim: # type: ignore
        query= relat_supress_periodo(request.vars.data_ini, request.vars.data_fim) # type: ignore
    else:
        query= None
    
    form = SQLFORM.factory(
        Field('Data_Inicial', type='date', requires=IS_EMPTY_OR(
            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx")
        )),
        Field('Data_Final', type='date', requires=IS_EMPTY_OR(
            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx")
        )))
    
    if form.process().accepted:
        redirect(URL(f=request.function, vars={'data_ini': form.vars.Data_Inicial, 'data_fim': form.vars.Data_Final })) # type: ignore
    else:
        pass
        
    fields = [db.Requerimentos.Endereco1, db.Requerimentos.Numero1,     
        db.Requerimentos.Bairro, db.Laudos.Despacho, db.Laudos.total_supressoes_laudadas,
        db.Requerimentos.tipo_imovel, db.Requerimentos.local_arvore, 
        db.Bairros.Regiao, db.Laudos.qtd_repor, db.Laudos.motivos, db.Laudos.Obs]
    
    links = [dict(header= 'Ver', body= lambda row: A('Ver', _href=URL(c='default', f='Requerimentos', args=[row.Requerimentos.Protocolo], vars={'f':'ver'} ) )        )] 
    
    if query:
        from gluon.sqlhtml import ExporterCSV
        grid = SQLFORM.grid( query, fields=fields ,user_signature=False, details=False, links=links,
            editable=False, searchable=False,deletable=False, create=False, groupby=db.Requerimentos.Protocolo,
            exportclasses=dict(csv=False, tsv=False, tsv_with_hidden_cols=False, json=False, xml=False,
                html=False, csv_with_hidden_cols=(ExporterCSV, 'CSV' ),), maxtextlength = 120, _class="table",
            represent_none= '',links_placement= 'left')
    
    return dict(form=form, grid=grid)


def Podas_por_periodo(): #Menu
    response.flash = ("Seja Bem Vindo") # type: ignore
    
    grid = None
    if request.vars.data_ini and request.vars.data_fim: # type: ignore
        query= relat_podas_periodo(request.vars.data_ini, request.vars.data_fim) # type: ignore
    else:
        query= None
    
    form = SQLFORM.factory(
        Field('Data_Inicial', type='date', requires=IS_EMPTY_OR(
            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx")
        )),
        Field('Data_Final', type='date', requires=IS_EMPTY_OR(
            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx")
        )))
    
    if form.process().accepted:
        redirect(URL(f=request.function, vars={'data_ini': form.vars.Data_Inicial, 'data_fim': form.vars.Data_Final })) # type: ignore
    else:
        pass
        
    fields = [db.Requerimentos.Endereco1, db.Requerimentos.Numero1,     
        db.Requerimentos.Bairro, db.Bairros.Regiao, db.Requerimentos.tipo_imovel,
        db.Requerimentos.local_arvore, db.Requerimentos.total_podas_requeridas]

    links = [dict(header= 'Ver', body= lambda row: A('Ver', _href=URL(c='default', f='Requerimentos', args=[row.Requerimentos.Protocolo], vars={'f':'ver'} ) ) )]
                  
    if query:
        from gluon.sqlhtml import ExporterCSV
        grid = SQLFORM.grid( query, fields=fields ,user_signature=False, details=False, links =links,
            editable=False, searchable=False,deletable=False, create=False, groupby=db.Requerimentos.Protocolo,
            exportclasses=dict(csv=False, tsv=False, tsv_with_hidden_cols=False, json=False, xml=False,
            html=False, csv_with_hidden_cols=(ExporterCSV, 'CSV' ),), maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left')
    
    return dict(form=form, grid=grid)