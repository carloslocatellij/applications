# -*- coding: utf-8 -*-


import datetime
from tkinter import Widget


if 0==1:
    from gluon import * 
    

    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db,\
     IS_CHKBOX01, IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, IS_DECIMAL_IN_RANGE, IS_DATE, CLEANUP, IS_NOT_EMPTY, auth
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
    #fake_migrate=True,
    #migrate='table.e593e149f9583a99bf743b74481027ab_Cidades'
    )


Bairros = db.define_table ('Bairros',
   	Field ('Id', 'id'),
   	Field ('Bairro', 'string', notnull=True, requires=IS_UPPER()),
   	Field ('Cor', 'string',),
   	Field ('IdCidade', 'reference Cidades', label='Cidade'), 		
	Field ('Regiao', 'integer', IS_IN_SET(range(11))),
	format = '%(Bairro)s',
    #fake_migrate=True,
    #migrate='table.e593e149f9583a99bf743b74481027ab_Bairros'
    )


Logradouros = db.define_table ('Logradouros',
	Field ('Logradouro', 'string', notnull=True, requires=IS_UPPER()),
	Field ('Cep', 'integer',),
	Field ('Id', 'id'),
	Field ('Denominacao',  requires=IS_IN_SET(['-','ALAMEDA','AVENIDA','ESTR. MUN.','ESTRADA','PRAÇA','RODOVIA','RUA','TRAVESSA','VIA']), notnull=True, label='Tipo'),
	Field ('Prefixo',  requires=IS_IN_SET(['-','DR.','COM.','GOV.','PRES.','PE.','CAP.','CEL.','DRA.','GAL.','PROF.','MAJ.','MISSIO','PAST',
'PAST.','SGTO.','FREI','BRIG.','IRMÃ','TEN.','PROFA.','SARG.','SRA.'])),
	Field ('No', 'integer', label='Nº expecifico'),
	Field ('NoInicial','integer', label='Nº inicial'),
	Field ('NoFinal', 'integer', label='Nº final'),
	Field ('Lado','boolean'),
	Field ('Complemento', 'string'),
	Field ('IdBairro', 'reference Bairros', label='Bairro'),
	Field ('IdCidade', 'reference Cidades', label='Cidade'),
	format = (lambda row : logradouro_represent(row)),
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Logradouros'
    )

def logradouro_represent(row):
	repr_logradouro = db((db.Logradouros.Id == int(row.id)) & (db.Logradouros.IdBairro == db.Bairros.Id)).select(db.Logradouros.Logradouro, db.Logradouros.NoInicial,
    db.Logradouros.NoFinal, db.Logradouros.Cep, db.Bairros.Bairro, cache=(cache.ram, 3600), cacheable=True).first()
	if repr_logradouro:
		logr = str(repr_logradouro.Logradouros.Logradouro) + ', Bairro: ' + str(repr_logradouro.Bairros.Bairro) + ', CEP: ' + str(repr_logradouro.Logradouros.Cep) + (', do n. ' if repr_logradouro.Logradouros.NoInicial else '') \
         + str(repr_logradouro.Logradouros.NoInicial if repr_logradouro.Logradouros.NoInicial else '') + (', até  n. ' if repr_logradouro.Logradouros.NoFinal else '')+ str(repr_logradouro.Logradouros.NoFinal if repr_logradouro.Logradouros.NoFinal else '')
		return logr
	else:
		return ''
    
Enderecos = db.define_table ('Enderecos',
	Field ('Id', 'id'),
	Field ('IdLogradouro', 'reference Logradouros', requires=IS_IN_DB(db, 'Logradouros.Id', logradouro_represent, cache=(cache.ram, 900)), label= 'Logradouro'),
	Field ('Num', 'integer', notnull=True),
	Field ('Quadra', 'string', default= ' ', ),
	Field ('Lote', 'string',  default= ' '),
	Field ('Tipo', 'string', default= '-', requires=IS_IN_SET(['','-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LJ.','CASA','MARJ.'])),
	Field ('Complemento', 'string', default= '-', ),
	Field ('TipoB', 'string', default= '-', requires= IS_IN_SET(['','-','BL.','FRENTE','ESQ.','FUNDO','SL.','N','ANDAR','LJ.','CASA','MARJ.']), label='outro tipo'),
	Field ('ComplementoB',  'string', default= '-', label='Outro compl.'),
	format = (lambda row : endereco_represent(row)),
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Enderecos'
    )

def endereco_represent(row):
	repr_endereco = db((db.Enderecos.Id == int(row.id)) & (db.Logradouros.Id == db.Enderecos.IdLogradouro)).select(db.Logradouros.Logradouro,
     db.Enderecos.Num, db.Enderecos.Quadra, db.Enderecos.Lote, orderby=db.Logradouros.Logradouro, cache=(cache.ram, 900)).first()
	if repr_endereco:
		end = str(repr_endereco.Logradouros.Logradouro) + ', ' + str(repr_endereco.Enderecos.Num) + ', Qd: ' + str(repr_endereco.Enderecos.Quadra)+ ', Lt: ' + str(repr_endereco.Enderecos.Lote)
		return end
	else:
		return ''


#PESSOAS
    
Pessoas = db.define_table ('Pessoas',
	Field ('Id', 'id'),
	Field ('Idm', 'integer' ),
	Field ('Nome', 'string', length='115', requires = [IS_NOT_EMPTY() ,IS_UPPER()], notnull=True),
    Field ('CPF', 'string', unique=True, requires=[IS_EMPTY_OR(IS_CPF_OR_CNPJ()), IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CPF', error_message='Já existe uma Pessoa com este Número de CPF'))],  represents= (lambda row: MASK_CPF()(row)) ),
    Field ('CNPJ', 'string', unique=True, requires=[IS_EMPTY_OR(IS_CPF_OR_CNPJ()),IS_EMPTY_OR(IS_NOT_IN_DB(db, 'Pessoas.CNPJ', error_message='Já existe uma Empresa com este Número de CNPJ')) ],  represents= (lambda row: MASK_CNPJ()(row)) ),
    Field ('IdEndereco', 'reference Enderecos', requires=IS_EMPTY_OR(IS_IN_DB(db, 'Enderecos.Id', endereco_represent,  cache=(cache.ram, 900))), label="Endereço"),
	Field ('Telefone', 'string'),
	Field ('celular', 'string'),
	Field ('Email', 'string'),
	Field ('Categoria', 'text'),
	format = (lambda row : pessoa_represent(row)), 
    #primarykey=['Id']
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Pessoas'
	)


def pessoa_represent(row):
	repr_pessoa = db(db.Pessoas.Id == int(row.id)).select(db.Pessoas.Nome, db.Pessoas.CPF, db.Pessoas.CNPJ, cache=(cache.ram, 900), cacheable=True).first()
	if repr_pessoa:
		pessoa = '{} - {}'.format(str(repr_pessoa.Nome) ,  str(repr_pessoa.CPF) if repr_pessoa.CPF else str(repr_pessoa.CNPJ))
		return pessoa
	else:
		return ''


UnidadeDestino = db.define_table('UnidadeDestino',
    Field ('Id', 'id'),
    Field ('IdEmpreendedor', 'reference Pessoas',  requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format)),
    Field ('IdEndereco', 'reference Enderecos'),
    Field ('Tipo', 'text'),
    Field ('Atividade', 'text'),
    Field ('Coordenadas', 'text'),
    Field ('Matricula', 'text'),
    Field ('Area', 'decimal(8,2)'),
    format = '%(Atividade)s',
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_UnidadeDestino'
    )

def Unid_Destino_represent(row):
	Unid_Destino = db((db.UnidadeDestino.Id == row.id) & (db.Pessoas.Id == db.UnidadeDestino.IdEmpreendedor)).select(db.Pessoas.Nome, cache=(cache.ram, 3600), cacheable=True).first()
	if Unid_Destino:
		destino = Unid_Destino.Nome 
		return destino
	else:
		return ''

veiculos = [(1, 'Carro'), (2, 'CARROCA'), (3, 'PICKUP'), (4, 'CARRETA_P'), (5, 'CARRETA_G'), (6, 'OUTRO')]


EntradaPonto = db.define_table('EntradaPonto',
    Field ('Id', 'id'),
    Field ('Placa',  'string', length='9', required=True, requires = IS_MATCH('[ABCDEFGHIJKLMNOPQRSTUVWXYZ#]{3}', error_message='Não é Placa')),
    Field ('TipoVeic', 'integer', requires = IS_IN_SET(veiculos)),
    Field ('Data', 'date', required=True, requires=IS_DATE(format=T(f'%d/%m/%Y'),error_message='deve ser no formato Dia/Mês/Ano!')),
    Field ('Volume', 'decimal(3,2)', default=1.0 ,requires=IS_IN_SET([1.0, 2.0 ]), widget=SQLFORM.widgets.radio.widget ),
    Field ('Sofa', 'integer',default=0 ,requires=IS_IN_SET([0, 1, 2, 3, 4 ]), widget=SQLFORM.widgets.radio.widget), 
    Field ('Colchao' , 'integer', default=0 ,requires=IS_IN_SET([0, 1, 2, 3, 4 ]), widget=SQLFORM.widgets.radio.widget, rname='Colchão'),
    Field ('Poda', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Moveis', 'integer',requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget), 
    Field ('Ferro', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Entulho', 'integer',  requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('PlastPapel', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Eletron', 'integer', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget),
    Field ('Outros', 'string', length='15',),
    Field ('IdPonto', 'reference UnidadeDestino', requires=IS_IN_DB(db(db.UnidadeDestino.Tipo=='Ponto de Apoio'), 'UnidadeDestino.Id', \
        db.UnidadeDestino._format, cache=(cache.ram, 1800)))
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_EntradaPonto'
    )


MedicoesOpac = db.define_table('MedicoesOpac',
    Field ('ID', 'id'),
    Field('PM', 'string', length='6'),
    Field('Placa','string', length='9', required=True, requires = IS_MATCH('[ABCDEFGHIJKLMNOPQRSTUVWXYZ#]{3}', error_message='Não é Placa')),
    Field('Data', 'date', required=True),
    Field('Hora', 'time', required=True),
    Field('Kmaximo', 'decimal(3,2)'),
    Field('KMedido', 'decimal(3,2)'),
    Field('Resultado', 'text' ),
    Field('BaseLegal', 'text', length='25'),
    Field('NvRingelmann', 'integer', requires=IS_IN_SET([1,2,3,4,5]), widget=SQLFORM.widgets.radio.widget),
    Field('Obs', 'text', length='150'),
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_MedicoesOpac'
    )


Dpto = db.define_table('Dpto', 
	Field('Idm', 'integer'),
	Field('Departamento', 'string', required=True),
	Field('Orgao', 'reference Dpto',  ),
	Field('Telefone', 'string'),
	primarykey= ['Idm'], 
	format='%(Departamento)s',
	#fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Dpto'
    )


Servicos = db.define_table('Servicos',
    Field('Servico', 'string', label='Serviço'),
    Field('Dpto', 'reference Dpto', label='Departamento'),
    format='%(Servico)s',
    #fake_migrate=True,
    #migrate='table.e593e149f9583a99bf743b74481027ab_Servicos'
)

Processos = db.define_table('Processos',
    
    Field('Protocolo',  'string', unique=True, notnull=True, requires=IS_NOT_IN_DB(db, 'Processos.Protocolo', error_message='Protocolo já Existe')),
    Field('IdPessoa',  'reference Pessoas' , label= 'Pessoa'),
    Field('IdDpto', 'reference Dpto' , label='Departamento'),
    Field('DataReg', 'datetime', label = 'Data de Registro', default=datetime.datetime.now(),  writable=False),
    Field('IdTipo', 'reference Servicos', requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format), label='Tipo' ),
    Field('Assunto', 'string'),
    Field('IdCateg', 'integer', label = 'Categoria'),
    format='%(Protocolo)s',
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Processos'
)
#BANCO CONSTRUCOES

Obras= db.define_table('Obras',
    Field('Id', 'id'),
    Field('Protocolo', 'reference Processos',  unique=True),
    Field('CadMunicipal', 'string', label='Cadastro Mun.',unique=True, requires=IS_NOT_IN_DB(db, 'Obras.CadMunicipal', error_message='Já existe Obra com este Número de Cadastro')),
    Field('Alvara', 'string', label='Alvará'),
    Field('DataAlvara', 'date', label='Data do alvará', requires = IS_EMPTY_OR(IS_DATE(format=T(f'%d/%m/%Y'),
                   error_message='deve ser no formato Dia/Mês/Ano!'))),
    Field('IdGerador', 'reference Pessoas', requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format), label='Gerador' ),
    Field('IdEndereco', 'reference Enderecos', unique=True, requires=IS_IN_DB(db, 'Enderecos.Id', endereco_represent ), label="Endereço"  ) ,
    Field('Finalidade', 'string', label='Finalidade'),
    Field('PrazoExec', 'decimal(7,2)', label='Prazo de execução', readable=False),
    Field('AreaTerreno', 'decimal(7,2)', IS_DECIMAL_IN_RANGE(10, 9999999,
dot=",", error_message="Valor fora do permitido ou mal formatado"), label= 'Área do Terreno'),
    Field('AreaConstrExist', 'decimal(7,2)',  IS_DECIMAL_IN_RANGE(0.00, 9999999.99,
dot=",", error_message="Valor fora do permitido ou mal formatado"), label= 'Área Construída anterior'),
    Field('AreaConstrDemolir', 'decimal(7,2)', IS_DECIMAL_IN_RANGE(0.00, 9999999.99,
dot=",", error_message="Valor fora do permitido ou mal formatado"),  label= 'Área Demolida/Demolir'),
    Field('AreaConstrExecutar', 'decimal(7,2)', IS_DECIMAL_IN_RANGE(5.00, 9999999.99, dot=",", error_message="Valor fora do permitido ou mal formatado"),  label= 'Área à Executar/Executada'),
    Field('Corte', 'decimal(7,2)', IS_DECIMAL_IN_RANGE(0.0, 9999999.99,
dot=",", error_message="Valor fora do permitido ou mal formatado"),  label= 'Corte de terra'),
    Field('Aterro', 'decimal(7,2)', IS_DECIMAL_IN_RANGE(0.0, 9999999.99,
dot=",", error_message="Valor fora do permitido ou mal formatado"),  ),
    Field('PavtosSubS', 'integer', label='Pavtos Inferiores'),
    Field('PavtosSobreS', 'integer', label='Pavtos Sob o Solo'),
    Field('Nquartos', 'integer', label='Num. de Quartos'),
    Field('Edicula', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)) ,widget=SQLFORM.widgets.boolean.widget),
    Field('Piscina', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)) ,widget=SQLFORM.widgets.boolean.widget),
    Field('CobertMetalica', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)) ,widget=SQLFORM.widgets.boolean.widget, label='Cobertura Metálica'),
    Field('MadeiraReflorest', 'integer', requires= IS_EMPTY_OR(IS_CHKBOX01(on=1, off=0)) ,widget=SQLFORM.widgets.boolean.widget, labe='Cobertura Mad. Reflorestada'),
    format = 'Cad.%(CadMunicipal)s - Alvará: %(Alvara)s/%(DataAlvara)s',
    #fake_migrate = True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Obras'
    )


Pgrcc = db.define_table('Pgrcc',
    Field('idgerador', 'reference Pessoas', requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format), label='Gerador' ),
    Field('idobra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id', db.Obras._format,), label='Obra' ),
    Field('protocolo', 'reference Processos', notnull=True,  requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
    Field('metodoconstrutivo', 'text', label='Método Construtivo' ),
    Field('resptecnico', 'reference Pessoas', requires=IS_IN_DB(db, 'Pessoas.Id', db.Pessoas._format), label='Responsável Técnico' ),
    Field('sigor', 'integer'),
    Field('obs', 'text'),
    Field('concreto', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('argamassa', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('alvenaria', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('ceramica', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('outros_ca', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido"), label='Outros Classe A'),
    Field('solo', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('madeira','decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('plastico', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido"), label='plástico'),
    Field('papel', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('metal', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('vidro', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('gesso', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('outros_cb', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido"),label='Outros Classe C'),
    Field('tinta', 'decimal(8,6)',IS_FLOAT_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('solvente', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('oleo', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    Field('outros_cd', 'decimal(9,6)',IS_DECIMAL_IN_RANGE(0.0, 999999.9, dot=",", error_message="Valor não permitido")),
    auth.signature,
    #fake_migrate = True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_Pgrcc'
    )


DofsObra = db.define_table('DofsObra',
    Field('id','id'),
    Field('IdDof','string', notnull=True, unique=True, label='DOF' ),
    Field('IdObra', 'reference Obras', requires=IS_IN_DB(db, 'Obras.Id', db.Obras._format, cache=(cache.ram, 900))),
    #primarykey=['IdDof']
    #fake_migrate = True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_DofsObra'
    )

MadeirasDof = db.define_table ('MadeirasDof',
	Field('Id', 'id'),
	Field('IdDof', 'string', requires=IS_IN_DB(db, 'DofsObra.IdDof', db.DofsObra._format, cache=(cache.ram, 900)),  notnull=True),
	Field('Item', 'integer',required=True),
	Field('Produto', 'text', length=45, required=True),
	Field('Especie', 'text', length=55, required=True),
	Field('Popular', 'text', length=35, required=True),
	Field('Qtd', 'decimal(7,4)',required=True ),
	Field('Unidade', 'text', length=2, required=True),
	Field('Valor', 'text', length=10, required=True),
    #fake_migrate=True,
    #migrate = 'table.c8b669d15150d7109e5f7ab36744a5b7_MadeirasDof'
    )



Transportadores = db.define_table('Transportadores',
Field('Id', 'id'),
Field('IdPessoa', 'reference Pessoas', label='Pessoa'),
Field('NomeFantasia',  'string', length='128', requires = IS_UPPER(),notnull=True, label='Nome Fantasia'),
Field('RazaoSocial',  'string', length='128', requires = IS_UPPER(),notnull=True, label='Razão Social'),
Field('CNPJ', 'string'),
Field('IM', 'integer', label='Inscrição Municipal'),
Field('Cadastro', 'integer', label='Nº de Cadastro de CTR'),
Field('Tipo'),
Field('Tel','string', label='Telefone'),
Field('email', 'string'),
#primarykey=['Id'],
format ='%(RazaoSocial)s',
#fake_migrate=True,
#migrate = 'table.c8b669d15150d7109e5f7ab36744a5b7_Transportadores'

 )

db.define_table('TransportadorStatus',
Field('Transportador', 'reference Transportadores'),
Field('Status', 'string', requires=IS_IN_SET(['Validado', 'Não Validado', 'Pendente']), default='Pendente', label='Situação'),
Field('StatusData', 'date', default=datetime.date.today(), requires=IS_DATE(format=T(f'%d/%m/%Y')), readable=False, label='Data de Registro da Situação'),
Field('Protocolo', 'reference Processos',  requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
Field('Doc_talao', 'upload', label='Documento do Talão de CTR'),
#fake_migrate=True,
#migrate='table.c8b669d15150d7109e5f7ab36744a5b7_TransportadorStatus'
)


EntradaATT = db.define_table('EntradaATT',
Field('CTR', 'integer'),
Field('Unid_Destino', 'reference UnidadeDestino', requires=IS_EMPTY_OR(IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent, cache=(cache.ram, 900))) ),
Field('Transportador', 'reference Transportadores'),
Field('Data', 'date' ),
Field('Veiculo_tipo', 'string'),
Field('Classe_Residuo', 'string', requires=IS_IN_SET(['A - CONCRETO / ALVENARIA', 'B - METAL/ PLASTICO/ PAPEL', 'PODA / VOLUMOSOS', 'A 80% / B 20% *', 'A 65% / B 35% *',
'A 50% / B 50% *', 'A 35% / B 65% *', 'A 20% / B 80% *', 'MADEIRA', 'GESSO' ,'D * NECESSITA CADRI', 'REJEITO']
)),
Field('Volume', 'decimal(7,2)'),
#format= '%(CTR)s'
#fake_migrate=True,
#migrate = 'table.e593e149f9583a99bf743b74481027ab_EntradaATT'
)



Licencas = db.define_table('Licenca',
Field('Num', 'string', ),
Field('Tipo', 'string', requires=IS_IN_SET(['L. Instalação', 'L. Operação', 'L. Renovação'])),
Field('Protocolo', 'reference Processos', requires = IS_IN_DB(db, 'Processos.id', db.Processos._format)),
Field('Anterior', 'string',),
Field('IdEmpresa', 'reference Pessoas'),
Field('Unid_Destino','reference UnidadeDestino', requires=IS_IN_DB(db, 'UnidadeDestino.Id', Unid_Destino_represent), label="ATT"),
Field('Data', 'date', requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!')),
Field('IdEndereco', 'reference Enderecos'),
Field('Exigencias', 'text'),
Field('validade', 'date',  requires=IS_DATE(format=T(f'%d/%m/%Y'), error_message='deve ser no formato Dia/Mês/Ano!') ),
Field('Status', 'boolean'),
format= '%(Num)s',
#fake_migrate=True,
#migrate = 'table.e593e149f9583a99bf743b74481027ab_Licenca'
)


Docs_do_Proc_PGRCC =     ['Requerimento', 'ART/RRT', 'PGRCC Municipal', 'PGR Sigor', 'Proj. Arquitetônico', 'Procuração' ]


Campos_do_Proc_PGRCC =   ['Nome Gerador', 'CPF/CNPJ Gerador', 'Nome Resp. Téc.', 'Finalidade da Obra', 'Endereco', 'Matrícula',
                        'Cadastro Mun.', 'Coordenadas', 'Área do terreno', 'Área existente', 'Área demolida'
                        'Área construida final', 'Área pavimentação', 'Corte ', 'Aterro ', 'Processos Construtivos', 
                        'Resíduos Classe A', 'Resíduos Classe B', 'Resíduos Classe C', 'Resíduos Classe D', 
                        'Inic. p/ Minimização', 'Inic. p/ Absorção na Obra', 'Inic. p/ Acondicionamento', 
                        'Destino a Ser Dado Classe A', 'Destino a Ser Dado Classe B', 'Destino a Ser Dado Classe C',
                        'Destino a Ser Dado Classe D', 'Destino a Ser Dado Outros', 'Identificação do transportador', 
                        'Identificação da área receptora', 'Declaração do Gerador', 'Declaração do Resp. Téc.',      'Ausente']
                        


TipoAnalise =            ['Dado não confere', 'Não assinado', 'Desacordo com PGR Sigor', 'Desacordo com PGR Mun.', 'Desacordo com Outros Docs.', 'Não atende a Lei 9393/2004',
                         'Abaixo das Estatísticas', 'Acima das Estatísticas', 'Muito Abaixo das Estatísticas', 'Muito Acima das Estatísticas', 'Ausente'
                          ]



db.define_table( 'AnaliseTec',
    Field('Protocolo', 'reference Processos',  requires = IS_IN_DB(db, 'Processos.id', db.Processos._format), readable=False ),
    Field('DocsProcesso', 'string', requires=IS_IN_SET( ('Requerimento', 'ART RRT', 'PGRCC Municipal', 'PGR Sigor', 'Proj. Arquitetonico', 'Procuração' )),
    label='Documento do Processo'),
    Field('CamposProcesso', 'string', requires=IS_IN_SET(Campos_do_Proc_PGRCC), label='Campo do Processo'),
    Field('TipoAnalise', 'string', requires=IS_IN_SET(TipoAnalise), label='Análise'),
    Field('Obs', 'text', label='Observações'),
    auth.signature,
    #fake_migrate=True,
    #migrate='table.c8b669d15150d7109e5f7ab36744a5b7_AnaliseTec',

)

Procedimentos = db.define_table('Procedimentos',
    Field('Procedimento', 'string', notnull=True, requires=IS_UPPER()),
    Field('Tipo','list:reference Servicos', multiple=True, requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format, multiple=True),  widget=SQLFORM.widgets.checkboxes.widget, label='Tipo' ),
    Field('ordem', 'integer'),

    auth.signature,
    format= '%(Procedimento)s',
    fake_migrate=True,
    #migrate='table.e593e149f9583a99bf743b74481027ab_Procedimentos',
)

Tarefas = db.define_table('Tarefas',
    Field('Titulo','string', notnull=True, requires=IS_UPPER() ),
    Field('Protocolo', 'reference Processos',  requires=[IS_IN_DB(db, 'Processos.id', db.Processos._format), IS_NOT_IN_DB(db, 'Tarefas.Protocolo', error_message='Protocolo já Existe') ]),
    Field('Responsavel', 'reference auth_user', requires=IS_IN_DB(db, 'auth_user.id', '%(first_name)s')),
    Field('DataIni', 'date', default=datetime.date.today(), label='Data Inicial', requires=IS_DATE(format=T('%d/%m/%Y'),
                   error_message='A data e deve estar no formato dia/mês/ano')),
    Field('DataFim', 'date', label='Data Final', requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),
                   error_message='A data e deve estar no formato dia/mês/ano'))),
    Field('Descricao', 'text', ),
    Field('Tipo', 'reference Servicos', requires = IS_IN_DB(db, 'Servicos.id', db.Servicos._format), label='Tipo' ), 
    Field('checklist','list:reference Procedimentos', multiple=True, requires=IS_IN_DB(db, 'Procedimentos.id', db.Procedimentos._format, multiple=True, zero='off'), widget=SQLFORM.widgets.checkboxes.widget),
    Field('Status', 'string', requires=IS_IN_SET(['---', 'Iniciada', 'Em Andamento', 'Aguardando retorno', 'Concluida']), default='Inicida'),
    auth.signature,
    #fake_migrate=True,
    #migrate='table.e593e149f9583a99bf743b74481027ab_Tarefas',
    )


    

num_tarefas = db((db.Tarefas.Status != 'Concluida') & (db.Tarefas.Responsavel == auth.user_id ) ).count()



