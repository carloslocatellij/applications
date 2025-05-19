from my_validador import *  # type: ignore

if 0 == 1:
    from gluon import *  # type: ignore
    from gluon import (
        db, configuration, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
        Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db, IS_CHKBOX01, DAL, IS_INT_IN_RANGE, IS_CPF_OR_CNPJ,  MASK_CPF,
        MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE, SQLFORM, IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC, )  # type: ignore

    request = current.request  # type: ignore
    response = current.response  # type: ignore
    session = current.session  # type: ignore
    cache = current.cache  # type: ignore
    T = current.T  # type: ignore


# Tabela para armazenar os modelos de despacho
db.define_table('despacho_template',
    Field('nome', 'string', required=True, label='Nome do Modelo'),
    Field('texto', 'text', required=True, label='Texto do Modelo'),
    Field('descricao', 'text', label='Descrição'),
    Field('tipo', 'string', requires=IS_IN_SET([
        'particular_deferido', 'particular_indeferido', 
        'publico_deferido', 'publico_indeferido',
        'pendencia_anuencia', 'pendencia_alvara',
        'denuncia_poda', 'denuncia_supressao'
    ])),
    Field('condicoes', 'json', 'list:string',
        requires=IS_IN_SET(db.Requerimentos.fields ,  multiple=True),
        label='Condições de Aplicação'),
    format='%(nome)s'
)

db.define_table('despacho_variaveis',
    Field('template_id', 'reference despacho_template'),
    Field('nome_variavel', 'string', label='Nome da Variável'),
    Field('descricao', 'text', label='Descrição'),
    Field('fonte_dados', 'string', label='Fonte de Dados',
          requires=IS_IN_SET(['query', 'relation_query', 'query_protoc_ref'])),
    Field('campo_dados', 'string', label='Campo de Dados'),
    Field('valor_padrao', 'string', label='Valor Padrão')
)