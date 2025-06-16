from my_validador import *  # type: ignore
import json

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
    Field('descricao', 'string', label='Descrição'),
    Field('condicoes', 'json', 
        label='Condições de Aplicação'),
    format='%(nome)s'
)


def dict_condicoes_de_templates():
    dict_condicoes = {}
    dict_textos = {}
    templates_conds = db(db.despacho_template.id > 0).select('id', 'condicoes', 'texto')
    
    for item in templates_conds.as_dict().items():
        if templates_conds.as_dict()[item[0]].get('_extra').get('condicoes'):
            conjunto_condicoes = json.loads(templates_conds.as_dict()[item[0]].get('_extra').get('condicoes'))
            dict_condicoes[item[1]['_extra'].get('id')  ] = conjunto_condicoes
            dict_textos[item[1]['_extra'].get('id')] = templates_conds.as_dict()[item[0]].get('_extra').get('texto')
        
    return dict_condicoes, dict_textos
            
    

def determinar_despacho(req):
    possiveis_despachos = []
    
    if req.get('Laudos'):
        dict_req = {'Despacho': req.get('Laudos').get('Despacho'),
                    'tipo_imovel': req.get('Requerimentos').get('tipo_imovel'),
                    'protocolo_anterior': req.get('Requerimentos').get('protocolo_anterior'),
                    'total_podas': req.get('Laudos').get('total_podas'),
                    'total_supressoes': req.get('Laudos').get('total_supressoes'),
                    'qtd_repor': req.get('Laudos').get('qtd_repor'),
                    'local_arvore': req.get('Requerimentos').get('local_arvore'),
                    'proprietario': req.get('Laudos').get('proprietario'),
                    'tecnico': req.get('Laudos').get('tecnico'),
                    'motivos': req.get('Laudos').get('motivos')
                    }
    else:
        dict_req = {'Despacho': req.get('Despacho'),
                    'tipo_imovel': req.get('tipo_imovel'),
                    'protocolo_anterior': req.get('protocolo_anterior'),
                    'total_podas': req.get('total_podas'),
                    'total_supressoes': req.get('total_supressoes'),
                    'local_arvore': req.get('local_arvore'),
                    }
    
    condic_templates, condic_txt = dict_condicoes_de_templates()
    
    for id , condicionais in condic_templates.items():
        condicoes_verificadas = {}
        condicionais = [condicionais] if not isinstance(condicionais, list) else condicionais
        for condicoes in condicionais:
            condic_campo = condicoes.get("campo")
            operador = condicoes.get('operador')
            condic_valor = condicoes.get("valor")
            if condic_campo not in dict_req.keys():
                condicoes_verificadas[condic_campo] =  False
            else:
                for campo, valor in dict_req.items():
                    if isinstance(condic_valor, str) and condic_valor.isnumeric():
                        condic_valor = int(condic_valor)
                    if isinstance(valor, str) and valor.isnumeric():
                        valor = int(valor)
                    if valor is None and operador not in ['=', '!=']:
                        continue    
                    if campo == condic_campo:
                        if operador == '=':
                                condicoes_verificadas[condic_campo] =  True if valor == condic_valor else False
                        elif operador == '!=':
                                condicoes_verificadas[condic_campo] =  True if valor != condic_valor else False
                        elif operador == '<':
                                condicoes_verificadas[condic_campo] =  True if valor < condic_valor else False
                        elif operador == '>':
                                condicoes_verificadas[condic_campo] =  True if valor > condic_valor else False
                        elif operador == '<=':
                                condicoes_verificadas[condic_campo] =  True if valor <= condic_valor else False
                        elif operador == '>=':
                                condicoes_verificadas[condic_campo] =  True if valor >= condic_valor else False 
                        else:
                            condicoes_verificadas[condic_campo] =  False
                           
        if len(condicoes_verificadas) > 0 and all(condicoes_verificadas.values()) and not id in possiveis_despachos:
            possiveis_despachos.append((id, condic_txt.get(id)))
                   
    return possiveis_despachos
                

def Despachar(prime_query, relation_query=None, query_protoc_ref=None):
    if not prime_query:
        print('Deve ser passado ao menos uma query válida')
        return None
    # 1. Determinar o tipo de despacho
    
    chaves_de_despacho = determinar_despacho(prime_query if not relation_query else relation_query)

    if not chaves_de_despacho:
        return ['Não foi possível determinar o modelo de despacho para este caso.']

    # 3. Preparar o contexto de dados (variáveis para o template)
    contexto = {}

# Adicionar dados brutos e campos virtuais de 'query' (Requerimentos)
# Os nomes das chaves no contexto DEVEM corresponder aos placeholders no template
    if prime_query:
        contexto['Protocolo'] = prime_query.get('Protocolo')
        contexto['Requerente'] = prime_query.get('Requerente')
        contexto['Endereco'] = prime_query.get('Endereco') # Campo Virtual
        contexto['data_do_laudo'] = prime_query.get('data_do_laudo').strftime('%d/%m/%Y') if prime_query.get('data_do_laudo') else ''
        contexto['total_podas'] = prime_query.get('total_podas') # Campo Virtual
        contexto['total_supressoes'] = prime_query.get('total_supressoes')
        contexto['Podas'] = prime_query.get('Podas')
        contexto['Supressoes'] = prime_query.get('Supressoes') # Campo Virtual
        contexto['num_extens_poda'] = prime_query.get('num_extens_poda')
        contexto['num_extens_supressoes'] = prime_query.get('num_extens_supressoes')
        
    if relation_query:
        contexto['tecnico'] = relation_query.get('Laudos').get('tecnico') or 'XXXXXXXXXXXXXX'
        contexto['tecnico'] = contexto['tecnico'].upper()
        contexto['data_do_laudo'] = relation_query.get('Laudos').get('data_do_laudo').strftime('%d/%m/%Y') if relation_query.get('data_do_laudo') else ''
        contexto['proprietario'] = relation_query.get('Laudos').get('proprietario')
        contexto['morador'] = relation_query.get('Laudos').get('morador')
        contexto['total_podas'] = relation_query.get('Laudos').get('total_podas') # Campo Virtual
        contexto['total_supressoes'] = relation_query.get('Laudos').get('total_supressoes')
        contexto['num_extens_poda'] = relation_query.get('Laudos').get('num_extens_poda')
        contexto['num_extens_supressoes'] = relation_query.get('Laudos').get('num_extens_supressoes')
        contexto['Supressoes'] = relation_query.get('Laudos').get('Supressoes') # Campo Virtual de Laudos
        contexto['Podas'] = relation_query.get('Laudos').get('Podas') # Campo Virtual de Laudos
        contexto['Obs'] = relation_query.get('Laudos').get('Obs')
        contexto['qtd_repor'] = relation_query.get('Laudos').get('qtd_repor')
        contexto['porte_repor'] = relation_query.get('Laudos').get('porte_repor')
        contexto['num_extens_repor'] = relation_query.get('Laudos').get('num_extens_repor')
        
    if query_protoc_ref:
        if query_protoc_ref.get('Laudos'): # Se a referência tem dados de Laudos
            contexto['Protocolo'] = query_protoc_ref.get('Laudos').get('Protocolo')
            contexto['Requerente'] = query_protoc_ref.get('Requerente')
            contexto['Endereco'] = query_protoc_ref.get('Endereco') # Campo Virtual
            contexto['total_podas'] = query_protoc_ref.get('Laudos').get('total_podas') # Campo Virtual
            contexto['total_supressoes'] = query_protoc_ref.get('Laudos').get('total_supressoes')
            contexto['Podas'] = query_protoc_ref.get('Laudos').get('Podas')
            contexto['Supressoes'] = query_protoc_ref.get('Laudos').get('Supressoes') # Campo Virtual
            contexto['num_extens_poda'] = query_protoc_ref.get('Laudos').get('num_extens_poda')
            contexto['num_extens_supressoes'] = query_protoc_ref.get('Laudos').get('num_extens_supressoes')
            contexto['tecnico'] = query_protoc_ref.get('Laudos').get('tecnico','').upper() or 'XXXXXXXXXXXXXX'
            data_laudo_ref_obj = query_protoc_ref.get('Requerimentos', {}).get('data_do_laudo')
            if data_laudo_ref_obj:
                    contexto['data_do_laudo'] = data_laudo_ref_obj.strftime('%d/%m/%Y')

        else: # Se a referência tem dados de Requerimentos
            contexto['Protocolo'] = query_protoc_ref.get('Protocolo')
            contexto['Requerente'] = query_protoc_ref.get('Requerente')
            contexto['Endereco'] = query_protoc_ref.get('Endereco') # Campo Virtual
            contexto['total_podas'] = query_protoc_ref.get('total_podas') # Campo Virtual
            contexto['total_supressoes'] = query_protoc_ref.get('total_supressoes') # Campo Virtual
            contexto['Podas'] = query_protoc_ref.get('Podas','')
            contexto['Supressoes'] = query_protoc_ref.get('Supressoes','')
            contexto['num_extens_poda'] = query_protoc_ref.get('num_extens_poda')
            contexto['num_extens_supressoes'] = query_protoc_ref.get('num_extens_supressoes')
            data_laudo_ref_obj = query_protoc_ref.get('data_do_laudo')
            if data_laudo_ref_obj:
                    contexto['data_do_laudo'] = data_laudo_ref_obj.strftime('%d/%m/%Y')
            contexto['tecnico'] = 'XXXXXXXXXXXXXX' # Default se não houver laudo na ref
        contexto['protocolo_anterior'] = prime_query.get('protocolo_anterior')


    Despachos = []
    for template in chaves_de_despacho:
        try:
            texto_final = template[1].format(**contexto)
            Despachos.append(texto_final)
        
        except KeyError as e:
            # Este erro é útil durante o desenvolvimento para achar placeholders não preenchidos
            return [str(f'''Erro ao popular o modelo {template}: 
                    A variável {str(e).strip("'")} não foi encontrada no contexto de dados. 
                    Verifique os placeholders do template e a preparação do contexto na função Despachar.''')]
        except Exception as e:
            return [f"Erro inesperado ao popular o modelo '{template}': {str(e)}"]
        
    return Despachos