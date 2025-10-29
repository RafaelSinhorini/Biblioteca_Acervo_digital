-- Script para criar o banco de dados e tabelas para o Acervo Digital

-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS acervo_digital;
USE acervo_digital;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(200) NOT NULL,
    data_nascimento DATE NOT NULL,
    tipo_usuario VARCHAR(10) NOT NULL CHECK (tipo_usuario IN ('aluno', 'docente'))
);

-- Tabela de cursos
CREATE TABLE IF NOT EXISTS curso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    turma VARCHAR(50) NOT NULL,
    data_inicio DATE NOT NULL,
    data_conclusao DATE NOT NULL
);

-- Tabela de trabalhos
CREATE TABLE IF NOT EXISTS trabalho (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    palavras_chave VARCHAR(200) NOT NULL,
    link VARCHAR(500) NOT NULL,
    usuario_id INT NOT NULL,
    curso_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (curso_id) REFERENCES curso(id)
);

-- Índices para melhorar a performance
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_trabalho_titulo ON trabalho(titulo);
CREATE INDEX idx_curso_nome ON curso(nome);
CREATE INDEX idx_curso_area ON curso(area);

-- Inserir alguns dados de exemplo para testes
-- Usuários (senha: 'senha123' com hash)
INSERT INTO usuario (nome, email, senha, data_nascimento, tipo_usuario) VALUES
('Professor Teste', 'professor@teste.com', 'pbkdf2:sha256:150000$abc123$abcdef1234567890abcdef1234567890abcdef1234567890', '1980-01-01', 'docente'),
('Aluno Teste', 'aluno@teste.com', 'pbkdf2:sha256:150000$abc123$abcdef1234567890abcdef1234567890abcdef1234567890', '2000-01-01', 'aluno');

-- Cursos
INSERT INTO curso (area, tipo, nome, turma, data_inicio, data_conclusao) VALUES
('Tecnologia da Informação', 'Curso Técnico', 'Desenvolvimento Web', 'Turma A', '2023-01-01', '2023-12-31'),
('Educação', 'Qualificação Profissional', 'Metodologias Ativas', 'Turma B', '2023-02-01', '2023-11-30');

-- Trabalhos
INSERT INTO trabalho (titulo, descricao, palavras_chave, link, usuario_id, curso_id) VALUES
('Desenvolvimento de Sistema Web para Biblioteca', 'Este trabalho apresenta o desenvolvimento de um sistema web para gerenciamento de biblioteca utilizando tecnologias modernas.', 'biblioteca, sistema web, desenvolvimento', 'https://exemplo.com/trabalho1', 1, 1),
('Aplicação de Metodologias Ativas no Ensino Fundamental', 'Estudo sobre a aplicação de metodologias ativas no ensino fundamental e seus impactos no aprendizado.', 'metodologias ativas, ensino fundamental, educação', 'https://exemplo.com/trabalho2', 2, 2);

-- Tabela para recuperação de senha com token temporário
CREATE TABLE IF NOT EXISTS token_recuperacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    token VARCHAR(100) NOT NULL UNIQUE,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    valido_ate DATETIME NOT NULL
);

-- Índice para buscar rápido pelo email
CREATE INDEX idx_token_email ON token_recuperacao(email);
