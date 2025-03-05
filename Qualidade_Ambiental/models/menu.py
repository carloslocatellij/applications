# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

import os
import re

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

if not configuration.get('app.production'):
    _app = request.application
    response.menu += [
        (('Admin'), False, '#', [
            (('Meio Ambiente', False, URL('MeioAmbienteRP', 'default', 'index'))),
            (T('Database'), False, URL(_app, 'appadmin', 'index')),
            (T('Errors'), False, URL('admin', 'default', 'errors/' + _app)),
            (T('About'), False, URL( 'admin', 'default', 'about/' + _app)),
        ]),
    ]

ctldir = os.path.join(request.folder,"controllers")
ctls=os.listdir(ctldir)
if 'appadmin.py' in ctls: ctls.remove('appadmin.py')
if 'plotdados.py' in ctls: ctls.remove('plotdados.py')
for ctl in ctls:
    if ctl.endswith(".bak") == False and ctl !='default.py' and ctl !='__init__.py' :
        filename = os.path.join(ctldir,ctl)
        data = open(filename, 'r', encoding='utf-8').read()
        pattern = 'def .[\w]*'
        functions = re.findall(pattern, data)
        ctl = ctl[:-3].replace("_"," ")
        response.menu.append([ctl.capitalize(), False, URL(request.application,ctl.replace(" ","_"),
         ctl.replace(" ","_")), 
        [[f.replace("_"," ").replace('def ','').capitalize(), False,
        URL(request.application,ctl.replace(" ","_"),f.replace('def ','') )] \
            for f in functions] ])

response.submenu = ['Menu', False, URL('default', 'index'), []]
inicio = 'default.py'
fileinicio = os.path.join(ctldir,inicio)
datadef = open(fileinicio, 'r', encoding='utf-8').read()
pattern = 'def .[\w]*'
functions = re.findall(pattern, datadef)

while 'default' in functions:
    functions.remove('default')

remover = ['def api_get_user_email', 'def wiki', 'def grid', 'def download',
 'def user', 'def Pessoa_selector', 'def Criar_Tarefa', 'def Analises', 
 'def updatedof', 'def Lista_de_Registros', 'def DofsObras', 'def estilo_do_status']

for f in remover:
    [functions.remove(f) if f in functions else None]


response.submenu[3] +=[[f.replace("_"," ").replace('def ','').capitalize() , False, URL('default',f.replace('def ','') ) ]
     for f in functions]
    

    
# response.submenu =[ 
#     'Menu', False, '/Qualidade_Ambiental/default/index', 
#     [
#         ['Logradouro', False, '/Qualidade_Ambiental/default/Logradouro'],
#         ['Enderecos', False, '/Qualidade_Ambiental/default/Enderecos'],
#         ['Obras', False, '/Qualidade_Ambiental/default/Obras'],
#         ['Pessoas', False, '/Qualidade_Ambiental/default/Pessoas'],
#         ['Processos', False, '/Qualidade_Ambiental/default/Processos'],
#    ]
   
# ]
