# coding: utf-8
#!/usr/bin/python3.8


#### Este namespace serve apenas para a IDE enchergar e trabalhar com os itens abaixo
if 0==1:
    from gluon import *
    from gluon import db, SQLFORM, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB,\
     IS_MATCH, redirect, URL, FORM_CPF
    from gluon import XML, a_db, db, auth, Auth, Field, buscador,\
     analise_de_residuos_projedatos, geradocspy, scrap_aprova_dig_
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
#### ----------------------------------------------------------------------------------

mensagem_contrução = "Em Contrução! 🛠"


import re


labels = {'Obras.Protocolo':'Obra no Protoc.' , 'Obras.protocolo_dof': 'Obra com DOF',
          'Obras.protocolo_grcc': 'Analise GRCC Obra' ,'Licenca.Protocolo': ' Licenças ',
          'AnaliseTec.Protocolo': ' Análises ','TransportadorStatus.Protocolo':' Transportador ',
          'Pgrcc.Protocolo':' PGRCC ', 'Tarefas.Protocolo': ' Tarefas ', 'Pgrcc.protocolo': 'PGRCC',
          'Publicidades.Protocolo':  'Publicidades','Pgrcc.IdGerador': 'Gerador PGR', 'Pgrcc.RespTecnico':'R. Téc. PGR' ,
          'UnidadeDestino.IdEmpreendedor':"Destinos", 'Transportadores.IdPessoa': 'Transportador',
        'Obras.IdGerador':"Obras",'Processos.IdPessoa':"Processos" , 'Licenca.IdEmpresa': "Licenças", }


class urlQuery:

    def __init__(self, arg, **kargs):
        self.args = arg.split('/')[-2:]
        print(f'args = {self.args}')
        self.argumento = ''
        self.func = ''
        self.kargs = kargs
        print(f'kargs = {self.kargs}')

        try:
            argumentos = self.args[-1].split('?')
        except Exception as e:
            print(f'Não há elemento query: {e}')
        else:
            try:
                self.argumento = str(int(argumentos[0])) if argumentos[0].startswith('?') else '/'+str(int(argumentos[0]))
                self.func = self.args[0]
            except:
                self.func = argumentos[0]
                itens = argumentos[-1].split('&')
                for item in itens:
                    self.kargs[item.split('=')[0]] =item.split('=')[-1]



        print(f'função = {self.func}')

        self.ctrl = request.env.HTTP_REFERER.split('/')[0] if request.controller != 'default' else ''
        print(f'controler = {self.ctrl}')


        self.string_kargs = '?'+'&'.join([f'{k}={v}' for k,v in self.kargs.items()]) if len(self.kargs) > 0 else ''
        print(f'str kargs = {self.string_kargs}')

    def __repr__(self):
        str_final = '/'+self.func+self.argumento+self.string_kargs
        print(f'str final = {str_final}')
        return  str_final
        #return  self.origem+'/'+self.ctrl+'/'+self.func+self.string_args+self.string_kargs


def define_botao_processo(titulo, controlador, funcao, **kwargs):
    return DIV(A("Registrar "+titulo, _href= URL(
            c=controlador,
            f=funcao, vars=kwargs),
            _class="btn btn-success"))


@auth.requires_login()
def index():
    response.flash = T("Bem Vindo!")

    num_de_protoc = db(db.Processos.IdDpto == 1024412).count()
    num_de_obras =  db(db.Obras.id > 0).count()
    num_de_pgrccs = db(db.Pgrcc.id > 0).count()
    num_de_dofs =   db(db.DofsObra.id > 0).count()

    numeros_do_dpto = dict(número_de_processos=num_de_protoc ,número_de_obras=num_de_obras,
                           número_de_pgrccs=num_de_pgrccs, número_de_dofs=num_de_dofs)


    tabela_de_numeros = dict(Processos = TABLE(*[TR(line) for line in numeros_do_dpto.items()], ))


    return dict(sistema=T('Sistema de Dados do Dpto. de Qualidade Ambiental!'), numeros_do_dpto=numeros_do_dpto)


@auth.requires_login()
def wiki():
    from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2
    from gluon.contrib.markdown import WIKI as markdown
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
#     return my_html

    meu_mark ='''
# Meu Titulo

## Outro Titulo

* <input type="checkbox" checked="checked" /> 1
* <input type="checkbox" checked="checked" /> 2
* <input type="checkbox" /> 3


    '''
    markdowner = Markdown2(html4tags=True, tab_width=4, )
    meu_mark = markdowner.convert(meu_mark)


    return dict(wiki = auth.wiki() ,mark = XML(meu_mark))

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
@auth.requires_login()
def  download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)




@auth.requires_login()
def Logradouros(): #Menu
    """
    Formulário de logradouros, com função de registro e modificação, podendo ser chamado
     em outros formulários com Load()
    """

    logradouro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        formlogr = SQLFORM(db.Logradouros, logradouro, )
    elif f=='ver':
        formlogr = SQLFORM(db.Logradouros, logradouro, readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller], ) ,
        labels = {'Enderecos.IdLogradouro': 'Endereços'} )
    else:
        formlogr = SQLFORM(db.Logradouros, formstyle='bootstrap3_stacked' )

    if formlogr.process().accepted:
        session.flash = f'Logradouro Atualizado' if logradouro else f'Logradouro Registrado'
        logradouro = formlogr.vars.id
        redirect(URL('default','Logradouros.html', args=[logradouro],vars={'f':'ver'} ), client_side=True)
    elif formlogr.errors:
        session.flash = f'Corrija os erros indicados'
    else:
        pass

    formxbusca = buscador( 'Logradouros', Logradouro={'label':'Logradouro'},
                         Cep= {'label':'CEP' },
                         IdBairro= {'label':'Bairro' })

    return response.render(dict(formlogr=formlogr, logradouro=logradouro, formxbusca=formxbusca))


@auth.requires_login()
def Bairros(): #Menu
    """
    Formulário de Bairros, com função de registro e modificação, podendo ser chamado
     em outros formulários com Load()
    """

    bairro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    db.Bairros.IdCidade.default = 9999

    if f=='editar':
        formbairro = SQLFORM(db.Bairros, bairro, formstyle='bootstrap3_stacked')
    elif f=='ver':
        formbairro = SQLFORM(db.Bairros, bairro, readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller], ) ,
         labels = {'Logradouros.IdBairro': 'Logradouros'}, formstyle='bootstrap3_stacked' )
    else:
        formbairro = SQLFORM(db.Bairros, formstyle='bootstrap3_stacked' )

    if formbairro.process().accepted:
        response.flash = f'Bairro Atualizado' if bairro else f'Bairro Registrado'
        bairro = formbairro.vars.id
        redirect(URL('default','Logradouros.html', vars={'f':'ver', 'bairro_id': formbairro.vars.id}, extension = '' ), client_side=True)
    elif formbairro.errors:
        session.flash = f'Corrija os erros indicados'
    else:
        pass

    formbusca = buscador( 'Bairros', Bairro={'label':'Bairro'},
                         Regiao= {'label':'Região' })

    return response.render(dict(formbairro=formbairro, bairro=bairro, formbusca=formbusca))


@auth.requires_login()
def Enderecos(): #Menu
    # session.connect(request, response, cookie_key=',.~~Grnt861@10.7.0.28',)
    # session.secure()
    # session.samesite('Strict')
    """
    .../default/Enderecos (Formulário de endereços, com função de registro)
    .../default/Enderecos/{id}?f=editar (função de edição de registro)
    .../default/Enderecos/{id}?f=ver (função de visualização de registro)
    Contém um buscador definido por formbusca = buscador('tabela', 'função',**campos) - definido em 0_estruct.py
    """
    import re

    endereco = request.args(0) if request.args(0) else request.vars['endereco_id']
    logradouro = request.vars.logradouro
    if logradouro:
        db.Enderecos.IdLogradouro.default = logradouro

    f = request.vars['f'] if request.vars['f']  else None
    if f=='editar':
        form = SQLFORM(db.Enderecos, endereco, formname='formendereco' , submit_button='Atualizar Endereço')
    elif f=='ver':
        form = SQLFORM(db.Enderecos, endereco, formname='formendereco' ,  readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller], ) ,
         labels = {'Pessoas.IdEndereco':"Pessoas", 'Obras.IdEndereco':"Obras",
         'UnidadeDestino.IdEndereco': 'Destinos', 'Licenca.IdEndereco': "Licenças"} )
    else:
        form = SQLFORM(db.Enderecos, formname='formendereco', submit_button='Registrar Endereço')


    if form.validate():

        query = ( ( (db.Enderecos.IdLogradouro == form.vars.IdLogradouro) &
        (db.Enderecos.Quadra == form.vars.Quadra) & (db.Enderecos.Lote == form.vars.Lote) & (db.Enderecos.Num == None)) |
        ((db.Enderecos.IdLogradouro == form.vars.IdLogradouro) &
        (db.Enderecos.Num == form.vars.Num) & (db.Enderecos.Quadra == None) &
        (db.Enderecos.Lote == None)) |
        ((db.Enderecos.IdLogradouro == form.vars.IdLogradouro) & (db.Enderecos.Quadra == form.vars.Quadra) &
        (db.Enderecos.Lote == form.vars.Lote) & (db.Enderecos.Num == form.vars.Num)))

        idx = db(query)
        existe_registros = bool(len(idx.select()))

        if endereco:
            db.Enderecos.validate_and_update(db.Enderecos.id == endereco, **dict(form.vars))
            db.commit()

        else:
            db.Enderecos.validate_and_update_or_insert(query, **dict(form.vars))
            db.commit()


        if request.env.HTTP_WEB2PY_COMPONENT_LOCATION != None:
            if endereco:
                session.flash = 'Dados atualizados'
            elif existe_registros:
                session.flash = 'Endereço já existente!, Dados atualizados! Considere acessar o registro já existente em "Ligações" para dar continuidade ao processo registrando os dados faltantes.'
            else:
                session.flash = 'Endereço Registrado. Aguarde a página recarregar!'

            url = str(urlQuery(request.env.HTTP_REFERER, endereco_id = str(idx.select().first().id)))
            x = re.split(r"(\d{1,3}.\d{1,2}.\d{1,2}.\d{1,2}:\d{3,4}/)",url)
            xurl = ''.join(url)

            redirect(xurl, client_side=True, )
        else:
            session.flash = 'Dados atualizados' if endereco else 'Endereço Registrado. Aguarde a página recarregar!'
            request.vars['f'] = 'ver'

    elif form.errors:
        response.flash = 'Corrija os dados indicados.'
    else:
        pass

    formbusca = buscador('Enderecos',  Logradouro={'label':'Logradouro', 'table':'Logradouros'},
                            Cep= {'type':'integer',  'label':'CEP',  'table':'Logradouros'},  )

    return response.render(dict(form=form, formbusca=formbusca, endereco=endereco))


@auth.requires_login()
def Obras(): #Menu
    """Formulário de obras, com função de registro e modificação, contendo subformulários para pessoas e endereços"""
    # response.headers['Cache-Control'] = 'public, max-age=360'
    # response.headers['Expires'] = (datetime.utcnow() + timedelta(hours=0.1)).strftime('%a, %d %b %Y %H:%M:%S GMT')

    try:
        obra = int(request.args(0))
    except:
        obra = None

    f = request.vars['f'] or None
    gerador_id = None
    resptec = request.vars.pessoa_id
    pessoa_id = resptec

    db.Obras.Finalidade.requires = IS_IN_SET(['COMERCIAL','DIVERSIFICADA','EDIFICIO COMERCIAL','EDUCACIONAL',
    'HOTELEIRA','LOTEAMENTO','RELIGIOSA','RESIDENCIAL MULTIFAMILIAR','RESIDENCIAL UNIFAMILIAR','SAUDE - MEDICINA'])
    redirect_button_pgrcc = None
    redirect_button_agrc = None

    if obra:
        query_obra = db.Obras(db.Obras.id == obra)
        if query_obra:
            gerador_id = query_obra.IdGerador
            pessoa_id = query_obra.resptecnico
            processo_id = query_obra.Protocolo or None
            redirect_button_pgrcc = define_botao_processo('PGRCC', 'default', 'Pgrcc',
            obra_id=obra,gerador_id=gerador_id, processo_id=processo_id)
            redirect_button_agrc = define_botao_processo('Analise_GRCC', 'default', 'Analise_GRCC',
            obra_id=obra,  processo_id=processo_id)
            endereco_id = query_obra.IdEndereco or None
        else:
            session.flash = "Não encontrado!"
            redirect(URL(c='default', f='Obras'))

    else:
        resptec = request.vars.pessoa_id or resptec
        gerador_id = db.Obras.IdGerador.default = request.vars.gerador_id  or  None
        processo_id = db.Obras.Protocolo.default = request.vars.processo_id or None
        endereco_id = db.Obras.IdEndereco.default = request.vars.endereco_id or  None
        db.Obras.IdEndereco.writable = False if not obra else True

    if f=='editar':
        formobra= SQLFORM(db.Obras, obra, submit_button='Atualizar Obra')
    elif f=='ver':
        formobra= SQLFORM(db.Obras, obra, readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller], ),
         labels = {'Pgrcc.idobra': 'PGRCCs da Obra', 'DofsObra.IdObra': 'DOFs', 'Analise_GRCC.idobra': 'Análise dos Resíduos' })
    else:
        formobra= SQLFORM(db.Obras, submit_button= 'Registrar Obra')

    if formobra.process(keepvalues=True).accepted:
        response.flash =  f'Obra Registrada'
        redirect(URL(c='default', f='Obras', args=[formobra.vars.id], vars={'f': 'ver'}))
    elif formobra.errors:
        response.flash = f'Corrija os erros indicados.'

    formbusca = SQLFORM.factory(
        Field('Gerador'),
        Field('Alvara'),
        Field('Cadastro'),
        Field('Endereco'),
        Field('Bairro'),
        Field('Protocolo'),
         formstyle='table3cols', formname='formbusca')

    if formbusca.process().accepted:
        session.buscaGerador =  formbusca.vars.Gerador
        session.buscaAlvara  = formbusca.vars.Alvara
        session.buscaCad = formbusca.vars.Cadastro
        session.buscaEndereco = formbusca.vars.Endereco
        session.buscaBairro = formbusca.vars.Bairro
        session.buscaProtoc = formbusca.vars.Protocolo
        response.flash = 'Exibindo dados para: ',str(session.Nome)
    elif formbusca.errors:
        response.flash = 'Erro no formulário'
    else:
        pass

    if session.buscaGerador:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (
        db.Pessoas.Nome.contains(session.buscaGerador.strip())))
        session.buscaGerador = None
    elif session.buscaAlvara:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (
        db.Obras.Alvara == session.buscaAlvara.strip()))
        session.buscaAlvara = None
    elif session.buscaCad:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (
        db.Obras.CadMunicipal.contains(session.buscaCad[1:-3].strip() )))
        session.buscaCad = None
    elif session.buscaEndereco:
        busca = db((db.Obras.IdEndereco == db.Enderecos.Id) & (
        db.Enderecos.IdLogradouro == db.Logradouros.Id) &
        (db.Logradouros.Logradouro.contains(session.buscaEndereco.strip())))
        session.buscaEndereco = None
    elif session.buscaBairro:
        busca = db((db.Obras.id > 0) & (db.Obras.IdEndereco == db.Enderecos.id) &
         (db.Enderecos.IdLogradouro == db.Logradouros.id ) &
         (db.Logradouros.IdBairro == db.Bairros.Id) & (db.Bairros.Bairro.contains(session.buscaBairro.strip())))
        session.buscaProtoc = None
    elif session.buscaProtoc:
        busca = db(
         (db.Processos.Protocolo.contains(session.buscaProtoc.strip()) ) &\
         ((db.Obras.Protocolo == db.Processos.id) | (db.Obras.protocolo_dof == db.Processos.id) | (db.Obras.protocolo_grcc == db.Processos.id))
        )
        session.buscaProtoc = None
    else:
        busca = db((db.Obras.IdGerador == db.Pessoas.Id) & (db.Obras.IdGerador < 0))

    fields_grd= [db.Pessoas.Nome, db.Obras.CadMunicipal ,db.Obras.IdEndereco,
    db.Obras.AreaTerreno, db.Obras.AreaConstrExecutar, db.Obras.Finalidade]

    links= [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Obras',
        args=row.Obras.id if 'Obras' in row else row.id , vars={'f':'ver'}, )))]

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, field_id=db.Obras.Id,
     links=links, editable=False,     searchable=False, deletable=False, create=False,
     details=False, csv=False,  maxtextlength = 120, _class="table", user_signature=False, )


    try:
        botao_despacho = define_botao_processo('Despacho' ,'Ferramentas', 'Despachar_Processos', processo=processo_id)
    except:
        botao_despacho = None


    obra_no_endereco = db(db.Obras.IdEndereco == endereco_id).select().first() if endereco_id else ''
    if obra_no_endereco:
        obra_no_endereco = obra_no_endereco.id

    return response.render(dict(formobra=formobra, formbusca=formbusca, grade=grade,
        botao_despacho = botao_despacho , obra=obra or None, gerador_id=gerador_id,
        pessoa_id=pessoa_id, processo_id=processo_id, endereco_id=endereco_id,
        redirect_button_pgrcc = redirect_button_pgrcc if request.vars['f'] == 'ver' else None,
        redirect_button_agrc = redirect_button_agrc if request.vars['f'] == 'ver' else None,
        obra_no_endereco= obra_no_endereco),
        stream=True)


def DofsObras():
    """Formulário de DOFs por Obra (vinculado por Id), com função de registro e modificação,
     contendo subformulários para DOFs e Modulo para importar dados do arquivo html de dof salvo"""


    # DofsObra = db.define_table('DofsObra',
    #     Field('id','id'),
    #     Field('IdDof','string', notnull=True, unique=True, label='DOF' ),
    #     Field('IdObra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id',
    #     db.Obras._format, )),
    #     #auth.signature,
    #     )


    # MadeirasDof = db.define_table ('MadeirasDof',
    #     Field('Id', 'id'),
    #     Field('IdDof', 'string', requires=IS_IN_DB(db, 'DofsObra.IdDof',
    #     db.DofsObra._format, ),  notnull=True),
    #     Field('Item', 'integer',required=True),
    #     Field('Produto', 'text', length=45, required=True),
    #     Field('Especie', 'text', length=55, required=True),
    #     Field('Popular', 'text', length=35, required=True),
    #     Field('Qtd', 'decimal(10,4)',required=True ),
    #     Field('Unidade', 'text', length=2, required=True),
    #     Field('Valor', 'text', length=10, required=True),
    #     #fake_migrate=True,
    #     )

    import pegaDof # type: ignore
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

    formarq = SQLFORM.factory(Field('arquivo', 'upload',
     label="Inserir a página html salva em seu computador."), formstyle='table3cols' )

    dofpego =''
    if formarq.process().accepted:
        response.flash = 'Enviado, aguarde'
        session.arquivo = formarq.vars.arquivo

        try:
            dofpego = pegaDof.pegaquali('file:///{}/{}'.format(
            str(os.path.join(request.folder, 'uploads')), session.arquivo))
        except:
            session.flash = 'Erro ao processar o arquivo enviado'
        try:
            os.remove('{}/{}'.format(str(os.path.join(request.folder, 'uploads')), session.arquivo))
        except OSError as e:
            session.flash = "Erro na remoção do arquivo do server: Error:{} : {}".format(e.strerror,
             str(os.path.join(request.folder, 'uploads')), session.arquivo)

        for i in dofpego[0]:
            try:
                db.MadeirasDof.insert(IdDof= dofpego[1], Item= int(i['Nº']), Produto= i['Produto'],
                 Especie= i['Espécie'], Popular= i['Nome Popular'],
                 Qtd= float(i['Quantidade'].replace(',','.')), Unidade= i['Unidade'], Valor= i['Valor Item'])
            except Exception as e:
                #session.flash = f"Erro com o Número do DOF:"
                session.flash = f"Erro ao inserir registro a partir do arquivo: Erro {e} no item {i['Nº']}"
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
        dofs_da_obra = db.DofsObra.IdObra == obra
        madeiras_do_dof = db.DofsObra.IdDof == db.MadeirasDof.IdDof
        madeiras = db(dofs_da_obra & madeiras_do_dof)
        volume_mad =  madeiras.select(db.MadeirasDof.Qtd.sum().with_alias('SomaMadeira'))
        vol = volume_mad[0]['SomaMadeira']
        fields = [db.MadeirasDof.IdDof, db.MadeirasDof.Item, db.MadeirasDof.Produto, db.MadeirasDof.Especie,
            db.MadeirasDof.Popular, db.MadeirasDof.Qtd, db.MadeirasDof.Unidade, db.MadeirasDof.Valor]

        madeirasgrade = SQLFORM.grid(madeiras, fields=fields,
            orderby='IdObra', editable=False, searchable=False,
            deletable=False, create=False, details=False, maxtextlength = 120,
             csv=False, user_signature=False, _class='table',
               args = request.args[:1])

        dofsgrade = SQLFORM.grid(db(dofs_da_obra),
            fields=[db.DofsObra.IdDof], orderby='IdDof', editable=True,
            searchable=False, deletable=False, create=False, details=False,
            field_id=db.DofsObra.id, maxtextlength = 120,
            csv=False, user_signature=False, _class='table',
            formargs = {'field_id': db.DofsObra.id}, onvalidation=updatedof,
            args = request.args[:1] ) # args = request.args[:1]

    if obra:
        return response.render(dict(formdof=formdof, dofsgrade=dofsgrade, madeirasgrade=madeirasgrade,
            obra=obra, vol=vol or '', formarq=formarq))
    else:
        return response.render(dict(formdof=formdof, iddof=session.iddof, ))



@auth.requires_login()
def Pgrcc(): #Menu
    """Formulário de PGRCC, com função de registro e modificação"""
    #TODO: a verificação de conformidade, atualmente é feita apenas para área a construir, deve considerar demolição

    pgr = request.args(0) or None
    gerador = request.get_vars.gerador_id or None
    obra = request.get_vars.obra_id or None
    protocolo = request.get_vars.processo_id or None
    resptec = request.get_vars.pessoa_id
    db.Pgrcc.idgerador.default = gerador
    db.Pgrcc.idobra.default = obra
    db.Pgrcc.protocolo.default = protocolo
    db.Pgrcc.protocolo.writable = False if protocolo else True
    db.Pgrcc.idobra.writable = False if obra else True

    f = request.vars['f'] if request.vars['f']  else None
    sigor = None
    if pgr:
        sigor = db.Pgrcc(db.Pgrcc.id == int(pgr)).sigor

    linksigor = A('Sigor' , _href=f'https://ctre.com.br/painel/fiscal/aprovacao-de-pgr-rcc-detalhes/{sigor}'
    ) if sigor else None

    if f=='editar':
        formpgr = SQLFORM(db.Pgrcc, pgr , detect_record_change=True,  deletable=False, ignore_rw=False )
    elif f =='ver':
        formpgr = SQLFORM(db.Pgrcc, pgr , readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller]),  labels = {} )
    else:
        formpgr = SQLFORM(db.Pgrcc )
    cls_a = ''

    if formpgr.process().accepted:

        response.flash = f'PGRCC Atualizado' if pgr else f'PGRCC Registrado'
        redirect(URL('default', 'Pgrcc', args=[formpgr.vars.id], vars={'f':'ver'} ))
    elif formpgr.errors:
        response.flash = f'Erro na Registro do PGRCC'

    cls_a = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_a if pgr else None
    cls_b = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_b if pgr else None
    cls_d = db.Pgrcc(db.Pgrcc.id == int(pgr)).cls_d if pgr else None

    if pgr:
        analise = analise_de_residuos_projedatos(pgr)
    else:
        analise = {'analise_res':{'A':'','B':'','D':''}}

    #TODO: Criar Buscador de Pgrcc
    #TODO: Verificar se buscar por sigor funciona
    formbusca = buscador('Pgrcc',  Protocolo={'label':'Protocolo', 'table':'Processos'},
                                    sigor= {'type':'integer',  'label':'Sigor',  'table':'Pgrcc'},  )


    return response.render(dict(formpgr=formpgr, obra=obra, pgr=pgr, cls_a=cls_a,
     cls_b=cls_b, cls_d=cls_d,
     analise=analise['analise_res']), formbusca=formbusca,  linksigor=linksigor,
     protocolo=protocolo, obra=obra, pessoa=gerador)


@auth.requires_login()
def Pessoas(): #Menu
    import re
    """Formulário de Pessoas, com função de registro e modificação"""

    if request.args(0):
        pessoa = db.Pessoas(request.args(0)).id
    elif request.vars.get('pessoa_id'):
        pessoa = request.vars['pessoa_id']
    else:
        pessoa = None

    f = request.vars.get('f') or None

    if f =='editar':
        formpessoa = SQLFORM(db.Pessoas, int(pessoa), formname='formpessoa', submit_button='Atualizar Pessoa')
    elif f =='ver':
        formpessoa = SQLFORM(db.Pessoas, pessoa , formname='formpessoa', readonly=True, linkto=URL(c='acessorios',
        f='Lista_de_Registros', args=['db', request.controller], ) , labels = labels )
    else:
        formpessoa = SQLFORM(db.Pessoas, formname='formpessoa', submit_button='Registrar Pessoa')

    if formpessoa.process().accepted:
        if request.env.HTTP_WEB2PY_COMPONENT_LOCATION != None:
            session.flash = 'Dados atualizados' if pessoa else 'Pessoa Registrada. Aguarde a página recarregar!'
            url = str(urlQuery(request.env.HTTP_REFERER, pessoa_id=formpessoa.vars.id))
            x = re.split(r"(\d{1,3}.\d{1,2}.\d{1,2}.\d{1,2}:\d{3,4}/)",url)
            xurl = ''.join(url)
            redirect(xurl, client_side=True)
        else:
            session.flash = 'Dados atualizados' if pessoa else 'Pessoa Registrada. Aguarde a página recarregar!'
            request.vars['f'] = 'ver'

    elif formpessoa.errors:
        response.flash = 'Corrija os dados indicados.'
    else:
        pass


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
    #TODO: Verificar sanitização para melhorar as pesquisas tirando caracteres não alphanumericos
    if session.buscaNome:
        busca = db(db.Pessoas.Nome.contains(session.buscaNome) )
        session.buscaNome = None
    elif session.buscaCPF:
        busca = db(db.Pessoas.CPF.contains(session.buscaCPF))
        session.buscaCPF = None
    elif session.buscaCNPJ:
        busca = db(db.Pessoas.CNPJ.contains(session.buscaCNPJ))
        session.buscaCNPJ = None
    else:
        busca = db(db.Pessoas.id < 0)


    fields_grd= [db.Pessoas.Id, db.Pessoas.Nome, db.Pessoas.CPF ,
     db.Pessoas.CNPJ, db.Pessoas.Telefone,
      db.Pessoas.celular, db.Pessoas.Email,]


    links= [dict(header='Ver', body=lambda row: A('Ver',
            _href=URL(c='default', f='Pessoas', args=row.Id, vars={'f':'ver'})))]


    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links,
        editable=False, searchable=False, deletable=False, create=False, details=False,
        csv=False,  maxtextlength = 120, _class="table", user_signature=False)



    return response.render(dict(formpessoa=formpessoa, pessoa=pessoa, formbusca=formbusca, grade=grade,))



@auth.requires_login()
def Processos(): #Menu
    tipo_id = None
    pessoa_id = session.pessoa_id or request.vars['pessoa_id'] or  None
    processo = request.args(0)
    if processo:
        tipo_id = db.Processos(db.Processos.id == request.args(0)).IdTipo
        pessoa_id = db.Processos(db.Processos.id == request.args(0)).IdPessoa
        try:
            processo = int(processo)
        except (ValueError, TypeError):
            processo = None

    fields = ['Protocolo','IdPessoa','DataReg', 'IdDpto', 'IdTipo', 'Assunto']

    db.Processos.IdDpto.default = 1024412

    f = request.vars.get('f') or None

    if f=='editar' and processo:
        formprocess = SQLFORM(db.Processos, record=db.Processos(processo),
        url=URL('default', 'Processos', args=[processo], vars={'f':'editar'}, host=True),
         linkto=URL(c='acessorios', f='Lista_de_Registros', args=['db', request.controller]),
         labels = labels , _formname='formprocesso_edit',  submit_button='Atualizar Processo')

    elif f=='ver' and processo:
        formprocess = SQLFORM(db.Processos, record=db.Processos(processo),
        url=URL('default', 'Processos', args=[processo], vars={'f':'ver'}, host=True),
        readonly=True, showid=True,
         linkto=URL(c='acessorios', f='Lista_de_Registros', args=['db', request.controller],  ),
         labels = labels  , _formname='formprocesso_ver')
        
    else:
        formprocess = SQLFORM(db.Processos, fields=fields, _formname='formprocesso', submit_button='Registrar Processo')


    if formprocess.validate(dbio=False, keepvalues=True):
        if f == 'editar' and processo:
            processo_id= db(db.Processos.id == processo).update(**dict(
                IdPessoa=formprocess.vars.IdPessoa,
                Protocolo=formprocess.vars.Protocolo,
                DataReg=formprocess.vars.DataReg,
                IdDpto=formprocess.vars.IdDpto,
                IdTipo=formprocess.vars.IdTipo,
                Assunto=formprocess.vars.Assunto ))
            redirect(URL('default', 'Processos', args=[processo_id], vars={'f':'ver'}))
        else:
            processo_id= db.Processos.insert(**formprocess.vars)
            response.flash= f'Dados do protocolo atualizados' if processo else f'Protocolo Registrado'
            redirect(URL('default', 'Processos', args=[processo_id], vars={'f':'ver'}))

    elif formprocess.errors:
        print("URL:", request.url)
        print("Application:", request.application)
        print("Controller:", request.controller)
        print("Function:", request.function)
        print("Args:", request.args)
        print("Vars:", request.vars)
        print("Form attributes:", formprocess.attributes)
        response.flash = 'Corrija os Erros indicados'
    else:
        pass

    if tipo_id in [3 , 4 , 17]:
        redirect_button = define_botao_processo('Obra', 'default', 'Obras',
         gerador_id=pessoa_id, processo_id=processo)
    elif tipo_id == 15:
        redirect_button = define_botao_processo('Transportador', 'Transportadores', 'Cadastro_de_Transportador',
         pessoa_id=pessoa_id, processo_id=processo)
    elif tipo_id in [18, 19, 20]:
        redirect_button = define_botao_processo('Licença de Destino', 'Destinos', 'Registro_de_Licencas',
         pessoa_id=pessoa_id, processo_id=processo)
    elif tipo_id == 16:
        redirect_button = define_botao_processo('Licença de Publicidade', 'default', 'Publicidades',
         processo_id=processo)

    else:
        session.processo_id = formprocess.vars.id
        redirect_button = None

    formbusca = SQLFORM.factory(
        Field('Pessoa'),
        Field('Protocolo')
        , formstyle='table3cols', formname='formbusca')
        #Field('Tipo', 'integer', requires = IS_IN_SET(servicos))

    if formbusca.process().accepted:
        session.buscaPessoa =  formbusca.vars.Pessoa
        session.buscaProtocolo  = formbusca.vars.Protocolo
        #session.buscaTipo = formbusca.vars.Tipo
        response.flash = 'Exibindo dados para: ',str(session.Pessoa)

    if session.buscaPessoa:
        busca = db((db.Processos.IdPessoa == db.Pessoas.Id) & (
        db.Pessoas.Nome.contains(session.buscaPessoa.strip() ) ) )
        if 'buscaPessoa' in session:
            del(session.buscaPessoa, session.buscaProtocolo)
    elif session.buscaProtocolo:
        busca = db((db.Processos.IdPessoa == db.Pessoas.Id) & (
        db.Processos.Protocolo.contains(session.buscaProtocolo.strip() )))
        if 'buscaPessoa' in session:
            del(session.buscaPessoa, session.buscaProtocolo)
    else:
        busca = db(db.Processos.Protocolo == '')
        if 'buscaPessoa' in session:
            del(session.buscaPessoa, session.buscaProtocolo)

    fields_grd= [db.Processos.id ,db.Processos.Protocolo, db.Processos.IdPessoa,
    db.Pessoas.Telefone, db.Processos.IdTipo, db.Processos.DataReg ]

    links= [
        dict(header='Pessoa', body=lambda row: A('Pessoa', _href=URL(c='default',
         f='Pessoas', args=row.Processos.IdPessoa, vars={'f':'ver'}))),
        dict(header='Ver',    body=lambda row: A('Ver', _href=URL(c='default',
         f='Processos', args=row.Processos.id, vars={'f':'ver'})))]

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links,
     editable=False, searchable=False, deletable=False, create=False, details=False,
      csv=False,  maxtextlength = 120, _class="table", user_signature=False,)

    return response.render(dict(formprocess=formprocess, processo=processo,
     formbusca=formbusca, grade=grade, pessoa_id= pessoa_id,
     redirect_button = redirect_button if request.vars['f'] == 'ver' else None))


@auth.requires_login()
def Publicidades(): #Menu

    #TODO: id do Endereco não está sendo pega pelo campo no form
    #TODO: Busca por protocolo não está funcionando
    #TODO: id do Resp. tec não está sendo pega pelo campo do form
    #TODO: O editor está alterando o padrão (tipo do dado) das dimensões e isto quebra o registro

    publicidade = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    processo_id = request.vars.processo_id or session.processo_id or None
    session.processo_id = cache.ram('processo_id', lambda: processo_id, time_expire=35)
    pessoa_id = request.vars.pessoa_id or session.pessoa_id or None
    session.pessoa_id = cache.ram('pessoa_id', lambda: pessoa_id, time_expire=35)
    endereco_id = request.vars.endereco_id or session.endereco_id or None
    session.endereco_id = cache.ram('endereco_id', lambda: endereco_id, time_expire=35)
    db.Publicidades.Protocolo.default = processo_id or None
    db.Publicidades.IdEndereco.default = endereco_id or None
    db.Publicidades.resptecnico.default = pessoa_id or None

    if f=='editar':
        formpublicidade = SQLFORM(db.Publicidades, publicidade, showid=True )

    elif f=='ver':
        formpublicidade = SQLFORM(db.Publicidades, publicidade, readonly=True, showid=True,
         linkto=URL(c='acessorios', f='Lista_de_Registros', args=['db', request.controller],  ),
         labels = {'Tarefas.Protocolo': ' Tarefas '} )

    else:
        formpublicidade = SQLFORM(db.Publicidades)


    if formpublicidade.process().accepted:
        response.flash = f'Dados da publicidade atualizados' if publicidade else f'Publicidade Registrada'
        redirect(URL('default', 'Publicidades', args=[formpublicidade.vars.id], vars={'f':'ver'}))

    elif formpublicidade.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    formbusca = buscador( 'Publicidades', Protocolo = {'label':'Protocolo'},
                                          resptecnico = {'label':'Responsável Técnico' })

    return response.render(dict(formpublicidade=formpublicidade, formbusca=formbusca, publicidade=publicidade))


@auth.requires_login()
def Criar_Tarefa():
    id_do_processo = request.args(0) or None
    protoc = db.Processos(db.Processos.id == id_do_processo).Protocolo
    user= auth.user_id or db.auth_user(db.auth_user.id == auth.user_id).id
    tipo = db.Processos(db.Processos.id == id_do_processo).IdTipo
    interessado =  db((db.Pessoas.id == db.Processos.IdPessoa) &
     (db.Processos.id == id_do_processo)).select(db.Pessoas.Nome).last().Nome
    tarefa_nome = '{} - {}'.format(interessado, protoc)
    inexiste = db(db.Tarefas.Protocolo == id_do_processo).isempty()

    if inexiste is False:
        session.flash = 'Já existe uma Tarefa para o Protocolo {}'.format(protoc)
        redirect(URL('default', 'Processos', args=[id_do_processo], vars={'f':'ver'} ))
    if id_do_processo and inexiste:
        id = db.Tarefas.insert(Titulo=tarefa_nome ,Protocolo=id_do_processo,
        Responsavel=user, Tipo=tipo)
        session.processo_id = None
        redirect(URL('default', 'Tarefas', args=[id]))


@auth.requires_login()
def Lista_de_Tarefas(): #Menu
    user = auth.user_id
    tipos = db(db.Servicos.Dpto == db.auth_user.IdDepto)

    tarefas = [ db((db.Tarefas.Protocolo == db.Processos.id) & (db.Tarefas.Tipo == tipo ) &
       (db.Processos.IdPessoa == db.Pessoas.Id) & (db.Tarefas.Responsavel == user) )\
        for tipo in tipos.select('Servicos.id',  distinct=True,
        ) if not db(db.Tarefas.Tipo == tipo).isempty()]

    headers = {'Tarefas.Protocolo': 'Protocolo', 'Pessoas.Nome': 'Nome',
    'Tarefas.Responsavel': 'Responsável', 'Tarefas.DataFim': 'Data Final',
    'Tarefas.Tipo': 'Tipo', 'Tarefas.checklist': 'Check-list',
    'Tarefas.Status': 'Status', 'Ver':'Ver'}
    fields = [db.Tarefas.id, db.Tarefas.Protocolo, db.Pessoas.Nome, db.Tarefas.Responsavel,
     db.Tarefas.DataFim, db.Tarefas.Tipo, db.Tarefas.checklist, db.Tarefas.Status]
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
    links= [dict(header='Editar', body=lambda row: A('Editar', _href=URL(c='default', f='Tarefas',
     args=row.Tarefas.id , vars={'f':'editar'}))),
            dict(header='Estado', body=lambda row: A(B(row.Tarefas.Status), _class='card',
             _align="center" ,_style= estilo_do_status(row.Tarefas.Status))) ]

    tabelas_tarefas =  [DIV(B(tarefa.select(db.Tarefas.Tipo, distinct=True ) ,
     #A('Ver Todos', _href=URL(c='default', f='Lista_de_Tarefas',  vars={'show_all':'True' if not show_all else None}))
     ),
     DIV(SQLFORM.grid(tarefa , links=links,  editable=False,
        searchable=True, deletable=False, create=False, details=False,  csv=False,
         orderby=~db.Tarefas.Status,   headers=headers, fields=fields,
         maxtextlength = 80, paginate=15 if not show_all else None,_class="web2py_grid"),
        _class="flex-box" ) ,  _class="card") for  tarefa in tarefas]

    return response.render(tabelas_tarefas=tabelas_tarefas)


@auth.requires_login()
def Tarefas(): #Menu
    id_da_tarefa = request.args(0) or None
    request.vars.id_da_tarefa = id_da_tarefa

    if id_da_tarefa:
        id_do_processo = db.Tarefas(db.Tarefas.id == id_da_tarefa).Protocolo or None
        request.vars.id_do_processo = id_do_processo
        protoc_tarefa = db.Processos(db.Processos.id == int(id_do_processo)).Protocolo or None
        request.vars.protoc_tarefa = protoc_tarefa

        if id_do_processo:
            dados_obra = db(db.Obras.Protocolo == id_do_processo).select( 'CadMunicipal', 'AreaTerreno',
             'AreaConstrExist', 'AreaConstrDemolir', 'AreaConstrExecutar', cache=(cache.ram, 900) )
            headers=dict(CadMunicipal='CadMunicipal', AreaTerreno='Área do Terreno',
             AreaConstrExist='Área Existente', AreaConstrDemolir='Área a demolir',
             AreaConstrExecutar='Área a Executar')
            dados_obra=SQLTABLE(dados_obra,  headers=headers, _class="table" ,
            _style="border: 2px solid; padding: 5px; word-wrap:break-word; color: darkslategray;",)
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

        formtarefa=SQLFORM(db.Tarefas, id_da_tarefa,  linkto=URL( c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller],  ), labels={} )
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

    busca = db(db.Tarefas.Titulo.contains(session.buscaTarefa)
    ) if session.buscaTarefa else db(db.Tarefas.id <0)
    db.Tarefas.id.readable = False
    db.Tarefas.Protocolo.readable = False
    db.Tarefas.checklist.readable = False

    links = [dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Tarefas',
     args=row.id, vars={'f': 'ver'})))]

    grade = SQLFORM.grid(busca, represent_none='', links=links, editable=False,
     searchable=False, deletable=False, create=False, details=False, csv=False,
     maxtextlength=120, _class="table", user_signature=False,)

    if id_da_tarefa:
        return dict(formtarefa=formtarefa, formbusca=formbusca, grade=grade,
         id_do_processo=id_do_processo, id_da_tarefa=id_da_tarefa,
         id_da_analise=id_da_analise, dados_obra=dados_obra)
    else:
        return dict(formtarefa=formtarefa, formbusca=formbusca, grade=grade)


@auth.requires_login()
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

    busca = db((db.AnaliseTec.Protocolo == id_do_processo) & (
    db.AnaliseTec.Protocolo == db.Processos.id) & (db.Tarefas.Protocolo == db.Processos.id) )

    fields_grd= [db.AnaliseTec.id, db.Processos.id, db.AnaliseTec.Protocolo,
      db.AnaliseTec.DocsProcesso, db.AnaliseTec.CamposProcesso,
      db.AnaliseTec.TipoAnalise, db.AnaliseTec.Obs ]
    db.AnaliseTec.id.readable = False
    db.Processos.id.readable = False

    links= [
        dict(header='Processos', body=lambda row: A('Processo', _href=URL(c='default', f='Processos',
        args=row.Processos.id, vars={'f':'ver'}))) ,
        dict(header='Ver', body=lambda row: A('Ver', _href=URL(c='default', f='Analises',
         args=row.AnaliseTec.id, vars={'f':'ver', 'id_do_processo': id_do_processo}),
         cid=request.cid, client_side=True))]

    grade = SQLFORM.grid( busca, represent_none='',fields=fields_grd, links=links,
                 editable=False, searchable=False, deletable=False, create=False,
                 details=False, csv=False, maxtextlength = 140, _class="table",
                 user_signature=False, args=request.args[:1], paginate=10)

    if id_do_processo:
        return response.render(dict(formanalise=formanalise, id_da_tarefa=id_da_tarefa,
         id_da_analise=id_da_analise, id_do_processo=id_do_processo, grade=grade))
    else:
        return response.render(dict(formanalise=formanalise, id_da_tarefa=id_da_tarefa,
        id_da_analise=id_da_analise, grade=grade))




def Analise_GRCC(): #Menu

    analise_grcc = request.args(0) or request.vars['analise_grcc'] or None
    f = request.vars['f'] if request.vars['f']  else None
    obra = request.get_vars.obra_id or None

    if not analise_grcc:
        protocolo = request.get_vars.processo_id or None
        #db.Pgrcc(db.Pgrcc.idobra == obra)
        db.Analise_GRCC.idobra.default = obra
        #db.Analise_GRCC.idpgrcc.default = protocolo
    else:
        obra = db.Analise_GRCC(db.Analise_GRCC.id == analise_grcc).idobra
        protocolo = db.Analise_GRCC(db.Analise_GRCC.id == analise_grcc).idpgrcc


    if f=='editar':
        formanalise_grcc = SQLFORM(db.Analise_GRCC, analise_grcc, formstyle='bootstrap3_stacked', submit_button="Salvar")
    elif f=='ver':
        formanalise_grcc = SQLFORM(db.Analise_GRCC, analise_grcc, readonly=True, linkto=URL(c='acessorios',
         f='Lista_de_Registros', args=['db', request.controller], ) ,
         labels = {}, formstyle='bootstrap3_stacked', separator=':___')
    else:
        formanalise_grcc = SQLFORM(db.Analise_GRCC, formstyle='bootstrap3_stacked' )

    if formanalise_grcc.process(keepvalues=True).accepted:
        response.flash = f'Análise Atualizada' if  analise_grcc == request.args(0) else None
        analise_grcc = formanalise_grcc.vars.id
        redirect(URL('default','Analise_GRCC.html', vars={'f':'ver', 'analise_grcc': formanalise_grcc.vars.id}, extension = '' ), client_side=True)
    elif formanalise_grcc.errors:
        session.flash = f'Corrija os erros indicados'
    else:
        pass

    formbusca = buscador( 'Analise_GRCC', idpgrcc={'label':'Protocolo PGRCC'},)

    return dict(formanalise_grcc=formanalise_grcc, analise_grcc=analise_grcc, formbusca=formbusca, obra_id=obra, protocolo=protocolo)




def solo_a_destinar(): #Menu
    pgrs_vol = db((db.Pgrcc.idobra == db.Obras.Id) & (db.Obras.Corte > db.Obras.Aterro) &
     (db.Processos.id == db.Obras.Protocolo) & (db.Enderecos.Id == db.Obras.IdEndereco))

    fields = [db.Obras.Protocolo, db.Obras.IdGerador, db.Obras.CadMunicipal ,
    db.Obras.Corte, db.Obras.Aterro ,db.Processos.DataReg, db.Obras.IdEndereco]
    links = [dict(header='Ver',
    body = lambda row: A('Maps', _href=
    f'https://www.google.com/maps/search/{endereco_represent(row.Obras.IdEndereco)}' )), # type: ignore
    dict(header='Vol', body= lambda row: (row.Obras.Aterro - row.Obras.Corte))
    ]

    table = SQLFORM.grid(pgrs_vol, links=links, fields=fields,user_signature=False,
    editable=False, searchable=False, details=False,  deletable=False, create=False,
    csv=True, represent_none='', maxtextlength = 120, paginate=50, _class="table")

    return response.render(dict(table=table))