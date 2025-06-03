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
    Field('descricao', 'string', label='Descrição'),
    Field('condicoes', 'text', 
        label='Condições de Aplicação'),
    format='%(nome)s'
)



def determinar_tipo_despacho_key(db, query, relation_query=None, query_protoc_ref=None):
    """
    Determina uma chave única (string) baseada nas condições dos dados de entrada.
    Esta chave corresponde ao campo 'tipo' na tabela 'despacho_template'.
    """
    
    # Lógica dos if/elif do despachador.py original para retornar uma string chave
    # Exemplo:
    if not relation_query:
          
        if (query.get('Despacho') == 'Deferido'
            and int(query.get('qtd_poda1') or 0) > 0
            and not int(query.get('qtd_ret1') or 0) > 0
            and not query.get('protocolo_anterior')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio',
                                             'institucional', 'residencia', 'residência', 'comercio', 'terreno']):
            return 'poda_particular_deferido_sem_laudo' # Esta chave DEVE existir em despacho_template.tipo


        elif (query.get('Despacho') == 'Deferido'
            and not query.get('protocolo_anterior')
            and query.get('tipo_imovel') in ['público']):
            return 'poda_publico_deferido_sem_laudo'
       
        
        elif (query.get('Despacho') == 'Com Pendência'):
            # Se houver sub-tipos de pendência, crie chaves mais específicas
            return 'pendencia_geral_sem_laudo'


        elif (query.get('protocolo_anterior')):
            return 'protocolo_anterior_referenciado'
        # ... Mapear TODAS as condições originais para chaves únicas
        
            
    else: # Com relation_query (TEM LAUDO)

        qtd_repor = relation_query.get('qtd_repor') or 0

        if (relation_query.get('Despacho') == 'Deferido' and qtd_repor > 0
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio',
                                             'institucional', 'residencia', 'residência', 'terreno']):
            return 'supressao_particular_deferido_com_replantio'

        elif (relation_query.get('Despacho') == 'Deferido'
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio',
                                             'institucional', 'residencia', 'residência', 'terreno']):
            # Este é o caso sem replantio (qtd_repor == 0 implícito pela ordem)
            return 'supressao_particular_deferido_sem_replantio'

        # ... Mapear TODAS as condições da seção "TEM LAUDO"

        elif (relation_query.get('Despacho') == 'Indeferido'
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio',
                                             'institucional', 'residencia', 'residência', 'terreno']):
            return 'indeferido_particular_com_laudo' # Antigo "INDEFERIDO PARTICULAR - SEM PODA"

    # Fallback se nenhuma condição bater (deve ser raro se o mapeamento for completo)
    return 'despacho_nao_mapeado'





def Despachar(db, query, relation_query=None, query_protoc_ref=None):
    # 1. Determinar o tipo de despacho
    tipo_chave = determinar_tipo_despacho_key(db, query, relation_query, query_protoc_ref)

    if tipo_chave == 'despacho_nao_mapeado':
        return 'Não foi possível determinar o modelo de despacho para este caso.'

    # 2. Buscar o template no banco de dados
    template_record = db(db.despacho_template.nome == tipo_chave).select().first()

    if not template_record:
        return f"Modelo de despacho para o tipo '{tipo_chave}' não encontrado no banco de dados."
    
    template_text = template_record.texto

    # 3. Preparar o contexto de dados (variáveis para o template)
    contexto = {}

    # Adicionar dados brutos e campos virtuais de 'query' (Requerimentos)
    # Os nomes das chaves no contexto DEVEM corresponder aos placeholders no template
    if query:
        contexto['Requerente'] = query.get('Requerente')
        contexto['Endereco'] = query.get('Endereco') # Campo Virtual
        contexto['Podas_solicitadas'] = query.get('total_podas') # Campo Virtual
        contexto['Supressoes_solicitadas'] = query.get('Supressoes') # Campo Virtual
        contexto['data_do_laudo'] = query.get('data_do_laudo').strftime('%d/%m/%Y') if query.get('data_do_laudo') else ''
        contexto['Podas'] = query.get('Podas')
        contexto['num_extens_poda'] = query.get('num_extens_poda')
        contexto['num_extens_supressoes'] = query.get('num_extens_supressoes')
        
        # Adicione outros campos de 'query' que seus templates usam

    # Adicionar dados brutos e campos virtuais de 'relation_query' (Laudos)
    if relation_query:
        contexto['tecnico'] = (relation_query.get('tecnico').upper() if relation_query.get('tecnico') else 'XXXXXXXXXXXXXX')
        contexto['data_do_laudo_laudo'] = relation_query.get('data_do_laudo').strftime('%d/%m/%Y') if relation_query.get('data_do_laudo') else ''
        contexto['proprietario_laudo'] = relation_query.get('proprietario')
        contexto['Supressoes_autorizadas'] = relation_query.get('Supressoes') # Campo Virtual de Laudos
        contexto['Podas_autorizadas'] = relation_query.get('Podas') # Campo Virtual de Laudos
        contexto['Obs_laudo'] = relation_query.get('Obs')
        contexto['porte_repor'] = relation_query.get('porte_repor')
        # Adicione outros campos de 'relation_query'

    # Adicionar dados de 'query_protoc_ref' (se aplicável ao template)
    if query_protoc_ref:
        # Exemplo de como acessar dados de protocolo referenciado
        if query_protoc_ref.get('Laudos'): # Se a referência tem dados de Laudos
            contexto['tecnico_prot_ref'] = query_protoc_ref.get('Laudos').get('tecnico','').upper() or 'XXXXXXXXXXXXXX'
            contexto['podas_prot_ref'] = query_protoc_ref.get('Laudos').get('Podas','')
            contexto['supressoes_prot_ref'] = query_protoc_ref.get('Laudos').get('Supressoes','')
            # A data do laudo da referência pode vir de Requerimentos ou Laudos dentro da referência
            data_laudo_ref_obj = query_protoc_ref.get('Requerimentos', {}).get('data_do_laudo')
            if data_laudo_ref_obj:
                 contexto['data_laudo_prot_ref'] = data_laudo_ref_obj.strftime('%d/%m/%Y')

        elif query_protoc_ref.get('Requerimentos'): # Se a referência tem dados de Requerimentos
            contexto['podas_prot_ref'] = query_protoc_ref.get('Requerimentos').get('Podas','')
            contexto['supressoes_prot_ref'] = query_protoc_ref.get('Requerimentos').get('Supressoes','')
            data_laudo_ref_obj = query_protoc_ref.get('Requerimentos').get('data_do_laudo')
            if data_laudo_ref_obj:
                 contexto['data_laudo_prot_ref'] = data_laudo_ref_obj.strftime('%d/%m/%Y')
            contexto['tecnico_prot_ref'] = 'XXXXXXXXXXXXXX' # Default se não houver laudo na ref
        
        contexto['protocolo_anterior_num'] = query.get('protocolo_anterior')



    if relation_query:
        soma_poda_aut = relation_query.get('total_podas')
        contexto['soma_poda_autorizada'] = soma_poda_aut
        soma_supress_aut = relation_query.get('total_supressoes')
        contexto['soma_supressao_autorizada'] = soma_supress_aut
        contexto['num_extens_supressao_autorizada'] = relation_query.get('num_extens_supressoes')
        
        qtd_repor_val = relation_query.get('qtd_repor') or 0
        contexto['qtd_repor_calculada'] = qtd_repor_val
        contexto['num_extens_repor_calculada'] = relation_query.get('num_extens_repor')




    try:
        texto_final = template_text.format(**contexto)
    except KeyError as e:
        # Este erro é útil durante o desenvolvimento para achar placeholders não preenchidos
        return str(f'''Erro ao popular o modelo {tipo_chave}: 
                   A variável {str(e).strip("'")} não foi encontrada no contexto de dados. 
                   Verifique os placeholders do template e a preparação do contexto na função Despachar.''')
    except Exception as e:
        return f"Erro inesperado ao popular o modelo '{tipo_chave}': {str(e)}"
        
    return texto_final