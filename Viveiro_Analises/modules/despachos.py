import num2words #type: ignore
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
from datetime import datetime


def Despachar(query, relation_query):
    
    query['data_do_laudo'] = query.get('data_do_laudo').strftime('%d/%m/%Y')
    if relation_query:
        relation_query['data_do_laudo'] = relation_query.get('data_do_laudo').strftime('%d/%m/%Y')

    soma_poda = sum([x for x in [query.get('qtd_poda1'), query.get('qtd_poda2'), query.get('qtd_poda3'), query.get('qtd_poda4')] if x])
    
    num_extens_poda = num2words.num2words(soma_poda, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZAS', 'DEZES')
        
    #   APENAS PODA - SEM LAUDO
    if not relation_query:
        
        
        # IMÓVEL PARTICULAR
        if (query.get('Despacho') == 'Deferido' 
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'comercio']):
            texto = f'''AUTORIZADA A PODA DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S) DE FORMA DISTRIBUÍDA E EQUILIBRADA, SENDO: PODA DE LIMPEZA E ADEQUAÇÃO DE {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')},  LOCALIZADA(S) NA {query.get('Endereco')}. A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018

ART. 66.

PARAGRAFO 1º. A PODA DE ESPÉCIMES ARBÓREAS EM CALÇADAS OU ÁREAS PARTICULARES É DE RESPONSABILIDADE DO MUNÍCIPE QUE DEVERÁ CONTRATAR UM PODADOR CADASTRADO NESSE MUNICÍPIO E DEVIDAMENTE CAPACITADO.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

ART. 81. O PODADOR DE ÁRVORE DEVERÁ OBRIGATORIAMENTE SER CADASTRADO NA SECRETARIA MUNICIPAL DO MEIO AMBIENTE E URBANISMO PARA OBTER AUTORIZAÇÃO/LICENÇA PARA A EXECUÇÃO DO SERVIÇO DE SUPRESSÃO OU PODA DE ÁRVORES NO MUNICÍPIO DE SÃO JOSÉ DO RIO PRETO.


DECRETO 18.301/2019

ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.

ART. 16. NÃO É PERMITIDA A PODA DE MANUTENÇÃO ENQUANTO A ÁRVORE ESTIVER EM FLORAÇÃO E/OU FRUTIFICAÇÃO.


A AUTORIZAÇÃO SÓ É VALIDA DENTRO DO PRAZO DE 60 (SESSENTA) DIAS.

O REQUERENTE CITADO DECLARA ASSUMIR AS RESPONSABILIDADES POR QUAISQUER DANOS OU PREJUÍZOS À POPULAÇÃO OU AO PATRIMÔNIO PÚBLICO OU PRIVADO QUE VENHAM A OCORRER POR IMPERÍCIA OU IMPRUDÊNCIA PRÓPRIA OU DE QUEM A SEU MANDO EXECUTAR A PODA OBJETO DESTE REQUERIMENTO.

Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.

A responsabilidade pela poda de árvore(s) e destinação dos resíduos gerados é do requerente. Caso o material resultante da poda seja disposto em local inadequado/não autorizado, o responsável ficará sujeito à penalidade de multa. Em pequenas quantidades (até 1m³), os resíduos podem ser levados até um ponto de apoio (mais informações: https://www.riopreto.sp.gov.br/pontodeapoio/). Troncos e maiores quantidades de resíduos devem ser levados diretamente para a Fazendinha Ambiental; em caso de dúvidas, entrar em contato com a Secretaria Municipal de Serviços Gerais pelo telefone (17) 3216-6310.
        '''
        
        # IMÓVEL PÚBLICO
        elif (query.get('Despacho') == 'Deferido' 
        and query.get('tipo_imovel') in ['público',  ]):
            texto = f'''
DE ACORDO COM A VISTORIA REALIZADA EM {query.get('data_do_laudo')} PELO TÉCNICO XXXXXXXXXXXXXXXXXXXX, CONSTATOU-SE A NECESSIDADE DE
PODA DE LIMPEZA E ADEQUAÇÃO DE  {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')}. 
NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR
SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS
NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA 
GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        
        '''
        elif (query.get('Despacho') == 'Com Pendência'):
            texto = f'''
                Existem pendências
            '''
            
        elif (not query.get('Despacho') and query.get('protocolo_anterior')):
            texto = f'''
INFORMAMOS QUE JÁ FOI REALIZADA VISTORIA TÉCNICA E AUTORIZAÇÃO PELO PROTOCOLO {query.get('protocolo_anterior')} EM XX/xxx/202x.

'''
        else:
            texto = 'Não foi possível a geração do texto.'
            
            
    #   SUPRESSÕES  -  TEM LAUDO
    else:
        tecnico = relation_query.get('tecnico').upper() if relation_query.get('tecnico') else 'XXXXXXXXXXXXXX'
        qtd_repor = relation_query.get('qtd_repor') or 0
        soma_supress = sum([x for x in [relation_query.get('qtd_ret1'), relation_query.get('qtd_ret2'), relation_query.get('qtd_ret3'), relation_query.get('qtd_ret4')] if x])
        num_extens_supress = num2words.num2words(soma_supress, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZAS', 'DEZES')
        num_extens_repor = num2words.num2words(qtd_repor, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZAS', 'DEZES')
        
        
        # DEFERIDO SUPRESSÃO PARTICULAR COM REPLANTIO
        if (relation_query.get('Despacho') == 'Deferido' and qtd_repor > 0 
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência']):
            
            texto = f'''
Ilmo.(a) Sr.(a) {query.get('Requerente')}

Fica estabelecido, de conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, regulamentada no Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a AUTORIZAÇÃO para a extração de árvores, sendo as quantidades {soma_supress} ({num_extens_supress}) e respectiva(s) espécie(s): {relation_query.get('Supressoes')}.

Endereço: {query.get('Endereco')}, nos termos do compromisso de plantio de muda de árvores, de sua responsabilidade, assinado no dia \_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_.

DECLARAÇÃO DE RESPONSABILIDADE E TERMO DE COMPROMISSO DE MEDIDA COMPENSATÓRIA

O requerente acima mencionado declara sob as penas da legislação em vigor, que **assume o compromisso de plantar {relation_query.get('qtd_repor')} ({num_extens_repor}) muda(s) de árvore(s) de porte ({relation_query.get('porte_repor')})** em substituição àquelas a serem removidas no local supracitado, no prazo de 60 (sessenta) dias a partir da data do recebimento desta autorização. Para cada muda a ser plantada, o canteiro permeável deverá ter dimensões no padrão ESPAÇO ÁRVORE, que deve ter como medidas mínimas 40% da largura da calçada e para o comprimento, o dobro da largura, respeitando sempre as medidas que concerne à acessibilidade (1,2m). PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO). 

Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Caso o material resultante da supressão/poda seja disposto em local inadequado/não autorizado, o responsável ficará sujeito à penalidade de multa. Em pequenas quantidades (até 1m³), os resíduos podem ser levados até um ponto de apoio (mais informações: https://www.riopreto.sp.gov.br/pontodeapoio/). Troncos e maiores quantidades de resíduos devem ser levados diretamente para a Fazendinha Ambiental; em caso de dúvidas, entrar em contato com a Secretaria Municipal de Serviços Gerais pelo telefone (17) 3216-6310. O NÃO CUMPRIMENTO DO PRAZO ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: {tecnico or ''}  '''


        # DEFERIDO SUPRESSÃO PARTICULAR SEM REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência']):
            texto= f'''
Ilmo.(a) Sr.(a) {query.get('Requerente')}

Fica estabelecido, de conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, regulamentada no Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a AUTORIZAÇÃO para a extração de árvores, sendo as quantidades {soma_supress} ({num_extens_supress}) e respectiva(s) espécie(s): {relation_query.get('Supressoes')}.

Endereço: {query.get('Endereco')}, nos termos do compromisso, de sua responsabilidade, assinado no dia \_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_.

DECLARAÇÃO DE RESPONSABILIDADE

Informamos que o prazo para a supressão da(s) árvore(s) é de 60 (sessenta) dias a partir da data do recebimento desta autorização. PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO).

Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Caso o material resultante da supressão/poda seja disposto em local inadequado/não autorizado, o responsável ficará sujeito à penalidade de multa. Em pequenas quantidades (até 1m³), os resíduos podem ser levados até um ponto de apoio (mais informações: https://www.riopreto.sp.gov.br/pontodeapoio/). Troncos e maiores quantidades de resíduos devem ser levados diretamente para a Fazendinha Ambiental; em caso de dúvidas, entrar em contato com a Secretaria Municipal de Serviços Gerais pelo telefone (17) 3216-6310.

O NÃO CUMPRIMENTO DO PRAZO, ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: {tecnico} ''' 
            
            
        # DEFERIDO SUPRESSÃO PÚBLICA COM REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
              and relation_query.get('qtd_repor') 
              and query.get('tipo_imovel') in ['público', ]):
            
            texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, CONSTATOU-SE A NECESSIDADE DE SUPRESSÃO DE {soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {query.get('Supressoes')}; PLANTIO DE SUBSTITUIÇÃO {qtd_repor} ({num_extens_repor}) MUDA(S) DE ÁRVORE(S) DE PORTE {relation_query.get('porte_repor')}.
E PODA DE LIMPEZA E ADEQUAÇÃO DE  {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')}. NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
        
        
        #TODO: DEFERIDO SUPRESSÃO PÚBLICA COM REPLANTIO
        
        
        # PENDÊNCIA DE ANUÊNCIA DO PROPRIENTÁRIO
        elif (relation_query.get('Despacho') == 'Aguardando' 
              and  relation_query.get('proprietario') in ['', None, 'NULL']):

            texto = f'''PENDÊNCIA: EM VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, VERIFICOU-SE QUE A SUPRESSÃO DA(S) ÁRVORE(S) SERÁ AUTORIZADA APÓS A ENTREGA DA ANUÊNCIA DO PROPRIETÁRIO DO IMÓVEL.

PROTOCOLAR A CÓPIA DESTE DOCUMENTO NO POUPATEMPO OU PREFEITURA REGIONAL NORTE. '''


            # DENÚNCIA SMAURB - PODA
        elif (relation_query.get('Despacho') == 'Deferido' 
                and  not relation_query.get('qtd_ret1')  and relation_query.get('qtd_poda1')
                and relation_query.get('proprietario') in ['', None, 'NULL'] and relation_query.get('morador') in ['', None, 'NULL']):
            
            texto = f'''
EM VISTORIA REALIZADA NO DIA {relation_query.get('data_do_laudo')} PELO TÉCNICO: {tecnico}, NO IMÓVEL LOCALIZADO À: 
{query.get('Endereco')}, VERIFICOU-SE A NECESSIDADE DE PODA DE LIMPEZA E ADEQUAÇÃO DE
{soma_poda} ({num_extens_poda}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Podas')}. 
SENDO ASSIM, SOLICITAMOS, POR GENTILEZA, QUE O PROPRIETÁRIO DO IMÓVEL SEJA NOTIFICADO PARA QUE O MESMO TOME AS
PROVIDÊNCIAS PARA A PODA (JÁ AUTORIZADA). 
A PODA DEVE SER REALIZADA POR PODADOR HABILITADO, COM O CORTE DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S) 
DE FORMA DISTRIBUÍDA E EQUILIBRADA.
            '''
            
            
            # DENÚNCIA SMAURB - SUPRESSÃO - REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
                and relation_query.get('qtd_ret1') and not relation_query.get('qtd_poda1')
                and relation_query.get('proprietario') in ['', None, 'NULL'] and relation_query.get('morador') in ['', None, 'NULL']):
            
            texto = f'''
EM VISTORIA REALIZADA NO DIA {relation_query.get('data_do_laudo')} PELO TÉCNICO: {tecnico}, NO IMÓVEL LOCALIZADO À: 
{query.get('Endereco')}, VERIFICOU-SE A NECESSIDADE DA SUPRESSÃO DE 
{soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Supressoes')}.
DEVENDO SER REALIZADO O REPLANTIO DE {relation_query.get('qtd_repor')} ({num_extens_repor}) MUDA(S) DE ÁRVORE(S)
DE PORTE ({relation_query.get('porte_repor')}) 
SENDO ASSIM, SOLICITAMOS, POR GENTILEZA, QUE O PROPRIETÁRIO DO IMÓVEL SEJA NOTIFICADO PARA QUE O MESMO TOME AS
PROVIDÊNCIAS PARA A(S) SUPRESSÃO(ÔES (JÁ AUTORIZADA(S)). 
A PODA DEVE SER REALIZADA POR PODADOR HABILITADO, COM O CORTE DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S)
DE FORMA DISTRIBUÍDA E EQUILIBRADA.
            '''
            
            
            #DENÚNCIA SMAURB - PODA E SUPRESSÃO - REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
                and relation_query.get('qtd_ret1') and relation_query.get('qtd_poda1')
                and relation_query.get('proprietario') in ['', None, 'NULL'] and relation_query.get('morador') in ['', None, 'NULL']):
            
            texto = f'''
EM VISTORIA REALIZADA NO DIA {relation_query.get('data_do_laudo')} PELO TÉCNICO: {tecnico}, NO IMÓVEL LOCALIZADO À: 
{query.get('Endereco')}, VERIFICOU-SE A NECESSIDADE DA SUPRESSÃO DE 
{soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Supressoes')}. 
DEVENDO SER REALIZADO O REPLANTIO DE {relation_query.get('qtd_repor')} ({num_extens_repor}) MUDA(S) DE ÁRVORE(S)
DE PORTE ({relation_query.get('porte_repor')})
SENDO ASSIM, SOLICITAMOS, POR GENTILEZA, QUE O PROPRIETÁRIO DO IMÓVEL SEJA NOTIFICADO PARA QUE O MESMO TOME AS
PROVIDÊNCIAS PARA A(S) PODA(S) E A(S) SUPRESSÃO(ÔES) (JÁ AUTORIZADA(S)). 
A PODA DEVE SER REALIZADA POR PODADOR HABILITADO, COM O CORTE DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S)
DE FORMA DISTRIBUÍDA E EQUILIBRADA.
            '''
            
            
            
            # indeferido
        elif (relation_query.get('Despacho') == 'Indeferido'
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência']):
           
            texto= f'''
Em vistoria realizada no dia 04/02/2025 pelo Técnico {tecnico}, na {query.get('Endereco')}, constatou-se o que segue:
As árvore(s) estão(s) bem desenvolvida e com galhos com boa conformação, com uma distância segura das fiações elétricas
e outras infraestruturas.
Como não foi constatada a presença de galhos secos, a árvore está equilibrada, sem galhos frágeis e conflito com as instalações
não há a necessidade de manejo.
Considerando que, a arborização desempenha um papel crucial na manutenção da temperatura em ambientes urbanos. Árvores,
especialmente aquelas com copas frondosas, contribuem significativamente para a estabilização térmica das áreas urbanas
por meio de sombreamento e evapotranspiração.
Além de regular a temperatura, as árvores melhoram a qualidade do ar ao absorver poluentes e liberar oxigênio.
Um ambiente mais fresco e limpo contribui para o bem-estar dos residentes e reduz o consumo de energia para resfriamento.
Não havendo necessidade para a supressão ou poda, fica indeferido o pedido.


LEI Nº 13.031 DE 26 DE SETEMBRO DE 2018
Seção II
Das Infrações
Art. 76. Constitui infração toda ação ou omissão contrária às disposições da presente Lei, respondendo solidariamente e sem prejuízo da responsabilidade penal e civil:
a) o proprietário do imóvel e/ou mandante;
b) o autor da ação;
c) quem, de qualquer modo, concorrer para a prática da infração. (...)
V. efetuar poda que comprometa o potencial de altura máxima da espécie;
VI. efetuar poda que comprometa o potencial de área máxima de sombreamento da espécie;
(...)
            '''
            
        
        else:
            texto = 'Não foi possível a geração do texto.'
        
    return texto