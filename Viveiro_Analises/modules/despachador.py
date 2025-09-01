import num2words #type: ignore
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
from datetime import datetime


def Despachar(query, relation_query, query_protoc_ref):
    
    query['data_do_laudo'] = query.get('data_do_laudo').strftime('%d/%m/%Y')

    if relation_query:
        relation_query['data_do_laudo'] = relation_query.get('data_do_laudo').strftime('%d/%m/%Y')

    soma_poda = sum([x for x in [query.get('qtd_poda1'), query.get('qtd_poda2'), query.get('qtd_poda3'), query.get('qtd_poda4')] if x])
    num_extens_poda = num2words.num2words(soma_poda, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
        
    #   APENAS PODA - SEM LAUDO
    if not relation_query:
        
        # IMÓVEL PARTICULAR - DEFERIDO
        if (query.get('Despacho') == 'Deferido' 
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'comercio', 'terreno']):
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

A responsabilidade pela poda de árvore(s) e destinação dos resíduos gerados é do requerente. Pequenas quantidades de resíduos vegetais  (1m³) de podas podem ser levadas a Pontos de Apoio da Prefeitura, consultar:  https://www.riopreto.sp.gov.br/pontodeapoio/. Resíduos florestais, principalmente madeira nativa bruta, exigem destinação a locais cadastrados no Sinaflor, seguindo leis federais e estaduais. O transporte e armazenamento de madeira nativa precisam de controle documental (DOF/Sinaflor) e cadastro no CTF. Destinar madeira nativa sem origem comprovada é infração punível. Recomenda-se procurar locais licenciados para destinação. Dúvidas podem ser esclarecidas com a CETESB, Instituto Florestal ou secretarias municipais (Meio Ambiente: 17 3202-4010; Serviços Gerais: 17 3216-6310).
        '''
        
        # IMÓVEL PÚBLICO
        elif (query.get('Despacho') == 'Deferido' 
        and not query.get('protocolo_anterior')
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
        
        # APENAS PENDÊNCIAS
        elif (query.get('Despacho') == 'Com Pendência'):
            texto = f'''
                Existem pendências
            '''
            
        # VISTORIA JÁ REALIZADA - PROTOCOLO ANTERIOR
        elif (query.get('protocolo_anterior')):
            if query_protoc_ref.get('Laudos'):
                data_do_laudo = query_protoc_ref['Requerimentos'].get('data_do_laudo').strftime('%d/%m/%Y')
                tecnico = query_protoc_ref.get('Laudos').get('tecnico').upper() if query_protoc_ref.get('tecnico') else 'XXXXXXXXXXXXXX'
                podas = 'Podas: ' + query_protoc_ref.get('Laudos').get('Podas') or ''
                supressoes = 'Supressões: ' + query_protoc_ref.get('Laudos').get('Supressoes') or ''
                
            else:
                data_do_laudo = query_protoc_ref.get('data_do_laudo').strftime('%d/%m/%Y')
                podas = 'Podas: ' + query_protoc_ref.get('Podas') or ''
                supressoes = 'Supressões: ' + query_protoc_ref.get('Supressoes') or ''
                tecnico = 'XXXXXXXXXXXXXX'
                    
            
            
            texto = f'''
INFORMAMOS QUE JÁ FOI REALIZADA VISTORIA TÉCNICA PELO TÉCNICO {tecnico} E AUTORIZAÇÃO PELO PROTOCOLO {query.get('protocolo_anterior')}
EM {data_do_laudo}:

{supressoes}
{podas}

SENDO ENCAMINHADA AO SETOR COMPETENTE PARA AS PROVIDENCIAS NECESSÁRIAS.

'''
        else:
            texto = 'Não foi possível a geração do texto.'
            
            
    #   TEM LAUDO
    else:
        tecnico = relation_query.get('tecnico').upper() if relation_query.get('tecnico') else 'XXXXXXXXXXXXXX'
        qtd_repor = relation_query.get('qtd_repor') or 0
        num_extens_repor = num2words.num2words(qtd_repor, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
        
        soma_supress = sum([x for x in [relation_query.get('qtd_ret1'), relation_query.get('qtd_ret2'), relation_query.get('qtd_ret3'), relation_query.get('qtd_ret4')] if x])
        num_extens_supress = num2words.num2words(soma_supress, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
        
        soma_poda_autorizada = sum([x for x in [relation_query.get('qtd_poda1'), relation_query.get('qtd_poda2'), relation_query.get('qtd_poda3'), relation_query.get('qtd_poda4')] if x])
        num_extens_poda_autorizada = num2words.num2words(soma_poda_autorizada, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
        
        observacoes= f'De acordo com as observações: "{relation_query.get('Obs')}"' if relation_query.get('Obs') else ''
        
        
        # DEFERIDO SUPRESSÃO PARTICULAR COM REPLANTIO
        if (relation_query.get('Despacho') == 'Deferido' and qtd_repor > 0 
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'terreno']):
            
            com_req_podas= f'e para poda de: {relation_query.get('Podas')}, ' if relation_query.get('qtd_podas1') else ''
            com_podas_autorizadas= f'E para Poda de: {soma_poda_autorizada} ({num_extens_poda_autorizada}),  e respectiva(s) espécie(s): {relation_query.get('Podas')}' if relation_query.get('qtd_poda1') else '' 
            
            texto = f'''
Ilmo.(a) Sr.(a) {query.get('Requerente')}

Fica estabelecido, de conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, regulamentada no Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a AUTORIZAÇÃO para a extração de árvores, sendo as quantidades {soma_supress} ({num_extens_supress}) e respectiva(s) espécie(s): {relation_query.get('Supressoes')}. {com_podas_autorizadas}

Endereço: {query.get('Endereco')}, nos termos do compromisso de plantio de muda de árvores, de sua responsabilidade, assinado no dia \_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_.

DECLARAÇÃO DE RESPONSABILIDADE E TERMO DE COMPROMISSO DE MEDIDA COMPENSATÓRIA

O requerente acima mencionado declara sob as penas da legislação em vigor, que **assume o compromisso de plantar {relation_query.get('qtd_repor')} ({num_extens_repor}) muda(s) de árvore(s) de porte ({relation_query.get('porte_repor')})** em substituição àquelas a serem removidas no local supracitado, no prazo de 60 (sessenta) dias a partir da data do recebimento desta autorização. Para cada muda a ser plantada, o canteiro permeável deverá ter dimensões no padrão ESPAÇO ÁRVORE, que deve ter como medidas mínimas 40% da largura da calçada e para o comprimento, o dobro da largura, respeitando sempre as medidas que concerne à acessibilidade (1,2m). PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO). 

Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Pequenas quantidades de resíduos vegetais  (1m³) de podas podem ser levadas a Pontos de Apoio da Prefeitura, consultar:  https://www.riopreto.sp.gov.br/pontodeapoio/. Resíduos florestais, principalmente madeira nativa bruta, exigem destinação a locais cadastrados no Sinaflor, seguindo leis federais e estaduais. O transporte e armazenamento de madeira nativa precisam de controle documental (DOF/Sinaflor) e cadastro no CTF. Destinar madeira nativa sem origem comprovada é infração punível. Recomenda-se procurar locais licenciados para destinação. Dúvidas podem ser esclarecidas com a CETESB, Instituto Florestal ou secretarias municipais (Meio Ambiente: 17 3202-4010; Serviços Gerais: 17 3216-6310). O NÃO CUMPRIMENTO DO PRAZO ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: {tecnico or ''}  '''



        # DEFERIDO SUPRESSÃO PARTICULAR SEM REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'terreno']):
            com_req_podas= f'e para poda de: {relation_query.get('Podas')}, ' if relation_query.get('qtd_podas1') else ''
            com_podas_autorizadas= f'E para Poda de: {soma_poda_autorizada} ({num_extens_poda_autorizada}),  e respectiva(s) espécie(s): {relation_query.get('Podas')}' if relation_query.get('qtd_poda1') else '' 
            texto= f'''
Ilmo.(a) Sr.(a) {query.get('Requerente')}

Fica estabelecido, de conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, regulamentada no Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a AUTORIZAÇÃO para a extração de árvores, sendo as quantidades {soma_supress} ({num_extens_supress}) e respectiva(s) espécie(s): {relation_query.get('Supressoes')}. {com_podas_autorizadas}

Endereço: {query.get('Endereco')}, nos termos do compromisso, de sua responsabilidade, assinado no dia \_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_.

DECLARAÇÃO DE RESPONSABILIDADE

Informamos que o prazo para a supressão da(s) árvore(s) é de 60 (sessenta) dias a partir da data do recebimento desta autorização. PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO).

Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Pequenas quantidades de resíduos vegetais  (1m³) de podas podem ser levadas a Pontos de Apoio da Prefeitura, consultar:  https://www.riopreto.sp.gov.br/pontodeapoio/. Resíduos florestais, principalmente madeira nativa bruta, exigem destinação a locais cadastrados no Sinaflor, seguindo leis federais e estaduais. O transporte e armazenamento de madeira nativa precisam de controle documental (DOF/Sinaflor) e cadastro no CTF. Destinar madeira nativa sem origem comprovada é infração punível. Recomenda-se procurar locais licenciados para destinação. Dúvidas podem ser esclarecidas com a CETESB, Instituto Florestal ou secretarias municipais (Meio Ambiente: 17 3202-4010; Serviços Gerais: 17 3216-6310).

O NÃO CUMPRIMENTO DO PRAZO, ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: {tecnico} ''' 
            
            
        # DEFERIDO SUPRESSÃO PÚBLICA COM REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
              and relation_query.get('qtd_repor') 
              and query.get('tipo_imovel') in ['público', ]):
            
            # DEFERIDO SUPRESSÃO PÚBLICA COM REPLANTIO - COM PODA
            if relation_query.get('qtd_poda1'):
                texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, CONSTATOU-SE A NECESSIDADE DE SUPRESSÃO DE {soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Supressoes')}; PLANTIO DE SUBSTITUIÇÃO {qtd_repor} ({num_extens_repor}) MUDA(S) DE ÁRVORE(S) DE PORTE {relation_query.get('porte_repor')}.
E PODA DE LIMPEZA E ADEQUAÇÃO DE  {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {relation_query.get('Podas')}. NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
            
            # DEFERIDO SUPRESSÃO PÚBLICA COM REPLANTIO - SEM PODA
            else:
                texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, CONSTATOU-SE A NECESSIDADE DE SUPRESSÃO DE {soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Supressoes')}; PLANTIO DE SUBSTITUIÇÃO {qtd_repor} ({num_extens_repor}) MUDA(S) DE ÁRVORE(S) DE PORTE {relation_query.get('porte_repor')}.
NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
        
        
        
        #TODO: DEFERIDO APENAS PODA PÚBLICA COM LAUDO 
        
        elif (relation_query.get('Despacho') == 'Deferido' 
              and not relation_query.get('qtd_repor')
              and not relation_query.get('qtd_ret1')
              and query.get('tipo_imovel') in ['público', ]):
            
            com_podas_autorizadas= f'PODA DE: {soma_poda_autorizada} ({num_extens_poda_autorizada}),  ÁRVORES DAS ESPÉCIES: {relation_query.get('Podas')}' if relation_query.get('qtd_poda1') else '' 
            
            
            texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, CONSTATOU-SE A NECESSIDADE DE {com_podas_autorizadas};
NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
    
    
        # DEFERIDO SUPRESSÃO PÚBLICA SEM REPLANTIO
        elif (relation_query.get('Despacho') == 'Deferido' 
              and not relation_query.get('qtd_repor') 
              and query.get('tipo_imovel') in ['público', ]):
            
            texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, CONSTATOU-SE A NECESSIDADE DE SUPRESSÃO DE {soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {relation_query.get('Supressoes')};
NO ENDEREÇO: {query.get('Endereco')}.

SEGUIR NORMA ABNT NBR 16246-1:2013.

A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

LEI 13.031/2018
ART. 66.
PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

DECRETO 18.301/2019
ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
        
        # PENDÊNCIA DE COMPENSAÇÃO AMBIENTAL:
        
        elif (query.get('Despacho') == 'Pendente de Compesação'):
            texto = f'''
## Autorização para Supressão de Árvores
#### A Secretaria do Meio Ambiente e Urbanismo, conforme a Lei nº 13.031/2018 e o Decreto nº 18.301/2019, autoriza a supressão de {soma_supress} ({num_extens_supress}) árvores, mediante as seguintes condições:
Árvores a serem suprimidas:

 {relation_query.get('Supressoes')}

* Árvore na área interna.

### Condições para a autorização:
#### O solicitante deve doar XX (XXXXXXXX) mudas de árvores ao Viveiro Municipal de São José do Rio Preto, seguindo as especificações da Portaria SMAURB nº 01/2023. :
- 25 mudas por árvore nativa suprimida (Área interna). 
- 50 mudas por árvore nativa ameaçada de extinção  (Área interna). 
- 10 mudas por árvore exótica suprimida  (Área interna). 
- 2 mudas por árvore na calçada

#### As mudas devem ter no mínimo 1,5 metro de altura, estar saudáveis e em ótimo estado vegetativo. 
#### Cada muda deve ter etiqueta de identificação da espécie (nome popular e científico). 
#### As mudas devem ser separadas por espécie, com lista da quantidade total de cada uma. 
#### A entrega das mudas deve ser agendada com Fernando no Viveiro Municipal, pelo telefone (17) 3225-9769, informando o número do protocolo. 
- Após a entrega das mudas e apresentação do alvará e projeto de construções aprovadas pela Secretaria Municipal de Obras, a autorização de supressão será liberada. 

### Informações adicionais:
#### A lista de espécies aceitas para compensação ambiental está disponível na Portaria SMAURB nº 01/2023, acessível em: https://www.riopreto.sp.gov.br/wp-content/uploads/arquivosPortalGOV/meio-ambiente/smaurb-PORTARIA_SMAURB_01_2023.pdf
Após a confirmação da efetiva entrega das respectivas mudas ao Viveiro Municipal, e apresentação do alvará e projeto de construção aprovado pela Secretaria Municipal de Obras, o requerente poderá retirar a autorização para a supressão de {soma_supress} ({num_extens_supress}) árvore(s) referenciada(s). 
            
            '''
        
        
        # PENDÊNCIA DE ANUÊNCIA DO PROPRIENTÁRIO
        elif (relation_query.get('Despacho') == 'Com Pendência' 
              and  relation_query.get('proprietario') in ['', None, 'NULL']):

            texto = f'''PENDÊNCIA: EM VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {tecnico}, VERIFICOU-SE QUE A SUPRESSÃO DA(S) ÁRVORE(S) SERÁ AUTORIZADA APÓS A ENTREGA DA ANUÊNCIA DO PROPRIETÁRIO DO IMÓVEL.

PROTOCOLAR A CÓPIA DESTE DOCUMENTO NO POUPATEMPO OU PREFEITURA REGIONAL NORTE. '''


        # PENDÊNCIA DE ALVARÁ OU PROJETO:
        elif (relation_query.get('Despacho') == 'Com Pendência' 
              and any([relation_query.get('p9'), relation_query.get('p10')])):

            texto = f'''PARA CONTINUIDADE DA ANÁLISE DA SOLICITAÇÃO DEVERÁ APRESENTAR CÓPIA DO ALVARÁ E PROJETO DE REFORMA APROVADO PELA SECRETARIA MUNICIPAL DE OBRAS .
            
PROTOCOLAR A CÓPIA DESTES DOCUMENTOS NO POUPATEMPO OU PREFEITURA REGIONAL NORTE FAZENDO REFERÊNCIA A ESTE PRESENTE PROTOCOLO.
'''


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
PROVIDÊNCIAS PARA A(S) SUPRESSÃO(ÕES) (JÁ AUTORIZADA(S)). 
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
        # INDEFERIDO PARTICULAR - SEM PODA
        elif (relation_query.get('Despacho') == 'Indeferido'
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'terreno']):
            
            
            texto = f'''Ilmo.(a) Sr.(a) {relation_query.get('proprietario')},

Após análise do protocolo acima mencionado, informamos que foi solicitada a autorização para supressão do(s) seguinte(s) exemplar(es) arbóreo(s): {relation_query.get('Supressoes')}.

Com base na vistoria técnica realizada por esta Secretaria Municipal do Meio Ambiente e Urbanismo, constatou-se que a(s) árvore(s) encontra(m)-se em ótimo estado fitossanitário (saudáveis).

Recomendamos, nos casos de danos ao calçamento, o alargamento do canteiro ao redor da(s) árvore(s) como solução para minimizar os problemas. O uso de canteiros maiores, com material permeável (como grade, grama ou pedriscos), pode reduzir os danos à calçada e proporcionar melhores condições para o desenvolvimento da(s) árvore(s).

Considerando a importância das árvores para o meio ambiente e o bem-estar urbano, bem como as disposições do Plano Diretor de Arborização Urbana de São José do Rio Preto (Lei Nº 13.031/2018 - Art. 55 e Art. 59), o pedido de supressão foi **indeferido**.

Informamos ainda que a realização de poda drástica (acima de 25% do volume da copa) é proibida, conforme o Decreto nº 18.301/2019.

Caso deseje solicitar reconsideração deste despacho, será necessário abrir um novo requerimento com justificativas e/ou documentação complementar para nova análise.

**Técnico responsável:** {tecnico}

Atenciosamente,
            '''
            #TEXTO NORMAL:
            '''
Ilmo.(a) Sr.(a)

Considerando que, através do protocolo acima mencionado, foi solicitada autorização para supressão do(s) seguinte(s) exemplar(es) arbóreo(s): {relation_query.get('Supressoes')}, e que, neste sentido, foi realizada a vistoria técnica por esta Secretaria Municipal do Meio Ambiente e Urbanismo.

Considerando que o Plano Diretor de Arborização Urbana de São José do Rio Preto - PDAU (Lei Nº 13.031 de 26 setembro de 2018 - Art. 55 e Art. 59), tecnicamente define quais as condições em que a supressão poderá ser autorizada.

Considerando que a árvore, como parte integrante do meio ambiente, deve ser protegida, pois além do fato de ser um ser vivo e da sua importância para o bem-estar dos cidadãos, exerce muitas funções ecológicas, como a regulação térmica, manutenção da qualidade do ar e abrigo à fauna. Desta forma, faz-se necessário considerá-la um equipamento urbano essencial, e como tal necessita de uma estrutura digna para seu pleno desenvolvimento. 

Considerando que a(s) árvore(s) avaliada(s) encontra(m)-se ótimo estado fitossanitário (saudáveis), nos casos em que o motivo da solicitação tratar de danos da calçada, recomenda-se o alargamento do canteiro ao redor da(s) árvore(s) para contornar o problema de danos no calçamento, a utilização de canteiros maiores pode minimizar a quantidade de danos na calçada, portanto, é necessário reservar uma área livre de canteiro com material permeável (grade, grama, pedriscos e outros). 

Sendo assim, a Secretaria Municipal do Meio Ambiente e Urbanismo, após a avaliação dos critérios e parâmetros para a concessão de autorização, pelo Município, INDEFERE o pedido para a supressão da(s) árvore(s) que se encontram sadias e localizadas em área de domínio público. Informamos ainda, que de acordo com a Lei, a realização de poda drástica (acima de 25% do volume da copa) é proibida (Decreto nº 18.301/2019). 

Em caso de solicitação de reconsideração de despacho, faz-se necessário abrir novo requerimento por protocolo, com justificativas e/ou documentação complementar para nova vistoria.

Técnico responsável: {tecnico}

Atenciosamente,'''
            '''Ilmo.(a) Sr.(a) {relation_query.get('proprietario')},

Após análise do protocolo, informamos que o pedido de supressão do(s) exemplar(es) arbóreo(s): {relation_query.get('Supressoes')} foi **indeferido**. A(s) árvore(s) encontra(m)-se saudável(is). Recomendamos o alargamento do canteiro para minimizar danos ao calçamento. Poda drástica é proibida (Decreto nº 18.301/2019). Para reconsideração, abra novo requerimento.

**Técnico responsável:** {tecnico}'''
           
           
        # INDEFERIDO PRIVADO - ÁREA INTERNA - VIZINHO
        elif (relation_query.get('Despacho') == 'Indeferido'
            and query.get('local_arvore') == 'área interna'
            and not relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'terreno']):
            
            texto = f'''
Por se tratar de árvore localizada em área interna de propriedade particular, não existe meio legal para notificar o proprietário para realizar o manejo da árvore em questão no momento.

Sendo assim, orientamos para que sejam tomadas as providências convenientes, seguindo os preceitos legais, diretamente com o proprietário do imóvel que detém a árvore.

Orientamos também, que diante a possibilidade de ocorrências severas, pode ser consultado a Defesa Civil.

Informamos também que, de acordo com o Código Civil, Lei nº 10.406/2002,

Seção II – Das Árvores Limítrofes, Art. 1.283. As raízes e os ramos de árvore, que ultrapassarem a estrema do prédio, poderão ser cortados, até o plano vertical divisório, pelo proprietário do terreno invadido.

Para vistoria de árvores localizadas no próprio imóvel ou em calçadas, o meio de solicitar vistorias técnicas é pelo Poupatempo ou Prefeitura Regional Norte ou pelo link: https://cidadao.riopreto.sp.gov.br/?apl=PODA_SUPRESSAO

Não possuímos equipe de manejo de árvores para áreas particulares.

Atenciosamente,

           '''
        elif (relation_query.get('Despacho') == 'Indeferido'
            and not relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência', 'terreno']):
            
            texto = f'''
Por se tratar de árvore localizada no passeio de fronte a área de propriedade particular, não existe meio legal para notificar o proprietário para realizar o manejo da árvore em questão.

Sendo assim, orientamos para que sejam tomadas as providências convenientes, seguindo os preceitos legais, diretamente com o proprietário do imóvel que detém a árvore.

Orientamos também, que diante a possibilidade de ocorrências severas, pode ser consultado a Defesa Civil.

Para vistoria de árvores localizadas no próprio imóvel ou em calçadas, o meio de solicitar vistorias técnicas é pelo Poupatempo ou Prefeitura Regional Norte ou pelo link: https://cidadao.riopreto.sp.gov.br/?apl=PODA_SUPRESSAO

           '''
           
           # INDEFERIDO PÚBLICO
            '''
Em vistoria realizada no dia {relation_query.get('data_do_laudo')} pelo Técnico {tecnico}, na {query.get('Endereco')}, constatou-se o que segue:
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
            #TEXTO ALTERNATIVO:
            '''
Em vistoria realizada no dia {relation_query.get('data_do_laudo')} pelo Técnico {tecnico}, na {query.get('Endereco')}, constatou-se que:

- As árvores estão bem desenvolvidas, com galhos em boa conformação e a uma distância segura das fiações elétricas e outras infraestruturas.
- Não foram identificados galhos secos, frágeis ou em conflito com instalações, e as árvores apresentam equilíbrio estrutural.
- Não há necessidade de manejo, pois as árvores contribuem para a regulação térmica e a qualidade do ar, desempenhando um papel essencial no ambiente urbano.

Dessa forma, considerando que não há justificativa técnica para a supressão ou poda, o pedido foi **indeferido**.

**Base Legal:**
- **Lei nº 13.031 de 26 de setembro de 2018**
  - Art. 76: Constitui infração toda ação ou omissão contrária às disposições da presente Lei, respondendo solidariamente:
    - O proprietário do imóvel e/ou mandante;
    - O autor da ação;
    - Quem concorrer para a prática da infração.
  - V: Efetuar poda que comprometa o potencial de altura máxima da espécie;
  - VI: Efetuar poda que comprometa o potencial de área máxima de sombreamento da espécie.

Atenciosamente,
            '''
            
        elif (relation_query.get('Despacho') == 'Indeferido'
            and relation_query.get('proprietario')
            and query.get('tipo_imovel') in ['rural']):
            texto = f'''
EM RESPOSTA AO REQUERIMENTO REFERENTE À AUTORIZAÇÃO DE SUPRESSÃO DE APROXIMADAMENTE {soma_supress} {num_extens_supress} LOCALIZADA(S)
NA RUA/AV. {query.get('Endereco')} QUE, POR SE TRATAR DE IMÓVEL LOCALIZADO EM ÁREA RUARAL, SOLICITAMOS AO PROPRIETÁRIO DO IMÓVEL QUE
CONSULTE A COMPANHIA AMBIENTAL DO ESTADO DE SÃO PAULO (CETESB), AGÊNCIA DE SÃO JOSÉ DO RIO PRETO, LOCALIZADA NA 
AV. FLORIANO ANDRÉ CABRERA, S/N, BAIRRO JARDIM SÃO MARCOS, OU O 4º BATALHÃO DE POLÍCIA MILITAR AMBIENTAL, LOCALIZADA NA
AV. GOV. ADHEMAR PEREIRA DE BARROS Nº 2100 - VILA DINIZ, PARA OBTER INFORMAÇÃO SOBRE DEVIDAS EXIGÊNCIAS LEGAIS NECESSÁRIAS PARA
EFETUAR A SUPRESSÃO DO(S) EXEMPLAR(ES) ARBÓREO(S). 
'''            
            

        # PARCIALMENTE DEFERIDO
        elif (relation_query.get('Despacho') == 'Parcialmente Deferido'
            and relation_query.get('proprietario')): 
            
            com_req_podas= f'e para poda de: {query.get('Podas')}, ' if query.get('qtd_podas1') else ''
            com_podas_autorizadas= f'E para Poda de: {soma_poda_autorizada} ({num_extens_poda_autorizada}),  e respectiva(s) espécie(s): {relation_query.get('Podas')}' if relation_query.get('qtd_poda1') else '' 
            area_publica= f'e localizadas em área de domínio público. ' if query.get('tipo_imovel') in ['publico', 'público'] else ''
            
            texto =f'''
Ilmo.(a) Sr.(a) {relation_query.get('proprietario')}

Considerando que, através do protocolo acima mencionado, foi solicitada autorização para supressão do(s) seguinte(s) exemplar(es) arbóreo(s): {query.get('Supressoes')}, {com_req_podas} e que, neste sentido, foi realizada a vistoria técnica por esta Secretaria Municipal do Meio Ambiente e Urbanismo.

Considerando que o Código Florestal Municipal (Lei Complementar Municipal 053/1996), tecnicamente define algumas condições em que a supressão poderá ser autorizada.

Considerando que as árvores encontram-se em ótimo estado fitossanitário e não foram constatados danos na estrutura do imóvel ou do calçamento. Recomenda-se o alargamento do canteiro ao redor da(s) árvore(s).

Sendo assim, a Secretaria Municipal do Meio Ambiente e Urbanismo, após a avaliação dos critérios e parâmetros para a concessão de autorização, pelo Município, **INDEFERE** o pedido para a supressão da(s) árvore(s) que se encontram sadias. {area_publica}

E concede, em conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a **AUTORIZAÇÃO** para a Extração de Árvore, sendo a quantidade {soma_supress} ({num_extens_supress}) árvore e respectiva(s) espécie(s): {relation_query.get('Supressoes')}. {com_podas_autorizadas}

Endereço: {query.get('Endereco')},  nos termos do compromisso de plantio de muda de árvores, de sua responsabilidade, assinado no dia \_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_de \_\_\_\_\_\_\_\_\_\_\_.
{observacoes}

DECLARAÇÃO DE RESPONSABILIDADE E TERMO DE COMPROMISSO DE MEDIDA COMPENSATÓRIA 

O requerente acima mencionado declara sob as penas da legislação em vigor, que **assume o compromisso de plantar {relation_query.get('qtd_repor')} ({num_extens_repor}) muda(s) de árvore(S)
de porte ({relation_query.get('porte_repor')})** em substituição àquelas a serem removidas no local supracitado, no prazo de 60 (sessenta) dias a partir da data do recebimento desta autorização. Para cada muda a ser plantada, o canteiro permeável deverá ter dimensões no padrão ESPAÇO ÁRVORE, que deve ter como medidas mínimas 40% da largura da calçada e para o comprimento, o dobro da largura, respeitando sempre as medidas que concerne à acessibilidade (1,2m). PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO). 
Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Pequenas quantidades de resíduos vegetais  (1m³) de podas podem ser levadas a Pontos de Apoio da Prefeitura, consultar:  https://www.riopreto.sp.gov.br/pontodeapoio/. Resíduos florestais, principalmente madeira nativa bruta, exigem destinação a locais cadastrados no Sinaflor, seguindo leis federais e estaduais. O transporte e armazenamento de madeira nativa precisam de controle documental (DOF/Sinaflor) e cadastro no CTF. Destinar madeira nativa sem origem comprovada é infração punível. Recomenda-se procurar locais licenciados para destinação. Dúvidas podem ser esclarecidas com a CETESB, Instituto Florestal ou secretarias municipais (Meio Ambiente: 17 3202-4010; Serviços Gerais: 17 3216-6310). O NÃO CUMPRIMENTO DO PRAZO ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: {relation_query.get('tecnico')}
            '''
            #TExTO ALTERNATIVO:
            '''
            Ilmo.(a) Sr.(a) {relation_query.get('proprietario')},

Após análise do protocolo acima mencionado, informamos que foi solicitada a autorização para supressão do(s) seguinte(s) exemplar(es) arbóreo(s): {query.get('Supressoes')}, {com_req_podas} e realizada a vistoria técnica por esta Secretaria Municipal do Meio Ambiente e Urbanismo.

**Decisão:**
- **Indeferido:** O pedido para supressão da(s) árvore(s) que se encontram em bom estado fitossanitário, sem danos estruturais ao imóvel ou calçamento. Recomenda-se o alargamento do canteiro ao redor da(s) árvore(s) para minimizar possíveis problemas.
{area_publica}
- **Autorizado:** A extração de {soma_supress} ({num_extens_supress}) árvore(s) da(s) espécie(s): {relation_query.get('Supressoes')}. {com_podas_autorizadas}

**Endereço:** {query.get('Endereco')}

**Compromisso de Plantio:**
O requerente compromete-se a plantar {relation_query.get('qtd_repor')} ({num_extens_repor}) muda(s) de árvore(s) de porte ({relation_query.get('porte_repor')}) no prazo de 60 (sessenta) dias a partir do recebimento desta autorização. O canteiro deve seguir o padrão ESPAÇO ÁRVORE, com dimensões mínimas de 40% da largura da calçada e comprimento equivalente ao dobro da largura, respeitando as normas de acessibilidade.

**Observações:** {observacoes}

**Responsabilidades:**
- A poda ou supressão deve ser realizada por profissional habilitado.
- O requerente é responsável pela destinação adequada dos resíduos gerados. Pequenas quantidades de resíduos vegetais  (1m³) de podas podem ser levadas a Pontos de Apoio da Prefeitura, consultar:  https://www.riopreto.sp.gov.br/pontodeapoio/. Resíduos florestais, principalmente madeira nativa bruta, exigem destinação a locais cadastrados no Sinaflor, seguindo leis federais e estaduais. O transporte e armazenamento de madeira nativa precisam de controle documental (DOF/Sinaflor) e cadastro no CTF. Destinar madeira nativa sem origem comprovada é infração punível. Recomenda-se procurar locais licenciados para destinação. Dúvidas podem ser esclarecidas com a CETESB, Instituto Florestal ou secretarias municipais (Meio Ambiente: 17 3202-4010; Serviços Gerais: 17 3216-6310).
- O não cumprimento do prazo acarretará penalidades previstas em lei.

**Técnico responsável:** {relation_query.get('tecnico')}
            '''
        else:
            texto = 'Não foi possível a geração do texto.'

    return texto