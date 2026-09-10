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

## Executando Scripts no Ambiente do Web2py

Para executar scripts diagnósticos ou migrações que exigem o contexto dos Models carregados:
```powershell
rtk python C:\Users\clocatelli\web2py\web2py.py -S Viveiro_Analises -M -R applications\Viveiro_Analises\caminho\script.py
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

## Padrões de Interface e Conteúdo (Base de Conhecimento / Wiki)
- **Cabeçalhos e Banners em Degradê:** Utilize o padrão escuro e elegante para destaque e alto contraste:
  `background: linear-gradient(135deg, #1f2937 0%, #111827 50%, #004d40 100%); color: #ffffff;`
- **Renderização Resiliente de Markdown:** O renderizador deve processar sintaxe Markdown (`#`, `-`, `**`, callouts `> [!NOTE]`, tabelas) mesmo se o atributo `render` no banco for `'html'`, `'markdown'` ou nulo, mantendo tags HTML seguras.

## Em caso de dúvidas: Verifique a documentação original do web2py e documentos relacionados em:
 https://web2py.com/book
 https://www.web2py.com/examples/default/examples
 https://www.web2pyref.com/

 