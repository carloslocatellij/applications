
if 0==1:
    from gluon import *
    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, auth, Auth
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T


def Modal(title, content, id, vbutton=False):
    ''' Cria um elemento modal html com titulo e informações a receber '''

    xis = '×'
    vbutton = vbutton
    
    return CAT(XML('<button class="btn btn-primary" data-toggle="up-modal" data-target="#{}">{}</button>'.format(id, vbutton)) if vbutton else '',
        DIV(DIV(DIV(DIV(
        XML('<button type="button" class="close" data-dismiss="up-modal"><span>{}</span></button>'.format(xis)),
                H4( title, _class="up-modal-title"),
                 DIV(BODY(content), _class="up-modal-body"),
                 DIV(CAT(XML('<button type="button" class="btn btn-default" data-dismiss="up-modal">{}</button>'.format(xis)),
                  _class="up-modal-footer"), DIV(_class="spinner-border text-success")),
     _class="up-modal-header"),
     _class="up-modal-content"),
     _class="up-modal-dialog", _style="max-width: 80%"),
     _class="up-modal", _id='grade'))

def buscador(tabela, regform=request.function ,**fields):
    campos = [Field(k, **v)  for k, v in fields.items()] 
    formbusca = SQLFORM.factory(*campos, formstyle='table3cols', formname='formbusca')

    busca = db(db[tabela].Protocolo < 0)
    tab2 = None

    if formbusca.process().accepted:
        for k,v in fields.items():
            session[k] =  formbusca.vars[k]
        q =[]
        for k,v in fields.items():
            if session[k] != None:

                if 'table' in v:
                    tab2 = v['table']

                    campo2 = 'Id'+ v['table'][:-1]  if  v['table'][-1] == 's' else 'Id'+ v['table']
                    if db[tab2][k].type == 'string':
                        q.append( ( db[tabela][campo2] == db[tab2].id) & (db[tab2][k].contains(str(session[k]))) )
                    elif db[tab2][k].type == 'integer':
                        q.append( ( db[tabela][campo2] == db[tab2].id) & (db[tab2][k] == int(session[k])) ) 
                        
                elif db[tabela][k].type == 'string':
                    q.append((db[tabela][k].contains(str(session[k]) ) ) )
                elif db[tabela][k].type == 'integer':
                    q.append((db[tabela][k] ==int(session[k])))
                else:
                    q.append((db[tabela][k] == session[k]))

        busca = db(*q) if q else db[tabela].id 
    grade =''
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=session.controller, f=regform, args=row[tabela]['id'] if tab2 != None else row['id'], vars={'f': 'ver'})))]
    grade = SQLFORM.grid( busca, represent_none='', links=links, editable=False, searchable=False, deletable=False, create=False, details=False,
                          csv=False,  maxtextlength = 120, _class="table", user_signature=False, )

    
   
    

    return dict(formbusca = formbusca, grade=Modal('Busca', grade, 'grade'))
