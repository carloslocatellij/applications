# -*- coding: utf-8 -*-

def Campanhas():
	formbusca=FORM(INPUT(_id='keyword',
	 _name='keyword',
	 _onkeyup="ajax('callback', ['keyword'], 'target');"))
	target_div=DIV(_id='target')
	return dict(formbusca=formbusca,target_div=target_div)


def callback():
    """A chamada de procedimento Ajax que returna a <ul> do links para as dicas"""
    query = db.Campanhas.Nome.contains(request.vars.keyword)
    campanhas = db(query).select(orderby=db.Campanhas.Nome)
    links = [A(p.Nome, _href=URL('Campanhas','Campanha', args=p.id)) for p in campanhas]
    return UL(*links)



@auth.requires_login()
def grd_campanha():
    grid = SQLFORM.smartgrid(db.Campanhas, linked_tables=['Cenarios'])
    return dict(grid = grid)


def Campanha():
    campanha = db.Campanhas(request.args(0, cast=int)) or redirect(URL('Campanhas'))
    return dict(
    	campanha = campanha
    	)


@auth.requires_login()
def Editar_Campanha():
	campanha = db.Campanhas(request.args(0, cast=int)) or redirect(URL('Campanhas'))
	form = SQLFORM(Campanhas)
	return dict(form = form, campanha=campanha)

@auth.requires_login()
def Criar_Campanha():
	form = SQLFORM(db.Campanhas)
	return dict(form = form)

def download():
    return response.download(request, db)