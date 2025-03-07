

def Despachar_dof(dados_processo, query_obra, imprime_cabacalho=False):

    dados_processo = dados_processo.get('Obras') if 'Obras' in dados_processo.keys() else dados_processo
    if query_obra:
        if len(query_obra['DofsObra'].select()) > 0:
            tipo_dof = 'Nativa'
        elif query_obra.CobertMetalica == 1:
            tipo_dof = 'Estrutura'
        elif query_obra.MadeiraReflorest == 1:
            tipo_dof = 'Reflorestada'
        else:
            tipo_dof = 'Não há'

    logradouro = dados_processo.get('IdEndereco').split(',')[0]
    num = dados_processo.get('IdEndereco').split(',')[1]
    quadra = dados_processo.get('IdEndereco').split(',')[2].replace('Qd:','')
    lote = dados_processo.get('IdEndereco').split(',')[3].replace('Lt:','')
    bairro = dados_processo.get('IdEndereco').split(',')[4].replace('Bairro:','')

    proprietario, cadmun,   = dados_processo.get('IdGerador'), dados_processo.get('CadMunicipal')
    alvara, data_alvara = dados_processo.get('Alvara'), dados_processo.get('DataAlvara')
    logradouro, quadra, lote, num, bairro = logradouro , quadra, lote, num, bairro

    if imprime_cabacalho:
        cabecalho = f'''
        PROPRIETÁRIO: {proprietario}
        CADASTRO MUNICIPAL: {cadmun} ALVARÁ: {alvara} DATA DO ALVARÁ: {data_alvara}
        LOGRADOURO: {logradouro}, QUADRA: {quadra}, LOTE: {lote}, NUM: {num} - BAIRRO: {bairro}
        '''
    else:
        cabecalho = ''

    estrutura_metalica = f'''
    ESTRUTURA METÁLICA:
    {cabecalho}
    Conforme documentação apresentada relacionada ao não uso de madeira nativa na obra, foram utilizada(s) estrutura(s) metálica(s) e/ou laje(alvenaria) na cobertura.
    Estando de acordo com o art. 78 da lei complementar 649/2021.
    Os dados do processo foram registrados no Sistema Municipal de Qualidade Ambiental de Obras.
    '''
    dof_nativa = f'''
###    MADEIRA NATIVA:
    {cabecalho}
    Conforme documentação apresentada, foram utilizada(s) madeira(s) nativa(s) na obra.
    Os documentos apresentados relacionados à compra de madeira nativa (DOF) estão de acordo com o art. 78 da lei complementar 649/2021.
    Os dados do processo foram registrados no Sistema Municipal da Qualidade Ambiental de Obras.
    '''
    dof_nativa_e_reflorestada = f'''
    MADEIRA NATIVA e REFLORESTADA:
    {cabecalho}
    Conforme documentação apresentada, foram utilizadas tanto madeira(s) nativa(s) quanto reflorestada(s) na cobertura.
    Os documentos apresentados relacionados à compra de madeira nativa (DOF) estão de acordo com o art. 78 da lei complementar 649/2021.
    '''
    madeira_reflorestada = f'''
    MADEIRA REFLORESTADA:
    {cabecalho}
    Conforme documentação apresentada, relacionada ao não uso de madeira nativa na obra, foram utilizada(s) madeira(s) reflorestada(s) na obra.
    Estando de acordo com o art. 78 da lei complementar 649/2021.
    Os dados do processo foram registrados no Sistema Municipal da Qualidade Ambiental de Obras.
    '''
    sem_dof = f'''
    Não há DOF:

    Referente ao processo em questão, considerando os documentos anexos como Requisito, não foram anexo(s) documento(s) de Origem Florestal ou documento(s) de comprovação/declaração de não utilização de madeira nativa.
    Para comprovação perante o art. 78 da lei complementar 649/2021, favor anexar declaração constando o material utilizado na obra ou nota fiscal comprobatória do material utilizado.

    ESTA SECRETARIA ESTÁ À DISPOSIÇÃO PARA EVENTUAIS DÚVIDAS E ESCLARECIMENTOS (TELEFONE: 3202-4010 E-MAIL: qualidadeambiental@riopreto.sp.gov.br)
    '''
    despachos_dof = {'Estrutura': estrutura_metalica,
                     'Nativa': dof_nativa,
                     'Nativa e Reflorestada': dof_nativa_e_reflorestada,
                     'Reflorestada': madeira_reflorestada,
                     'Não há': sem_dof
                    }
    despacho = despachos_dof.get(tipo_dof)

    return despacho

def Despachar_Agrcc():

    texto = f'''
    A liberação do PGR foi deferida considerando as informações protocoladas pelo gerador e responsável técnico, referente a geração, coleta, transporte e destinação.
    A geração de resíduos apresentada pelos CTRs demonstra normalidade evidenciando boa gestão de resíduos na obra. Sendo os dados anotados nos registros desta secretaria.
    A Política Nacional de Resíduos Sólidos - PNRS Lei 12.305/2010 e a Lei Municipal 9.393/2004, exige que se faça sempre a gestão de resíduos da obra e destinação final ambientalmente correta.
    Esta observação se faz necessária para que permaneça a gestão de resíduos em futuros projetos e execução de obra.
    Esta Secretaria, por meio deste departamento se coloca à disposição, para orientações quando necessário para gestão de resíduos da construção civil.
    '''

    return texto


def Despacho_Poda_Particular():
    soma = ''
    texto = f'''AUTORIZADA A PODA DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S) DE FORMA DISTRIBUÍDA E EQUILIBRADA, SENDO: PODA DE LIMPEZA E ADEQUAÇÃO DE {soma} (TREZE) ÁRVORE(S) DA(S) ESPÉCIE(S): (03) OITI, (10) PATA-DE-VACA,  LOCALIZADA(S) NA RUA DA PRIMAVERA, 450, JARDIM SANTA CATARINA. A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.


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
    
    return