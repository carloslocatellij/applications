
if 0==1:
    from gluon import * # type: ignore
    from gluon import db, IS_IN_SET, IS_UPPER, DIV, XML, BODY, H4, CAT, Field, SQLFORM, A, URL, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, a_db, db, auth, Auth # type: ignore
    request = current.request # type: ignore
    response = current.response # type: ignore
    session = current.session # type: ignore
    cache = current.cache # type: ignore
    T = current.T # type: ignore


def Modal(title, content, id, vbutton=False):
    ''' Cria um elemento modal html com titulo e informações a receber '''

    xis = 'X'
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
     _class="up-modal", _id=id))


def padronizaprotoc(protoc):
    import re
    REGEX = re.compile(r'^(\d\d\d\d)(0+)(\d+)$')
    match = REGEX.match(protoc)
    
    if not match:
        
        print('Não é protcolo')
    else:
        
        
        return match.group(1) + match.group(3)
    

def buscador(tabela, regform=request.function, list_fields=[] ,**fields, ):
    campos = [Field(k, **v)  for k, v in fields.items()] 
    formbusca = SQLFORM.factory(*campos, formstyle='table3cols', formname='formbusca')

    try:
        busca = db(db[tabela].Protocolo > 0)
    except:
        busca = db(db[tabela].id > 0)
    
    tab2 = None

    if formbusca.process():
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
                        
                elif 'string' in db[tabela][k].type:
                    q.append((db[tabela][k].contains(str(session[k]).upper().strip() ) ) )
                elif db[tabela][k].type == 'integer':
                    q.append((db[tabela][k] ==int(session[k])))
                else:
                    q.append((db[tabela][k] == session[k]))

        try:
            busca = db(*q) if len(q) > 0 else db[tabela].Protocolo == '0'
        except:
            busca = db(*q) if len(q) > 0 else db[tabela].id == '0'

    grade =''
    
    links = [dict(header='Ver', body=lambda row: A('Ver', _class='btn btn-primary' , _href=URL(c=session.controller,
                              f=regform, args=row[tabela]['Protocolo' if 'Protocolo' in db[tabela].fields else 'id'] if tab2 != None else row['Protocolo'  if 'Protocolo' in db[tabela].fields else 'id'], vars={'f': 'ver'})))]
    grade = SQLFORM.grid( busca, represent_none='', links=links, editable=False, searchable=False, deletable=False, create=False,
                         details=False, paginate=30, csv=True,  maxtextlength = 120, _class="table", user_signature=False,
                          fields=list_fields, links_placement = 'left',
                          orderby=~db.Requerimentos.data_do_laudo if tabela=='Requerimentos' else None)

    
   
    

    return dict(formbusca = formbusca, grade=Modal('Busca', grade, 'grade'))
