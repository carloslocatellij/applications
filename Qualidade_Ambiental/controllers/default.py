# coding: utf-8 
#!/usr/bin/python3.8

if 0==1:
    from gluon import *
    from gluon import db, SQLFORM, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, redirect, URL, XML, a_db, db, auth, Auth, buscador
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    

def index():
    response.flash = T("Bem Vindo!")
    return dict(sistema=T('Sistema de Dados do Dpto. de Qualidade Ambiental!'))


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})
    

# ---- Smart Grid (example) -----
#@auth.requires_membership('admin') # can only be accessed by members of admin groupd
@auth.requires_login()
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
    """
    exposes:
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
    to decorate ftions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@cache.action()
def Logradouros():
    """
    Formulário de logradouros, com função de registro e modificação, podendo ser chamado em outros formulários com Load()
    """

    logradouro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    if f=='editar':
        formlogr = SQLFORM(db.Logradouros, logradouro, )
    elif f=='ver':
        formlogr = SQLFORM(db.Logradouros, logradouro, readonly=True, linkto=URL('Lista_de_Registros', args='db') , labels = {'Enderecos.IdLogradouro': 'Endereços'} )
    else:
        formlogr = SQLFORM(db.Logradouros, formstyle='bootstrap3_stacked' )

    if formlogr.process().accepted:
        response.flash = f'Logradouro Atualizado' if logradouro else f'Logradouro Registrado'
        logradouro = formlogr.vars.id
        redirect(URL('default','Logradouros.html', vars=dict(logradouro=logradouro) ), client_side=True)
    elif formlogr.errors:
        session.flash = f'Corrija os erros indicados'
    else:
        pass

    formxbusca = buscador( 'Logradouros', Logradouro={'label':'Logradouro'},
                         Cep= {'label':'CEP' },
                         Bairro= {'label':'Bairro' })  

    return dict(formlogr=formlogr, logradouro=logradouro, formxbusca=formxbusca)


@cache.action(time_expire=3, cache_model=cache.ram, quick='VP')
def Enderecos():
    """
    .../default/Enderecos (Formulário de endereços, com função de registro) 
    .../default/Enderecos/{id}?f=editar (função de edição de registro)
    .../default/Enderecos/{id}?f=ver (função de visualização de registro)
    Contém um buscador definido por formbusca = buscador('tabela', 'função',**campos) - definido em 0_estruct.py
    """
    
    endereco = request.args(0) if request.args(0) else None
    f = request.vars['f'] if request.vars['f']  else None
    logradouro = request.vars.logradouro
    if logradouro:
        db.Enderecos.IdLogradouro.default = logradouro

    if f=='editar':
        form = SQLFORM(db.Enderecos, endereco,)
    elif f=='ver':
        form = SQLFORM(db.Enderecos, endereco, readonly=True, linkto=URL('Lista_de_Registros', args='db') , labels = {'Pessoas.IdEndereco':"Pessoas",
        'Obras.IdEndereco':"Obras", 'UnidadeDestino.IdEndereco': 'Destinos', 'Licenca.IdEndereco': "Licenças"} )
    else:
        form = SQLFORM(db.Enderecos )

    if form.process().accepted:
        session.endereco_id = form.vars.id
        response.flash = f'Endereço Atualizado' if endereco else f'Endereço Registrado'
        redirect(request.env.http_web2py_component_location, client_side=True)
    elif form.errors:
        response.flash= f'Corrija os erros indicados.'
    else:
        pass

    formbusca = buscador('Enderecos',  Logradouro={'label':'Logradouro', 'table':'Logradouros'}, 
                                       Cep= {'type':'integer',  'label':'CEP',  'table':'Logradouros'},  )   

    return response.render(dict(form=form, formbusca=formbusca, endereco=endereco))

    
@cache.action(time_expire=10 , cache_model=cache.ram, quick='VP')
def Obras():
    """Formulário de obras, com função de registro e modificação, contendo subformulários para pessoas e endereços"""

    obra = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    endereco = session.endereco_id or None
    if obra:
        pessoa = db.Obras(db.Obras.id == obra).IdGerador 
        protocolo_id = db.Obras((db.Obras.id == obra)).Protocolo or None
        session.processo_id = db.Obras((db.Obras.id == obra)).Protocolo or None
        session.processo_protoc = db.Processos(db.Processos.id == protocolo_id).Protocolo if protocolo_id else None
        session.endereco = db.Obras((db.Obras.id == obra)).IdEndereco or None

    else:
        pessoa = session.pessoa_id or request.vars.pessoa_id or None
        protocolo_id = session.processo_id or request.vars.protocolo_id or None
        endereco = session.endereco or request.vars.endereco or None

    db.Obras.Finalidade.requires = IS_IN_SET(['COMERCIAL','DIVERSIFICADA','EDIFICIO COMERCIAL','EDUCACIONAL','HOTELEIRA','LOTEAMENTO',
    'RELIGIOSA','RESIDENCIAL','RESIDENCIAL MULTIFAMILIAR','RESIDENCIAL UNIFAMILIAR','SAUDE - MEDICINA'])

    if f=='editar':
        formobra= SQLFORM(db.Obras, obra)
        session.pessoa_id = None 
    elif f=='ver':
        formobra= SQLFORM(db.Obras,obra, readonly=True, linkto=URL('Lista_de_Registros', args='db') ,  labels = {'Pgrcc.IdObra': 'PGRCC', 'DofsObra.IdObra': 'DOFs' }) 
    else:
        db.Obras.IdGerador.default = int(pessoa) if pessoa else None
        db.Obras.IdEndereco.default = int(endereco) if endereco else None
        db.Obras.Protocolo.default = protocolo_id if protocolo_id else session.processo_protoc or None

        formobra= SQLFORM(db.Obras,)
        session.pessoa_id = None
    

    if formobra.process(keepvalues=True).accepted:
        response.flash =  f'Obra Registrada'
        session.pessoa_id = pessoa = None
        session.endereco_id = formobra.vars.IdEndereco
        redirect(URL(c='default', f='Obras', args=[formobra.vars.id], vars={'f': 'ver'}))
    elif formobra.errors:
        response.flash = f'Corrija os erros indicados.'
    else:
        pass

    formbusca = SQLFORM.factory(
        Field('Gerador'),
        Field('Alvara'),
        Field('Cadastro'),
        Field('Endereco'),
        Field('Protocolo'),
         formstyle='table3cols', formname='formbusca')

    if formbusca.process().accepted:
        session.buscaGerador =  formbusca.vars.Gerador
        session.buscaAlvara  = formbusca.vars.Alvara
        session.buscaCad = formbusca.vars.Cadastro
        session.buscaEndereco = formbusca.vars.Endereco
        session.buscaProtoc = formbusca.vars.Protocolo
        response.flash = 'Exibindo dados para: ',str(session.Nome)
    elif formbusca.errors:
        response.flash = 'Erro no formulário'
    else:
        pass
    
    if session.buscaGerador:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (db.Pessoas.Nome.contains(session.buscaGerador)))
        session.buscaGerador = None
    elif session.buscaAlvara:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (db.Obras.Alvara == session.buscaAlvara))
        session.buscaAlvara = None
    elif session.buscaCad:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (db.Obras.CadMunicipal == session.buscaCad))
        session.buscaCad = None
    elif session.buscaEndereco:
        busca = db((db.Obras.IdEndereco == db.Enderecos.Id) & (db.Enderecos.IdLogradouro == db.Logradouros.Id) & (db.Logradouros.Logradouro.contains(session.buscaEndereco)))
        session.buscaEndereco = None
    elif session.buscaProtoc:
        busca = db((db.Obras.Protocolo == db.Processos.id) & (db.Processos.Protocolo.contains(session.buscaProtoc)))
        session.buscaProtoc = None
    else:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (db.Obras.IdGerador < 0))

    fields_grd= [db.Pessoas.Nome, db.Obras.CadMunicipal, db.Obras.Alvara, db.Obras.DataAlvara ,db.Obras.IdEndereco, db.Obras.AreaTerreno, db.Obras.AreaConstrExecutar, db.Obras.Finalidade]

    links= [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Obras', args=row.Obras.id if 'Obras' in row else row.id , vars={'f':'ver'})))]

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links, editable=False, searchable=False, deletable=False, create=False, details=False,
                         csv=False,  maxtextlength = 120, _class="table", user_signature=False, field_id=db.Obras.Id, )

    request.get_vars.obra_id = obra
    request.get_vars.gerador_id = pessoa
    request.get_vars.endereco_id = endereco

    return response.render(dict(formobra=formobra, formbusca=formbusca, grade=grade, obra=obra, f=f, pessoa=pessoa, endereco=endereco))

#@cache.action(time_expire=30, cache_model=cache.ram, quick='VP')
def DofsObras():
    """Formulário de DOFs por Obra (vinculado por Id), com função de registro e modificação,
     contendo subformulários para DOFs e Modulo para importar dados do arquivo html de dof salvo"""

    import pegaDof
    import os
    obra = request.args(0) or None
    dof = request.get_vars.dof
    db.DofsObra.IdObra.default = obra

    formdof = SQLFORM(db.DofsObra, dof, fields=['IdDof'], formstyle='table3cols', )
    if formdof.process().accepted:
        response.flash = f'DOF atualizados' if dof else f'DOF Registrado'
        session.iddof = formdof.vars.IdDof
        redirect(request.env.http_web2py_component_location, client_side=True,)
    elif formdof.errors:
        response.flash = f'Corrija o(s) erro(s) indicados' 
    else:
        pass

    formarq = SQLFORM.factory(Field('arquivo', 'upload', label="Inserir a página html salva em seu computador."), formstyle='table3cols' )

    dofpego =''
    
    if formarq.process().accepted:
        response.flash = 'Enviado, aguarde'
        session.arquivo = formarq.vars.arquivo

        try:
            dofpego = pegaDof.pegaquali('file:///{}/{}'.format(str(os.path.join(request.folder, 'uploads')), session.arquivo))
        except:
            session.flash = 'Erro ao processar o arquivo enviado'
        try:
            os.remove('{}/{}'.format(str(os.path.join(request.folder, 'uploads')), session.arquivo))
        except OSError as e:
            session.flash = "Erro na remoção do arquivo do server: Error:{} : {}".format( e.strerror, str(os.path.join(request.folder, 'uploads')), session.arquivo)
      
        for i in dofpego[0]:
            try:
                db.MadeirasDof.insert(IdDof= dofpego[1], Item= i['Nº'], Produto= i['Produto'], Especie= i['Espécie'], Popular= i['Nome Popular'],
                    Qtd= i['Quantidade'], Unidade= i['Unidade'], Valor= i['Valor Item'])
            except:
                #session.flash = f"Erro com o Número do DOF:"
                session.flash = "Erro ao inserir registro a partir do arquivo: Erro no item {}".format(i['Nº'])
                redirect(request.env.http_web2py_component_location, client_side=True,)
            else:
                response.flash = 'Madeiras Registradas.'
        redirect(request.env.http_web2py_component_location, client_side=True,)
    elif formarq.errors:
        response.flash = 'Ocorreu um erro'
    else:
        pass
    
    def updatedof(dofsgrade):
        session.iddof =  dofsgrade.vars.IdDof
        redirect(request.env.http_web2py_component_location, client_side=True)

    if obra:
        dofs = db(db.DofsObra.IdObra == obra )
        madeiras = db((db.DofsObra.IdObra == obra ) & (db.DofsObra.IdDof == db.MadeirasDof.IdDof))
        volume_mad =  db((db.DofsObra.IdObra == obra ) & (db.DofsObra.IdDof == db.MadeirasDof.IdDof)).select(db.MadeirasDof.Qtd.sum().with_alias('SomaMadeira'))
        vol = volume_mad[0]['SomaMadeira'] 
        fields = [db.MadeirasDof.IdDof, db.MadeirasDof.Item, db.MadeirasDof.Produto, db.MadeirasDof.Especie, db.MadeirasDof.Popular, db.MadeirasDof.Qtd, db.MadeirasDof.Unidade, db.MadeirasDof.Valor]
        madeirasgrade = SQLFORM.grid(madeiras, fields=fields, orderby='IdObra', editable=False, searchable=False, deletable=False, create=False, details=False,
        maxtextlength = 120, csv=False, user_signature=False, _class='table',  args = request.args[:1])
        dofsgrade = SQLFORM.grid(dofs, fields=[db.DofsObra.IdDof], orderby='IdDof', editable=True, searchable=False, deletable=False, create=False, details=False, field_id=db.DofsObra.id,
        maxtextlength = 120, csv=False, user_signature=False, _class='table', formargs = {'field_id': db.DofsObra.id}, onvalidation=updatedof,  args = request.args[:1] ) # args = request.args[:1]


    if obra:
        return response.render(dict(formdof=formdof, dofsgrade=dofsgrade, madeirasgrade=madeirasgrade, obra=obra, vol=vol or '', formarq=formarq))
    else:
        return response.render(dict(formdof=formdof, iddof=session.iddof, ))

@auth.requires_login()
def Importar_do_Aprova():
    import scrap_aprova_dig_
    import os
    import re
    from gluon.contrib.pymysql.err import IntegrityError

    formarqhtml = SQLFORM.factory(Field('arquivo', 'upload', label="Inserir a página html salva em seu computador."), formstyle='table3cols' )

    dados_do_processo =''
    process_errors = []

    if formarqhtml.process().accepted:
        session.flash = 'Enviado, aguarde'
        session.arquivo = formarqhtml.vars.arquivo
        try:
            dados_do_processo = scrap_aprova_dig_.raspa_aprova('file:///{}/{}'.format(str(os.path.join(request.folder, 'uploads')), session.arquivo))
        except OSError as e:
            session.flash = "Erro ao enviar arquivo: Error:{} : {}".format( e.strerror, str(os.path.join(request.folder, 'uploads')), session.arquivo)
            process_errors.append(e)
        
        except Exception as e:
            session.flash = f'Erro ao processar o arquivo enviado: {e}'
            process_errors.append(e)

        else:
            try:
                os.remove('{}/{}'.format(str(os.path.join(request.folder, 'uploads')), session.arquivo))
            except OSError as e:
                session.flash = "Erro na remoção do arquivo do server: Error:{} : {}".format( e.strerror, str(os.path.join(request.folder, 'uploads')), session.arquivo)
                process_errors.append(e)
            except Exception as e:
                session.flash = f'Erro na remoção do arquivo enviado: {e}'
                process_errors.append(e)
                      
            try:
                scrap_aprova_dig_.criar_pasta_compartilhada(dados_do_processo)
            except Exception as e:
                session.flash = f"Erro ao criar pasta:: {e}"
                process_errors.append(e)

            try:
                scrap_aprova_dig_.criar_atualizar_arq_de_dados(dados_do_processo)
            except Exception as e:
                session.flash = f"Erro ao criar arquivo de dados:: {e}"

        
        if not  dados_do_processo['dados_gerador']['CNPJ'] == '' and db.Pessoas(db.Pessoas.CNPJ == dados_do_processo['dados_gerador']['CNPJ']) :
            idpessoa = db.Pessoas(db.Pessoas.CNPJ == dados_do_processo['dados_gerador']['CNPJ']).id

        elif  db.Pessoas(db.Pessoas.CNPJ == dados_do_processo['dados_gerador']['CNPJ'].replace('.','').replace('-','')) :
            idpessoa = db.Pessoas(db.Pessoas.CNPJ == dados_do_processo['dados_gerador']['CNPJ'].replace('.','').replace('-','')).id

        elif len(dados_do_processo['dados_gerador']['CNPJ']) > 0:
            idpessoa = db.Pessoas.validate_and_insert(Nome=dados_do_processo['dados_gerador']['Nome'], 
                CNPJ=dados_do_processo['dados_gerador']['CNPJ'].replace('.','').replace('/','').replace('-',''),
                CPF=None,
                Telefone=dados_do_processo['dados_gerador']['tel'],
                Email=dados_do_processo['dados_gerador']['email'],)
            process_errors.append(idpessoa)
            idpessoa = idpessoa.id

        elif dados_do_processo['dados_gerador']['CPF'] != '' and (db.Pessoas(db.Pessoas.CPF == dados_do_processo['dados_gerador']['CPF']) or db.Pessoas(db.Pessoas.CPF == dados_do_processo['dados_gerador']['CPF'].replace('.','').replace('-','')) ):
            try:
                idpessoa = db.Pessoas(db.Pessoas.CPF == dados_do_processo['dados_gerador']['CPF']).id
            except:
                idpessoa = db.Pessoas(db.Pessoas.CPF == dados_do_processo['dados_gerador']['CPF'].replace('.','').replace('-','')).id
        else:
            try:
                idpessoa = db.Pessoas.validate_and_insert(Nome=dados_do_processo['dados_gerador']['Nome'], 
                    CPF=dados_do_processo['dados_gerador']['CPF'],
                    CNPJ=None,
                    Telefone=dados_do_processo['dados_gerador']['tel'],
                    Email=dados_do_processo['dados_gerador']['email'],)
                idpessoa = idpessoa.id
                process_errors.append(idpessoa)
            except IntegrityError as ie:
                session.flash= f'Esta Pessoa Já está Registrada. Erro: {ie.args}'
        try:
            assert db.Pessoas(db.Pessoas.Id == idpessoa) , 'Requerente Não Registrado'
            try:
                session.pessoa_id = idpessoa
            except Exception as e:
                print('Requerente Não Registrado')
        except AssertionError as Ae:
            session.flash = f"Erro ao registrar/encontrar o requerente apontado: {Ae}"
        except Exception as e:
            session.flash = f"Ocorreu um erro do tipo: {e}"
        finally:

            if db.Processos(db.Processos.Protocolo == dados_do_processo['protocolo']):
                idproc = db.Processos(db.Processos.Protocolo == dados_do_processo['protocolo']).id
            else:
                try:
                    idproc = db.Processos.validate_and_insert(Protocolo=dados_do_processo['protocolo'], 
                        IdPessoa=idpessoa,
                        IdDpto='1024412',
                        IdTipo=3,)
                    process_errors.append(idproc.errors)
                    idproc = idproc.id
                    session.processo_id = idproc
                except IntegrityError as ie:
                    response.flash = f'Este Processo já está registrado. Erro: {ie.args}'
                except Exception as e:
                    session.flash = f'{e}'
                    redirect(URL('default', 'Processos'))

        if db.Logradouros(db.Logradouros.Cep == dados_do_processo['endereco_obra']['Cep']):
            idlogradouro = db.Logradouros(db.Logradouros.Cep == dados_do_processo['endereco_obra']['Cep']).id
            try:
                idendereco = db.Enderecos.validate_and_insert(IdLogradouro=idlogradouro,
                    Num=dados_do_processo['endereco_obra']['Num'],
                    Quadra=dados_do_processo['endereco_obra']['Quadra'],
                    Lote=dados_do_processo['endereco_obra']['Lote'],
                    Complemento=dados_do_processo['endereco_obra']['Compl'],)
                process_errors.append(idendereco.errors)    
                idendereco = idendereco.id
            except IntegrityError as ie:
                response.flash = f'Este Endereço já está Registrado. Erro: {ie.args}'
            except Exception as e:
                session.flash = f'{e}'
                redirect(URL('default', 'Endereco'))
        else:
            nomebairro = re.sub(' - .*$', '' ,dados_do_processo['endereco_obra']['Bairro'])
            if db.Bairros(db.Bairros.Bairro.contains(nomebairro)):
                logradouro = re.sub('^\w+ ', '' ,dados_do_processo['endereco_obra']['Logradouro'])
                denomin = re.sub(' .*$', '' ,dados_do_processo['endereco_obra']['Bairro'])
                idbairro = db.Bairros(db.Bairros.Bairro.contains(nomebairro)).id
                try:
                    idlogradouro = db.Logradouros.validate_and_insert(Logradouro=logradouro,
                        Cep=dados_do_processo['endereco_obra']['Cep'],
                        Denominacao=denomin,
                        IdBairro=idbairro,
                        dCidade=9999)
                    process_errors.append(idlogradouro.errors)
                    idlogradouro = idlogradouro.id
                except IntegrityError as ie:
                    response.flash = f'Este Logradouro já está Registrado. Erro: {ie.args}'
                except Exception as e:
                    session.flash = "Erro ao cadastrar Logradouro"
                    redirect(URL('default', 'Logradouro'))

                if not idlogradouro == None:

                    if db.Enderecos((db.Enderecos.IdLogradouro == idlogradouro) & 
                    (db.Enderecos.Quadra == dados_do_processo['endereco_obra']['Quadra'] ) \
                        & (db.Enderecos.Lote == dados_do_processo['endereco_obra']['Lote'] )):
                        
                        idendereco = db.Enderecos((db.Enderecos.IdLogradouro == idlogradouro) & 
                        (db.Enderecos.Quadra == dados_do_processo['endereco_obra']['Quadra'] ) \
                        & (db.Enderecos.Lote == dados_do_processo['endereco_obra']['Lote'] ))

                    elif db.Enderecos((db.Enderecos.IdLogradouro == idlogradouro) & 
                    (db.Enderecos.Num == dados_do_processo['endereco_obra']['Num'] )):

                        idendereco = db.Enderecos((db.Enderecos.IdLogradouro == idlogradouro) & (db.Enderecos.Num == dados_do_processo['endereco_obra']['Num'] ))
                    
                    else:

                        try:
                            idendereco = db.Enderecos.validate_and_insert(IdLogradouro=idlogradouro,
                                Num=dados_do_processo['endereco_obra']['Num'],
                                Quadra=dados_do_processo['endereco_obra']['Quadra'],
                                Lote=dados_do_processo['endereco_obra']['Lote'],
                                Complemento=dados_do_processo['endereco_obra']['Compl'],)
                            process_errors.append(idendereco.errors)
                            idendereco = idendereco.id
                        except IntegrityError as ie:
                            session.flash = f'Este Endereço já está Registrado. Erro: {ie.args}'

                        except Exception as e:
                            session.flash = f'{e}'
                            redirect(URL('default', 'Endereco'))
                try:
                    session.endereco = idendereco
                except Exception:
                    print('Endereço não encontrado')

        try:
            idobra = db.Obras(db.Obras.CadMunicipal == dados_do_processo['endereco_obra']['CadMunicipal']).Id
        
        except Exception as e:

            try:
                idobra = db.Obras.validate_and_insert(Protocolo=int(idproc),
                        CadMunicipal=dados_do_processo['endereco_obra']['CadMunicipal'],
                        Alvara=dados_do_processo['dados_obra']['alvara'],
                        DataAlvara=dados_do_processo['dados_obra']['data_alvara'] ,
                        IdGerador=idpessoa, IdEndereco=idendereco, 
                        Finalidade=dados_do_processo['dados_obra']['finalidade'],
                        AreaTerreno=dados_do_processo['dados_obra']['area_do_terreno'],
                        AreaConstrExist=dados_do_processo['dados_obra']['area_existente'],
                        AreaConstrDemolir=dados_do_processo['dados_obra']['area_demolir'],
                        AreaConstrExecutar=dados_do_processo['dados_obra']['area_construida_final'],
                        PavtosSubS=dados_do_processo['dados_obra']['pavimentos_sub'],
                        PavtosSobreS=dados_do_processo['dados_obra']['pavimentos_sup'], safe=True 
                        )
                
            except Exception as e:
                session.flash = f'Ocorreu um erro: {e}'
                redirect(URL('default', 'Importar_do_Aprova'))


        if isinstance(idobra, int):
            session.flash = f"Registros efetuados: Requerente, Processo, Endereço e Obra {process_errors}"
            redirect(URL('default', 'Obras',  args=[idobra], vars={'f':'editar'}))


        else:
            try:
                idobra = db.Obras(db.Obras.CadMunicipal == dados_do_processo['endereco_obra']['CadMunicipal']).Id
                redirect(URL('default', 'Obras', args=[int(idobra)], vars={'f':'ver'}))
                
            except Exception as e:
                print(e)
                print(idobra)
                redirect(URL('default', 'Obras', args=[int(idobra)], vars={'f':'ver'}))
                session.flash = f'Obra não registrada e não encontrada {e.args}'

    return dict(dados_do_processo=dados_do_processo, formarqhtml=formarqhtml, process_errors=process_errors)
    

def PGRCCs():
    """Formulário de PGRCC, com função de registro e modificação"""

    pgr = request.args(0) or None
    gerador = request.get_vars.pessoa_id or None
    obra = request.get_vars.obra_id or None
    protocolo = request.get_vars.processo_id or None


    db.Pgrcc.idgerador.default = gerador
    db.Pgrcc.idobra.default = obra
    db.Pgrcc.protocolo.default = session.processo_id


    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formpgr = SQLFORM(db.Pgrcc, pgr , detect_record_change=True, record_id=int(pgr), deletable=False, ignore_rw=False )
    elif f =='ver':
        formpgr = SQLFORM(db.Pgrcc, pgr , readonly=True, linkto=URL('Lista_de_Registros', args='db') ,  labels = {} )
    else:
        formpgr = SQLFORM(db.Pgrcc )
    

    if formpgr.process().accepted:

        response.flash = f'PGRCC Atualizad0' if pgr else f'PGRCC Registrado'
        redirect(URL('default', 'PGRCCs', args=[formpgr.vars.id], vars={'f':'ver'} ))
    elif formpgr.errors:
        response.flash = f'Erro na Registro do PGRCC'

    #TODO: Criar Buscador de PGRCCs

    return response.render(dict(formpgr=formpgr, obra=obra, pgr=pgr))


@cache.action(time_expire=15, cache_model=cache.ram, quick='VP')
def Pessoas():
    """Formulário de Pessoas, com função de registro e modificação"""
    
    pessoa = db.Pessoas(request.args(0)).Id if request.args(0) else session.pessoa_id or None
    f = request.vars['f'] if request.vars['f']  else None
    fields = ['Id' ,'Nome', 'CPF', 'CNPJ', 'IdEndereco', 'Telefone', 'celular', 'Email']
    endereco = session.endereco_id or None

    if endereco:
        db.Pessoas.IdEndereco.default = int(endereco)
    
    if f=='editar':
        formpessoa = SQLFORM(db.Pessoas, pessoa)
        session.endereco_id = None
    elif f =='ver':
        formpessoa = SQLFORM(db.Pessoas, pessoa , readonly=True, linkto=URL('Lista_de_Registros', args='db') ,  labels = {'Pgrcc.IdGerador': 'Gerador PGR',
         'Pgrcc.RespTecnico':'R. Téc. PGR' ,'UnidadeDestino.IdEmpreendedor':"Destinos", 'Transportadores.IdPessoa': 'Transportador',
        'Obras.IdGerador':"Obras",'Processos.IdPessoa':"Processos" , 'Licenca.IdEmpresa': "Licenças", } )
        session.endereco_id = None
    else:
        formpessoa = SQLFORM(db.Pessoas , fields=fields)
        session.endereco_id = None

    if formpessoa.process().accepted:
        session.pessoa_id = formpessoa.vars.id
        request.vars.pessoa_id = formpessoa.vars.id
        session.flash = f'Dados atualizados' if pessoa else f'Pessoa Registrada'
        # if 'Pessoas' in request.env.request_uri :
        #     redirect(URL('default', 'Pessoas', args=[formpessoa.vars.id], vars={'f': 'ver'}))
        # else:
        #     #redirect(URL('default', request.function , vars={'pessoa_id': request.vars.pessoa_id}))
        redirect(request.env.http_web2py_component_location, client_side=True,)

    elif formpessoa.errors:
        response.flash = f'Corrija os dados indicados.'
    else:
        pass
    
    # formbusca = buscador( 'Pessoas', Nome={'label':'Nome'},
    #                      CPF= {'label':'CPF', 'requires' : IS_CPF_OR_CNPJ() },
    #                      CNPJ= {'label':'CNPJ', 'represents': MASK_CNPJ() }) 

    formbusca = SQLFORM.factory(
        Field('Nome'),
        Field('CPF'),
        Field('CNPJ'), formstyle='table3cols', formname='formbusca')

    if formbusca.process().accepted:
        session.buscaNome =  formbusca.vars.Nome
        session.buscaCPF  = formbusca.vars.CPF
        session.buscaCNPJ = formbusca.vars.CNPJ
        response.flash = 'Exibindo dados para: ',str(session.Nome)
    elif formbusca.errors:
        response.flash = 'Erro no formulário'
    else:
        pass
    
    if session.buscaNome:
        busca = db(db.Pessoas.Nome.contains(session.buscaNome) ) 
        session.buscaNome = None
    elif session.buscaCPF:
        busca = db(db.Pessoas.CPF.contains(session.buscaCPF)) #TODO: Verificar sanitização para melhorar as pesquisas tirando caracteres não alphanumericos
        session.buscaCPF = None
    elif session.buscaCNPJ:
        busca = db(db.Pessoas.CNPJ.contains(session.buscaCNPJ))
        session.buscaCNPJ = None
    else:
        busca = db(db.Pessoas.id < 0)

    fields_grd= [db.Pessoas.Id, db.Pessoas.Nome,db.Pessoas.CPF, db.Pessoas.CNPJ, db.Pessoas.IdEndereco, db.Pessoas.Telefone, db.Pessoas.celular, db.Pessoas.Email, db.Pessoas.Categoria]
    db.Pessoas.IdEndereco.readable = False
    db.Pessoas.Id.readable = False
    links= [
            dict(header='Endereço', body=lambda row: A(db.Pessoas.IdEndereco.represent(row.IdEndereco), _href=URL(c='default',f='Enderecos', args=row.IdEndereco, vars={'f':'ver'}))),
            dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Pessoas', args=row.Id, vars={'f':'ver'})))]

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links, editable=False, searchable=False, deletable=False, create=False, details=False,
                         csv=False,  maxtextlength = 120, _class="table", user_signature=False,)
    
    return response.render(dict(formpessoa=formpessoa, pessoa=pessoa, formbusca=formbusca, grade=grade))


def Processos():
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    pessoa_id = request.vars.pessoa_id or session.pessoa_id or None
    fields = ['Protocolo','IdPessoa','DataReg', 'IdDpto', 'IdTipo', 'Assunto']

    db.Processos.IdPessoa.default = pessoa_id or None

    if f=='editar':
        formprocess = SQLFORM(db.Processos, processo, showid=True )
        session.pessoa_id = None
    elif f=='ver':
        formprocess = SQLFORM(db.Processos, processo, readonly=True, showid=True, linkto=URL('Lista_de_Registros', args='db' ), labels = {'Obras.Protocolo':'Obras' ,'Licenca.Protocolo': ' Licenças ',
         'AnaliseTec.Protocolo': ' Análises ', 'TransportadorStatus.Protocolo':' Transportador ', 'Pgrcc.Protocolo':' PGRCC ', 
         'Tarefas.Protocolo': ' Tarefas '} )
        session.pessoa_id = None
    else:
        formprocess = SQLFORM(db.Processos, fields=fields)


    if formprocess.process().accepted:
        response.flash = f'Dados do protocolo atualizados' if processo else f'Protocolo Registrado'
        if int(formprocess.vars.IdTipo) in [3 , 4 , 13 , 14]:
            session.processo_id = formprocess.vars.id
            redirect(URL(c='default', f='Obras', vars={'pessoa': formprocess.vars.IdPessoa}))

        elif formprocess.vars.IdTipo == '15':
            session.processo_id = formprocess.vars.id
            redirect(URL(c='Transportadores', f='Cadastro_de_Transportador', vars={'pessoa': formprocess.vars.IdPessoa}))

        elif int(formprocess.vars.IdTipo) in [18, 19, 20]:
            session.processo_id = formprocess.vars.id
            redirect(URL(c='Destinos', f='Registro_de_Licencas', vars={'pessoa': formprocess.vars.IdPessoa}))

        else:
            session.processo_id = formprocess.vars.id
            redirect(URL('default', 'Processos', args=[formprocess.vars.id], vars={'f':'ver'}))

    elif formprocess.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass

    formbusca = SQLFORM.factory(
        Field('Pessoa'),
        Field('Protocolo')
        , formstyle='table3cols', formname='formbusca')
        #Field('Tipo', 'integer', requires = IS_IN_SET(servicos))

    if formbusca.process().accepted:
        session.buscaPessoa =  formbusca.vars.Pessoa
        session.buscaProtocolo  = formbusca.vars.Protocolo
        response.flash = 'Exibindo dados para: ',str(session.Pessoa) 
    
    if session.buscaPessoa:
        busca = db((db.Processos.IdPessoa == db.Pessoas.Id) & (db.Pessoas.Nome.contains(session.buscaPessoa) ) )
        session.buscaPessoa = None
    elif session.buscaProtocolo:
        busca = db((db.Processos.IdPessoa == db.Pessoas.Id) & (db.Processos.Protocolo.contains(session.buscaProtocolo)))
        session.buscaProtocolo = None
    else:
        busca = db(db.Processos.Protocolo == '')

    fields_grd= [db.Processos.id ,db.Processos.Protocolo, db.Processos.IdPessoa, db.Pessoas.Telefone, db.Processos.IdTipo, db.Processos.DataReg ]

    links= [
        dict(header='Pessoa', body=lambda row: A('Pessoa', _href=URL(c='default', f='Pessoas', args=row.Processos.IdPessoa, vars={'f':'ver'}))) ,
        dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Processos', args=row.Processos.id, vars={'f':'ver'})))] 


    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links, editable=False, searchable=False, deletable=False, create=False, details=False, csv=False,  maxtextlength = 120, _class="table", user_signature=False,)
        
    return response.render(dict(formprocess=formprocess, processo=processo, formbusca=formbusca, grade=grade))


@auth.requires_login()
def Criar_Tarefa():
    
    id_do_processo = request.args(0) or None

    protoc = db.Processos(db.Processos.id == id_do_processo).Protocolo
    user= db.auth_user(db.auth_user.id == auth.user_id).id
    tipo = db.Processos(db.Processos.id == id_do_processo).IdTipo
    interessado =  db((db.Pessoas.id == db.Processos.IdPessoa) & (db.Processos.id == id_do_processo)).select(db.Pessoas.Nome).last().Nome
    tarefa_nome = '{} - {}'.format(interessado, protoc)

    inexiste = db(db.Tarefas.Protocolo == id_do_processo).isempty() 

    if inexiste is False:
        session.flash = 'Já existe uma Tarefa para o Protocolo {}'.format(protoc)
        redirect(URL('default', 'Processos', args=[id_do_processo], vars={'f':'ver'} ))
    if id_do_processo and inexiste:
        id = db.Tarefas.insert(Titulo=tarefa_nome ,Protocolo=id_do_processo, Responsavel=user, Tipo=tipo)
        session.processo_id = None
        redirect(URL('default', 'Tarefas', args=[id]))



def Lista_de_Tarefas():

    tipos = db(db.Servicos.Dpto == db.auth_user.IdDepto)

    # tarefas = db((db.Tarefas)).select(db.Tarefas.Protocolo, db.Tarefas.Responsavel, db.Tarefas.DataFim, db.Tarefas.Tipo, db.Tarefas.checklist, db.Tarefas.Status, distinct=True)

    tarefas = [ db((db.Tarefas.Protocolo == db.Processos.id) & (db.Tarefas.Tipo == tipo ) & (db.Processos.IdPessoa == db.Pessoas.Id) )\
          for tipo in tipos.select('Servicos.id',  distinct=True,) if not db(db.Tarefas.Tipo == tipo).isempty()]
    
    # return dict(tarefas=tarefas, tipos=tipos.select( 'Servicos.id', distinct=True)) 
    headers = {'Tarefas.Protocolo': 'Protocolo', 'Pessoas.Nome': 'Nome', 'Tarefas.Responsavel': 'Responsável', 'Tarefas.DataFim': 'Data Final',
     'Tarefas.Tipo': 'Tipo', 'Tarefas.checklist': 'Check-list', 'Tarefas.Status': 'Status', 'Ver':'Ver'}
    fields = [db.Tarefas.id, db.Tarefas.Protocolo, db.Pessoas.Nome, db.Tarefas.Responsavel, db.Tarefas.DataFim,
     db.Tarefas.Tipo, db.Tarefas.checklist, db.Tarefas.Status]
    
    db.Tarefas.Status.readable = False
    
    def estilo_do_status(status):
        if status == 'Concluida':
            return "background-color: #0a2; border: solid 1px; text-align: center"
        elif status == 'Iniciada':
            return "background-color: lightblue; border: solid 1px"
        elif status == 'Em Andamento':
            return "background-color: lightyellow; border: solid 1px"
        elif status == 'Aguardando retorno':
            return "background-color: orange; border: solid 1px"
        else:
            return "background-color: #fff; border: solid 1px"

    show_all = request.vars['show_all'] or None
    links= [dict(header='Editar', body=lambda row: A('Editar', _href=URL(c='default', f='Tarefas', args=row.Tarefas.id , vars={'f':'editar'}))),
            dict(header='Estado', body=lambda row: A(B(row.Tarefas.Status), _class='card', _align="center" ,_style= estilo_do_status(row.Tarefas.Status))) ]

    tabelas_tarefas =  [DIV(B(tarefa.select(db.Tarefas.Tipo, distinct=True ) , A('Ver Todos', _href=URL(c='default', f='Lista_de_Tarefas',  vars={'show_all':'True' if not show_all else None}))) ,  DIV(SQLFORM.grid(tarefa , links=links,  editable=False,
        searchable=True, deletable=False, create=False, details=False,  csv=False, orderby=~db.Tarefas.Status,
        headers=headers, fields=fields, maxtextlength = 80, paginate=20 if not show_all else None,_class="web2py_grid"),_class="flex-box" ) , _class="card") for  tarefa in tarefas]


    # tabelas_tarefas =  [DIV(tarefa.select(db.Tarefas.Tipo, distinct=True ) ,
    #  SQLTABLE(tarefa.select(db.Tarefas.Protocolo, db.Tarefas.Protocolo, db.Pessoas.Nome, db.Tarefas.Responsavel,
    #   db.Tarefas.DataFim, db.Tarefas.Tipo, db.Tarefas.checklist, db.Tarefas.Status, distinct=True), 
    #   selectid=db.Tarefas.Protocolo ,
    #       headers=headers, truncate = 80, _class="web2py_grid"))  for tarefa in tarefas]

    return dict(tabelas_tarefas=tabelas_tarefas)





def Tarefas():
    id_da_tarefa = request.args(0) or None #redirect(URL('default', 'Processos'))
    request.vars.id_da_tarefa = id_da_tarefa
    if id_da_tarefa:
        id_do_processo = db.Tarefas(db.Tarefas.id == id_da_tarefa).Protocolo or None
        request.vars.id_do_processo = id_do_processo
        protoc_tarefa = db.Processos(db.Processos.id == int(id_do_processo)).Protocolo or None
        request.vars.protoc_tarefa = protoc_tarefa
        if id_do_processo:
            dados_obra = db(db.Obras.Protocolo == id_do_processo).select( 'CadMunicipal', 'AreaTerreno', 'AreaConstrExist', 'AreaConstrDemolir', 'AreaConstrExecutar', cache=(cache.ram, 900) )
            headers=dict(CadMunicipal='CadMunicipal', AreaTerreno='Área do Terreno', AreaConstrExist='Área Existente', AreaConstrDemolir='Área a demolir', AreaConstrExecutar='Área a Executar')
            dados_obra=SQLTABLE(dados_obra,  headers=headers, _class="table" , _style="border: 2px solid; padding: 5px; word-wrap:break-word; color: darkslategray;",)
            # dados_pgr = db(db.Pgrcc.Protocolo == id_do_processo)
            # if dados_pgr:
            #     dados_pgr = SQLFORM.grid(dados_pgr)
        else:
            dados_pgr = ''
            dados_obra = ''

    id_da_analise = request.args(1) or None
    request.vars.id_da_analise = id_da_analise

    f = request.vars['f'] or None   


    if id_da_tarefa:
        lst_requer = [(0,'')]
        requer = db(db.Procedimentos.id >0).select(db.Procedimentos.id ,db.Procedimentos.Procedimento,
         db.Procedimentos.Tipo).find(lambda row: db.Tarefas(db.Tarefas.id == id_da_tarefa).Tipo in row.Tipo)
        for v in requer:
            tup =( v['id'], v['Procedimento'])
            lst_requer.append(tup)
        if requer:
            db.Tarefas.checklist.requires = IS_IN_SET((lst_requer),  multiple=(1, len(lst_requer)) )

    db.Tarefas.Responsavel.writable = False  
    db.Tarefas.Protocolo.writable = False

    if f == 'ver':
        db.Tarefas.Titulo.writable = False
        db.Tarefas.Status.writable = False
        db.Tarefas.DataIni.writable = False
        db.Tarefas.DataFim.writable = False
        db.Tarefas.Tipo.writable = False
        db.Tarefas.Descricao.writable = False

        formtarefa=SQLFORM(db.Tarefas, id_da_tarefa,  linkto=URL('Lista_de_Registros', args='db' ), labels={} )
    else:
        db.Tarefas.checklist.show_if = (db.Tarefas.Tipo==3)
        formtarefa=SQLFORM(db.Tarefas, id_da_tarefa)

    if formtarefa.process().accepted:
        response.flash = f'Tarefa Atualizada' if id_da_tarefa else f'Tarefa Registrada'
        redirect(URL('default', 'Tarefas', args=[id_da_tarefa, id_da_analise], vars={'f':'ver' }))
    elif formtarefa.errors:
        response.flash = f'Erro na tarefa - {formtarefa.errors}'


    
    atributo = {'up-submit':'',  'up-target':"#grade"}
    
    formbusca = SQLFORM.factory(
        Field('Tarefa'), buttons=[TAG.button('Busca',  _class="btn btn-primary",)],
         formstyle='table3cols', formname='formbusca', _id='formbusca', **atributo)
        #Field('Tipo', 'integer', requires = IS_IN_SET(servicos))

    session.buscaTarefa = None
    if formbusca.validate(dbio=False, keepvalues=True):
        session.buscaTarefa = formbusca.vars.Tarefa
    elif formbusca.errors:
        response.flash = 'Erro no formulário'
    else:
        pass

    busca = db(db.Tarefas.Titulo.contains(session.buscaTarefa)) if session.buscaTarefa else db(db.Tarefas.id <0)
    db.Tarefas.id.readable = False
    db.Tarefas.Protocolo.readable = False
    db.Tarefas.checklist.readable = False


    links = [
        dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Tarefas', args=row.id, vars={'f': 'ver'})))]

    grade = SQLFORM.grid(busca, represent_none='', links=links, editable=False, searchable=False, deletable=False, create=False, details=False,
                         csv=False,  maxtextlength=120, _class="table", user_signature=False,)



    if id_da_tarefa:
        return dict(formtarefa=formtarefa, formbusca=formbusca, grade=grade,  id_do_processo=id_do_processo,
     id_da_tarefa=id_da_tarefa, id_da_analise=id_da_analise, dados_obra=dados_obra)
    else:
        return dict(formtarefa=formtarefa, formbusca=formbusca, grade=grade)
        

@cache.action() 
def Analises():
    id_da_analise= request.args(0) or None
    id_do_processo =  request.get_vars['id_do_processo'] or request.vars.id_do_processo or None
    id_da_tarefa = request.get_vars['id_da_tarefa']

    f = request.get_vars['f'] or None

    if f=='editar':
        formanalise = SQLFORM(db.AnaliseTec, int(id_da_analise), showid=False, )
    elif f=='ver':      
        formanalise = SQLFORM(db.AnaliseTec, int(id_da_analise), readonly=True , showid=False,
         formstyle='table3cols')
    else:
        db.AnaliseTec.Protocolo.default = id_do_processo  if id_do_processo else None
        formanalise = SQLFORM(db.AnaliseTec)

    if formanalise.process().accepted:
        response.flash = f'Analise do Processo Atualizada' if id_da_analise else f'Analise do Processo Registrada'
        redirect(URL(c='default', f='Analises', vars={'id_do_processo':formanalise.vars.Protocolo}))
    elif formanalise.errors:
        response.flash = "Verifique os erros no formulário"
    else:
        pass

    busca = db((db.AnaliseTec.Protocolo == id_do_processo) & (db.AnaliseTec.Protocolo == db.Processos.id) & (db.Tarefas.Protocolo == db.Processos.id) )

    fields_grd= [db.AnaliseTec.id, db.Processos.id, db.AnaliseTec.Protocolo, db.AnaliseTec.DocsProcesso,  db.AnaliseTec.CamposProcesso, db.AnaliseTec.TipoAnalise, db.AnaliseTec.Obs ]
    db.AnaliseTec.id.readable = False
    db.Processos.id.readable = False

    links= [
        dict(header='Processos', body=lambda row: A('Processo', _href=URL(c='default', f='Processos', 
        args=row.Processos.id, vars={'f':'ver'}))) ,
        dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Analises',
         args=row.AnaliseTec.id, vars={'f':'ver', 'id_do_processo': id_do_processo}),    cid=request.cid, client_side=True))] 

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links, editable=False, 
                        searchable=False, deletable=False, create=False, details=False,
                         csv=False,  maxtextlength = 140, _class="table", user_signature=False, args=request.args[:1], paginate=10)


    if id_do_processo:
        return response.render(dict(formanalise=formanalise, id_da_tarefa=id_da_tarefa, id_da_analise=id_da_analise, id_do_processo=id_do_processo , grade=grade))
    else:
        return response.render(dict(formanalise=formanalise, id_da_tarefa=id_da_tarefa, id_da_analise=id_da_analise, grade=grade))


@cache.action()
def Lista_de_Registros():
    import re
    REGEX = re.compile('^(\w+).(\w+).(\w+)\=\=(\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error'))

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=session.controller, f=table, args=row.id, vars={'f': 'ver'})))]

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False, deletable=False, create=False,csv=False,
    represent_none='', maxtextlength = 120, _class="table"), table=table)


def Gerador_de_Docs():
    import geradocspy
    import os
    from pathlib import Path
    
    formmodarq = SQLFORM.factory(Field('Arq_mod', type='upload', label='Procurar Modelo'), table_name='formmodarq'
        )

    tables = [tab for tab in db.tables if not 'auth' in tab]

    formprocessos = SQLFORM.factory( Field('Protocolo', requires=IS_IN_DB(db, 'Processos.id', db.Processos._format)), table_name='formprocessos')

    formregis = ''

    if formprocessos.process(tablename='formprocessos' ).accepted:
        pass

    if formmodarq.process(tablename='formmodarq').accepted:
        pasta = Path(request.folder,)
        arquivo_mod = Path(pasta,  'uploads', Path(formmodarq.vars.Arq_mod))
        session.Arq_mod = arquivo_mod
        response.flash = "Enviando Arquivo de Modelo."
        try:
            conteudo = geradocspy.ler_o_arq_modelo(session.Arq_mod)
            campos = geradocspy.pegar_campos_do_modelo(conteudo)
            campos_form = [A(c.replace('{', '').replace('}', '') ) for c in campos]
            #formulario = SQLFORM.factory(*campos_form, formstyle='table3cols', formname='formbusca')
            formulario = UL(*campos_form)

        except OSError as e:
            session.flash = "Erro ao enviar arquivo: Error:{} : {}".format(pasta, session.Arq_mod)


        

    return dict(formmodarq=formmodarq, formprocessos=formprocessos, formregis=formregis) if not 'formulario' in locals() else \
        dict(formmodarq=formmodarq, formulario=formulario, formprocessos=formprocessos, formregis= formregis)



# def Pessoa_selector():
#     if not request.vars['Nome']:
#         return ''  
#     pattern= request.vars['Nome']
#     selected= [row.Nome for row in db(db.Pessoas.Nome.contains(pattern)).select(limitby=(0, 10))]

#     return DIV(*[DIV(k,
#                  _onclick="jQuery('#Pessoas_Nome').val('%s')" % k,
#                  _onmouseover="this.style.backgroundColor='yellow'",
#                  _onmouseout="this.style.backgroundColor='white'"
#                  ) for k in selected], )

