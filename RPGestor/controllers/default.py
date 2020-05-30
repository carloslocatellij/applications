# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------



# ---- example index page ----
def index():
    response.flash = T(" RPGestor")
    li_campanhas = db(Campanhas).select(Campanhas.Nome, Campanhas.Img, Campanhas.id, orderby=Campanhas.Nome)

    li_cenarios = db(Cenarios).select(Cenarios.Nome, Cenarios.Img, Cenarios.id, orderby=Cenarios.Nome)

    li_personagens = db(Personagens).select(Personagens.Nome, Personagens.Img, Personagens.id, orderby=Personagens.Nome)

    return dict(message=T('Bem Vindo ao RPGestor, Sistema de Gestão de jogos de RPG!'),
        msg_campanhas=T('Campanhas em andamento:'),

        li_campanhas = li_campanhas, li_personagens= li_personagens, li_cenarios = li_cenarios,

        msg_personagens=T('Ultimos Personagens criados:'),

        msg_cenarios=T('Cenários em destaque:'),
        )




def Criar_Cenario():
    form = SQLFORM(Cenarios)
    return dict(form = form)




# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})



# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki()

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_membership("admin") 
def list_users(): 
    btn = lambda row: A("Edit", _href=URL('manage_user', args=row.auth_user.id)) 
    db.auth_user.edit = Field.Virtual(btn) 
    rows = db(db.auth_user).select() 
    headers = ["ID", "Name", "Last Name", "Email", "Edit"] 
    fields = ['id', 'first_name', 'last_name', "email", "edit"] 
    table = TABLE(THEAD(TR(*[B(header) for header in headers])), TBODY(*[TR(*[TD(row[field]) for field in fields])  for row in rows]))
    table["_class"] = "table table-striped table-bordered table-condensed"
    return dict(table=table) 


@auth.requires_membership("admin")

def manage_user():
    user_id = request.args(0) or redirect(URL('list_users')) 
    form = SQLFORM(db.auth_user, user_id). process() 
    membership_panel = LOAD(request.controller, 'manage_membership.html', args=[user_id], ajax=True) 
    return dict(form=form,membership_panel=membership_panel)


@auth.requires_membership("admin") 

def manage_membership(): 
    user_id = request.args(0) or redirect(URL('list_users'))
    db.auth_membership.user_id.default = int(user_id) 
    db.auth_membership.user_id.writable = False 
    form = SQLFORM.grid(db.auth_membership.user_id == user_id, args=[user_id], searchable=False, deletable=False, details=False, selectable=False, csv=False, user_signature=False) # change to True in production 
    return form 