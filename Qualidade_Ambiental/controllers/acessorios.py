

@auth.requires_login()
def Lista_de_Registros():
    import re
    REGEX = re.compile('^(\\w+).(\\w+).(\\w+)\\=\\=(\\d+)$')
    match = REGEX.match(request.vars.query)
    if not match:
        redirect(URL('error'))

    table, field, id = match.group(2), match.group(3), match.group(4)
    records = db(db[table][field]==id)
    links = [
    dict(header='Ver', body=lambda row: A('Ver', _href=URL(c=request.args(1) , f= table,
     args=row.id, vars={'f': 'ver'}))),
    dict(header='Editar', body=lambda row: A('Editar', _href=URL(c=request.args(1) , f= table,
     args=row.id, vars={'f': 'editar'})))
     ]

    return dict(records=SQLFORM.grid(records,  links=links,user_signature=False, editable=False, searchable=False,
    deletable=False, create=False,csv=False, maxtextlength = 120, _class="table", represent_none= '',links_placement= 'left'), table=table)