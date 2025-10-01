# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
import num2words
from pathlib import Path

if 0 == 1:
    from gluon import *  # type: ignore
    from gluon import (
        db, configuration, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP, IS_LENGTH, IS_IMAGE, # type: ignore
        Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db, IS_CHKBOX01, DAL, IS_INT_IN_RANGE, IS_CPF_OR_CNPJ,  MASK_CPF,
        MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE, SQLFORM, IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC, )  # type: ignore

    request = current.request  # type: ignore
    response = current.response  # type: ignore
    session = current.session  # type: ignore
    cache = current.cache  # type: ignore
    T = current.T  # type: ignore


if configuration.get("app.production"):
    tabela_solicitacoes = """tab Solicitacoes"""
    tabela_laudos = """tab Protocolos"""
    tab_ruas = """tab Ruas"""
else:
    tabela_solicitacoes = """tab_Solicitacoes"""
    tabela_laudos = """tab_Protocolos"""
    tab_ruas = """Ruas"""


Avisos = db.define_table('Avisos',
                Field('titulo','string'),
                Field('corpo', 'text'),
                Field('recebido_por', 'list:integer', ),
                )


regiao_nome ={1:'CENTRAL', 2:'BOSQUE', 3:'TALHADO', 4:'REPRESA',
            5:'VILA TONINHO', 6:'SCHIMITT',7:'HB', 8:'CIDADE DAS CRIANÇAS',
            9:'PINHEIRINHO' , 10:'CÉU'}

represent_regiao= lambda val, row : regiao_nome.get(val)

Bairros = db.define_table(
    "Bairros",
    Field('id', 'id'),
    Field("Bairro", "string"),
    Field("Regiao", 'integer',requires= IS_IN_SET(regiao_nome, zero=None), represent=represent_regiao ),
    Field("Perimetro", "string"),
    format="Bairro",
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False
)

Ruas = db.define_table(
    "Ruas",
    Field("ID", "id"),
    Field("Endereco1"),
    Field("Denominacao", rname="DENOMINACAO"),
    rname="`{}`".format(tab_ruas),
    primarykey=["ID"],
    format="%(Endereco1)s - %(Denominacao)s",
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
)


def especie_represent(row):
    esp_repr = db(db.Especies.id == int(row.id)).select().first()
    
    if esp_repr.Especie:
        if len(esp_repr.Especie.split(' ')) > 0:
            nome_cientifico = f"{str(esp_repr.Especie[0])}. {str(esp_repr.Especie.split(' ')[-1]) }"
        else:
            nome_cientifico = f"{str(esp_repr.Especie[0])}"
            
    else:
        nome_cientifico = ''
    nome = esp_repr.Nome.replace('-', ' ')
    return f"{nome} - {nome_cientifico}"
        
        
ameaças = {
    '(EX)': 'Extinta',
    '(EW)': 'Extinta na Natureza',
    '(CR)': 'Criticamente em Perigo',
    '(EN)': 'Em Perigo',
    '(VU)': 'Vulnerável',
    '(NT)': 'Quase Ameaçada',
    '(LC)': 'Pouco Preocupante'
}

familias = [
    'Acanthaceae', 'Achariaceae', 'Amaryllidaceae', 'Anacardiaceae', 'Anisophylleaceae', 'Annonaceae',
    'Apodanthaceae', 'Arecaceae', 'Asteraceae', 'Begoniaceae', 'Biebersteiniaceae', 'Bignoniaceae',
    'Boraginaceae', 'Brassicaceae', 'Bromeliaceae', 'Burmanniaceae', 'Burseraceae', 'Cabombaceae',
    'Cactaceae', 'Calceolariaceae', 'Campanulaceae', 'Canellaceae', 'Cannabaceae', 'Capparaceae',
    'Caprifoliaceae', 'Caricaceae', 'Celastraceae', 'Chrysobalanaceae', 'Cistaceae', 'Cleomaceae',
    'Clusiaceae', 'Combretaceae', 'Commelinaceae', 'Convolvulaceae', 'Costaceae', 'Crassulaceae',
    'Cucurbitaceae', 'Cunoniaceae', 'Cyperaceae', 'Dichapetalaceae', 'Dilleniaceae', 'Dipterocarpaceae',
    'Ebenaceae', 'Elaeocarpaceae', 'Ericaceae', 'Eriocaulaceae', 'Erythroxylaceae', 'Escalloniaceae',
    'Euphorbiaceae', 'Fabaceae', 'Flacourtiaceae', 'Gelsemiaceae', 'Gentianaceae', 'Geraniaceae',
    'Gesneriaceae', 'Gnetaceae', 'Griseliniaceae', 'Haemodoraceae', 'Haloragaceae', 'Herreriaceae',
    'Hugoniaceae', 'Hydnoraceae', 'Hydrocharitaceae', 'Hypericaceae', 'Icacinaceae', 'Iridaceae',
    'Ixonanthaceae', 'Juglandaceae', 'Juncaceae', 'Lamiaceae', 'Lauraceae', 'Lecythidaceae',
    'Lepidobotryaceae', 'Linaceae', 'Linderniaceae', 'Lissocarpaceae', 'Loasaceae', 'Lobeliaceae',
    'Loganiaceae', 'Loranthaceae', 'Lythraceae', 'Malpighiaceae', 'Malvaceae', 'Marantaceae',
    'Marcgraviaceae', 'Martyniaceae', 'Melastomataceae', 'Menispermaceae', 'Monimiaceae', 'Moraceae',
    'Moringaceae', 'Myristicaceae', 'Myrsinaceae', 'Ochnaceae', 'Oleaceae', 'Onagraceae', 'Orchidaceae',
    'Orobanchaceae', 'Oxalidaceae', 'Papaveraceae', 'Passifloraceae', 'Phrymaceae', 'Phyllanthaceae',
    'Phytolaccaceae', 'Picrodendraceae', 'Piperaceae', 'Plantaginaceae', 'Poaceae', 'Podocarpaceae',
    'Polygalaceae', 'Polygonaceae', 'Potamogetonaceae', 'Primulaceae', 'Proteaceae', 'Quiinaceae',
    'Rafflesiaceae', 'Ranunculaceae', 'Rhamnaceae', 'Rhizophoraceae', 'Rosaceae', 'Rubiaceae',
    'Rutaceae', 'Sabiaceae', 'Salicaceae', 'Santalaceae', 'Sapindaceae', 'Scrophulariaceae',
    'Simaroubaceae', 'Solanaceae', 'Styracaceae', 'Symplocaceae', 'Tetrameristaceae', 'Theaceae',
    'Theophrastaceae', 'Thymelaeaceae', 'Trigoniaceae', 'Triuridaceae', 'Turneraceae', 'Ulmaceae',
    'Urticaceae', 'Valerianaceae', 'Velloziaceae', 'Verbenaceae', 'Violaceae', 'Vivianiaceae',
    'Vochysiaceae', 'Welwitschiaceae', 'Winteraceae', 'Xyridaceae'
]

meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro',
'outubro', 'novembro', 'dezembro']

dispersoes = {'Anemocoria': 'ANE' , 'Zoocoria': 'ZOO', 'Autocoria': 'AUT' , 'Barocoria': 'BAR' }
polinizasoes = {'Anemofilia': 'ANE' , 'Hidrofilia': 'HID', 'Entomofilia': 'ENT', 'Ornitofilia': 'ORN' , 'Quiropterofilia': 'QUI', 'Zoofilia': 'ZOO' }
cores = ['vermelho', 'amarelo', 'rosa', 'branco', 'azul', 'lilás', 'creme', 'salmão', 'laranja', 'roxo', 'verde', 'preto']

Especies = db.define_table(
    "Especies",
    Field('id', 'id'),
    Field("Nome", "string", length=40, notnull=True, requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'Especies.Nome'), IS_LOWER()]),
    Field("Especie", "string", length=40, requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'Especies.Especie')]),
    Field("Familia", "string", requires=IS_IN_SET(familias), length=30),
    Field("OutroNome", "string", label='Outros Nomes', length=250),
    Field("Bioma", "string", requires=IS_IN_SET([
        'Amazônia', 'Caatinga', 'Cerrado', 'Deserto', 'Floresta Temperada',
        'Floresta Tropical', 'Mata Atlântica', 'Pampa' , 'Pantanal',
        'Pradaria', 'Taiga', 'Tundra', 'Savanas'
        ] ) ),
    Field("Regiao", "string", requires=IS_IN_SET(['',  'Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']), length=15),
    Field("Ameaca", "string", requires=IS_EMPTY_OR(IS_IN_SET(ameaças)), length=20),
    Field("GrupoEco", "string", length=10),
    Field("ClasseSucessao", "string", requires=IS_EMPTY_OR(IS_IN_SET(['Pioneira', 'Intermediária', 'Climax'])), length=20),
    Field("Porte",  "string",  requires=IS_IN_SET(['Pequeno', 'Médio', 'Grande']), length=10),
    Field("TamanhoMax", "decimal(3,2)"),
    Field("IniFloracao", "string", requires=IS_EMPTY_OR(IS_IN_SET(meses)), length=15),
    Field("FimFloracao", "string", requires=IS_EMPTY_OR(IS_IN_SET(meses)), length=15),
    Field("IniFrutificacao", "string", requires=IS_EMPTY_OR(IS_IN_SET(meses)), length=15),
    Field("FimFrutificacao", "string", requires=IS_EMPTY_OR(IS_IN_SET(meses)), length=15),
    Field("CorDaFlor", "string", requires=IS_EMPTY_OR(IS_IN_SET(cores)), length=20),
    Field("TipoFruto", "string", requires=IS_EMPTY_OR(IS_IN_SET(['Carnoso','Seco'])), length=10),
    Field("SinPolinizacao", "string", requires=IS_EMPTY_OR(IS_IN_SET(polinizasoes)), length=20),
    Field("SinDispercao", "string", requires=IS_EMPTY_OR(IS_IN_SET(dispersoes)), length=20),
    Field("NativaBr", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field("Frutifera", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field("Calcada", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field('DAP_max',  "decimal(3,2)"),
    Field("obs", "text"),
    format = (lambda row : especie_represent(row)),
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
    
)


Requerimentos = db.define_table(
    "Requerimentos",
    Field("Protocolo", 'integer' , requires= [IS_NOT_EMPTY(), ProtocPattern()]),  # type: ignore
    Field("Requerente", requires=[IS_UPPER(), Remove_Acentos()]),
    Field(
        "data_entrada",
        "date",
        requires=IS_EMPTY_OR(
            IS_DATE(format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx")
        ),
        rname="`Data de Entrada`",
        label='Data de Entrada'
    ),
    Field(
        "Endereco1", "string", requires=[IS_UPPER(), Remove_Acentos()],
        label='Endereço'
    ),
    Field("Numero1", label='Número'),
    Field("Bairro",requires=IS_IN_DB(db, "Bairros.Bairro", "%(Bairro)s", error_message='Bairro não registrado.'),
    widget=SQLFORM.widgets.autocomplete(
     request, db.Bairros.Bairro,  limitby=(0, 7), min_length=3),
     label='Bairro'),
    Field("cpf_cnpj", rname="`cpf-cnpj`", label='CPF/CNPJ'),
    Field("cep", label='CEP'),
    Field("telefone1", label='Telefone'),
    Field("email", rname="`e-mail`", label='E-mail'),
    Field("especie_ret1", widget=SQLFORM.widgets.autocomplete(
     request, db.Especies.Nome, limitby=(0, 7), min_length=3),rname="`especie ret1`", label='1ª Especie retirada'),
    Field("especie_ret2", rname="`especie ret2`"),
    Field("especie_ret3", rname="`especie ret3`"),
    Field("especie_ret4", 'list:string' ,rname="`especie ret4`"),
    Field("qtd_ret1", rname="`qtd ret1`"),
    Field("qtd_ret2", rname="`qtd ret2`"),
    Field("qtd_ret3", rname="`qtd ret3`"),
    Field("qtd_ret4", rname="`qtd ret4`"),
    Field("especie_poda1", rname="`especie poda1`"),
    Field("especie_poda2", rname="`especie poda2`"),
    Field("especie_poda3", rname="`especie poda3`"),
    Field("especie_poda4", 'list:string', rname="`especie poda4`"),
    Field("qtd_poda1", rname="`qtd poda1`"),
    Field("qtd_poda2", rname="`qtd poda2`"),
    Field("qtd_poda3", rname="`qtd poda3`"),
    Field("qtd_poda4", rname="`qtd poda4`"),
    Field("especie_ret2", rname="`especie ret2`", label='2ª Especie retirada'),
    Field("especie_ret3", rname="`especie ret3`", label='3ª Especie retirada'), 
    Field("especie_ret4", 'list:string' ,rname="`especie ret4`", label='4ª Especie retirada'),
    Field("qtd_ret1", rname="`qtd ret1`", label='Qtd 1ª retirada'),
    Field("qtd_ret2", rname="`qtd ret2`", label='Qtd 2ª retirada'),
    Field("qtd_ret3", rname="`qtd ret3`", label='Qtd 3ª retirada'),
    Field("qtd_ret4", rname="`qtd ret4`", label='Qtd 4ª retirada'),
    Field("especie_poda1", rname="`especie poda1`", label='1ª Especie poda'),
    Field("especie_poda2", rname="`especie poda2`", label='2ª Especie poda'),
    Field("especie_poda3", rname="`especie poda3`", label='3ª Especie poda'),
    Field("especie_poda4", 'list:string', rname="`especie poda4`", label='4ª Especie poda'),
    Field("qtd_poda1", rname="`qtd poda1`", label='Qtd 1ª poda'),
    Field("qtd_poda2", rname="`qtd poda2`", label='Qtd 2ª poda'),
    Field("qtd_poda3", rname="`qtd poda3`", label='Qtd 3ª poda'),
    Field("qtd_poda4", rname="`qtd poda4`", label='Qtd 4ª poda'),
    Field("no_carteira", rname="`no. carteira`", label='Nº Carteira'),
    Field(
        "data_do_laudo",
        "date",
        requires=IS_DATE(
            format=T("%d/%m/%Y"), error_message="Deve ter o formato xx/xx/20xx"
        ),
        rname="`data do laudo`",
        label='Data do Laudo'
    ),
    Field(
        "Despacho",
        requires=IS_IN_SET(
            [
                "Deferido",
                "Parcialmente Deferido",
                "Indeferido",
                "Em Análise",
                "Aguardando",
                "Com Pendência",
                "Pendente de Compesação",
                "",
            ]
        ),
    ),
    Field(
        "local_arvore",
        rname="`local arvore`",
        label="Local",
        requires=IS_IN_SET(
            ["calçada", "calçada com fiação", "área interna", "área aberta", "praça", "canteiro central", "não há árvore"]
        ),
    ),
    Field(
        "tipo_imovel",
        rname="`tipo imovel`",
        label="Tipo de Imóvel",
        requires=IS_IN_SET(["público", "privado", "institucional", "terreno", "rural"]),
    ),
    Field("protocolo_anterior", 'reference Requerimentos',
          requires=IS_EMPTY_OR(IS_IN_DB(db, "Requerimentos.Protocolo" ))),
    rname="`{}`".format(tabela_solicitacoes),
    primarykey=["Protocolo"],
    format="%(Protocolo)s",
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
)


db.Requerimentos.Endereco = Field.Virtual(
    "Endereco",
    lambda row: str(
        ", ".join(
            [
                f"RUA/AV. {row.Requerimentos.Endereco1}" or "",
                f"Nº {row.Requerimentos.Numero1}" or "",
                f"BAIRRO: {row.Requerimentos.Bairro}" or "",
            ]
        )
    ),
)



db.Requerimentos.total_podas_requeridas = Field.Virtual(
    "total_podas_requeridas",
        lambda row: sum([int(row.Requerimentos.qtd_poda1 or 0), int(row.Requerimentos.qtd_poda2 or 0),
        int(row.Requerimentos.qtd_poda3 or 0) , int(row.Requerimentos.qtd_poda4 or 0)]
        ))


db.Requerimentos.total_supressoes_requeridas = Field.Virtual(
    "total_supressoes_requeridas",
        lambda row: sum([int(row.Requerimentos.qtd_ret1 or 0), int(row.Requerimentos.qtd_ret2 or 0),
        int(row.Requerimentos.qtd_ret3 or 0) , int(row.Requerimentos.qtd_ret4 or 0)]
        ))

db.Requerimentos.num_extens_poda_requeridas = Field.Virtual(
    "num_extens_poda_requeridas",
    lambda row: num2words.num2words(row.Requerimentos.total_podas_requeridas, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Requerimentos.num_extens_supressoes_requeridas = Field.Virtual(
    "num_extens_supressoes_requeridas",
    lambda row: num2words.num2words(row.Requerimentos.total_supressoes_requeridas, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Requerimentos.Supressoes_requeridas = Field.Virtual(
    "Supressoes_requeridas",
    lambda row: " ".join(
        [
            f"({row.Requerimentos.qtd_ret1}) {row.Requerimentos.especie_ret1}"
            if row.Requerimentos.qtd_ret1
            else "",
            f", ({row.Requerimentos.qtd_ret2}) {row.Requerimentos.especie_ret2}"
            if row.Requerimentos.qtd_ret2
            else "",
            f", ({row.Requerimentos.qtd_ret3}) {row.Requerimentos.especie_ret3}"
            if row.Requerimentos.qtd_ret3
            else "",
            f", ({row.Requerimentos.qtd_ret4}) {row.Requerimentos.especie_ret4}"
            if row.Requerimentos.qtd_ret4
            else "",
        ]
    ).replace("'", "").replace("[", "").replace("]", ""),
)


db.Requerimentos.Podas_requeridas = Field.Virtual(
    "Podas_requeridas",
    lambda row: " ".join(
        [
            f"({row.Requerimentos.qtd_poda1}) {row.Requerimentos.especie_poda1}"
            if row.Requerimentos.qtd_poda1
            else "",
            f", ({row.Requerimentos.qtd_poda2}) {row.Requerimentos.especie_poda2}"
            if row.Requerimentos.qtd_poda2
            else "",
            f", ({row.Requerimentos.qtd_poda3}) {row.Requerimentos.especie_poda3}"
            if row.Requerimentos.qtd_poda3
            else "",
            f", ({row.Requerimentos.qtd_poda4}) {row.Requerimentos.especie_poda4}"
            if row.Requerimentos.qtd_poda4
            else "",
        ]
    ).replace("'", "").replace("[", "").replace("]", ""),
)


Laudos = db.define_table(
    "Laudos",
    Field("Protocolo", "reference Requerimentos"),
    Field(
        "Despacho",
        "string",
        requires=IS_EMPTY_OR(
            IS_IN_SET(
                [
                    "Deferido",
                    "Parcialmente Deferido",
                    "Indeferido",
                    "Em Análise",
                    "Aguardando",
                    "Com Pendência",
                    "Pendente de Compesação",
                    "Pendente de Compesação",
                    "Vistoriado por outro protocolo",
                    "",
                ]
            )
        ),
    ),
    Field(
        "data_do_laudo",
        "date",
        rname="`data do laudo`",
        requires=IS_EMPTY_OR(IS_DATE(format="%d/%m/%Y")),
    ),
    Field("proprietario", "string"),
    Field("morador", "string"),
    Field("especie_ret1", "string", rname="`especie ret1`"),
    Field("qtd_ret1", rname="`qtd ret1`"),
    Field("especie_ret2", "string", rname="`especie ret2`"),
    Field("qtd_ret2", rname="`qtd ret2`"),
    Field("especie_ret3", "string", rname="`especie ret3`"),
    Field("qtd_ret3", rname="`qtd ret3`"),
    Field("especie_ret4", "list:string", rname="`especie ret4`"),
    Field("qtd_ret4", rname="`qtd ret4`"),
    Field("qtd_repor", rname="`qtd repor`"),
    Field(
        "porte_repor",
        rname="`porte repor`",
        default="",
        requires=IS_IN_SET(
            ["PEQUENO", "PEQUENO OU MÉDIO", "MÉDIO", "MÉDIO OU GRANDE", "GRANDE", ""]
        ),
    ),
    Field("especie_poda1", "string", rname="`especie poda1`"),
    Field("qtd_poda1", rname="`qtd poda1`"),
    Field("especie_poda2", "string", rname="`especie poda2`"),
    Field("qtd_poda2", rname="`qtd poda2`"),
    Field("especie_poda3", "string", rname="`especie poda3`"),
    Field("qtd_poda3", rname="`qtd poda3`"),
    Field("especie_poda4", "list:string", rname="`especie poda4`"),
    Field("qtd_poda4", rname="`qtd poda4`"),
    Field("tipo"),
    Field(
        "p1", 'integer',
        label="Conflito com fiação elétrica",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p2", 'integer',
        label="Prejuízo a rede de água/esgoto",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p3", 'integer',
        label="Danos à estrutura da construção",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p4", 'integer',
        label="Restrição à passagem de pedestres",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p5", 'integer',
        label="Porte ou espécie inadequada",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p6", 'integer',
        label="Árvore senescente, debilitada por poda/pragas/parasitas",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p7", 'integer',
        label="Árvore morta/seca",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p8", 'integer',
        label="Passagem de veículos",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p9", 'integer',
        label="Obras, reforma, construção, demolição",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p10", 'integer',
        label="Projetos e/ou atividades",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field(
        "p11", 'integer',
        label="Risco à população, patrimônio",
        requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " ",
    ),
    Field("Obs", rname="`Obs.`"),
    Field(
        "tecnico",
        "string",
        requires=IS_EMPTY_OR(
            IS_IN_SET(
                [
                    "Guilherme Cavenaghi",
                    "Renan Fabrizzio Viche",
                    "Otton Garcia Arruda",
                    "Larissa Tiago Volpi"
                    "",
                ]
            )
        ),
    ),
    primarykey=["Protocolo"],
    format="%(Protocolo)s",
    rname="`{}`".format(tabela_laudos),
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
)


db.Laudos.Supressoes_laudadas = Field.Virtual(
    "Supressoes_laudadas",
    lambda row: " ".join(
        [
            f"({row.Laudos.qtd_ret1}) {row.Laudos.especie_ret1}"
            if row.Laudos.especie_ret1
            else "",
            f", ({row.Laudos.qtd_ret2}) {row.Laudos.especie_ret2}"
            if row.Laudos.especie_ret2
            else "",
            f", ({row.Laudos.qtd_ret3}) {row.Laudos.especie_ret3}"
            if row.Laudos.especie_ret3
            else "",
            f", {row.Laudos.especie_ret4 or ''}"
            if ',' in str(row.Laudos.especie_ret4)
            else f", ({row.Laudos.qtd_ret4  or ''}) {row.Laudos.especie_ret4 or ''}" 
            if row.Laudos.qtd_ret4 else '',
        ]
    ).replace("'", "").replace("[", "").replace("]", "").replace('"', ''),
)


db.Laudos.Podas_laudadas = Field.Virtual(
    "Podas_laudadas",
    lambda row: " ".join(
        [
            f"({row.Laudos.qtd_poda1}) {row.Laudos.especie_poda1}"
            if row.Laudos.especie_poda1
            else "",
            f", ({row.Laudos.qtd_poda2}) {row.Laudos.especie_poda2}"
            if row.Laudos.especie_poda2
            else "",
            f", ({row.Laudos.qtd_poda3}) {row.Laudos.especie_poda3}"
            if row.Laudos.especie_poda3
            else "",
            f", {row.Laudos.especie_poda4}"
            if ',' in str(row.Laudos.especie_poda4)
            else f", ({row.Laudos.qtd_poda4}) {row.Laudos.especie_poda4}"
            if row.Laudos.qtd_poda4 else '',
        ]
    ).replace("'", "").replace("[", "").replace("]", "").replace('"', ''),
)



db.Laudos.total_podas_laudadas = Field.Virtual(
    "total_podas_laudadas",
        lambda row: sum([int(row.Laudos.qtd_poda1 or 0), int(row.Laudos.qtd_poda2 or 0),
        int(row.Laudos.qtd_poda3 or 0) , int(row.Laudos.qtd_poda4 or 0)]
        ))


db.Laudos.total_supressoes_laudadas = Field.Virtual(
    "total_supressoes_laudadas",
            lambda row: sum([int(row.Laudos.qtd_ret1 or 0), int(row.Laudos.qtd_ret2 or 0),
            int(row.Laudos.qtd_ret3 or 0) , int(row.Laudos.qtd_ret4 or 0)]
            ))


db.Laudos.num_extens_poda_laudadas = Field.Virtual(
    "num_extens_poda_laudadas",
    lambda row: num2words.num2words(row.Laudos.total_podas_laudadas, lang='pt-br').upper()
    .replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Laudos.num_extens_supressoes_laudadas = Field.Virtual(
    "num_extens_supressoes_laudadas",
    lambda row: num2words.num2words(row.Laudos.total_supressoes_laudadas, lang='pt-br').upper()
    .replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Laudos.num_extens_repor = Field.Virtual(
    "num_extens_repor",
    lambda row: num2words.num2words(row.Laudos.qtd_repor or 0, lang='pt-br').upper()
    .replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)

db.Laudos.motivos = Field.Virtual(
    "motivos",
    lambda row: ''.join( [
        f", {db.Laudos.p1.label}" if row.Laudos.p1 == 1 else '',
        f", {db.Laudos.p2.label}" if row.Laudos.p2 == 1 else '',
        f", {db.Laudos.p3.label}" if row.Laudos.p3 == 1 else '',
        f", {db.Laudos.p4.label}" if row.Laudos.p4 == 1 else '',
        f", {db.Laudos.p5.label}" if row.Laudos.p5 == 1 else '',
        f", {db.Laudos.p6.label}" if row.Laudos.p6 == 1 else '',
        f", {db.Laudos.p7.label}" if row.Laudos.p7 == 1 else '',
        f", {db.Laudos.p8.label}" if row.Laudos.p8 == 1 else '',
        f", {db.Laudos.p9.label}" if row.Laudos.p9 == 1 else '',
        f", {db.Laudos.p10.label}" if row.Laudos.p10 == 1 else '',
        f", {db.Laudos.p11.label}" if row.Laudos.p11 == 1 else '']                     
                         )
)

 

fotos = db.define_table('fotos',
        Field('titulo'),
        Field('foto', 'upload',               
                uploadseparate=True, uploadfolder= Path(pasta_viveiro_fotos, session.function if session.function else 'Outras_fotos')  ,
                requires=[IS_EMPTY_OR(IS_LENGTH( 7864320, 20480, error_message= 'deve ser maior que 20k e menor que 7,5 megabites')),
                          IS_IMAGE_COMPACT( error_message='deve ser imagem no formato jpeg ou png')], autodelete = True,   # type: ignore
                ),
        Field('caminho', 'string'),
        Field('idEspecie', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Especies.id', "%(Nome)s"))),
        Field('idLaudo', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Laudos.Protocolo', "%(Protocolo)s")), ),
        Field('fonte', 'string'),
        Field('url', 'string'),
        Field('tipo', label='tipo da foto'),
        Field('obs', 'text'),
        Field('created_by', default=auth.user_id,
              label='Registrado por:',
              represent = lambda row, val: authdb.auth_user(authdb.auth_user.id== row).first_name), # type: ignore
        Field('created_on', label='Registrado em:', default=request.now),
        Field('modified_by', update=auth.user_id,
              label='Modificado por:',
              represent = lambda row, val: authdb.auth_user(authdb.auth_user.id== row).first_name if row else ''), # type: ignore
        Field('modified_on', label='Modificado em:', default=request.now, update=request.now), 
        
        migrate= True if not configuration.get('app.production') else False,
        fake_migrate= True if not configuration.get('app.production') else False,
                        )




# DADOS DE TESTE INSERIDOS AUTOMÁTICAMENTE EM AMBIENTE DE TESTE.
if not configuration.get("app.production"):

    from faker import Faker  # type: ignore

    fake = Faker("pt_BR")
    if not db(db.Bairros).count():
        db.Bairros.insert(
            Bairro="ALTO RIO PRETO (JARDIM)", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALVORADA (ESTANCIA)", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="AMERICA (JARDIM)", Perimetro="URBANO",  Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ALICE (JARDIM)", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="ANCHIETA (VILA)", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )

    if not db(db.Ruas).count():
        db.Ruas.insert(Endereco1="Av. Paulista", Denominacao="Paulista")
        db.Ruas.insert(Endereco1="Rua Augusta", Denominacao="Augusta")
        db.Ruas.insert(Endereco1="Rua Oscar Freire", Denominacao="Oscar Freire")
        db.Ruas.insert(
            Endereco1="Rua Teodoro Sampaio", Denominacao="Teodoro Sampaio"
        )
    if not db(db.Requerimentos).count():
        for i in range(1000):
            db.Requerimentos.insert(
                Protocolo=i,  #fake.random_int(min=20190001, max=2025009999),
                Requerente=fake.name(),
                data_entrada=fake.date(),
                Endereco1=fake.street_name(),
                Numero1=fake.random_int(min=1, max=9999),
                Bairro=fake.random_element(
                   elements=[el.get('Bairro') for el in db(db.Bairros.id > 0).select(db.Bairros.Bairro).as_list()]
                ),
                cpf_cnpj=fake.cpf(),
                telefone1=fake.phone_number(),
                email=fake.email(),
                especie_ret1=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret1=fake.random_int(min=1, max=10),
                especie_ret2=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret2=fake.random_int(min=1, max=10),
                especie_ret3=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret3=fake.random_int(min=1, max=10),
                especie_ret4=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret4=fake.random_int(min=1, max=10),
                especie_poda1=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda1=fake.random_int(min=1, max=10),
                especie_poda2=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda2=fake.random_int(min=1, max=10),
                especie_poda3=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda3=fake.random_int(min=1, max=10),
                especie_poda4=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda4=fake.random_int(min=1, max=10),
                podador_coleta=fake.random_element(elements=["Sim", "Não", ""]),
                no_carteira=fake.random_int(min=1000, max=9999),
                data_do_laudo=fake.date(),
                Despacho=fake.random_element(
                    elements=[
                        "Deferido",
                        "Parcialmente Deferido",
                        "Indeferido",
                        "Em Análise",
                        "Aguardando",
                        "",
                    ]
                ),
                local_arvore=fake.random_element(
                    elements=[
                        "calçada",
                        "calçada com fiação",
                        "área interna",
                        "área aberta",
                    ]
                ),
                tipo_imovel=fake.random_element(
                    elements=["público", "privado", "institucional"]
                ),
            )
            db.commit()

    if not db(db.Laudos).count():
        for _ in range(666):
            db.Laudos.insert(
                Protocolo=fake.random_element(
              elements= [el.get('Protocolo') for el in db(db.Requerimentos.Protocolo!=0).select(db.Requerimentos.Protocolo)]),
                Despacho=fake.random_element(
                    elements=[
                        "Deferido",
                        "Parcialmente Deferido",
                        "Indeferido",
                        "Em Análise",
                        "Aguardando",
                        "",
                    ]
                ),
                data_do_laudo=fake.date(),
                proprietario=fake.name(),
                morador=fake.name(),
                especie_ret1=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret1=fake.random_int(min=1, max=10),
                especie_ret2=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret2=fake.random_int(min=1, max=10),
                especie_ret3=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret3=fake.random_int(min=1, max=10),
                especie_ret4=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_ret4=fake.random_int(min=1, max=10),
                qtd_repor=fake.random_int(min=1, max=10),
                porte_repor=fake.random_element(
                    elements=[
                        "PEQUENO",
                        "PEQUENO OU MÉDIO",
                        "MÉDIO",
                        "MÉDIO OU GRANDE",
                        "GRANDE",
                        "",
                    ]
                ),
                especie_poda1=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda1=fake.random_int(min=1, max=10),
                especie_poda2=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda2=fake.random_int(min=1, max=10),
                especie_poda3=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda3=fake.random_int(min=1, max=10),
                especie_poda4=fake.random_element(
                    elements=["Ipe", "Pau-Brasil", "Pau-Ferro", "Pau-Jacaré"]
                ),
                qtd_poda4=fake.random_int(min=1, max=10),
                tipo=fake.random_element(
                    elements=["Supressão", "Poda", "Reposição", ""]
                ),
                p1=fake.random_element(elements=[0,1]),
                p2=fake.random_element(elements=[0,1]),
                p3=fake.random_element(elements=[0,1]),
                p4=fake.random_element(elements=[0,1]),
                p5=fake.random_element(elements=[0,1]),
                p6=fake.random_element(elements=[0,1]),
                p7=fake.random_element(elements=[0,1]),
                p8=fake.random_element(elements=[0,1]),
                p9=fake.random_element(elements=[0,1]),
                p10=fake.random_element(elements=[0,1]),
                p11=fake.random_element(elements=[0,1]),
                Obs=fake.text(),
                tecnico=fake.random_element(
                    elements=[
                        "Gandalf the Mage",
                        "Sauruman the White",
                        "Galadriel daugther of Finarfin",
                        "",
                    ]
                ),
            )
            db.commit()


