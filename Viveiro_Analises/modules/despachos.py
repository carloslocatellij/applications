import num2words #type: ignore

def Despachar(query, relation_query):
    
    soma_poda = sum([x for x in [query.get('qtd_poda1'), query.get('qtd_poda2'), query.get('qtd_poda3'), query.get('qtd_poda4')] if x])
    
    num_extens_poda = num2words.num2words(soma_poda, lang='pt-br')
    num_extens_poda = num_extens_poda.upper()
    
    
    if not relation_query:
        
        if query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência']:
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
        
        elif query.get('tipo_imovel') in ['público', ]:
            texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {query.get('data_do_laudo')} PELO TÉCNICO XXXXXXXXXXXXXXXXXXXX, CONSTATOU-SE A NECESSIDADE DE PODA DE LIMPEZA E ADEQUAÇÃO DE  {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')}. NO ENDEREÇO: {query.get('Endereco')}.

    SEGUIR NORMA ABNT NBR 16246-1:2013.

    A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

    LEI 13.031/2018
    ART. 66.
    PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

    DECRETO 18.301/2019
    ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        
        '''

        else:
            texto = 'Não foi possível a geração do texto.'
    else:
        
        
        soma_supress = sum([x for x in [relation_query.get('qtd_ret1'), relation_query.get('qtd_ret2'), relation_query.get('qtd_ret3'), relation_query.get('qtd_ret4')] if x])
        num_extens_supress = num2words.num2words(soma_supress, lang='pt-br')
        num_extens_supress = num_extens_supress.upper()
        
        if relation_query.get('Despacho') == 'Deferido' and query.get('tipo_imovel') in ['privado', 'particular', 'próprio', 'institucional', 'residencia', 'residência']:
            texto = f'''
Ilmo.(a) Sr.(a) {query.get('Requerente')}

Fica estabelecido, de conformidade com os termos do Art. 59º da Lei nº 13.031, de 26 de setembro de 2018, regulamentada no Anexo I do Decreto nº 18.301, de 02 de maio de 2019, a AUTORIZAÇÃO para a extração de árvores, sendo as quantidades {soma_supress} ({num_extens_supress}) e respectiva(s) espécie(s): {relation_query.get('Supressoes')}.

Endereço: {query.get('Endereco')}, nos termos do compromisso de plantio de muda de árvores, de sua responsabilidade, assinado no dia ______de ____________de ______.

DECLARAÇÃO DE RESPONSABILIDADE E TERMO DE COMPROMISSO DE MEDIDA COMPENSATÓRIA

O requerente acima mencionado declara sob as penas da legislação em vigor, que **assume o compromisso de plantar {relation_query.get('qtd_repor')} ({num_extens_supress}) muda(s) de árvore(s) de porte ({relation_query.get('porte_repor')})** em substituição àquelas a serem removidas no local supracitado, no prazo de 60 (sessenta) dias a partir da data do recebimento desta autorização. Para cada muda a ser plantada, o canteiro permeável deverá ter dimensões no padrão ESPAÇO ÁRVORE, que deve ter como medidas mínimas 40% da largura da calçada e para o comprimento, o dobro da largura, respeitando sempre as medidas que concerne à acessibilidade (1,2m). PROIBIDO POR LEI Nº 13.031/2018 O USO DE MANILHA (TUBO). 

###### Para qualquer interdição parcial ou total de via pública para realização de serviços, deverá ser requerida autorização junto à Secretaria Municipal de Trânsito, Transportes e Segurança.
###### A responsabilidade pela supressão/poda de árvore(s) e destinação dos resíduos gerados é do requerente. Caso o material resultante da supressão/poda seja disposto em local inadequado/não autorizado, o responsável ficará sujeito à penalidade de multa. Em pequenas quantidades (até 1m³), os resíduos podem ser levados até um ponto de apoio (mais informações: https://www.riopreto.sp.gov.br/pontodeapoio/). Troncos e maiores quantidades de resíduos devem ser levados diretamente para a Fazendinha Ambiental; em caso de dúvidas, entrar em contato com a Secretaria Municipal de Serviços Gerais pelo telefone (17) 3216-6310. O NÃO CUMPRIMENTO DO PRAZO ACARRETA A APLICAÇÃO DAS PENALIDADES DA LEI.

Técnico responsável: Guilherme Cavenaghi - Técnico Agrícola
            '''
            
        elif relation_query.get('Despacho') == 'Deferido' and query.get('tipo_imovel') in ['público', ]:
            
            texto = f'''DE ACORDO COM A VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {relation_query.get('tecnico').upper()}, CONSTATOU-SE A NECESSIDADE DE SUPRESSÃO DE {soma_supress} ({num_extens_supress}) ÁRVORES DAS ESPÉCIES: {query.get('Supressoes')}; PLANTIO DE SUBSTITUIÇÃO DE XX (XXX) MUDA(S) DE ÁRVORE(S) DE PORTE XXXX.
    E PODA DE LIMPEZA E ADEQUAÇÃO DE  {soma_poda} ({num_extens_poda}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')}. NO ENDEREÇO: {query.get('Endereco')}.

    SEGUIR NORMA ABNT NBR 16246-1:2013.

    A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

    LEI 13.031/2018
    ART. 66.
    PARAGRAFO 2°. A REALIZAÇÃO DA PODA DE ÁRVORES, ARBUSTOS E OUTRAS PLANTAS LENHOSAS EM ÁREAS URBANAS, DEVERÃO SEGUIR OS PROCEDIMENTOS DAS NORMAS TÉCNICAS, EM CONFORMIDADE COM A LEGISLAÇÃO APLICÁVEL.

    DECRETO 18.301/2019
    ART.15. NÃO É PERMITIDA A PODA DE TOPIARISMO DAS ÁRVORES, OU SEJA, NÃO É PERMITIDA PODA NA QUAL A COPA DA ÁRVORE FIQUE COM FORMA GEOMÉTRICA ARTIFICIAL, OU QUE ALTERE A FORMA E ARQUITETURA NATURAL DE CADA ESPÉCIE.
        '''
        elif relation_query.get('Despacho') == 'Aguardando' and  relation_query.get('proprietario') in ['', None, 'NULL']:

            texto = f'''PENDÊNCIA: EM VISTORIA REALIZADA EM {relation_query.get('data_do_laudo')} PELO TÉCNICO {relation_query.get('tecnico').upper()}, VERIFICOU-SE QUE A SUPRESSÃO DA(S) ÁRVORE(S) SERÁ AUTORIZADA APÓS A ENTREGA DA ANUÊNCIA DO PROPRIETÁRIO DO IMÓVEL.

PROTOCOLAR A CÓPIA DESTE DOCUMENTO NO POUPATEMPO OU PREFEITURA REGIONAL NORTE. '''
        else:
            texto = 'Não foi possível a geração do texto.'
        
    return texto