---
name: web2py-migration
description: "Guia para auditoria e aplicação segura de alterações de esquema de banco de dados (PyDAL migrations) no Web2py."
---

# Skill: web2py-migration

Esta skill orienta como realizar e auditar alterações em tabelas PyDAL (`models/`) com segurança para evitar perda de dados ou bloqueios de tabela.

## Auditoria de Schemas antes da Alteração

1. **Inspecione os modelos existentes:**
   Antes de adicionar ou modificar campos, verifique como as tabelas foram definidas em `models/a_db.py`, `models/db.py` ou outros arquivos da pasta `models/`.
2. **Checar referências cruzadas:**
   Campos do tipo `'reference tabela'` criam chaves estrangeiras. Certifique-se de que a tabela referenciada foi definida em um arquivo executado ANTES em ordem alfabética (ex: tabela em `a_db.py` sendo referenciada em `db.py`).

## Regras para Migrações com PyDAL

- **Campos Obrigatórios:** Ao adicionar novos campos obrigatórios (`requires=IS_NOT_EMPTY()`), certifique-se de definir um valor padrão (`default=...`) se a tabela já contiver registros em produção.
- **Tipos de Dados suportados:**
  - `'string'`, `'text'`, `'integer'`, `'double'`, `'boolean'`
  - `'date'`, `'datetime'`, `'time'`
  - `'blob'`, `'upload'`, `'reference outra_tabela'`
- **Desativar Migração em Produção:** Em ambientes de produção sensíveis, o Web2py pode ter `fake_migrate=True` ou `migrate=False` configurado na inicialização do DAL (`DAL(..., migrate=False)`).

## Procedimento de Validação de Migration

1. Avise o usuário antes de adicionar/alterar/remover campos que exigem migração no banco de dados.
2. NUNCA altere os arquivos contidos em `databases/*.table` manualmente. Deixe o PyDAL gerenciar ou consulte o usuário para criar scripts de migração de dados customizados.
