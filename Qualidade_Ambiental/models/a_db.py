# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
import copy

if 0==1:
    from gluon import *
    from gluon import db, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH,\
     a_db, db, auth, Auth, pegaDof
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

#if request.global_settings.web2py_version < "2.15.5":
#    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=False)


# session.connect(request, response, cookie_key=configuration.take("db")['password'],)
# session.secure()
# session.samesite('Strict')



db = DAL('{}://{}:{}@{}/{}'.format(
                configuration.take("db")['engine'],
                configuration.take("db")['username'],
                configuration.take("db")['password'],
                configuration.take("db")['uri'],
                configuration.take("db")['database'] ) ,
            pool_size=50,
            migrate_enabled=True, migrate=False, fake_migrate_all=True, lazy_tables=True,
            check_reserved=['mysql'], adapter_args={'safe': True},
            )

#db._adapter.types = copy.copy(db._adapter.types)
db._adapter.types['boolean']='TINYINT(1)'
db._adapter.TRUE = 1
db._adapter.FALSE = 0

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = []
#if request.is_local and not configuration.get('app.production'):

#response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(
    db, host_names=configuration.get('host.names'),
     )

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------




# from validador import IS_CPF
auth.settings.extra_fields['auth_user'] = [
    Field('IdDepto', 'integer'),
    #Field('CPF', 'text', requires=IS_CPF()),
]

auth.define_tables(username=True, signature=True, fake_migrate=True, )

auth.settings.update_fields = [ 'first_name', 'last_name', 'username', 'email', 'IdDepto']

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------

from gluon.tools import Mail
from gluon.html import XML

# Crie uma nova classe de Mail que herda da original
# class CustomMail(Mail):
#     def send(self, to, subject, message, **kwargs):
#         if hasattr(subject, 'xml'):  # Se for lazyT
#             subject = str(subject)
#         if hasattr(message, 'xml'):  # Se for lazyT
#             message = str(message)
#         return super().send(to, subject, message, **kwargs)

# # Configure o auth para usar o novo mailer
# auth.settings.mailer = CustomMail()

import smtplib
import logging

class DebugMail(Mail):
    def send(self, to, subject, message, **kwargs):
        try:
            result = super().send(to, subject, message, **kwargs)
            logging.info(f"Email sent successfully to {to}")
            return result
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise

auth.settings.mailer = DebugMail()

mail = auth.settings.mailer
mail.settings.server = configuration.get('smtp.server') # 'logging' if request.is_local else
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = f"{configuration.get('smtp.username')}:{configuration.get('smtp.password')}" #configuration.get('smtp.login')
mail.settings.tls = True
mail.settings.ssl = False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id
# -------------------------------------------------------------------------
#response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
# if configuration.get('scheduler.enabled'):
#     from gluon.scheduler import Scheduler
#     scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------
