# -*- coding: utf-8 -*-

if 0==1: # Este namespace serve apenas para a IDE enchergar e trabalhar com os itens abaixo
    from gluon import * # type: ignore
    from gluon import (db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, IS_EMAIL, # type: ignore
     IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, IS_CPF_OR_CNPJ,  MASK_CNPJ, Remove_Acentos, IS_LENGTH,
     IS_DECIMAL_IN_RANGE, IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC)
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore
    
from pathlib import Path



# --------------------MODELOS DO BANCO DE DADOS --------------------------------

db.define_table('disparos_de_email',
    Field('status', default='pending', requires=IS_IN_SET(['pending', 'sent', 'failed', 'retry'])),
    Field('destinatario', 'string', requires=IS_EMAIL()),
    Field('assunto', 'string', length=255),
    Field('mensagem', 'text'),
    Field('mensagem_html', 'text'),  # Para e-mails HTML
    Field('record_id', 'integer'),  # ID do registro que gerou o e-mail
    Field('record_table', 'string'), # Nome da tabela do registro
    Field('anexos', 'string'),
    Field('tentativas', 'integer', default=0),
    Field('max_tentativas', 'integer', default=3),
    Field('created_on', 'datetime', default=request.now),
    Field('sent_on', 'datetime'),
    Field('error_message', 'text'),
    Field('prioridade', 'integer', default=1),  # 1=alta, 2=média, 3=baixa
    format='%(subject)s (%(status)s)'
)


db.define_table('email_templates',
    Field('nome', 'string', unique=True),
    Field('assunto', 'string'),
    Field('corpo', 'text'),
    Field('html_corpo', 'text'),
    Field('descricao', 'text'),
    format='%(name)s'
)


db.define_table('Requerimentos',
Field('IdProcesso', 'reference Processos', requires= IS_IN_DB(db, 'Processos.id', '%(Protocolo)s')),
Field('IdEndereco', 'reference Enderecos', requires= IS_IN_DB(db, 'Enderecos.id',)), # type: ignore
Field('IdProtocolo_de_Ref'),
Field('Status'),
Field('Obs'),
auth.signature,
migrate=True
# ->Qtd_Req_Supress (virt.)
# ->Qtd_Req_Poda (virt.)
    
)


db.define_table('Vistoria',
    Field('IdProcesso', 'reference Processos', requires= IS_IN_DB(db, 'Processos.id', '%(Protocolo)s')),
    Field('Data', 'datetime'),
    Field('Vistoriante', 'string'),
    Field('Assunto', 'string'),
    Field('Descricao', 'string'),
    Field('obs', 'text'),
                )




fotos = db.define_table('fotos',
    Field('titulo'),
    Field('foto', 'upload',               
            uploadseparate=True, uploadfolder= Path(pasta_viveiro_fotos, session.function if session.function else 'Outras_fotos')  , # type: ignore
            requires=[IS_EMPTY_OR(IS_LENGTH( 7864320, 20480, error_message= 'deve ser maior que 20k e menor que 7,5 megabites')),
                        IS_IMAGE_COMPACT( error_message='deve ser imagem no formato jpeg ou png')], autodelete = True,   # type: ignore
            ),
    Field('caminho', 'string'),
    Field('idEspecie', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Especies.id', "%(Nome)s"))),
    Field('idLaudo', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Laudos.Protocolo', "%(Protocolo)s")), ),
    Field('fonte', 'string'),
    Field('url', 'string'),
    Field('tipo', label='tipo da foto'),
    Field('obs', 'text'),
    Field('created_by', default=auth.user_id,
            label='Registrado por:',
            represent = lambda row, val: authdb.auth_user(authdb.auth_user.id== row).first_name), # type: ignore
    Field('created_on', label='Registrado em:', default=request.now),
    Field('modified_by', update=auth.user_id,
            label='Modificado por:',
            represent = lambda row, val: authdb.auth_user(authdb.auth_user.id== row).first_name if row else ''), # type: ignore
    Field('modified_on', label='Modificado em:', default=request.now, update=request.now), 
    migrate= True if not configuration.get('app.production') else False, # type: ignore
    fake_migrate= True if not configuration.get('app.production') else False, # type: ignore
                )



# DADOS DE TESTE INSERIDOS AUTOMÁTICAMENTE EM AMBIENTE DE TESTE.
if not configuration.get("app.production"): # pyright: ignore[reportUndefinedVariable]

    from faker import Faker  # type: ignore

    fake = Faker("pt_BR")
    if not db(db.Bairros).count():
        db.Bairros.insert(
            Bairro="ALTO RIO PRETO (JARDIM)", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALVORADA (ESTANCIA)",  Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="AMERICA (JARDIM)",  Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALICE (JARDIM)", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ANCHIETA (VILA)",  Regiao=fake.random_int(min=1, max=10)
        )

        
    
    if not db(db.Enderecos).count():
        pass
            
            
    if not db(db.Pessoas).count() >1:
        for _ in range(1, 180):
            db.Pessoas.insert(Nome=fake.name(), CPF=fake.cpf(), IdEndereco=fake.random_int(min=1, max=15),
                              Telefone=fake.phone_number()
                
            )
    # if not db(db.Processos).count():
    #     for _ in range (1, 25):
    #         db.Processos.insert(
    #             Protocolo=fake.random_number(fix_len=True, digits=7,),
                
    #         )
    
    db.commit()
    
    