# -*- coding: utf-8 -*-

def Campanhas():
	grid = SQLFORM.smartgrid(db.Campanhas, linked_tables=['Cenarios'])

	return dict(
		grid = grid
		#msg_campanhas=T('Campanhas em andamento:'),


		)



def Campanha():
    campanha = db.Campanhas(request.args(0, cast=int)) or redirect(URL('Campanhas'))

    return dict(
    	campanha = campanha

    	)


def Criar_Campanha():
    return dict(form = form)
    form = SQLFORM(Campanhas)


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)