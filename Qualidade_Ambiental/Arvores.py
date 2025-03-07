# coding: utf-8
#!/usr/bin/python3.8
session.forget(response)

if 0==1:
    from gluon import *
    from gluon import db, SQLFORM, IS_IN_SET, IS_UPPER, IS_EMPTY_OR, IS_IN_DB, IS_NOT_IN_DB, IS_MATCH, redirect, URL, XML, a_db, db, auth, Auth, buscador
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    T = current.T


def index():
    response.flash = T("Bem Vindo!")
    return dict(sistema=T('Sistema de Dados do Dpto. de Qualidade Ambiental!'))


def  Requerimento_arvore():
    ...
