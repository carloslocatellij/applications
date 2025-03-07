

import num2words

def Despacho_Poda_Particular(query):
    soma = sum([x for x in [query.get('qtd_poda1'), query.get('qtd_poda2'), query.get('qtd_poda3'), query.get('qtd_poda4')] if x])
    num_extenso = num2words.num2words(soma, lang='pt-br')
    texto = f'''AUTORIZADA A PODA DE NO MÁXIMO 25% DO VOLUME DA COPA DA(S) ÁRVORE(S) DE FORMA DISTRIBUÍDA E EQUILIBRADA, SENDO: PODA DE LIMPEZA E ADEQUAÇÃO DE {soma} ({num_extenso}) ÁRVORE(S) DA(S) ESPÉCIE(S): {query.get('Podas')},  LOCALIZADA(S) NA {query.get('Endereco')}. A PODA REALIZADA EM VOLUME MAIOR QUE 25% (VINTE E CINCO POR CENTO) DA COPA ORIGINAL DA ÁRVORE É CONSIDERADA DRÁSTICA E PODE CAUSAR SÉRIOS DANOS À SAÚDE DA ÁRVORE.

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
    
    return texto