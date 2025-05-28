from cProfile import label
from datetime import datetime
from my_validador import *  # type: ignore
import num2words
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')


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


if configuration.get("app.production"):
    tabela_solicitacoes = """tab Solicitacoes"""
    tabela_laudos = """tab Protocolos"""
    tab_ruas = """tab Ruas"""
else:
    tabela_solicitacoes = """tab_Solicitacoes"""
    tabela_laudos = """tab_Protocolos"""
    tab_ruas = """Ruas"""


db.define_table('Avisos',
                Field('titulo','string'),
                Field('corpo', 'text'),
                Field('recebido_por', 'list:integer', requires=IS_IN_DB(db, 'auth_user.id', multiple=True)),
                auth.signature
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
        nome_cientifico = f"{str(esp_repr.Especie[0])}. {str(esp_repr.Especie.split(' ')[1])}"
    else:
        nome_cientifico = ''
    nome = esp_repr.Nome.replace('-', ' ')
    return f"{nome} - {nome_cientifico}"
        
        
Especies = db.define_table(
    "Especies",
    Field('id', 'id'),
    Field("Nome", "string", length=30, notnull=True),
    Field("Especie", "string", length=40),
    Field("Familia", "string", length=30),
    Field("OutroNome", "string", length=250),
    Field("Bioma", "string", length=15),
    Field("Regiao", "string", length=15),
    Field("Ameaca", "string", length=20),
    Field("GrupoEco", "string", length=10),
    Field("ClasseSucessao", "string", length=20),
    Field("Porte", "string", length=10),
    Field("TamanhoMax", "decimal(3,2)"),
    Field("IniFloracao", "string", length=15),
    Field("FimFloracao", "string", length=15),
    Field("IniFrutificacao", "string", length=15),
    Field("FimFrutificacao", "string", length=15),
    Field("CorDaFlor", "string", length=20),
    Field("TipoFruto", "string", length=10),
    Field("SinPolinizacao", "string", length=20),
    Field("SinDispercao", "string", length=20),
    Field("NativaBr", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field("Frutifera", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field("Calcada", "integer", requires=IS_CHKBOX01(on=True, off=False),
        widget=SQLFORM.widgets.boolean.widget,
        represent=lambda v, r: " [ X ]  " if v else " "),
    Field("foto", "text"),
    Field("obs", "text"),
    format = (lambda row : especie_represent(row)),
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
)


Requerimentos = db.define_table(
    "Requerimentos",
    Field("Protocolo", requires= [IS_INT_IN_RANGE("202000", "2030009999999")], label='Protocolo'),
    Field("Requerente", requires=[IS_UPPER(), Remove_Acentos()], label='Requerente'),
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
     request, db.Especies.Nome, limitby=(0, 7), min_length=3),rname="`especie ret1`",
          label='1ª Especie retirada'),
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
    Field(
        "podador_coleta",
        rname="`podador coleta`",
        requires=IS_IN_SET(["Sim", "Não", ""]),
        label='Podador coleta'
    ),
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



db.Requerimentos.total_podas = Field.Virtual(
    "total_podas",
        lambda row: sum([int(row.Requerimentos.qtd_poda1 or 0), int(row.Requerimentos.qtd_poda2 or 0),
        int(row.Requerimentos.qtd_poda3 or 0) , int(row.Requerimentos.qtd_poda4 or 0)]
        ))


db.Requerimentos.total_supressoes = Field.Virtual(
    "total_supressoes",
        lambda row: sum([int(row.Requerimentos.qtd_ret1 or 0), int(row.Requerimentos.qtd_ret2 or 0),
        int(row.Requerimentos.qtd_ret3 or 0) , int(row.Requerimentos.qtd_ret4 or 0)]
        ))

db.Requerimentos.num_extens_poda = Field.Virtual(
    "num_extens_poda",
    lambda row: num2words.num2words(row.Requerimentos.total_podas, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Requerimentos.num_extens_supressoes = Field.Virtual(
    "num_extens_supressoes",
    lambda row: num2words.num2words(row.Requerimentos.total_supressoes, lang='pt-br').upper().replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Requerimentos.Supressoes = Field.Virtual(
    "Supressoes",
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


db.Requerimentos.Podas = Field.Virtual(
    "Podas",
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
                    "",
                ]
            )
        ),
    ),
    primarykey=["Protocolo"],
    rname="`{}`".format(tabela_laudos),
    migrate=True if not configuration.get('app.production') else False,
    fake_migrate=True if not configuration.get('app.production') else False,
)


db.Laudos.Supressoes = Field.Virtual(
    "Supressoes",
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


db.Laudos.Podas = Field.Virtual(
    "Podas",
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



db.Laudos.total_podas = Field.Virtual(
    "total_podas",
        lambda row: sum([int(row.Laudos.qtd_poda1 or 0), int(row.Laudos.qtd_poda2 or 0),
        int(row.Laudos.qtd_poda3 or 0) , int(row.Laudos.qtd_poda4 or 0)]
        ))


db.Laudos.total_supressoes = Field.Virtual(
    "total_supressoes",
            lambda row: sum([int(row.Laudos.qtd_ret1 or 0), int(row.Laudos.qtd_ret2 or 0),
            int(row.Laudos.qtd_ret3 or 0) , int(row.Laudos.qtd_ret4 or 0)]
            ))


db.Laudos.num_extens_poda = Field.Virtual(
    "num_extens_poda",
    lambda row: num2words.num2words(row.Laudos.total_podas, lang='pt-br').upper()
    .replace('UM', 'UMA').replace('DOIS', 'DUAS').replace('DEZA', 'DEZE')
)


db.Laudos.num_extens_supressoes = Field.Virtual(
    "num_extens_supressoes",
    lambda row: num2words.num2words(row.Laudos.total_supressoes, lang='pt-br').upper()
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

def relat_supress_periodo(data_inicial, data_final):
    query = db.Requerimentos.Protocolo == db.Laudos.Protocolo
    query &= (db.Requerimentos.Bairro == db.Bairros.Bairro)
    query &= (db.Requerimentos.data_do_laudo >= data_inicial) 
    query &= (db.Requerimentos.data_do_laudo <= data_final)

    rows = db(query, )
    return rows


def relat_podas_periodo(data_inicial, data_final):
    query =  db.Requerimentos.qtd_poda1 > 0
    query &= (db.Requerimentos.Bairro == db.Bairros.Bairro)
    query &= (db.Requerimentos.data_do_laudo >= data_inicial) 
    query &= (db.Requerimentos.data_do_laudo <= data_final)

    rows = db(query, )
    return rows


# DADOS DE TESTE INSERIDOS AUTOMÁTICAMENTE EM AMBIENTE DE TESTE.
from faker import Faker  # type: ignore
if not configuration.get("app.production"):


    fake = Faker("pt_BR")
    if not db(db.Bairros).count():
        db.Bairros.insert(
            Bairro="Jardim Paulista", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="Vila Mariana", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="Moema", Perimetro="URBANO",  Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="Vila Madalena", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )
        db.Bairros.insert(
            Bairro="Vila Tuníca", Perimetro="URBANO", Regiao=fake.random_int(min=1, max=10)
        )

    if not db(db.Ruas).count():
        db.Ruas.insert(Endereco1="Av. Paulista", Denominacao="Paulista")
        db.Ruas.insert(Endereco1="Rua Augusta", Denominacao="Augusta")
        db.Ruas.insert(Endereco1="Rua Oscar Freire", Denominacao="Oscar Freire")
        db.Ruas.insert(
            Endereco1="Rua Teodoro Sampaio", Denominacao="Teodoro Sampaio"
        )
    if not db(db.Requerimentos).count():
        for _ in range(1000):
            db.Requerimentos.insert(
                Protocolo=fake.random_int(min=20190001, max=2025009999),
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
                p1=fake.random_element(elements=['F','T']),
                p2=fake.random_element(elements=['F','T']),
                p3=fake.random_element(elements=['F','T']),
                p4=fake.random_element(elements=['F','T']),
                p5=fake.random_element(elements=['F','T']),
                p6=fake.random_element(elements=['F','T']),
                p7=fake.random_element(elements=['F','T']),
                p8=fake.random_element(elements=['F','T']),
                p9=fake.random_element(elements=['F','T']),
                p10=fake.random_element(elements=['F','T']),
                p11=fake.random_element(elements=['F','T']),
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
