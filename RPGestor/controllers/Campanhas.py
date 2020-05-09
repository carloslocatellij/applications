# -*- coding: utf-8 -*-

def Campanhas():

	grid = SQLFORM.smartgrid(db.Campanhas, linked_tables=['Cenarios'])

	return dict(
		grid = grid

)



def Campanha():
    campanha = db.Campanhas(request.args(0, cast=int)) or redirect(URL('Campanhas'))
    return dict(
    	campanha = campanha
    	)

def Criar_Campanha():
	form = SQLFORM(Campanhas)
	return dict(form = form)

def download():
    return response.download(request, db)