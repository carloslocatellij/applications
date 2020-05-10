

Cenarios = db.define_table("Cenarios",
    Field('Nome', 'string', unique=True),
    Field('Ambientacao', 'string', label=u'Ambientação'),
    Field('Desc_Geral', 'text', label=u'Descrição Geral'),
    Field('Img', 'upload', label='imagem'),
    auth.signature,
    format = '%(Nome)s',

)


Campanhas = db.define_table('Campanhas',
    Field('Nome', 'string', unique=True),
    Field('IdCenario', 'reference Cenarios', label=u'Cenário'),
    Field('IdMestre', 'integer', label='Mestre'),
    Field('Ambientacao', 'string', label=u'Ambientação'),
    Field('Nv_Desafio_Atual', 'integer', label=u'Nível de desafio atual'),
    Field('Descricao', 'text', label=u'Descrição'),
    Field('Min_Jogadores', 'integer', label=u'mínimo de jogadore'),
    Field('Max_jogadores', 'integer', label=u'máximo de jogadores'),
    Field('Img', 'upload', label='imagem'),
    auth.signature,
    format = '%(Nome)s',
)

Quests = db.define_table('Quests',
	Field('Nome', 'string', unique=True),
	Field('Nivel', 'integer', label=u'Nível'),
	Field('Descricao', 'text', label=u'Descrição'),
	Field('Img', 'upload', label='imagem'),
    Field('Min_Jogadores', 'integer', label=u'mínimo de jogadores'),
    Field('Max_jogadores', 'integer', label=u'máximo de jogadores'),
	auth.signature,
    format = '%(Nome)s',
)

db.define_table('CampanhaQuest',
	Field('IdCampanha', 'reference Campanhas'),
	Field('IdQuest', 'reference Quests'),

)


Racas = db.define_table('Racas',
    Field('Nome', 'string', unique=True),
    Field('Descricao', 'text', label=u'Descrição'),
    Field('Img', 'upload', label='imagem'),
    format = '%(Nome)s'
    )

Classes = db.define_table('Classes',
    Field('Nome', 'string', unique=True),
    Field('AtributoBase', 'string', label='Atributo Base'),
    Field('Img', 'upload', label='imagem'),
    auth.signature,
    format = '%(Nome)s',
)

Personagens = db.define_table('Personagens',
    Field('Nome', 'string', unique=True),
    Field('IdRaca', 'reference Racas', label=u'Raça'),
    Field('Sexo', 'string'),
    Field('IdClasseBase', 'reference Classes', label='Classe Base'),
    Field('Arquetipo', 'string', label=u'Arquétipo'),
    Field('Profissao', 'string', label=u'Profissão'),
    Field('Descricao', 'text', label=u'Descrição'),
    Field('Img', 'upload', label='imagem'),
	auth.signature,
    format = '%(Nome)s',

)

db.define_table('PersonagemCampanha',
	Field('IdPersonagem', 'reference Personagens'),
	Field('IdCampanha', 'reference Campanhas'),
 )

db.define_table('PersonagemQuest',
	Field('IdPersonagem', 'reference Personagens'),
	Field('IdQuest', 'reference Quests'),
 )


Sistemas = db.define_table('Sistemas',
    Field('Nome', 'string', unique=True),
    Field('Descricao', 'text', label=u'Descrição'),
    format = '%(Nome)s'
)

Atributos = db.define_table('Atributos',
    Field('Atributo', 'string'),
    Field('IdSistema', 'reference Sistemas', label=u'Sistema'),
    Field('Descricao', 'text', label=u'Descrição'),
    format = '%(Atributo)s'
)

Pericias = db.define_table('Pericias',
    Field('Pericia', 'string', label=u'Perícia'),
    Field('IdSistema', 'reference Sistemas', label=u'Sistema'),
    Field('Descricao', 'text', label=u'Descrição'),
    Field('AtrBase', 'reference Atributos', label='Atributo base'),
    format= '%(Pericia)s'
    )


Propriedades = db.define_table('Propriedades',

    )
