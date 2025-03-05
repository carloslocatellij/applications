
from datetime import datetime

if 0 == 1:
    from gluon import * # type: ignore
    from gluon import (db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01,
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE,
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC) # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore

tabela_solicitacoes = "tab_Solicitacoes"

Requerimentos = db.define_table('Requerimento',
    Field('Protocolo',),
    Field('Requerente'),
    Field('data_entrada' , rname='"Data de Entrada"'),
    Field('Endereco1'),
    Field('Numero1'),
    Field('Bairro'),
    Field('cpf_cnpj', rname= '"cpf-cnpj"'),
    Field('cep'),
    Field('telefone1'),
    Field('email', rname='"e-mail"'),
    Field('especie_ret1', rname='"especie ret1"'),
    Field('especie_ret2', rname='"especie ret2"'),
    Field('especie_ret3', rname='"especie ret3"'),
    Field('especie_ret4', rname='"especie ret4"'),
    Field('qtd_ret1', rname='"qtd ret1"'),
    Field('qtd_ret2', rname='"qtd ret2"'),
    Field('qtd_ret3', rname='"qtd ret3"'),
    Field('qtd_ret4', rname='"qtd ret4"'),
    Field('especie_poda1', rname='"especie poda1"'),
    Field('especie_poda2', rname='"especie poda2"'),
    Field('especie_poda3', rname='"especie poda3"'),
    Field('especie_poda4', rname='"especie poda4"'),
    Field('qtd_poda1', rname='"qtd poda1"'),
    Field('qtd_poda2', rname='"qtd poda2"'),
    Field('qtd_poda3', rname='"qtd poda3"'),
    Field('qtd_poda4', rname='"qtd poda4"'),
    Field('podador_coleta', rname='"podador coleta"'),
    Field('no_carteira', rname='"no. carteira"'),
    Field('data_do_laudo', rname='"data do laudo"'),
    Field('Despacho'),
    Field('local_arvore', rname='"local arvore"'),
    Field('tipo_imovel',rname='"tipo imovel"'),
    rname = f'''{tabela_solicitacoes}''',
    primarykey = ['Protocolo'],
    format='%(Protocolo)s',
    migrate=False,
    fake_migrate=False)

Bairros = db.define_table('Bairros',
    Field('Bairro', 'string'),
    Field('Perimetro', 'string'),
    Field('Area', 'string'),
    Field('Regiao', 'string')
    )