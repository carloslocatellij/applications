# -*- coding: utf-8 -*-

import datetime
import os
from pathlib import Path

if 0==1: # Este namespace serve apenas para a IDE enchergar e trabalhar com os itens abaixo
    from gluon import *
    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH,\
     IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01, IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos,\
     IS_DECIMAL_IN_RANGE, IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T



#BANCO LOCAIS
Cidades = db.define_table ('Cidades',
	Field ('Cidade', 'string', notnull=True, requires=IS_UPPER()),
	Field ('CEP', 'integer', notnull=True),
	Field ('Id', 'id'),
	format = '%(Cidade)s',
    fake_migrate=True,
    )


regiao_cor ={1:'CENTRAL', 2:'BOSQUE', 3:'TALHADO', 4:'REPRESA', 5:'VILA TONINHO', 6:'SCHIMITT',
7:'HB', 8:'CIDADE DAS CRIANÇAS', 9:'PINHEIRINHO' , 10:'CÉU'}


Bairros = db.define_table ('Bairros',
   	Field ('Id', 'id'),
   	Field ('Bairro', 'string', notnull=True, requires=IS_UPPER()),
   	Field ('Cor', 'string',),
   	Field ('IdCidade', 'reference Cidades', label='Cidade'),
	Field ('Regiao', 'integer',requires= IS_IN_SET(regiao_cor, zero=None)),
	format = '%(Bairro)s',
    fake_migrate=True,
    )


Logradouros = db.define_table ('Logradouros',
	Field ('Logradouro', 'string', notnull=True, requires=[IS_NOT_EMPTY() ,IS_UPPER(), Remove_Acentos()]),
	Field ('Cep', 'integer',),
	Field ('Id', 'id'),
	Field ('Denominacao',  requires=IS_IN_SET(['-','ALAMEDA','AVENIDA','ESTR. MUN.','ESTRADA',
    'PRAÇA','RODOVIA','RUA','TRAVESSA','VIA']),notnull=True, label='Tipo'),
	Field ('Prefixo',  requires=IS_IN_SET(['-','DR.','COM.','GOV.','PRES.','PE.','CAP.','CEL.',
    'DRA.','GAL.','PROF.','MAJ.','MISSIO','PAST',
'PAST.','SGTO.','FREI','BRIG.','IRMÃ','TEN.','PROFA.','SARG.','SRA.'])),
	Field ('No', 'integer', label='Nº expecifico'),
	Field ('NoInicial','integer', label='Nº inicial'),
	Field ('NoFinal', 'integer', label='Nº final'),
	Field ('Lado'),
	Field ('Complemento', 'string'),
	Field ('IdBairro', 'reference Bairros', label='Bairro', cache=(cache.ram, 900), cacheable=True),
	Field ('IdCidade', 'reference Cidades', label='Cidade', cache=(cache.ram, 900), cacheable=True),
	format = (lambda row : logradouro_represent(row)),
    fake_migrate=True,
    )


def logradouro_represent(row):
	repr_logradouro = db((db.Logradouros.Id == int(row.id)) &
    (db.Logradouros.IdBairro == db.Bairros.Id)).select(
    db.Logradouros.Logradouro, db.Logradouros.NoInicial,
    db.Logradouros.NoFinal, db.Logradouros.Cep, db.Bairros.Bairro).first()
	if repr_logradouro:
		logr = str(repr_logradouro.Logradouros.Logradouro) + ', Bairro: ' + str(repr_logradouro.Bairros.Bairro) + \
        ', CEP: ' + str(repr_logradouro.Logradouros.Cep) + (', do n. ' if repr_logradouro.Logradouros.NoInicial else '') \
         + str(repr_logradouro.Logradouros.NoInicial if repr_logradouro.Logradouros.NoInicial else '') + \
         (', até  n. ' if repr_logradouro.Logradouros.NoFinal else '')+\
          str(repr_logradouro.Logradouros.NoFinal if repr_logradouro.Logradouros.NoFinal else '')
		return logr
	else:
		return ''


Enderecos = db.define_table ('Enderecos',
	Field ('Id', 'id'),
	Field ('IdLogradouro', 'reference Logradouros',
     requires=IS_IN_DB(db, 'Logradouros.Id', logradouro_represent), label= 'Logradouro', ),
	Field ('Num'),
	Field ('Quadra', 'string', ),
	Field ('Lote', 'string'),
	Field ('Tipo', 'string', default= '-',
     requires=IS_IN_SET([None,'-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LOJA.','CASA','MARGINAL.'])),
	Field ('Complemento', 'string', default= '-', ),
	Field ('TipoB', 'string', default= '-',
     requires= IS_IN_SET([None,'-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LOJA.','CASA','MARGINAL.']),
     label='outro tipo'),
	Field ('ComplementoB',  'string', default= '-', label='Outro compl.'),
	format = (lambda row : endereco_represent1(row)),
    fake_migrate=True,
    )


def endereco_represent(row):
	repr_endereco = db((db.Enderecos.Id == int(row.id)) &
     (db.Logradouros.Id == db.Enderecos.IdLogradouro) &
     (db.Logradouros.IdBairro == db.Bairros.Id)).select(db.Logradouros.Logradouro,
     db.Logradouros.Denominacao, db.Logradouros.Prefixo,
     db.Enderecos.Num, db.Enderecos.Quadra, db.Enderecos.Lote, db.Bairros.Bairro,
      orderby=db.Logradouros.Logradouro).first()
	if repr_endereco:
		endereco = '' if repr_endereco.Logradouros.Denominacao in ['NULL', 'None', '-'] else\
         str(repr_endereco.Logradouros.Denominacao) + ' ' +str('' if repr_endereco.Logradouros.Prefixo
          in ['NULL', 'None', '-']  else str(repr_endereco.Logradouros.Prefixo  ))  +  ' '+\
            str(repr_endereco.Logradouros.Logradouro) + ', ' \
            + str(repr_endereco.Enderecos.Num if repr_endereco.Enderecos.Num != 0 else ' Nº: S/N') \
            + ',  Qd: ' + str(repr_endereco.Enderecos.Quadra) \
            + ',  Lt: ' + str(repr_endereco.Enderecos.Lote) \
            + ',   Bairro: ' + str(repr_endereco.Bairros.Bairro)
		return endereco
	else:
		return ''


def endereco_represent1(row):
	repr_endereco = db((db.Enderecos.Id == int(row.id)) &
     (db.Logradouros.Id == db.Enderecos.IdLogradouro) &
     (db.Logradouros.IdBairro == db.Bairros.Id)).select(db.Logradouros.Logradouro,
     db.Logradouros.Denominacao, db.Logradouros.Prefixo,  db.Enderecos.Num,
      db.Enderecos.Quadra, db.Enderecos.Lote, db.Bairros.Bairro, orderby=db.Logradouros.Logradouro).first()
	if repr_endereco:
		endereco = str(repr_endereco.Logradouros.Logradouro) + ', ' \
            + str(repr_endereco.Enderecos.Num if repr_endereco.Enderecos.Num != 0 else ' Nº: S/N') \
            + ',  Qd: ' + str(repr_endereco.Enderecos.Quadra) \
            + ',  Lt: ' + str(repr_endereco.Enderecos.Lote) \
            + ',   Bairro: ' + str(repr_endereco.Bairros.Bairro)
		return endereco
	else:
		return ''

#PESSOAS



Pessoas = db.define_table ('Pessoas',
	Field ('Id', 'id'),
	Field ('Idm', 'integer' ),
	Field ('Nome', 'string', length='115',
     requires = [IS_NOT_EMPTY() ,IS_UPPER(), Remove_Acentos()], notnull=True),
    Field ('CPF', 'string', unique=True,
     requires=[IS_EMPTY_OR(IS_CPF_OR_CNPJ()), IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CPF',
     error_message='Já existe uma Pessoa com este Número de CPF'))],
    represents= (lambda row: MASK_CPF()(row)) ),
    Field ('CNPJ', 'string', unique=True,
     requires=[IS_EMPTY_OR(IS_CPF_OR_CNPJ()),IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CNPJ',
     error_message='Já existe uma Empresa com este Número de CNPJ')) ],
     represents= (lambda row: MASK_CNPJ()(row)) ),
    Field ('IdEndereco', 'reference Enderecos',
     requires=IS_EMPTY_OR(IS_IN_DB(db, 'Enderecos.Id', endereco_represent)), label="Endereço"),
	Field ('Telefone', 'string'),
	Field ('celular', 'string'),
	Field ('Email', 'string', requires=IS_LOWER()),
	Field ('Categoria', 'text'),
    Field ('RegistroProf', 'string'),
    auth.signature,
	format = (lambda row : pessoa_represent(row)),
    #primarykey=['Id']
    fake_migrate=True,
	)

db.Pessoas.CPF.filter_out = lambda row: MASK_CPF()(row) if row else ''
db.Pessoas.CNPJ.filter_out = lambda row: MASK_CNPJ()(row) if row else ''




def pessoa_represent(row):
	repr_pessoa = db(db.Pessoas.Id == int(row.id)).select(db.Pessoas.Nome,
    db.Pessoas.CPF, db.Pessoas.CNPJ, orderby=db.Pessoas.Nome).first()
	if repr_pessoa:
		pessoa = '{} - {}'.format(str(repr_pessoa.Nome) ,  str(repr_pessoa.CPF)
        if repr_pessoa.CPF else str(repr_pessoa.CNPJ))
		return pessoa
	else:
		return ''


Dpto = db.define_table('Dpto',
	Field('Idm', 'integer'),
	Field('Departamento', 'string', required=True),
	Field('Orgao', 'reference Dpto',  ),
	Field('Telefone', 'string'),
	primarykey= ['Idm'],
	format='%(Departamento)s',
	fake_migrate=True,
    )


Servicos = db.define_table('Servicos',
    Field('Servico', 'string', label='Serviço'),
    Field('Dpto', 'reference Dpto', label='Departamento'),
    format='%(Servico)s',
    fake_migrate=True,
)

Processos = db.define_table('Processos',
    Field('Protocolo',  'string', unique=True, notnull=True,
     requires= [IS_NOT_IN_DB(db, 'Processos.Protocolo',
     error_message='Protocolo já Existe'), CLEANUP()]),
    Field('IdPessoa',  'reference Pessoas' , label= 'Pessoa'),
    Field('IdDpto', 'reference Dpto' , label='Departamento'),
    Field('DataReg', 'datetime', label = 'Data de Registro',
     default=datetime.datetime.now(),  writable=False),
    Field('IdTipo', 'reference Servicos',
     requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format), label='Tipo' ),
    Field('Assunto', 'string'),
    Field('IdCateg', 'integer', label = 'Categoria'),
    auth.signature,
    format='%(Protocolo)s',
    fake_migrate=True,
)
#BANCO CONSTRUCOES

Obras= db.define_table('Obras',
    Field('Id', 'id'),
    Field('Protocolo', 'reference Processos',  unique=True),
    Field('protocolo_dof', 'reference Processos',  unique=True),
    Field('protocolo_grcc', 'reference Processos',  unique=True),
    Field('CadMunicipal', 'string', label='Cadastro Mun.', unique=True,
     requires=[IS_ALPHANUMERIC(), IS_MATCH(r"(\d{8})",error_message="Valor não permitido")
     ,IS_NOT_IN_DB(db, 'Obras.CadMunicipal',
     error_message='Já existe Obra com este Número de Cadastro')] ),
    Field('Alvara', 'string', label='Alvará'),
    Field('DataAlvara', 'date', label='Data do alvará',
     requires = IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),
     error_message='deve ser no formato Dia/Mês/Ano!'))),
    Field('IdGerador', 'reference Pessoas',
     requires=IS_IN_DB(db, 'Pessoas.Id', pessoa_represent), label='Gerador' ),
    Field('resptecnico', 'reference Pessoas', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format),
     ),label='Responsável Técnico' ),
    Field('IdEndereco', 'reference Enderecos', unique=True,
     requires=IS_IN_DB(db, 'Enderecos.Id', endereco_represent1 ), label="Endereço"  ) ,
    Field('Finalidade', 'string', label='Finalidade'),
    Field('PrazoExec', 'decimal(7,2)', label='Prazo de execução', readable=False),
    Field('AreaTerreno', 'decimal(7,2)', requires=  IS_DECIMAL_IN_RANGE(10, 9999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"), label= 'Área do Terreno'),
    Field('AreaConstrExist', 'decimal(7,2)',
     requires=  IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado")), label= 'Área Construída anterior'),
    Field('AreaConstrDemolir', 'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado")),  label= 'Área Demolida/Demolir'),
    Field('AreaConstrExecutar', 'decimal(7,2)',
    requires= IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
    error_message="Valor fora do permitido ou mal formatado"),  label= 'Área à Executar/Executada'),
    Field('Corte', 'decimal(7,2)', requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.0, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado")),  label= 'Corte de terra'),
    Field('Aterro', 'decimal(7,2)', requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.0, 999999,dot=",",
     error_message="Valor fora do permitido ou mal formatado")),  ),
    Field('PavtosSubS', 'integer', label='Pavtos Inferiores'),
    Field('PavtosSobreS', 'integer', label='Pavtos Sob o Solo'),
    Field('Nquartos', 'integer', label='Num. de Quartos'),
    Field('Edicula', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)), represent=lambda v, r: '  ' if v is None else 'X',
     widget=SQLFORM.widgets.boolean.widget),
    Field('Piscina', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)), represent=lambda v, r: '  ' if v is None else 'X',
     widget=SQLFORM.widgets.boolean.widget),
    Field('CobertMetalica', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)), represent=lambda v, r: '  ' if v is None else 'X',
     widget=SQLFORM.widgets.boolean.widget, label='Cobertura Metálica'),
    Field('MadeiraReflorest', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)), represent=lambda v, r: '  ' if v is None else 'X',
    widget=SQLFORM.widgets.boolean.widget, labe='Cobertura Mad. Reflorestada'),
    Field('Deck', 'string', requires=IS_IN_SET(['', 'Nativa', 'Reflorestada', 'Outro'])),
    Field('Pergolado', 'string', requires=IS_IN_SET(['', 'Nativa', 'Reflorestada', 'Outro'])),
    Field('Obs', 'text'),
    auth.signature,
    plural = 'Obras',
    format = '%(CadMunicipal)s Cadastro - : %(Alvara)s/%(DataAlvara)s Alvará',
    fake_migrate = True,
    )





Pgrcc = db.define_table('Pgrcc',
    Field('idgerador', 'reference Pessoas', requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format),
    label='Gerador' ),
    Field('idobra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id', db.Obras._format,),
    label='Obra' ),
    Field('protocolo', 'reference Processos',  requires=IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('metodoconstrutivo', 'text', label='Método Construtivo' ),
    Field('resptecnico', 'reference Pessoas', requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format),
     label='Responsável Técnico' ),
    Field('sigor', 'integer', requires = IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pgrcc.sigor',
     error_message='já Existe PGRCC com este número de Sigor'))),
    Field('obs', 'text'),
    Field('concreto', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('argamassa', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('alvenaria', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('ceramica', 'decimal(7,2)', requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('outros_ca', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")), label='Outros Classe A'),
    Field('solo', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('madeira','decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('plastico', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")), label='plástico'),
    Field('papel', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('metal', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('vidro', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('gesso', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('outros_cb', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),label='Outros Classe B'),
    Field('outros_cc', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),label='Outros Classe C'),
    Field('tinta', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('solvente', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('oleo', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    Field('outros_cd', 'decimal(7,2)',requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(
    0.00, 99999.99, dot=",", error_message="Valor fora do permitido ou mal formatado")),),
    auth.signature,
    plural = 'Pgrccs',
    format = (lambda row : pgrcc_represent(row)),
    )

db.Pgrcc.cls_a = Field.Virtual('cls_a', lambda row: sum([row.Pgrcc.concreto or 0 , row.Pgrcc.argamassa or 0
 , row.Pgrcc.alvenaria or 0, row.Pgrcc.ceramica or 0, row.Pgrcc.outros_ca or 0]))

db.Pgrcc.cls_b = Field.Virtual('cls_b', lambda row: sum([row.Pgrcc.madeira or 0 , row.Pgrcc.plastico or 0,
 row.Pgrcc.papel or 0 , row.Pgrcc.metal or 0 , row.Pgrcc.vidro or 0 , row.Pgrcc.gesso or 0 , row.Pgrcc.outros_cb or 0]) )

db.Pgrcc.cls_c = Field.Virtual('cls_c', lambda row: sum([row.Pgrcc.outros_cc or 0]) )

db.Pgrcc.cls_d = Field.Virtual('cls_d', lambda row: sum( [row.Pgrcc.tinta or 0 , row.Pgrcc.solvente or 0
 , row.Pgrcc.oleo or 0, row.Pgrcc.outros_cd or 0 ]) )

#db.Pgrcc.modified_on.filter_out = lambda row: row.strftime("%d/%M/%Y %H:%M:%S")


def pgrcc_represent(row):
	represent = db((db.Pgrcc.protocolo == int(row.protocolo)) & (db.Pgrcc.protocolo == db.Processos.id)).select(db.Processos.Protocolo).first()
	if represent:
		return represent.Protocolo
	else:
		return ''


DofsObra = db.define_table('DofsObra',
    Field('id','id'),
    Field('IdDof','string', notnull=True, unique=True, label='DOF' ),
    Field('IdObra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id',
    db.Obras._format, )),
    #auth.signature,
    )


MadeirasDof = db.define_table ('MadeirasDof',
	Field('Id', 'id'),
	Field('IdDof', 'string', requires=IS_IN_DB(db, 'DofsObra.IdDof',
    db.DofsObra._format, ),  notnull=True),
	Field('Item', 'integer',required=True),
	Field('Produto', 'text', length=45, required=True),
	Field('Especie', 'text', length=55, required=True),
	Field('Popular', 'text', length=35, required=True),
	Field('Qtd', 'decimal(10,4)',required=True ),
	Field('Unidade', 'text', length=2, required=True),
	Field('Valor', 'text', length=10, required=True),
    #fake_migrate=True,
    )



Analise_GRCC = db.define_table('Analise_GRCC',
    Field('idobra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id', db.Obras._format, )),
    Field('idpgrcc', 'reference Pgrcc', requires=IS_IN_DB(db, 'Pgrcc.id', pgrcc_represent)),
    Field('r_cls_a', 'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"))),
    Field('r_cls_b',  'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"))),
    Field('r_cls_c',  'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"))),
    Field('r_cls_d',  'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"))),
    Field('solo',  'decimal(7,2)',
    requires= IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0.00, 999999, dot=",",
     error_message="Valor fora do permitido ou mal formatado"))),
    Field('Obs', 'text'),
    auth.signature,
    plural = "Analise_GRCC",
    #fake_migrate=True
)
db.Analise_GRCC._plural = "Analise_GRCC"

# Licencas = db.define_table('Licenca',
#     Field('Num', 'string', ),
#     Field('Tipo', 'string', requires=IS_IN_SET(['L. Instalação', 'L. Operação', 'L. Renovação'])),
#     Field('Protocolo', 'reference Processos', requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
#     Field('Anterior', 'string',),
#     Field('IdEmpresa', 'reference Pessoas'),
#     Field('Unid_Destino','reference UnidadeDestino', requires=IS_IN_DB(db, 'UnidadeDestino.Id',
# Unid_Destino_represent), label="ATT"),
#     Field('Data', 'date', requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!')),
#     Field('IdEndereco', 'reference Enderecos'),
#     Field('Exigencias', 'text'),
#     Field('validade', 'date',  requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!') ),
#     Field('Status', 'boolean'),
#     #auth.signature,
#     format= '%(Num)s',
#     #fake_migrate=True,
# )


Docs_do_Proc_PGRCC =   ['Requerimento', 'ART/RRT', 'PGRCC Municipal', 'PGR Sigor', 'Proj. Arquitetônico', 'Procuração' ]


Campos_do_Proc_PGRCC = ['Nome Gerador', 'CPF/CNPJ Gerador', 'Nome Resp. Téc.', 'Finalidade da Obra', 'Endereco',
                        'Matrícula', 'Cadastro Mun.', 'Coordenadas', 'Área do terreno', 'Área existente', 'Área demolida'
                        'Área construida final', 'Área pavimentação', 'Corte ', 'Aterro ', 'Processos Construtivos',
                        'Resíduos Classe A', 'Resíduos Classe B', 'Resíduos Classe C', 'Resíduos Classe D',
                        'Inic. p/ Minimização', 'Inic. p/ Absorção na Obra', 'Inic. p/ Acondicionamento',
                        'Destino a Ser Dado Classe A', 'Destino a Ser Dado Classe B', 'Destino a Ser Dado Classe C',
                        'Destino a Ser Dado Classe D', 'Destino a Ser Dado Outros', 'Identificação do transportador',
                        'Identificação da área receptora', 'Declaração do Gerador', 'Declaração do Resp. Téc.', 'Ausente']


TipoAnalise =            ['Dado não confere', 'Não assinado', 'Desacordo com PGR Sigor', 'Desacordo com PGR Mun.',
 'Desacordo com Outros Docs.', 'Não atende a Lei 9393/2004',
                         'Abaixo das Estatísticas', 'Acima das Estatísticas', 'Muito Abaixo das Estatísticas',
 'Muito Acima das Estatísticas', 'Ausente'
                          ]



db.define_table( 'AnaliseTec',
    Field('Protocolo', 'reference Processos',
     requires = IS_IN_DB(db, 'Processos.id', db.Processos._format), readable=False ),
    Field('DocsProcesso', 'string',
     requires=IS_IN_SET( ('Requerimento', 'ART RRT', 'PGRCC Municipal', 'PGR Sigor',
     'Proj. Arquitetonico', 'Procuração' )),
     label='Documento do Processo'),
    Field('CamposProcesso', 'string',
     requires=IS_IN_SET(Campos_do_Proc_PGRCC), label='Campo do Processo'),
    Field('TipoAnalise', 'string',
     requires=IS_IN_SET(TipoAnalise), label='Análise'),
    Field('Obs', 'text', label='Observações'),
    auth.signature,
    #fake_migrate=True,
)


Procedimentos = db.define_table('Procedimentos',
    Field('Procedimento', 'string', notnull=True, requires=IS_UPPER()),
    Field('Tipo','list:reference Servicos', multiple=True,
     requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format, multiple=True),
     widget=SQLFORM.widgets.checkboxes.widget, label='Tipo' ),
    Field('ordem', 'integer'),

    auth.signature,
    format= '%(Procedimento)s',
    fake_migrate=True,
)


Tarefas = db.define_table('Tarefas',
    Field('Titulo','string', notnull=True, requires=IS_UPPER() ),
    Field('Protocolo', 'reference Processos',
     requires=[IS_IN_DB(db, 'Processos.id', db.Processos._format), IS_NOT_IN_DB(
     db, 'Tarefas.Protocolo', error_message='Protocolo já Existe') ]),
    Field('Responsavel', 'reference auth_user',
     requires=IS_IN_DB(db, 'auth_user.id', '%(first_name)s')),
    Field('DataIni', 'date', default=datetime.date.today(), label='Data Inicial',
     requires=IS_DATE(format=T('%d/%m/%Y'),
     error_message='A data e deve estar no formato dia/mês/ano')),
    Field('DataFim', 'date', label='Data Final',
     requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),
     error_message='A data e deve estar no formato dia/mês/ano'))),
    Field('Descricao', 'text', ),
    Field('Tipo', 'reference Servicos',
     requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format), label='Tipo' ),
    Field('checklist','list:reference Procedimentos', multiple=True,
     requires=IS_IN_DB(db, 'Procedimentos.id', db.Procedimentos._format, multiple=True, zero='off'),
     widget=SQLFORM.widgets.checkboxes.widget),
    Field('Status', 'string',
     requires=IS_IN_SET(['---', 'Iniciada', 'Em Andamento', 'Aguardando retorno', 'Concluida']),
     default='Iniciada'),
    auth.signature,
    #fake_migrate=True,
    )




Publicidades = db.define_table('Publicidades',
    Field('Protocolo', 'reference Processos',
     requires=IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('resptecnico', 'reference Pessoas',
     requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format), label='Responsável Técnico' ),
    Field('IdEndereco', 'reference Enderecos', unique=True,
     requires=IS_IN_DB(db, 'Enderecos.Id', endereco_represent ), label="Endereço"  ) ,
    Field('Descricao', 'text'),
    Field('Materiais', 'string'),
    Field('Dimensoes', 'list:string', multiple=True,
     requires=IS_FLOAT_IN_RANGE(0.00, 9999, dot=".", error_message="Valor não permitido")),
    auth.signature,
    #fake_migrate=False,
    )

#TODO: Fazer este campo calculado funcionar
db.Publicidades.area_total = Field.Virtual('area_total',
 lambda row: sum( [float(d) for d in list(row.Publicidades.Dimensoes)]) )


pasta_servidor_de_arq = Path('F:\\')
pasta_qualidade = Path(pasta_servidor_de_arq, 'Qualidade Ambiental')
pasta_qualidade_habite_se = Path(pasta_qualidade, 'HABITE-SE - APROVA Digital')
pasta_qualidade_pgr = Path(pasta_qualidade, 'PGRCC - GESTÃO DIGITAL')
pasta_qualidade_pgr_ano = Path(pasta_qualidade_pgr, str(datetime.datetime.today().year))
pasta_de_modelos_do_servidor_de_arquivos = Path('F:\\Qualidade Ambiental\\DOCUMENTOS\\MODELOS')

pastas_aprova = ['A - RECEPÇÃO - AVALIAÇÃO',
 'B - COMPARECIMENTO DOF E CTR',
 'C - ANÁLISE TÉC - DOF E CTR',
 'D - LANÇADOS NO SISTEMA - DEFERIDOS']

Modelos_de_docs = db.define_table('Modelos_de_docs',
    Field('arq_modelo_doc', 'upload', uploadfolder = pasta_de_modelos_do_servidor_de_arquivos, length= 40, tablename='n', filename= 'x'),
    Field('nome_modelo_doc', 'string'),
    Field('servico_refere', 'reference Servicos', requires=IS_IN_DB(db, 'Servicos.id', db.Servicos._format)),
    auth.signature,
    format= '%(nome_modelo_doc)s',
)




num_tarefas = db((db.Tarefas.Status != 'Concluida') & (db.Tarefas.Responsavel == auth.user_id ))


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)