# -*- coding: utf-8 -*-

if 0==1: # Este namespace serve apenas para a IDE enchergar e trabalhar com os itens abaixo
    from gluon import *
    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, IS_EMAIL,\
     IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, IS_CPF_OR_CNPJ,  MASK_CNPJ, Remove_Acentos,\
     IS_DECIMAL_IN_RANGE, IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T
    


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



# DADOS DE TESTE INSERIDOS AUTOMÁTICAMENTE EM AMBIENTE DE TESTE.
if not configuration.get("app.production"): # pyright: ignore[reportUndefinedVariable]

    from faker import Faker  # type: ignore

    fake = Faker("pt_BR")
    if not db(db.Bairros).count():
        db.Bairros.insert(
            Bairro="ALTO RIO PRETO (JARDIM)", IdCidade=1, Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALVORADA (ESTANCIA)", IdCidade=1, Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="AMERICA (JARDIM)", IdCidade=1,  Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALICE (JARDIM)", IdCidade=1, Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ANCHIETA (VILA)", IdCidade=1, Regiao=fake.random_int(min=1, max=10)
        )
    if not db(db.Logradouros).count():
        db.Logradouros.insert(Logradouro="Paulista", Cep=15012345, Denominacao="Av.", IdBairro=3, IdCidade=1)
        db.Logradouros.insert(Logradouro="Augusta", Cep=15012346,Denominacao="Rua", IdBairro=2, IdCidade=1)
        db.Logradouros.insert(Logradouro="Oscar Freire", Cep=15012347,Denominacao="Rua", IdBairro=1, IdCidade=1)
        db.Logradouros.insert(Logradouro="Teodoro Sampaio", Cep=15012348,Denominacao="Rua", IdBairro=4, IdCidade=1)
        db.Logradouros.insert(Logradouro="Jose Firmino", Cep=15012349,Denominacao="Rua", IdBairro=3, IdCidade=1)
        db.Logradouros.insert(Logradouro="Jose Fulano", Cep=15012350,Denominacao="Rua", IdBairro=2, IdCidade=1)
        db.Logradouros.insert(Logradouro="Ondina", Cep=15012351,Denominacao="Rua", IdBairro=2, IdCidade=1)
        
    
    if not db(db.Enderecos).count():
        for _ in range(1, 35):  
            db.Enderecos.insert(IdLogradouro=int(fake.random_choices([x['_extra']['id'] for x in db(db.Logradouros.id >0).select('id').as_list()], 1)[0]),
                                Num=fake.random_int(min=1, max=9999),
                                )
            
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
    
    