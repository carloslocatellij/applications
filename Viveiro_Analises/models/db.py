
from datetime import datetime
from my_validador import * # type: ignore 

if 0 == 1:
    from gluon import * # type: ignore
    from gluon import (db, configuration, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, CLEANUP,  # type: ignore
                       Field, auth, IS_MATCH, IS_FLOAT_IN_RANGE, a_db, db,  IS_CHKBOX01,  DAL, IS_INT_IN_RANGE, 
                       IS_CPF_OR_CNPJ, MASK_CPF, MASK_CNPJ, Remove_Acentos, IS_DECIMAL_IN_RANGE,
                       IS_DATE, CLEANUP, IS_NOT_EMPTY, IS_LOWER, Field, auth, IS_ALPHANUMERIC) # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore


if configuration.get('app.production'):
    tabela_solicitacoes = '''tab Solicitacoes'''
    tabela_laudos = '''tab Protocolos'''
    tab_ruas = '''tab Ruas'''
else:
    tabela_solicitacoes= '''tab_Solicitacoes'''
    tabela_laudos='''tab_Protocolos'''
    tab_ruas= '''tab_Ruas'''


Bairros = db.define_table('Bairros',
    Field('Bairro', 'string'),
    Field('Perimetro', 'string'),
    Field('Area', 'string'),
    Field('Regiao', 'string'),
    primarykey=['Bairro'],
    format='Bairro',
    migrate=True
    )


Ruas = db.define_table('tab_Ruas',
    Field('ID', 'id'),
    Field('Endereco1'),
    Field('Denominacao', rname='DENOMINACAO'),
    rname='`{}`'.format(tab_ruas),
    primarykey=['ID'],
    format='%(Endereco1)s - %(Denominacao)s',
    migrate=True
                       )

Requerimentos = db.define_table('Requerimentos',
    Field('Protocolo', requires=IS_INT_IN_RANGE('0','2025999999999')),
    Field('Requerente'),
    Field('data_entrada', 'date', 
            requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'),
            error_message='Deve ter o formato xx/xx/20xx')),
            rname='`Data de Entrada`'),
    Field('Endereco1', 'string',),
          #requires=IS_IN_DB(db, 'tab_Ruas.Endereco1')),
    Field('Numero1'),
    Field('Bairro', 
          requires=IS_IN_DB(db, 'Bairros.Bairro', '%(Bairro)s')),
    Field('cpf_cnpj', rname= '`cpf-cnpj`'),
    Field('cep'),
    Field('telefone1'),
    Field('email', rname='`e-mail`'),
    Field('especie_ret1', rname='`especie ret1`'),
    Field('especie_ret2', rname='`especie ret2`'),
    Field('especie_ret3', rname='`especie ret3`'),
    Field('especie_ret4', rname='`especie ret4`'),
    Field('qtd_ret1', rname='`qtd ret1`'),
    Field('qtd_ret2', rname='`qtd ret2`'),
    Field('qtd_ret3', rname='`qtd ret3`'),
    Field('qtd_ret4', rname='`qtd ret4`'),
    Field('especie_poda1', rname='`especie poda1`'),
    Field('especie_poda2', rname='`especie poda2`'),
    Field('especie_poda3', rname='`especie poda3`'),
    Field('especie_poda4', rname='`especie poda4`'),
    Field('qtd_poda1',  rname='`qtd poda1`'),
    Field('qtd_poda2', rname='`qtd poda2`'),
    Field('qtd_poda3', rname='`qtd poda3`'),
    Field('qtd_poda4', rname='`qtd poda4`'),
    Field('podador_coleta', rname='`podador coleta`',
          requires=IS_IN_SET(['Sim', 'Não', ''])),
    Field('no_carteira', rname='`no. carteira`'),
    Field('data_do_laudo', 'date',  
            requires=IS_DATE(format=T('%d/%m/%Y'),
            error_message='Deve ter o formato xx/xx/20xx'),
            rname='`data do laudo`'),
    Field('Despacho', 
          requires=IS_IN_SET(['Deferido', 'Parcialmente Deferido', 'Indeferido', 'Em Análise', 'Aguardando', ''])),
    Field('local_arvore', rname='`local arvore`', label='Local',
          requires=IS_IN_SET(['calçada', 'calçada com fiação', 'área interna', 'área aberta'])),
    Field('tipo_imovel',rname='`tipo imovel`', label='Tipo de Imóvel',
          requires=IS_IN_SET(['público', 'privado', 'institucional'])),
    rname = '`{}`'.format(tabela_solicitacoes) ,
    primarykey = ['Protocolo'],
    format='%(Protocolo)s',
    migrate=False,
    fake_migrate=False
    )


Laudos = db.define_table('Laudos',
      Field('Protocolo', 'reference Requerimentos'),
      Field('Despacho', 'string', 
            requires=IS_EMPTY_OR(IS_IN_SET(['Deferido', 
            'Parcialmente Deferido', 'Indeferido',
            'Em Análise', 'Aguardando', '']))),
      Field('data_do_laudo', 'date',
            rname='`data do laudo`',
            requires=IS_EMPTY_OR(IS_DATE(format='%d/%m/%Y') )),
      Field('proprietario', 'string', ),
      Field('morador', 'string'),
      Field('especie_ret1', 'string', rname='`especie ret1`'),
      Field('qtd_ret1', rname='`qtd ret1`' ),
      Field('especie_ret2', 'string', rname='`especie ret2`'),
      Field('qtd_ret2', rname='`qtd ret2`' ),    
      Field('especie_ret3', 'string', rname='`especie ret3`'),
      Field('qtd_ret3', rname='`qtd ret3`' ),
      Field('especie_ret4', 'string', rname='`especie ret4`'),
      Field('qtd_ret4', rname='`qtd ret4`' ),
      Field('qtd_repor', rname='`qtd repor`' ),
      Field('porte_repor', rname='`porte repor`', default='' , requires=IS_IN_SET(['PEQUENO', 'PEQUENO OU MÉDIO', 'MÉDIO', 'MÉDIO OU GRANDE', 'GRANDE', ''])),
      Field('especie_poda1', 'string', rname= '`especie poda1`'),
      Field('qtd_poda1', rname='`qtd poda1`' ),
      Field('especie_poda2', 'string', rname= '`especie poda2`'),
      Field('qtd_poda2', rname='`qtd poda2`' ),
      Field('especie_poda3', 'string', rname= '`especie poda3`'),
      Field('qtd_poda3', rname='`qtd poda3`' ),
      Field('especie_poda4', 'string', rname= '`especie poda4`'),
      Field('qtd_poda4', rname='`qtd poda4`' ),  
      Field('tipo'),
      Field('p1', 'integer', label='Conflito com fiação elétrica', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]' ),
      Field('p2', 'integer', label='Prejuizo a rede de água/esgoto', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p3', 'integer', label='Danos a estrutura da construção', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p4', 'integer', label='Restrição a passagem de pedestres', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p5', 'integer', label='Porte ou espécie inadequada', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p6', 'integer', label='Árvore senescente, debilitada por poda/pragas/parasitas', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p7', 'integer', label='Árvore morta/seca', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p8', 'integer', label='Passagem de Veículos', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p9' , 'integer', label='Obras, Reforma, Construção, Demolição', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p10', 'integer', label='Projetos e/ou Atividades', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('p11', 'integer', label='Risco a população, patrimônio', requires= IS_CHKBOX01(on=1, off=0) ,widget=SQLFORM.widgets.boolean.widget, represent=lambda v, r: '  ' if v not in [ 'on', '1', 1 ] else '[X]'),
      Field('Obs', rname='`Obs.`'),
      Field('tecnico', 'string', requires=IS_EMPTY_OR(IS_IN_SET(['Guilherme Cavenaghi', 'Renan Fabrizzio Lima Viche', 'Otton Garcia Arruda', '']) )),
      primarykey=['Protocolo'],
      rname = '`{}`'.format(tabela_laudos)
)


db.Requerimentos.Endereco1.type = 'string'
db.Requerimentos.Endereco = Field.Virtual('Endereco',
        lambda row: str(', '.join([f'Av./Rua {row.Requerimentos.Endereco1}' or '' ,
                                    f'Nº {row.Requerimentos.Numero1}' or '', f'Bairro: {row.Requerimentos.Bairro}' or ''])) )

db.Requerimentos.Supressoes = Field.Virtual('Supressoes',
        lambda row: ', '.join([f'({row.Requerimentos.qtd_ret1}) {row.Requerimentos.especie_ret1} ' if row.Requerimentos.especie_ret1 else ''
                                ,f'({row.Requerimentos.qtd_ret2}) {row.Requerimentos.especie_ret2}' if row.Requerimentos.especie_ret2 else ''
                                ,f'({row.Requerimentos.qtd_ret3}) {row.Requerimentos.especie_ret3} ' if row.Requerimentos.especie_ret3 else ''
                                ,f'({row.Requerimentos.qtd_ret4}) {row.Requerimentos.especie_ret4}' if row.Requerimentos.especie_ret4 else '']))

db.Requerimentos.Podas = Field.Virtual('Podas',
        lambda row: ', '.join([f'({row.Requerimentos.qtd_poda1}) {row.Requerimentos.especie_poda1} ' if row.Requerimentos.especie_poda1 else ''
                                ,f'({row.Requerimentos.qtd_poda2}) {row.Requerimentos.especie_poda2}' if row.Requerimentos.especie_poda2 else ''
                                ,f'({row.Requerimentos.qtd_poda3}) {row.Requerimentos.especie_poda3} ' if row.Requerimentos.especie_poda3 else ''
                                ,f'({row.Requerimentos.qtd_poda4}) {row.Requerimentos.especie_poda4}' if row.Requerimentos.especie_poda4 else '']))

db.Laudos.Supressoes = Field.Virtual('Supressoes',
        lambda row: ', '.join([f'({row.Laudos.qtd_ret1}) {row.Laudos.especie_ret1} ' if row.Laudos.especie_ret1 else ''
                                ,f'({row.Laudos.qtd_ret2}) {row.Laudos.especie_ret2}' if row.Laudos.especie_ret2 else ''
                                ,f'({row.Laudos.qtd_ret3}) {row.Laudos.especie_ret3} ' if row.Laudos.especie_ret3 else ''
                                ,f'({row.Laudos.qtd_ret4}) {row.Laudos.especie_ret4}' if row.Laudos.especie_ret4 else '']))

db.Laudos.Podas = Field.Virtual('Podas',
        lambda row: ', '.join([f'({row.Laudos.qtd_poda1}) {row.Laudos.especie_poda1} ' if row.Laudos.especie_poda1 else ''
                                ,f'({row.Laudos.qtd_poda2}) {row.Laudos.especie_poda2}' if row.Laudos.especie_poda2 else ''
                                ,f'({row.Laudos.qtd_poda3}) {row.Laudos.especie_poda3} ' if row.Laudos.especie_poda3 else ''
                                ,f'({row.Laudos.qtd_poda4}) {row.Laudos.especie_poda4}' if row.Laudos.especie_poda4 else '']))