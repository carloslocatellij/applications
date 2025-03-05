
if 0==1:
    from gluon import * 
    

    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, IS_CHKBOX01, IS_CPF_OR_CNPJ, UnidadeDestino, Pessoas, IS_DATE, EntradaATT, Unid_Destino_represent
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T


from datetime import date

UnidadeDestino = db.UnidadeDestino
Pessoas = db.Pessoas
EntradaATT = db.EntradaATT

def Destinos():

    return dict()


def Cadastro_de_Destino():
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formdest = SQLFORM(db.UnidadeDestino, reg, showid=True)
    elif f=='ver':      
        formdest = SQLFORM(db.UnidadeDestino, reg, readonly=True , showid=True, linkto=URL(c='default', f='Lista_de_Registros', args='db' ), 
        labels={})
    else:
        formdest = SQLFORM(db.UnidadeDestino)


    if formdest.process().accepted:
        response.flash = f'Destino Atualizado' if reg else f'Destino Registrado'
        redirect(URL(c='Destinos', f='Cadastro_de_Destino', args=[formdest.vars.id], vars={'f': 'ver'}),)
    elif formdest.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass

    b = buscador('UnidadeDestino', Tipo={'label':'Tipo'}, 
                                    Matricula= {'label':'Matricula', }, 
    )

    return dict(formdest=formdest, b=b)

def Registro_de_Licencas():

    hoje = date.today()
    este_ano = date.today().year

    def num_licenca():
        return db(db.Licenca.Data > date(este_ano, 1, 1)).count()+1
    
    db.Licenca.Num.default= lambda: f'{este_ano}-{num_licenca()}'
    reg = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formlicenca = SQLFORM(db.Licenca, reg)
    elif f=='ver':      
        formlicenca = SQLFORM(db.Licenca, reg, readonly=True,  )
    else:
        formlicenca = SQLFORM(db.Licenca)


    if formlicenca.process().accepted:
        response.flash = f'Licença Atualizada' if reg else f'Licença Registrada'
        redirect(URL(c='Destinos', f='Registro_de_Licencas', args=[formlicenca.vars.id], vars={'f': 'ver'}),)
    elif formlicenca.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass



    return dict(formlicenca=formlicenca, )


def lista_areas_licenciadas():

    lstatts = db((db.UnidadeDestino.IdEmpreendedor == db.Pessoas.Id) &(db.UnidadeDestino.id  == db.Licenca.Unid_Destino) &(db.Licenca.Status == True) & (db.Licenca.validade >= date.today() )).select(
                UnidadeDestino.IdEmpreendedor, UnidadeDestino.Tipo,
                UnidadeDestino.Coordenadas, Pessoas.Telefone, Pessoas.Email,db.Licenca.Num, db.Licenca.validade, db.Licenca.Protocolo )
    
    lstatts = SQLTABLE(lstatts, headers='fieldname:capitalize',
            truncate=100,
            upload=URL('download'), _class="web2py_grid",
            _border='1px    ')

    return dict(lstatts=lstatts, )

def relatorio_entradas_atts():


        consulta = SQLFORM.factory(
                Field('Ctr'),
                Field('Unidade',requires=IS_EMPTY_OR(IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent))),
                Field('Transportador', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Transportadores.Id', db.Transportadores._format))),
                Field('DataIni', label='Data Inicial', type='date', requires= IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('DataFim', label='Data Final', type='date', requires= IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y')))),
                Field('Classe',  requires=IS_IN_SET(['', 'A - CONCRETO / ALVENARIA', 'B - METAL/ PLASTICO/ PAPEL',
                 'PODA / VOLUMOSOS', 'A 80% / B 20% *', 'A 65% / B 35% *',
'A 50% / B 50% *', 'A 35% / B 65% *', 'A 20% / B 80% *', 'MADEIRA','GESSO', 'D * NECESSITA CADRI', 'REJEITO'])),
                table_name='EntrAtt', formstyle='table3cols',
		buttons = [INPUT(_name='Gerar', _class='btn btn-primary btn-lg',
                _type="submit",value='Gerar', _value="Consulta",
                _onclick="this.form.action.value=Gerar;this.form.submit()")])

        DataIni = DataFim = Unidade = Transportador = Classe = Ctr = ''
        if consulta.process().accepted:
                session.Ctr = Ctr = consulta.vars.Ctr
                session.Unidade = Unidade = consulta.vars.Unidade
                session.Transportador = Transportador = consulta.vars.Transportador
                session.DataIni = DataIni = consulta.vars.DataIni
                session.DataFim = DataFim =consulta.vars.DataFim
                session.Classe = Classe = consulta.vars.Classe
                response.flash = 'Exibindo dados para: ',str(session.Unidade) if str(session.Unidade) else '' , str(session.Transportador) ,str(session.DataIni),str(session.DataFim) ,str(session.Classe)
        elif consulta.errors:
                response.flash = 'Erro no formulário'
        else:
                pass
        
        if DataIni or DataFim or Unidade or Transportador or Classe or Ctr:
                query = db(((EntradaATT.Data>=DataIni) if DataIni else (EntradaATT.Data>='2020-01-01')) &\
                          ((EntradaATT.Data<=DataFim) if DataFim else (EntradaATT.Data<= date.today() ) ) &\
                          ((EntradaATT.CTR == Ctr) if Ctr else (EntradaATT.CTR != None))      &\
                          ((EntradaATT.Unid_Destino == Unidade) if Unidade else (EntradaATT.Unid_Destino != None)) &\
                          ((EntradaATT.Transportador == Transportador) if Transportador else (EntradaATT.Transportador != None)) &\
                          ((EntradaATT.Classe_Residuo == Classe) if Classe else (EntradaATT.Classe_Residuo != None))      
                        )
        else:
                query = db((EntradaATT.Data>='2020-01-01') & (EntradaATT.Data<=date.today()))
        
        response.query = SQLFORM.grid(query, searchable=False, paginate=50,  
                fields=(db.EntradaATT.CTR, db.Pessoas.Nome,
                 db.EntradaATT.Transportador, db.EntradaATT.Data,
                 db.EntradaATT.Classe_Residuo, db.EntradaATT.Volume),\
                field_id=db.EntradaATT.id,\
                 left=db.EntradaATT.on((EntradaATT.Unid_Destino == UnidadeDestino.Id) & (db.UnidadeDestino.IdEmpreendedor == db.Pessoas.Id)),\
                 exportclasses=dict(csv=False, csv_with_hidden_cols=False , html=False, xml=False ,tsv_with_hidden_cols=False, tsv=False),
                 maxtextlength = 120, _class="web2py_grid",
                 )
        
        return dict(consulta=consulta, query= response.query)
