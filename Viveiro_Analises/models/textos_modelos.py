from gluon import widget
from gluon.packages.dal.pydal.validators import IS_LIST_OF
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

class DespachoTemplateProcessor:
    def __init__(self, db):
        self.db = db

    def get_template_by_conditions(self, query, relation_query=None):
        """
        Seleciona o template apropriado baseado nas condições do protocolo
        """
        tipo = self._determine_template_type(query, relation_query)
        template = self.db(self.db.despacho_template.tipo == tipo).select().first()
        return template if template else None

    def _determine_template_type(self, query, relation_query):
        """
        Determina o tipo de template baseado nas condições do protocolo
        """
        if not relation_query:
            if query.get('Despacho') == 'Deferido':
                if query.get('tipo_imovel') in ['privado', 'particular', 'próprio']:
                    return 'particular_deferido'
                elif query.get('tipo_imovel') == 'público':
                    return 'publico_deferido'
        # Adicionar mais condições conforme necessário
        return None

    def process_template(self, template, query, relation_query=None, query_protoc_ref=None):
        """
        Processa o template substituindo as variáveis pelos valores
        """
        if not template:
            return "Não foi possível gerar o texto do despacho."

        text = template.texto
        variables = self.db(self.db.despacho_variaveis.template_id == template.id).select()
        
        for var in variables:
            value = self._get_variable_value(var, query, relation_query, query_protoc_ref)
            text = text.replace(f"{{{var.nome_variavel}}}", str(value))
            
        return text

    def _get_variable_value(self, variable, query, relation_query, query_protoc_ref):
        """
        Obtém o valor de uma variável baseado em sua fonte de dados
        """
        if variable.fonte_dados == 'query':
            return query.get(variable.campo_dados, variable.valor_padrao)
        elif variable.fonte_dados == 'relation_query':
            return relation_query.get(variable.campo_dados, variable.valor_padrao) if relation_query else variable.valor_padrao
        elif variable.fonte_dados == 'query_protoc_ref':
            return query_protoc_ref.get(variable.campo_dados, variable.valor_padrao) if query_protoc_ref else variable.valor_padrao
        return variable.valor_padrao