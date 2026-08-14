# Regras de Desenvolvimento e Segurança - Web2py no Antigravity CLI

## 1. Escopo e Segurança do Ambiente
- **Restrição de Diretório:** Todas as modificações e scripts devem operar dentro da pasta da aplicação local (`.`), a menos que explicitamente autorizado pelo usuário.
- **Proteção do Banco de Dados:** É ESTRITAMENTE PROIBIDO deletar, mover ou sobrescrever arquivos diretamente dentro de `databases/`, `sessions/` ou `uploads/`.
- **Migrations Seguras:** Qualquer modificação de schema nos modelos em `models/` que cause migração de tabela (ex: alteração ou remoção de campos no PyDAL) deve ser auditada e confirmada com o usuário antes de ser executada.
- **Diagnóstico de Erros:** Em caso de exceções no servidor web2py, inspecione os logs gerados na pasta `errors/` lendo o arquivo de ticket correspondente. NUNCA apague ou altere os relatórios de erro da pasta `errors/`.

## 2. Padrão Arquitetural MVC e Convenções do Web2py
- **Injeção de Globais:** O Web2py injeta objetos globais automaticamente no escopo de execução. NUNCA adicione declarações de `import` em controllers ou models para:
  `db`, `auth`, `request`, `response`, `session`, `redirect`, `URL`, `Field`, `IS_NOT_EMPTY`, `IS_IN_SET`, `SQLFORM`, `FORM`, `DIV`, `A`, `INPUT`.
- **Ordem de Execução dos Modelos:** Arquivos em `models/` são executados em ordem alfabética a cada requisição HTTP antes de qualquer controller. Mantenha as definições base em `0_estruct.py`, conexões e tabelas base em `a_db.py` e `db.py`, e lógicas adicionais em arquivos posteriores.
- **Controladores (Controllers):**
  - Toda função pública em um controller deve retornar um `dict(...)` para ser renderizada pela view `.html` correspondente.
  - Funções utilitárias privadas em controllers DEVEM iniciar com underline (ex: `def _calcular_totais():`).
- **Visões (Views):**
  - Combine HTML estruturado com a sintaxe delimitadora do web2py: `{{=variavel}}` e `{{for item in lista:}} ... {{pass}}`.

## 3. Qualidade e Testes Automatizados
- Sempre que criar ou refatorar funções de modelos ou módulos em `modules/`, atualize ou adicione os testes unitários correspondentes no diretório `tests/`.
- Execute a suíte de testes com `pytest` ou via interpretador Python antes de declarar uma tarefa concluída.
