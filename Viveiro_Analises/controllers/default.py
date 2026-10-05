# -*- coding: utf-8 -*-
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2  # type: ignore
from gluon.sqlhtml import ExporterCSV  # type: ignore
from gluon.utils import secure_dumps, secure_loads  # type: ignore

if 0 == 1:
    from gluon import (db, current, IS_IN_SET, HTTP, SQLFORM, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, BEAUTIFY, BUTTON, SPAN, IS_IMAGE_COMPACT,
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE, redirect, URL, CAT, A, SCRIP,  # type: ignore
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC, IS_DATE_IN_RANGE, SCRIPT) # type: ignore
    
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore
    configuration = current.configuration

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})


# ---- Integração SiGM / EMPRO ----
def _normalizar_logradouro(logr):
    """
    Normaliza o logradouro removendo repetições de prefixo (ex: 'rua Rua ...' -> 'Rua ...')
    e convertendo para letras maiúsculas.
    """
    if not logr:
        return ""
    logr = str(logr).strip()
    padroes = [
        r'^(rua|r\.)\s+(rua|r\.)\s+',
        r'^(avenida|av\.|av)\s+(avenida|av\.|av)\s+',
        r'^(alameda|al\.)\s+(alameda|al\.)\s+',
        r'^(travessa|tv\.)\s+(travessa|tv\.)\s+',
        r'^(praca|praça|pc\.)\s+(praca|praça|pc\.)\s+',
        r'^(rodovia|rod\.)\s+(rodovia|rod\.)\s+',
    ]
    for padrao in padroes:
        m = re.match(padrao, logr, re.IGNORECASE)
        if m:
            primeiro = m.group(1).capitalize()
            logr = re.sub(padrao, f"{primeiro} ", logr, count=1, flags=re.IGNORECASE)
            break
    return logr.upper()


def _obter_config_sigm():
    """
    Recupera a URL e a API Key do SiGM a partir do appconfig.json com fallback robusto.
    """
    url = None
    api_key = None
    try:
        sigm_data = configuration.take('sigm') 
        if isinstance(sigm_data, dict):
            url = sigm_data.get('url')
            api_key = sigm_data.get('api_key')
    except Exception:
        pass

    if not url:
        url = configuration.get('sigm.url')
    if not api_key:
        api_key = configuration.get('sigm.api_key')

    if not api_key or not url:
        try:
            cfg_path = Path(request.folder, 'private', 'appconfig.json')
            if cfg_path.exists():
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    sigm = raw.get('sigm') or {}
                    url = url or sigm.get('url')
                    api_key = api_key or sigm.get('api_key')
        except Exception:
            pass

    url = (url).rstrip('/')
    api_key = api_key or ''
    return url, api_key


def _obter_chave_cripto():
    try:
        _, api_key = _obter_config_sigm()
        if api_key:
            return api_key
        db_cfg = configuration.take("db")
        key = db_cfg.get('password') if isinstance(db_cfg, dict) else None
        if not key:
            key = configuration.get('app.name', 'Viveiro_Secret_Key_Default')
    except Exception:
        key = 'Viveiro_Secret_Key_Default'
    return str(key)


def _salvar_credenciais_sigm(user, password):
    if not user or not password:
        return False
    key = _obter_chave_cripto()
    payload = {'user': user, 'pass': password}
    token = secure_dumps(payload, key)
    session.sigm_auth = token.decode('utf-8') if isinstance(token, bytes) else str(token)
    return True


def _recuperar_credenciais_sigm():
    token = session.get('sigm_auth')
    if not token:
        return None, None
    key = _obter_chave_cripto()
    try:
        data = secure_loads(token, key)
        if isinstance(data, dict):
            return data.get('user'), data.get('pass')
    except Exception:
        session.sigm_auth = None
    return None, None


@auth.requires_login()
def sigm_consulta():
    """
    Endpoint para consulta de protocolo na API do SiGM.
    Retorna JSON com os dados tratados do protocolo ou status para autenticação/erro.
    """
    protocolo = (request.vars.get('protocolo') or '').strip()
    if not protocolo:
        return response.json({'status': 'error', 'message': 'Número de protocolo não informado.'})

    empro_user = (request.vars.get('empro_user') or '').strip()
    empro_pass = request.vars.get('empro_pass') or ''

    if empro_user and empro_pass:
        user = empro_user
        password = empro_pass
        is_new_auth = True
    else:
        user, password = _recuperar_credenciais_sigm()
        is_new_auth = False

    if not user or not password:
        return response.json({
            'status': 'auth_required',
            'message': 'Credenciais EMPRO necessárias para consultar o SiGM.'
        })

    base_url, api_key = _obter_config_sigm()
    if not api_key:
        return response.json({
            'status': 'error',
            'message': 'Chave de API do SiGM (api_key) não encontrada no appconfig.json.'
        })

    target_url = f"{base_url}/api/v1/protocolos/detalhes/{protocolo}"
    req = urllib.request.Request(target_url, headers={
        'User-Agent': 'Web2py-Viveiro/1.0',
        'Accept': 'application/json',
        'X-API-Key': api_key,
        'X-Empro-User': user,
        'X-Empro-Pass': password
    })

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode('utf-8')
            dados = json.loads(body)
    except urllib.error.HTTPError as e:
        status_code = e.code
        err_msg = ""
        try:
            raw_body = e.read().decode('utf-8', errors='ignore')
            err_json = json.loads(raw_body)
            err_msg = err_json.get('detail') or ""
        except Exception:
            err_msg = ""

        if err_msg:
            err_msg = re.sub(r'<[^>]+>', ' ', err_msg).strip()

        if status_code == 401:
            session.sigm_auth = None
            return response.json({
                'status': 'auth_error',
                'message': err_msg or 'Usuário ou senha EMPRO inválidos.'
            })
        elif status_code == 403:
            return response.json({
                'status': 'error',
                'message': f"Acesso negado pela API SiGM (403): {err_msg or 'X-API-Key inválida ou não autorizada.'}"
            })
        elif status_code == 404:
            return response.json({
                'status': 'not_found',
                'message': err_msg or f'Protocolo {protocolo} não encontrado no SiGM.'
            })
        else:
            return response.json({
                'status': 'error',
                'message': err_msg or f'Erro retornado pela API SiGM: Código HTTP {status_code}.'
            })
    except urllib.error.URLError as e:
        return response.json({
            'status': 'error',
            'message': f'Não foi possível conectar ao servidor SiGM ({base_url}): {e.reason}'
        })
    except Exception as e:
        return response.json({
            'status': 'error',
            'message': f'Erro ao processar dados do SiGM: {str(e)}'
        })

    if is_new_auth:
        _salvar_credenciais_sigm(user, password)

    solicitante = str(dados.get('solicitante') or '').strip().upper()

    dados_desc = dados.get('dados_descricao') or {}
    logradouro_raw = dados_desc.get('logradouro') or ''
    logradouro = _normalizar_logradouro(logradouro_raw)

    num_casa = dados_desc.get('número_da_casa')
    numero = '' if num_casa is None else str(num_casa).strip()

    data_abertura = str(dados.get('data_abertura') or '').strip()

    tipo_solic = str(dados_desc.get('tipo_de_solicitação') or '').lower()
    is_poda = 'poda' in tipo_solic

    qtd_arvores = dados_desc.get('quantidade_de_árvores')
    quantidade = '' if qtd_arvores is None else str(qtd_arvores).strip()

    return response.json({
        'status': 'success',
        'solicitante': solicitante,
        'logradouro': logradouro,
        'numero': numero,
        'data_abertura': data_abertura,
        'is_poda': is_poda,
        'quantidade': quantidade
    })


@auth.requires_login()
def sigm_receber():
    """
    Endpoint para efetivar o recebimento de protocolo na API do SiGM.
    Chama /api/v1/protocolos/receber/{id_protocolo} via POST/GET.
    """
    protocolo = (request.vars.get('protocolo') or '').strip()
    if not protocolo:
        return response.json({'status': 'error', 'message': 'Número de protocolo não informado.'})

    empro_user = (request.vars.get('empro_user') or '').strip()
    empro_pass = request.vars.get('empro_pass') or ''

    if empro_user and empro_pass:
        user = empro_user
        password = empro_pass
        is_new_auth = True
    else:
        user, password = _recuperar_credenciais_sigm()
        is_new_auth = False

    if not user or not password:
        return response.json({
            'status': 'auth_required',
            'message': 'Credenciais EMPRO necessárias para receber no SiGM.'
        })

    base_url, api_key = _obter_config_sigm()
    if not api_key:
        return response.json({
            'status': 'error',
            'message': 'Chave de API do SiGM (api_key) não encontrada no appconfig.json.'
        })

    target_url = f"{base_url}/api/v1/protocolos/receber/{protocolo}"
    req = urllib.request.Request(target_url, data=b'', headers={
        'User-Agent': 'Web2py-Viveiro/1.0',
        'Accept': 'application/json',
        'X-API-Key': api_key,
        'X-Empro-User': user,
        'X-Empro-Pass': password
    })

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode('utf-8')
            dados = json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        status_code = e.code
        err_msg = ""
        try:
            raw_body = e.read().decode('utf-8', errors='ignore')
            err_json = json.loads(raw_body)
            err_msg = err_json.get('detail') or err_json.get('message') or ""
        except Exception:
            err_msg = ""

        if err_msg:
            err_msg = re.sub(r'<[^>]+>', ' ', err_msg).strip()

        if status_code == 401:
            session.sigm_auth = None
            return response.json({
                'status': 'auth_error',
                'message': err_msg or 'Usuário ou senha EMPRO inválidos.'
            })
        elif status_code == 403:
            return response.json({
                'status': 'error',
                'message': f"Acesso negado pela API SiGM (403): {err_msg or 'X-API-Key inválida ou não autorizada.'}"
            })
        elif status_code == 404:
            return response.json({
                'status': 'not_found',
                'message': err_msg or f'Protocolo {protocolo} não encontrado no SiGM.'
            })
        else:
            return response.json({
                'status': 'error',
                'message': err_msg or f'Erro retornado pela API SiGM ao receber: Código HTTP {status_code}.'
            })
    except urllib.error.URLError as e:
        return response.json({
            'status': 'error',
            'message': f'Não foi possível conectar ao servidor SiGM ({base_url}): {e.reason}'
        })
    except Exception as e:
        return response.json({
            'status': 'error',
            'message': f'Erro ao receber no SiGM: {str(e)}'
        })

    if is_new_auth:
        _salvar_credenciais_sigm(user, password)

    msg = dados.get('message') or dados.get('detail') or f'Protocolo {protocolo} recebido com sucesso no SiGM.'
    return response.json({
        'status': 'success',
        'message': msg,
        'dados': dados
    })





def avisos():
    registros_de_avisos = db(~(db.Avisos.recebido_por.contains(auth.user_id))).select()
    
    aviso = registros_de_avisos[-1]
    
    
    recebido = aviso.recebido_por or []
    if auth.user_id not in recebido:
        recebido.append(auth.user_id)
        aviso.update_record(recebido_por=recebido)
        
    db.commit()
    
    markdowner = Markdown2(html4tags=True, tab_width=4, )
    
    
    return dict(aviso=XML(markdowner.convert(aviso.corpo))) # type: ignore


def dashboard():
    # Recebe o novo estado e atualiza a sessão
    from datetime import datetime as dt
    hoje = dt.today()
    periodo = hoje.replace(day=1).strftime('%Y-%m-%d')
    
    if request.vars.periodo in ['Ano', 'Mês']:
        session.periodo = request.vars.periodo
        
    if session.periodo == 'Ano':
        periodo = hoje.replace(month=1, day=1).strftime('%Y-%m-%d')
        
    em_analises = db((db.Requerimentos.Despacho in ['Em Análise', 'Aguardando']) & (
        db.Requerimentos.data_entrada >= periodo)).count()
    deferidos = db((db.Requerimentos.Despacho == 'Deferido') & (
        db.Requerimentos.data_entrada >= periodo)).count()
    
    indeferidos = db((db.Requerimentos.Despacho == 'Indeferido') & (
        db.Requerimentos.data_entrada >= periodo)).count()
    parcial_deferidos = db((db.Requerimentos.Despacho ==
                            'Parcialmente Deferido') & (
        db.Requerimentos.data_entrada >= periodo)).count()
    arvores_para_replantio = db((db.Laudos.Protocolo > 0) & (db.Laudos.data_do_laudo >= periodo)).select(db.Laudos.qtd_repor.sum()).first() 
    arvores_para_replantio = arvores_para_replantio._extra.get('SUM(`tab Protocolos`.`qtd repor`)')
    compensar = db((db.Laudos.Despacho == 'Pendente de Compesação') & (
        db.Laudos.data_do_laudo >= periodo)).count()
    
    supress_autorizadas = db.executesql(f'''SELECT SUM( COALESCE(`qtd ret1`, 0) + COALESCE(`qtd ret2`, 0) + COALESCE(`qtd ret3`, 0) + COALESCE(`qtd ret4`, 0) ) 
            FROM `DadosGestArvores`.`tab Protocolos` AS `tab Protocolos` 
            WHERE  `tab Protocolos`.`data do laudo` >= '{periodo}'  AND `tab Protocolos`.`Despacho` IN ('Deferido', 'Parcialmente Deferido')
                ''')
    supress_autorizadas = int(supress_autorizadas[0][0] or 0)
    
    supress_nao_autorizadas = db.executesql(f''' SELECT COALESCE(`Select_Indeferidas`.`soma_Indeferidas`, 0) + 
            (COALESCE(`Select_solicitadas`.`solicitadas`, 0) - COALESCE(`deferidas_parciais`, 0)) 
            AS `soma_Indeferidas`
    FROM
            (SELECT SUM( COALESCE(`qtd ret1`, 0) + COALESCE(`qtd ret2`, 0) + COALESCE(`qtd ret3`, 0) + COALESCE(`qtd ret4`, 0) ) AS `soma_Indeferidas`
            FROM `DadosGestArvores`.`tab Protocolos` AS `tab Protocolos` 
            WHERE `tab Protocolos`.`data do laudo` >= '{periodo}' AND `tab Protocolos`.`Despacho` = 'Indeferido') AS `Select_Indeferidas`,
            (SELECT  SUM( COALESCE(`qtd ret1`, 0) + COALESCE(`qtd ret2`, 0) + COALESCE(`qtd ret3`, 0) + COALESCE(`qtd ret4`, 0) ) AS `solicitadas`
            FROM `DadosGestArvores`.`tab Solicitacoes` AS `tab Solicitacoes` 
            WHERE `tab Solicitacoes`.`data do laudo`>= '{periodo}' AND `tab Solicitacoes`.`Despacho` = 'Parcialmente Deferido') AS `Select_solicitadas`,
            (SELECT  SUM( COALESCE(`qtd ret1`, 0) + COALESCE(`qtd ret2`, 0) + COALESCE(`qtd ret3`, 0) + COALESCE(`qtd ret4`, 0) ) AS `deferidas_parciais`
            FROM `DadosGestArvores`.`tab Protocolos` AS `tab Protocolos` 
            WHERE `tab Protocolos`.`data do laudo` >= '{periodo}' AND `tab Protocolos`.`Despacho` = 'Parcialmente Deferido') AS `Select_Pacial_Deferidas`
                                    ''')
    supress_nao_autorizadas = int(supress_nao_autorizadas[0][0])
    
    podas_autorizadas = db.executesql(f'''SELECT SUM( COALESCE(`qtd ret1`, 0) + COALESCE(`qtd ret2`, 0) + COALESCE(`qtd ret3`, 0) + COALESCE(`qtd ret4`, 0) ) 
            FROM `DadosGestArvores`.`tab Solicitacoes` AS `tab Solicitacoes`
            WHERE `tab Solicitacoes`.`Despacho` = 'Deferido' AND `tab Solicitacoes`.`data do laudo` >= '{periodo}'   
                ''')
    
    qtd_podas = db.executesql(f'''SELECT
            Select_total_por_pedido.soma_solicitadas AS `Total de árvores solicitadas`, 
            COALESCE ( Select_deferidas.soma_deferidas, 0 ) + COALESCE ( `Select_Pacial_Deferidas`.`deferidas_parciais`, 0 ) AS `Total_Deferidas`,
            COALESCE ( `Select_Indeferidas`.`soma_indeferidas`, 0 ) + COALESCE ( `Select_solicitadas_parcial_deferidas`.`solicitadas_parcial_deferida`, 0 ) - COALESCE ( `Select_Pacial_Deferidas`.`deferidas_parciais`, 0 ) AS `Total_Indeferidas`,
            COALESCE (`solicitadas_parcial_deferida`, 0 ) AS `solicitadas_parcial_deferida`,
            COALESCE ( `deferidas_parciais`, 0 ) AS `Parcialmente deferidas` 

            FROM 
            ( SELECT SUM( COALESCE(`qtd poda1`, 0) + COALESCE(`qtd poda2`, 0) + COALESCE(`qtd poda3`, 0) + COALESCE(`qtd poda4`, 0)) AS soma_solicitadas
                FROM `DadosGestArvores`.`tab Solicitacoes`
                WHERE `data do laudo` >= '{periodo}'  AND `Despacho` IN ('Deferido', 'Indeferido', 'Parcialmente Deferido'))  AS Select_total_por_pedido,
            ( SELECT SUM( COALESCE(`qtd poda1`, 0) + COALESCE(`qtd poda2`, 0) + COALESCE(`qtd poda3`, 0) + COALESCE(`qtd poda4`, 0)) AS soma_deferidas
                FROM `DadosGestArvores`.`tab Solicitacoes` AS `tab Solicitacoes`
                WHERE `tab Solicitacoes`.`data do laudo` >= '{periodo}' AND `tab Solicitacoes`.`Despacho` = 'Deferido' ) AS Select_deferidas,
            ( SELECT SUM( COALESCE(`qtd poda1`, 0) + COALESCE(`qtd poda2`, 0) + COALESCE(`qtd poda3`, 0) + COALESCE(`qtd poda4`, 0)) AS soma_indeferidas
                FROM `DadosGestArvores`.`tab Solicitacoes` AS `tab Solicitacoes`
                WHERE `tab Solicitacoes`.`data do laudo` >= '{periodo}' AND `tab Solicitacoes`.`Despacho` = 'Indeferido' ) AS Select_Indeferidas,
            ( SELECT SUM( COALESCE(`qtd poda1`, 0) + COALESCE(`qtd poda2`, 0) + COALESCE(`qtd poda3`, 0) + COALESCE(`qtd poda4`, 0)) AS `solicitadas_parcial_deferida`
                FROM `DadosGestArvores`.`tab Solicitacoes` AS `tab Solicitacoes`
                WHERE `tab Solicitacoes`.`data do laudo` >= '{periodo}' AND `tab Solicitacoes`.`Despacho` = 'Parcialmente Deferido' ) AS `Select_solicitadas_parcial_deferidas`,
            ( SELECT SUM( COALESCE(`qtd poda1`, 0) + COALESCE(`qtd poda2`, 0) + COALESCE(`qtd poda3`, 0) + COALESCE(`qtd poda4`, 0)) AS `deferidas_parciais`
                FROM `DadosGestArvores`.`tab Protocolos` AS `tab Protocolos` 
                WHERE `tab Protocolos`.`data do laudo` >= '{periodo}' AND `tab Protocolos`.`Despacho` = 'Parcialmente Deferido' ) AS `Select_Pacial_Deferidas`                               
                                        ''')
    podas_autorizadas = int(qtd_podas[0][1])
    podas_nao_autorizadas = int(qtd_podas[0][2])
        
    return dict(
        compensar=f"{compensar:,}".replace(',', '.'),
                        em_analises=f"{em_analises:,}".replace(',', '.'),
                        deferidos=f"{deferidos:,}".replace(',', '.'),
                        parcial_deferidos=f"{parcial_deferidos:,}".replace(',', '.'),
                        indeferidos=f"{indeferidos:,}".replace(',', '.'),
                        supress_autorizadas=f"{supress_autorizadas:,}".replace(
                            ',', '.'),
                        podas_autorizadas=f"{podas_autorizadas:,}".replace(',', '.'),
                        supress_nao_autorizadas=f"{supress_nao_autorizadas:,}".replace(
                            ',', '.'),
                        podas_nao_autorizadas=f"{podas_nao_autorizadas:,}".replace(',', '.'),
                        arvores_para_replantio=f"{arvores_para_replantio:,}".replace(',', '.'),
    )


def index():   
    user = auth.user
    mensagens = ''
    avisos = []
    if user:
        registros_de_avisos = db(~(db.Avisos.recebido_por.contains(user.id ) ) ).select()
        avisos = [aviso for aviso in registros_de_avisos] 
        num_avisos = len(avisos)
        
        mensagens = TABLE([P(f'''Olá {user.first_name if user else ""}! Você está no Sistema de Dados da Sec. Municipal de Meio Ambiente'''), # type: ignore
                    P(str(f'''Você tem {num_avisos}'''  if num_avisos > 0 else '') + str(' aviso' if num_avisos > 0 else 'avisos'))  if num_avisos > 0 else '', # type: ignore
                        ])
        

    return dict(mensagem=mensagens,
                periodo = session.periodo,
                
                avisos=avisos if user else '')




# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)


# ---- Wiki & Base de Conhecimento (Redirecionamento transparente) ----
def wiki():
    """
    Encaminha rotas de default/wiki para o controller moderno de wiki.
    """
    if request.args:
        arg0 = request.args(0)
        if arg0 in ('_create', 'create', 'novo'):
            redirect(URL('wiki', 'create', vars=request.vars))
        elif arg0 in ('_search', 'search', 'busca'):
            redirect(URL('wiki', 'search', vars=request.vars))
        elif arg0 in ('_pages', 'pages', 'artigos'):
            redirect(URL('wiki', 'pages', vars=request.vars))
        elif arg0 in ('_tags', 'tags', '_cloud', 'topicos'):
            redirect(URL('wiki', 'index', vars=request.vars))
        elif arg0 in ('_edit', 'edit'):
            redirect(URL('wiki', 'edit', args=request.args[1:], vars=request.vars))
        else:
            redirect(URL('wiki', 'view', args=request.args, vars=request.vars))
    redirect(URL('wiki', 'index', vars=request.vars))

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
    para decorar funções que precisam de controle de acesso
    Observe também que há http: //..../ [app] / appadmin / manage / auth para permitir que o administrador gerencie usuários"""
    return dict(form=auth())

# ---- ação ao conteúdo estático enviado pelo servidor (required) ---
@cache.action()
def download():
    """
    permite o download de arquivos enviados
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@auth.requires_login()
def Requerimentos(): #Menu
    table='Requerimentos'
    tablename = f'{db[table]._tablename[:-1]}'
    processo = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    session.registro = processo
    session.function = table
    tem_laudo = db(db.Laudos.Protocolo == processo).count() > 0
    
    # if isinstance(processo, int) or processo == None:
    #     tem_laudo = db(db.Laudos.Protocolo == processo).count() > 0
    # else:
    #     tem_laudo = False 


    if f=='editar':
        if not auth.has_membership('Analise e Laudos'):
            session.flash = "Você não tem permissão para editar."
            redirect(URL('default', table, args=[processo], vars={'f':'ver'}))
        else:
            formprocess = SQLFORM(db[table], processo, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        formprocess = SQLFORM(db[table], processo, readonly=True, ) 
    else:
        if not auth.has_membership('Analise e Laudos'):
            session.flash = "Você não tem permissão para inserir requerimentos."
            redirect(URL('default', table, vars={'f':'ver'}))
        else:
            db.Requerimentos.Protocolo.requires = IS_NOT_IN_DB(db, 'Requerimentos.Protocolo', error_message='Já está registrado.')
            formprocess = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        

    if formprocess.process().accepted:
        session.flash = f'Dados do {tablename} atualizados' if processo else f'{tablename} Registrado'
        redirect(URL('default', table, args=[formprocess.vars.Protocolo], vars={'f':'ver'})) # type: ignore

    elif formprocess.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    list_fields= [db.Requerimentos.Protocolo, db.Requerimentos.Requerente,
                  db.Requerimentos.Endereco, db.Requerimentos.data_do_laudo, db.Requerimentos.telefone1,
                  db.Requerimentos.Supressoes_requeridas, db.Requerimentos.Podas_requeridas, db.Requerimentos.Despacho,
                  db.Requerimentos.local_arvore, db.Requerimentos.tipo_imovel
                  ]
    
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.Protocolo] , vars={'f': 'ver'})))]
    
    tem_filtro = any(key.startswith('_f_') or key == 'keywords' 
                     for key in request.vars)
    
    # Define os exportadores (desabilita CSV se não houver filtro)
    export_config = dict(csv=False, tsv=False, tsv_with_hidden_cols=False,
                         json=False, xml=False, html=False, csv_with_hidden_cols=False)
    
    export_config['csv'] = (ExporterCSV, 'CSV' ) if tem_filtro else None

    formbusca = SQLFORM.grid(db(db.Requerimentos.Protocolo > 0), orderby=~db.Requerimentos.data_do_laudo, represent_none='',
                         editable=False, searchable=True, deletable=False, links=links, create=False, details=False, paginate=20,
                         maxtextlength = 120, _class="table", exportclasses=export_config, user_signature=False,
                         fields=list_fields, links_placement = 'left',)
    
        
    return dict(formprocess=formprocess, processo=processo, formbusca=formbusca, tem_laudo=tem_laudo)


def editar_laudo():
    protoc = request.args(0)
    session.edit_laudo = True if session.edit_laudo == False else False
    redirect(URL('default','Requerimentos', extension='', args=[protoc], vars={'f':'ver'}), client_side=True) # type: ignore
    

@auth.requires_login()
def Registrar_Laudo():
    
    #TODO: O botão de registrar laudo deve oferecer caixa de confirmação em caso de não ouver supressões no processo.
    protoc = request.args(0)
    processo = db(db.Requerimentos.Protocolo == protoc).select().first()
    
    # form = SQLFORM.factory()
    # if not any([processo.qtd_ret1, processo.qtd_ret2, processo.qtd_ret3, processo.qtd_ret4]):
    #     my_extra_element = TR(LABEL('Registrar Laudo mesmo sem supressões no Requerimento.'), INPUT(_name='agree', value=True, _type='checkbox')) # type: ignore
    #     form[0].insert(-1, my_extra_element) # type: ignore
    # print(processo.Protocolo)
    # response.render(BEAUTIFY(Modal('Atenção', form, id='atencao')))
    # if form.process().accepted:
    #     if form.vars.agree:  
    
    
    try:
        db.Laudos.validate_and_insert(Protocolo=protoc, proprietario=processo.Requerente, data_do_laudo=processo.data_do_laudo,
                                    Despacho=processo.Despacho, qtd_poda1=processo.qtd_poda1, qtd_poda2=processo.qtd_poda2,
                                    qtd_poda3=processo.qtd_poda3, qtd_poda4=processo.qtd_poda4, especie_poda1=processo.especie_poda1,
                                    especie_poda2=processo.especie_poda2, especie_poda3=processo.especie_poda3, 
                                    especie_poda4=processo.especie_poda4, qtd_ret1=processo.qtd_ret1, qtd_ret2=processo.qtd_ret2, 
                                    qtd_ret3=processo.qtd_ret3, qtd_ret4=processo.qtd_ret4, especie_ret1=processo.especie_ret1,
                                    especie_ret2=processo.especie_ret2, especie_ret3=processo.especie_ret3, especie_ret4=processo.especie_ret4)
        session.edit_laudo = True
    except Exception as e:
        session.flash = f'Erro {e}'
    
    redirect(URL('default','Requerimentos', extension='', args=[protoc], vars={'f':'ver'})) # type: ignore
    
    
@auth.requires_login()
def Laudos():
    table= 'Laudos'
    laudo = request.args(0) or None
    try:
        if session.edit_laudo==True and auth.has_membership('Analise e Laudos'):
            form = SQLFORM(db[table], laudo, submit_button=f'Atualizar {db[table]._tablename[:-1]}', deletable=True)
        else:
            form = SQLFORM(db[table], laudo, readonly=True, represent_none='')
    except Exception as e:
        print(f"Erro {e}")
        form = SQLFORM(db[table], submit_button=f'Registrar {db[table]._tablename[:-1]}')
    
        
    if form.process().accepted:
        session.flash = f'Dados do Laudo atualizados' if laudo else 'Laudo Registrado'
        editar_laudo()
        redirect(URL('default','Requerimentos', extension='', args=[laudo], vars={'f':'ver'}), client_side=True) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass


    return response.render(dict(form=form, laudo=laudo))




@auth.requires_login()
def Despachar_Processos(): #Menu
    from gluon.contrib.markdown.markdown2 import MarkdownWithExtras as Markdown2 # type: ignore
      # type: ignore

    processo= request.vars.processo or ''  
    prime_query= ''
    conteudo= ''
    copybtn= ''
    form=''
    returnbtn = A('Voltar', _href=URL('default', 'Requerimentos', args=[processo], vars={'f':'ver'}), _class='btn btn-primary')# type: ignore
    newbtn = A('Novo', _href=URL('default', 'Requerimentos'), _class='btn btn-primary')# type: ignore
    
    if processo:
        prime_query = db(db.Requerimentos.Protocolo == processo).select().first()
        relation_query = db((db.Requerimentos.Protocolo == processo) & (db.Laudos.Protocolo == processo)).select().first()
        query_protoc_ref = None
        if prime_query.protocolo_anterior:
            if  db(db.Laudos.Protocolo == prime_query.protocolo_anterior).count() > 0:
                query_protoc_ref = db((db.Requerimentos.Protocolo == prime_query.protocolo_anterior) &
                                        (db.Laudos.Protocolo == db.Requerimentos.Protocolo)).select().first()
            else:
                query_protoc_ref = db((db.Requerimentos.Protocolo == prime_query.protocolo_anterior)).select().first()
            
        textos_despacho = Despachar(prime_query, relation_query, query_protoc_ref) #type: ignore
        markdowner = Markdown2(html4tags=True,  )
        
        conteudo= []
        for texto_despacho in textos_despacho:
            texto_md = markdowner.convert(texto_despacho) or None
            texto_md_escaped = texto_md.replace('\n', '\\n').replace('"', r'\\\\"').replace('<p>', '').replace('</p>', '')
            conteudo.append(DIV(XML(texto_md), _class='card', _style="border-color : silver")) # type: ignore
            copybtn = TAG.button('<Copiar>', _class='btn btn-info', _onclick='navigator.clipboard.writeText("{}").then(function(){{alert("Texto copiado!");}})'.format(texto_md_escaped))  # type: ignore
            conteudo.append(copybtn)
            conteudo.append(XML(markdowner.convert('-----'))) #type: ignore
        
        
    else:
        form = SQLFORM.factory(Field('Protocolo'))
        
    if not processo:  
        if form.process().accepted:
            session.flash = f'Procurando'
            redirect(URL('default', 'Despachar_Processos', vars={'processo' : form.vars.Protocolo}) )# type: ignore


    return dict(returnbtn=returnbtn, newbtn=newbtn, copybtn=copybtn, conteudo = conteudo, form= form) # type: ignore


@auth.requires_login()
@auth.requires_membership('Analise e Laudos', otherwise=URL('default', 'index'))
def Especies(): #Menu
    table = 'Especies'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    
    f = request.vars['f'] if request.vars['f']  else None
    session.registro = registro
    session.function = table

    if request.vars.nome:
        db.Especies.Nome.default = request.vars.nome

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}', formname=table + registro if registro else '') # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, formname=table + registro if registro else '') 
    else:
        db[table].id.requires = IS_NOT_IN_DB(db, f'{table}.id', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}', formname=table)
        
    if form.process().accepted:
        session.flash = f'Dados atualizados' if registro else 'Registrado'
        redirect(URL('default', session.function , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
   
  
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.id] , vars={'f': 'ver'})))]
    
    
    grd_especies = SQLFORM.grid(db(db.Especies.id >0), orderby=db.Especies.Nome, links=links, user_signature=False, editable=False, searchable=True,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left')


    return response.render(dict(form=form,  especie=registro, grd_especies=grd_especies))


def processar_formulario(form):
    # Acessar o validador do campo de imagem
    validator = None
    requires = form.table.foto.requires or []
    if not isinstance(requires, (list, tuple)):
        requires = [requires]
    for val in requires:
        if isinstance(val, IS_IMAGE_COMPACT):
            validator = val
            break
    
    if validator and getattr(validator, 'coordinate', None):
        # Preencher automaticamente o outro campo
        form.vars.obs = validator.coordinate
        

@auth.requires_login()
def fotos():
    table = 'fotos'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None
    fields = ['titulo', 'foto', 'fonte', 'tipo', 'idEspecie', 'obs'] if not f else None
    
    item_em_questao = session.registro or None
    
    
    if session.function:
        vinculo = 'id'+session.function[:-1] if not session.function == 'Requerimentos' else 'idLaudo'
        db.fotos[vinculo].default = item_em_questao 

    db.fotos.tipo.requires = IS_IN_SET(['árvore', 'caule', 'casca', 'copa', 'galho', 'folha', 'flor', 'fruto', 'muda', 'raiz', 'semente', 'tronco', 'outro' ])   
    db.fotos.idEspecie.label = 'Espécie'
    db.fotos.idEspecie.widget = SQLFORM.widgets.autocomplete(
        request, db.Especies.Nome, id_field=db.Especies.id, limitby=(0, 20), min_length=1
    )
    db.fotos.idEspecie.comment = CAT(
        A('Adicionar Espécie', 
          _id='btn-add-especie', 
          _class='btn btn-info btn-xs', 
          _style='margin-left:10px;',
          _target='_blank',
          _href=URL('default', 'Especies', extension='' )),
        SCRIPT(""" 
            jQuery(document).ready(function() {
                var $btnAdd = jQuery('#btn-add-especie');
                
                function getInputValue() {
                    var $auto = jQuery('input[name*="_autocomplete_Especies"]');
                    if ($auto.length && $auto.val()) {
                        return $auto.val().trim();
                    }
                    var $id = jQuery('#fotos_idEspecie');
                    if ($id.length && $id.val()) {
                        return $id.val().trim();
                    }
                    return '';
                }
                
                function updateAddUrl() {
                    var val = getInputValue();
                    var baseUrl = '%(base_url)s';
                    if (val) {
                        $btnAdd.attr('href', baseUrl + '?nome=' + encodeURIComponent(val));
                    } else {
                        $btnAdd.attr('href', baseUrl);
                    }
                }
                
                updateAddUrl();
                
                jQuery(document).on('input change blur focus autocompleteselect autocompletechange', 
                    '#fotos_idEspecie, input[name*="_autocomplete_Especies"]', 
                    function() {
                        setTimeout(updateAddUrl, 100);
                    }
                );
                
                $btnAdd.on('mouseenter focus mousedown click', function() {
                    updateAddUrl();
                });
            });
        """ % dict(
            base_url=URL('default', 'Especies', extension='')
        ))
    )
    
    if f=='editar':
        db.fotos.foto.writable = False
        db.fotos.foto.readable = False
        db.fotos.foto.requires = None
        fields_editar = ['titulo', 'fonte', 'tipo', 'idEspecie','idLaudo', 'obs']
        form = SQLFORM(db.fotos, registro, submit_button=f'Alterar dados da {tablename}', fields=fields_editar, formname= table, deletable=True)
    elif f=='ver':
        form = SQLFORM(db.fotos, registro, readonly=True, fields=fields, formname= table, )
    else:
        form = SQLFORM(db.fotos, submit_button=f'Registrar {tablename}', fields=fields, formname= table)
    
    
    if form.process(onvalidation=processar_formulario).accepted:
        session.flash = f'Registrado'
        if form.vars.foto:
            db(db.fotos.id == form.vars.id).update(**dict(caminho=Path(str(pasta_viveiro_fotos),# type: ignore
                    
                                                                       session.function or 'Outras_fotos',
                                                                       form.vars.foto[:10], form.vars.foto[11:13], form.vars.foto)))
        
        if item_em_questao:
            redirect(URL('default', session.function , extension='', args=[item_em_questao], vars={'f':'ver'})) # type: ignore
        else:
            redirect(URL('default', 'fotos', args=[request.args(0)], vars={'f':'ver'})) # type: ignore
            
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
        
    
    if session.function:
        fotos_do_item_em_questao = db(db.fotos[vinculo] == item_em_questao)
    
    listagem_fotos = []
    
    form_num_col = ''
    
    if not f and item_em_questao:
        for foto in fotos_do_item_em_questao.select(orderby=~db.fotos.tipo).as_list():
            listagem_fotos.append((foto.get('id'), foto.get('foto'), foto.get('titulo'), foto.get('tipo')))

        # form_num_col = SQLFORM.factory(Field('num_de_col', requires=IS_IN_SET(['3', '4']), label='Colunas') )
        # #Adiciona script jQuery para atualizar num_col e recarregar a página em tempo real
        # script = SCRIPT("""
        #     $(document).ready(function(){
        #     $('#no_table_num_de_col').on('change', function(){
        #         var val = $(this).val();
        #         window.num_col = parseInt(val) || 4;
        #         // Recarrega a página ao alterar o valor
        #         window.location.href = window.location.pathname + '?num_de_col=' + window.num_col;
        #     });
        #     // Inicializa a variável global na primeira carga
        #     window.num_col = parseInt($('#no_table_num_de_col').val()) || 4;
        #     });
        # """)
        # session.num_col = request.vars.get('num_de_col') or 4
        
        num_col = 3
        
        # form_num_col[0].append(script)

        # Atualiza num_col com base no parâmetro da URL, se existir
        resto = len(listagem_fotos) % num_col
        
        table_fotos = TABLE( _align='center', paginate=10) # type: ignore
        linha_cards_fotos = TR( ) # type: ignore
            
            
        for item, elemento in enumerate(listagem_fotos):
            if item < 9:
                card_foto = TD( B(A(f'Foto: {elemento[2]}', # type: ignore
                _href=URL(c=request.controller, f='fotos', extension='', # type: ignore
                args=[elemento[0]], vars={'f':'ver'} ))),  # type: ignore
                DIV(  IMG( _src=URL(r=request, f='download', args=elemento[1]), # type: ignore
                    _alt=f'foto não encontrada', _width='20%', 
                    _style='display: block;  margin-left: auto; margin-right: auto; width: 20%; height: auto;'),
                    _align='center', _class="card", _style='padding:20px', _width='20%' ), f'tipo: {elemento[3]}',  _width='20%') 
                linha_cards_fotos.append(card_foto)
        
                if len(listagem_fotos) <= num_col and len(linha_cards_fotos) == len(listagem_fotos):          
                    table_fotos.append(linha_cards_fotos)               
                    linha_cards_fotos = TR() # type: ignore
                
                elif len(table_fotos) >= len(listagem_fotos) // num_col:
                    if len(linha_cards_fotos) == resto: 
                        table_fotos.append(linha_cards_fotos)
                        linha_cards_fotos = TR() # type: ignore
                else:
                    if len(linha_cards_fotos) == num_col:
                        table_fotos.append(linha_cards_fotos)
                        linha_cards_fotos = TR() # type: ignore
                    
            elif request.vars['mais'] == 'true':
                card_foto = TD( B(A(f'Foto: {elemento[2]}', # type: ignore
                _href=URL(c=request.controller, f='fotos', extension='', # type: ignore
                args=[elemento[0]], vars={'f':'ver'} ))),  # type: ignore
                DIV(  IMG( _src=URL(r=request, f='download', args=elemento[1]), # type: ignore
                    _alt=f'foto não encontrada', _width='20%', 
                    _style='display: block;  margin-left: auto; margin-right: auto; width: 20%; height: auto;'),
                    _align='center', _class="card", _style='padding:20px', _width='20%' ), f'tipo: {elemento[3]}',  _width='20%') 
                linha_cards_fotos.append(card_foto)
        
                if len(listagem_fotos) <= num_col and len(linha_cards_fotos) == len(listagem_fotos):          
                    table_fotos.append(linha_cards_fotos)               
                    linha_cards_fotos = TR() # type: ignore
                
                elif len(table_fotos) >= len(listagem_fotos) // num_col:
                    if len(linha_cards_fotos) == resto: 
                        table_fotos.append(linha_cards_fotos)
                        linha_cards_fotos = TR() # type: ignore
                else:
                    if len(linha_cards_fotos) == num_col:
                        table_fotos.append(linha_cards_fotos)
                        linha_cards_fotos = TR() # type: ignore
            else:
                table_fotos.append(DIV(A('Clique para mais', _href=URL(c=request.controller, f=request.function, vars={'mais':'true'})),_class='card')) # type: ignore
                break
                
    return dict(listagem_fotos=listagem_fotos if not f else '',
                table_fotos=table_fotos if not f and item_em_questao else '',
                form=form, form_num_col=form_num_col, f=f)



@auth.requires_login()
def Bairros(): #Menu
    table = 'Bairros'
    tablename = f'{db[table]._tablename[:-1]}'
    registro = request.args(0) or None
    f = request.vars['f'] if request.vars['f']  else None

    if f=='editar':
        form = SQLFORM(db[table], registro, submit_button=f'Atualizar {tablename}' ) # type: ignore
    elif f=='ver':
        form = SQLFORM(db[table], registro, readonly=True, ) 
    else:
        db[table][table[:-1]].requires = IS_NOT_IN_DB(db, f'{table}.{table[:-1]}', error_message='Já está registrado.')
        form = SQLFORM(db[table], submit_button=f'Registrar {tablename}')
        
    if form.process().accepted:
        session.flash = f'Dados do {tablename} atualizados' if registro else '{tablename} Registrado'
        redirect(URL('default', table , extension='', args=[form.vars.id], vars={'f':'ver'})) # type: ignore
    elif form.errors:
        response.flash = 'Corrija os Erros indicados'
    else:
        pass
    
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.id] , vars={'f': 'ver'}))),
             dict(header='Editar', body=lambda row: A('Editar', _class='btn btn-primary' , _href=URL(c=request.controller, # type: ignore
                              f=request.function, args=[row.id] , vars={'f': 'editar'})))]
    
    formbusca= SQLFORM.grid(db[table].id > 0, represent_none='', editable=False, searchable=True, deletable=False, links=links,
                         create=False, details=False, paginate=30,  maxtextlength = 120, _class="table", 
                         exportclasses=dict(csv=False, tsv=False, tsv_with_hidden_cols=False, json=False, xml=False,
                         html=False, csv_with_hidden_cols=(ExporterCSV, 'CSV' )), user_signature=False, links_placement = 'left', 
                          )

    return response.render(dict(form=form, formbusca=formbusca, registro=registro, tabela=table))




@auth.requires_login()
def Lista_de_Registros():
    import re
    REGEX = re.compile(r'^(\w+).(\w+).(\w+)\=\=(\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error')) # type: ignore

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [
    dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=request.args(1) , f= table, # type: ignore
     args=row.id, vars={'f': 'ver'}))),
    dict(header='Editar', body=lambda row: A('Editar', _href=URL(c=request.args(1) , f= table, # type: ignore
     args=row.id, vars={'f': 'editar'})))
     ]

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left'), table=table)


def obter_id_especie():
    nome = request.vars.nome
    if nome:
        nome_clean = nome.strip()
        if nome_clean.isdigit():
            registro = db(db.Especies.id == int(nome_clean)).first()
            if registro:
                return response.json(dict(id=registro.id))
        
        registro = db((db.Especies.Nome == nome_clean.lower()) | 
                      (db.Especies.Nome == nome_clean) | 
                      (db.Especies.Especie == nome_clean)).first()
        if not registro:
            registro = db(db.Especies.Nome.like(nome_clean)).first() or db(db.Especies.Especie.like(nome_clean)).first()
        
        if registro:
            return response.json(dict(id=registro.id))
            
    return response.json(dict(id=None))
