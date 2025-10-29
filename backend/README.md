# 📚 Biblioteca Acervo Digital

Este projeto consiste em um sistema web para arquivar e consultar trabalhos desenvolvidos por alunos de uma escola de cursos técnicos. O sistema foi desenvolvido como parte de um trabalho da graduação em **Ciência de Dados pela UNIVESP**, para atender às necessidades reais de um cliente (não identificado por questões de privacidade).

## 🛠 Tecnologias utilizadas

- Python
- Flask
- HTML
- CSS
- JavaScript (animações)
- MySQL
- Flask-Login (autenticação)
- SQLAlchemy (ORM)

## 💡 Objetivo

O objetivo do sistema é permitir que os trabalhos produzidos por alunos sejam armazenados, organizados e consultados de forma simples, acessível e centralizada em uma plataforma web. A ideia é facilitar a troca de conhecimento e promover a visibilidade dos projetos entre os próprios alunos e os docentes.

## 🔍 Funcionalidades

- Tela inicial com animações em JavaScript
- Sistema de autenticação com diferenciação entre alunos e docentes
- Cadastro de novos usuários com validação
- Busca de projetos arquivados com filtros
- Cadastro de novos trabalhos (exclusivo para docentes)
- Cadastro de cursos vinculados aos projetos (exclusivo para docentes)
- Armazenamento de dados em banco MySQL
- Controle de acesso baseado no tipo de usuário

## 👨‍💻 Como usar

Para rodar o projeto localmente:

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar o banco de dados

1. Certifique-se de que o MySQL está instalado e em execução
2. Execute o script de inicialização do banco de dados:

```bash
python init_db.py
```

Este script irá:
- Criar o banco de dados `acervo_digital` se não existir
- Criar as tabelas necessárias
- Inserir dados de exemplo para testes

### 3. Executar a aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 👥 Usuários de Teste

### Docente
- Email: professor@teste.com
- Senha: senha123

### Aluno
- Email: aluno@teste.com
- Senha: senha123

