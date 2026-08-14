---
name: web2py-dev
description: "Guia de desenvolvimento, testes automatizados e diagnóstico de erros para a aplicação Web2py no Antigravity CLI."
---

# Skill: web2py-dev

Esta skill fornece instruções para testar, diagnosticar e desenvolver funcionalidades nesta aplicação Web2py com segurança.

## Executando Testes Automatizados

Para executar os testes unitários do projeto usando o ambiente Python local:

```powershell
rtk python -m pytest tests/
```

Se precisar rodar um teste específico em um módulo:
```powershell
rtk python -m pytest tests/models/test_textos_modelos.py
```

## Diagnóstico de Erros (Tickets Web2py)

Quando uma requisição Web2py falha em tempo de execução, o framework gera um ticket numerado em `errors/`.

1. **Listar tickets recentes:**
   ```powershell
   Get-ChildItem errors/ | Sort-CreationTime -Descending | Select-Object -First 3
   ```
2. **Inspecionar traceback do ticket:**
   Use `view_file` para ler o arquivo dentro de `errors/<ticket_id>`. O arquivo contém o traceback Python completo, variáveis locais e requisição.
3. Baseie a solução estritamente na causa raiz identificada no traceback.

## Boas Práticas ao Editar Código

- **Modelos (`models/`):**
  Defina tabelas com PyDAL:
  ```python
  db.define_table('nome_tabela',
      Field('nome', 'string', requires=IS_NOT_EMPTY()),
      Field('observacao', 'text'),
      auth.signature
  )
  ```
- **Controladores (`controllers/`):**
  ```python
  @auth.requires_login()
  def minha_acao():
      registros = db(db.nome_tabela.id > 0).select()
      return dict(registros=registros)
  ```
- **Visões (`views/`):**
  ```html
  {{extend 'layout.html'}}
  <h2>Lista de Registros</h2>
  {{for r in registros:}}
      <p>{{=r.nome}}</p>
  {{pass}}
  ```
