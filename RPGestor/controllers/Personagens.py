# -*- coding: utf-8 -*-

def Personagens():
    formbusca=FORM(INPUT(_id='keyword',
     _name='keyword',
     _onkeyup="ajax('callback', ['keyword'], 'target');"))
    target_div=DIV(_id='target')
    return dict(formbusca=formbusca,target_div=target_div)

def callback():
    """A chamada de procedimento Ajax que returna a <ul> do links para as dicas"""
    query = db.Personagens.Nome.contains(request.vars.keyword)
    personagens = db(query).select(orderby=db.Personagens.Nome)
    links = [A(p.Nome, _href=URL('Personagens','Personagem', args=p.id)) for p in personagens]
    return UL(*links)


def Personagem():
    personagem = db.Personagens(request.args(0, cast=int)) or redirect(URL('Personagens'))

    return dict(
    	personagem = personagem

    	)

@auth.requires_login()
def Editar_Campanha():
    personagem = db.Personagens(request.args(0, cast=int)) or redirect(URL('Personagens'))
    db.Personagens.id.default = personagem.id
    form = SQLFORM(db.Personagens)
    return dict(form = form, campanha=campanha)

@auth.requires_login()
def Criar_Personagem():
    form = SQLFORM(db.Personagens)
    return dict(form = form)


def download():

    return response.download(request, db)