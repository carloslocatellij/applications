# 🌳 Sistema de Gestão de Laudos Ambientais - Web2py

## Sobre o Projeto

Sistema web desenvolvido em Python/Web2py para gestão completa de requerimentos e laudos técnicos relacionados à arborização urbana. Permite o controle e acompanhamento de solicitações de poda e supressão de árvores, emissão de laudos técnicos e gestão do patrimônio arbóreo municipal.

## 🚀 Funcionalidades

- Cadastro e gestão de requerimentos
- Emissão e controle de laudos técnicos
- Sistema de busca avançada com múltiplos filtros
- Geração automatizada de documentos
- Histórico completo de intervenções por região
- Interface responsiva e intuitiva
- Controle de acesso por usuários

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Web2py Framework**
- **SQLite/PostgreSQL**
- **HTML5/CSS3/JavaScript**
- **Bootstrap**
- **Faker (para dados de teste)**

## 📋 Pré-requisitos

```bash
Python 3.x
Web2py
```

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/viveiro-analises.git
```

2. Instale o Web2py:
```bash
wget http://www.web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip
```

3. Copie a aplicação para a pasta applications do Web2py:
```bash
cp -r viveiro-analises /path/to/web2py/applications/
```

## 📦 Estrutura do Projeto

```
applications/
└── Viveiro_Analises/
    ├── models/
    │   ├── db.py
    │   └── 0_estruct.py
    ├── controllers/
    │   └── default.py
    ├── views/
    │   └── default/
    └── static/
```

## 💻 Como Usar

1. Inicie o servidor Web2py:
```bash
python web2py.py
```

2. Acesse a aplicação através do navegador:
```
http://localhost:8000/Viveiro_Analises
```

## 🔍 Funcionalidades Principais

### Requerimentos
- Cadastro de solicitações
- Acompanhamento de status
- Histórico de alterações

### Laudos Técnicos
- Emissão de laudos
- Avaliação técnica
- Registro fotográfico

### Busca Avançada
- Filtros por data
- Busca por protocolo
- Pesquisa por endereço
- Filtros por região

## 👥 Contribuição

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## ✒️ Autores

* **Seu Nome** - *Desenvolvimento* - [SeuUsuario](https://github.com/SeuUsuario)

## 📄 Notas

- O sistema inclui dados de teste gerados automaticamente em ambiente de desenvolvimento
- Configurável para diferentes ambientes (desenvolvimento/produção)
- Suporte a múltiplos bancos de dados

---

⌨️ com ❤️ por [Seu Nome](https://github.com/SeuUsuario)