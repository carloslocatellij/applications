# -*- coding: utf-8 -*-

def Personagens():
	grid = SQLFORM.smartgrid(db.Personagens, linked_tables=['Campanhas'])

	return dict(
		grid = grid
		#msg_Personagems=T('Personagens em andamento:'),


		)



def Personagem():
    personagem = db.Personagens(request.args(0, cast=int)) or redirect(URL('Personagens'))

    return dict(
    	personagem = personagem

    	)


def Criar_Personagem():
    return dict(form = form)
    form = SQLFORM(Personagens)


def download():

    return response.download(request, db)