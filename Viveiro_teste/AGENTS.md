# Diretrizes de Desenvolvimento e Segurança - Projeto Web2py

## Contexto do Framework
- Este projeto utiliza o framework web2py (Python 3).
- **Regra de Ouro:** NUNCA adicione `import` para modelos ou bancos de dados nos Controllers ou Models. O web2py injeta o objeto `db` e globais (`auth`, `request`, `response`, `session`, `redirect`, `URL`, `Field`, `IS_NOT_EMPTY`, etc.) automaticamente.
- Arquivos em `models/` são executados em ordem alfabética antes dos controllers.

## Estrutura do Workspace
- Pasta raiz `.`: Aplicação no framework web2py (`web2py/applications/Viveiro_Analises`).
- `models/`: Definições de tabelas do PyDAL (ex: `0_estruct.py`, `a_db.py`, `db.py`, `menu.py`, `textos_modelos.py`).
- `controllers/`: Funções públicas expostas como endpoints. Ex: `default.py`, `despachos.py`, `relatorios.py`, `geral.py`.
- `views/`: Arquivos HTML com tags de renderização `{{=...}}`.
- `modules/`: Módulos Python puros que EXIGEM importação manual se utilizados.
- `tests/`: Testes unitários do projeto (executáveis com `pytest`).
- `.agents/`: Regras e skills estendidas para o Antigravity CLI.

## Regras de Segurança e Banco de Dados
- Restrição de escopo: Operar estritamente dentro deste repositório da aplicação local.
- Proteção de dados: PROIBIDO deletar, mover ou alterar diretamente os arquivos das pastas `databases/`, `sessions/` ou `uploads/`.
- Migrations: Qualquer alteração destrutiva ou nova migração em `models/` deve ser auditada e confirmada antes de ser executada.
- Erros: Em caso de falhas, inspecione os tickets em `errors/` para identificar a causa raiz antes de aplicar correções.

## Padrões de Código
- Toda função pública em um controller que retorna um dicionário expõe uma View correspondente.
- Funções utilitárias privadas em controllers devem iniciar com underline (ex: `def _funcao_privada():`).
- Use `db.tabela.insert()` e `db(db.tabela.id == x).select()` para interações com o banco de dados.
- Mantenha respostas concisas e indique claramente a pasta do arquivo modificado (`models/`, `controllers/`, `views/`, `modules/`, `tests/`).
