# -*- coding: utf-8 -*-

# ---------------------CONFIGURAÇÕES INICIAIS-------------------------------

from gluon.contrib.appconfig import AppConfig # type: ignore
from gluon.tools import Auth # type: ignore
from configs import pasta_viveiro_fotos # type: ignore
from my_validador import * # type: ignore
import datetime

if 0==1:
    from gluon import * # type: ignore
    from gluon import (db, IS_IN_SET, IS_UPPER, HTTP, IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, IS_LENGTH,  DAL, IS_INT_IN_RANGE, IS_EMPTY_OR,  # type: ignore
    IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, auth, Auth, Field, pegaDof) # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore



if request.global_settings.web2py_version < "2.27.1":
   raise HTTP(500, "Requires web2py 2.27.1 or newer")
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------

configuration = AppConfig(reload=False)
# session.connect(request, response, cookie_key=configuration.take("db")['password'],)
# session.secure()
# session.samesite('Strict')



# - Banco Produção 
if configuration.get('app.production'):
    db = DAL('{}://{}:{}@{}/{}'.format(
                configuration.take("db")['engine'],
                configuration.take("db")['username'],
                configuration.take("db")['password'],
                configuration.take("db")['uri'],
                configuration.take("db")['database'] ) ,
            pool_size=50,
            migrate_enabled=True, migrate=False, fake_migrate_all=False, lazy_tables=True,
            check_reserved=['mysql'], adapter_args={'safe': True},
            )


# Banco Teste
else:
    db = DAL(configuration.take("db")['uri'], #type: ignore
                pool_size=50,
                migrate_enabled=True,
                migrate=True, 
                fake_migrate_all=True, 
                lazy_tables=True,
                check_reserved=[configuration.take("db")['engine']],
                adapter_args={'safe': True},
            )

#db._adapter.types = copy.copy(db._adapter.types)
db._adapter.types['boolean']='TINYINT(1)'
db._adapter.TRUE = 1
db._adapter.FALSE = 0


# -------------------------------------------------------------------------
# Padrões Genéricos
# -------------------------------------------------------------------------
response.generic_patterns = []
#if request.is_local and not configuration.get('app.production'):
response.generic_patterns.append('*')


# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''


# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'


# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'


# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------


# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth( db, host_names=configuration.get('host.names') )


# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------


auth.settings.extra_fields['auth_user'] = [
    Field('IdDepto', 'integer'), # type: ignore
]

auth.define_tables(username=True,  
                   migrate=True if not configuration.get('app.production') else False,   
                   fake_migrate=True if not configuration.get('app.production') else False, )


#auth.settings.update_fields = [ 'first_name', 'last_name', 'username', 'email', 'IdDepto']
auth.settings.remember_me_form = False


# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------

from gluon.tools import Mail # type: ignore
from gluon.html import XML # type: ignore

import logging

class DebugMail(Mail):
    def send(self, to, subject, message, **kwargs):
        try:
            result = super().send(to, subject, message, **kwargs)
            logging.info(f"Email sent successfully to {to}")
            return result
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise

auth.settings.mailer = DebugMail()

mail = auth.settings.mailer
mail.settings.server = configuration.get('smtp.server') # 'logging' if request.is_local else
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = f"{configuration.get('smtp.username')}:{configuration.get('smtp.password')}" #configuration.get('smtp.login')
mail.settings.tls = True
mail.settings.ssl = False


# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True


# -------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')



# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
# if configuration.get('scheduler.enabled'):
#     from gluon.scheduler import Scheduler
#     scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

auth.wiki(resolve=False)


regiao_cor ={1:'CENTRAL', 2:'BOSQUE', 3:'TALHADO', 4:'REPRESA', 5:'VILA TONINHO', 6:'SCHIMITT',
7:'HB', 8:'CIDADE DAS CRIANÇAS', 9:'PINHEIRINHO' , 10:'CÉU'}


#BANCO LOCAIS

Bairros = ['Bairros',
   	Field ('Bairro', 'string', notnull=True, requires=IS_UPPER()),
	Field ('Regiao', 'integer',requires= IS_IN_SET(regiao_cor, zero=None)),
    dict(format = '%(Bairro)s')
]


Enderecos = ['Enderecos',
    Field ('Cep', 'integer',),
	Field ('Logradouro', 'string', label= 'Logradouro'),
    Field ('idBairro', 'reference Bairros', label='Bairro'),
	Field ('Num'),
	Field ('Quadra', 'string', ),
	Field ('Lote', 'string'),
    Field ('Complemento', 'string'),
	Field ('Tipo', 'string',
     requires=IS_IN_SET([None,'-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LOJA.','CASA','MARGINAL.'])),
	Field ('Complemento', 'string', ),
	Field ('TipoB', 'string', default= '-',
     requires= IS_IN_SET([None,'-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LOJA.','CASA','MARGINAL.']),
     label='outro tipo'),
	Field ('ComplementoB',  'string', default= '-', label='Outro compl.'),
    dict(format= '%(IdLogradouro)s - %(Num)s ')
]


#PESSOAS
Pessoas = ['Pessoas',
	Field ('Nome', 'string', length= 115, notnull=True, requires=[IS_MATCH('.*[a-zA-Z].*', error_message='Deve possuir ao menos uma letra.')] ),
	Field ('Idm', 'integer' ),
    Field ('CPF', 'string', unique=True),
    Field ('CNPJ', 'string', unique=True),
    Field ('IdEndereco', 'reference Enderecos', label="Endereço"),
	Field ('Telefone', 'string'),
	Field ('celular', 'string'),
	Field ('Email', 'string', requires=IS_EMPTY_OR(IS_LOWER())), # type: ignore
	Field ('Categoria', 'text'),
    Field ('RegistroProf', 'string'),
    dict(format= '%(Nome)s - %(CPF)s')
]


Dpto = ['Dpto',
	Field('Idm', 'id'),
	Field('Departamento', 'string', required=True),
	Field('Orgao', 'reference Dpto'),
	Field('Telefone', 'string'),
    dict(format='%(Departamento)s')
]


Servicos = ['Servicos',
    Field('Servico', 'string', label='Serviço'),
    Field('Dpto', 'reference Dpto', label='Departamento'),
    dict(format='%(Servico)s')
]


Processos = ['Processos',
    Field('Protocolo',  'string', unique=True, notnull=True,),
    Field('IdPessoa',  'reference Pessoas' , label= 'Pessoa'),
    Field('IdDpto', 'reference Dpto' , label='Departamento'),
    Field('DataReg', 'datetime', label = 'Data de Registro',
     default=datetime.datetime.now(),  writable=False),
    Field('IdTipo', 'reference Servicos',label='Tipo' ),
    Field('Assunto', 'string'),
    Field('IdCateg', 'integer', label = 'Categoria'),
    dict(format='%(Protocolo)s')
]


lista_de_tabelas = [Bairros, Enderecos, Pessoas, Dpto, Servicos, Processos]


for tabela in lista_de_tabelas:
    nome_tabela = tabela[0]       # primeiro elemento é o nome da tabela (string)
    kwargs = tabela[-1]
    
    if isinstance(kwargs, dict):
        campos = tabela[1:-1] 
        if not nome_tabela in db.tables:
            db.define_table(nome_tabela, *campos, **kwargs)
    else:
        campos = tabela[1:] 
        if not nome_tabela in db.tables:
            db.define_table(nome_tabela, *campos)


#define_tabelas_em_lote(lista_de_tabelas)
  

def endereco_represent(row):
    repr_endereco = db((db.Enderecos.id == int(row.id)) &
     (db.Enderecos.idBairro == db.Bairros.id)).select(db.Enderecos.Logradouro,
     db.Enderecos.Num, db.Enderecos.Quadra, db.Enderecos.Lote, db.Bairros.Bairro,
      orderby=db.Enderecos.Logradouro).first()
    Num = 'Nº: S/N' if repr_endereco.Enderecos.Num in ['NULL', None, '-'] else str(repr_endereco.Enderecos.Num)
    Qd =  ',  Qd: ' + str(repr_endereco.Enderecos.Quadra) if repr_endereco.Enderecos.Quadra else ''
    Lt =  ',  Lt: ' + str(repr_endereco.Enderecos.Lote) if repr_endereco.Enderecos.Lote else ''
    
    if repr_endereco:
        endereco =  str(repr_endereco.Enderecos.Logradouro) + ', ' \
            + Num  + Qd   + Lt  + ',   Bairro: ' + str(repr_endereco.Bairros.Bairro)
        return endereco
    else:
        return ''


def pessoa_represent(row):
    Nome = db.Pessoas(db.Pessoas.id == int(row.id)).Nome
    CPF = db.Pessoas(db.Pessoas.id == int(row.id)).CPF
    if Nome:
        pessoa = '{} - {}'.format(str(Nome) ,  str(CPF))
        return pessoa
    else:
        return ''

try:
    db.Pessoas.CPF.requires= [IS_EMPTY_OR(IS_CPF_OR_CNPJ()), IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CPF', error_message='Já existe uma Pessoa com este Número de CPF'))]
    db.Pessoas.CNPJ.requires= [IS_EMPTY_OR(IS_CPF_OR_CNPJ()), IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CNPJ', error_message='Já existe uma Empresa com este Número de CNPJ'))]
except Exception as e:
    print(f'Erro em requires {e}')


db.Enderecos.Endereco = Field.Virtual(
    "Endereco",
    lambda row: str(
        ", ".join(
            [
                f"{row.Enderecos.Logradouro}" or "",
                f"Nº {row.Enderecos.Num}" or ""
            ]
        )
    ),
)


db.Pessoas.IdEndereco.requires = IS_EMPTY_OR(IS_IN_DB(db, 'Enderecos.id', endereco_represent))
db.Processos.Protocolo.requires= [IS_NOT_IN_DB(db, 'Processos.Protocolo', error_message='Protocolo já Existe'), CLEANUP()] # type: ignore
db.Pessoas.CPF.filter_out = lambda row: MASK_CPF()(row) if row else ''
db.Pessoas.CNPJ.filter_out = lambda row: MASK_CNPJ()(row) if row else ''



db.Pessoas.Nome_repr = Field.Virtual(
    "Nome_repr",
    lambda row: str(" - ".join([ f"{row.Pessoas.Nome}" or "", f"{row.Pessoas.CPF}" or "" ])),
    )
