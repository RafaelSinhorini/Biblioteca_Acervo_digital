from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config import Config

# Inicialização do Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Criação das tabelas do banco de dados com app.app_context() conforme Flask 3.x
with app.app_context():
    db.create_all()

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Definição dos modelos de dados
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    tipo_usuario = db.Column(db.String(10), nullable=False)  # 'aluno' ou 'docente'
    trabalhos = db.relationship('Trabalho', backref='autor', lazy=True)

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_conclusao = db.Column(db.Date, nullable=False)
    trabalhos = db.relationship('Trabalho', backref='curso', lazy=True)

class Trabalho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    palavras_chave = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)

class TokenRecuperacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(32), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)
    data_expiracao = db.Column(db.DateTime, nullable=False)  # Campo esperado pelo banco de dados
    valido_ate = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rota para a tela inicial
@app.route('/')
def tela_inicial():
    return render_template('tela-inicial.html')

# Rota para a tela de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Verifica se a senha está no formato pbkdf2:sha256
            if not usuario.senha.startswith('pbkdf2:sha256'):
                # Tenta verificar com o método antigo
                if check_password_hash(usuario.senha, senha):
                    # Atualiza a senha para o novo formato
                    usuario.senha = generate_password_hash(senha, method='pbkdf2:sha256')
                    db.session.commit()
                    login_user(usuario)
                    flash('Sua senha foi atualizada para um formato mais seguro.')
                    return redirect(url_for('home'))
                else:
                    flash('Email ou senha incorretos. Tente novamente.')
            elif check_password_hash(usuario.senha, senha):
                login_user(usuario)
                return redirect(url_for('home'))
            else:
                flash('Email ou senha incorretos. Tente novamente.')
        else:
            flash('Email ou senha incorretos. Tente novamente.')
    
    return render_template('tela-login.html')

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('tela_inicial'))

# Rota para recuperação de senha
@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    # Limpar tokens expirados a cada acesso à página
    limpar_tokens_expirados()
    
    if request.method == 'POST':
        step = request.form.get('step', 'solicitar')
        
        # Etapa 1: Solicitar recuperação
        if step == 'solicitar':
            email = request.form.get('email')
            
            # Verificar se o usuário existe
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario:
                flash('Email não encontrado. Verifique e tente novamente.', 'error')
                return render_template('recuperar-senha.html', step='solicitar')
            
            # Remover tokens antigos para este email
            TokenRecuperacao.query.filter_by(email=email).delete()
            
            # Gerar novo token de recuperação
            token = gerar_token_recuperacao()
            valido_ate = datetime.now() + timedelta(minutes=15)
            
            # Salvar token no banco de dados
            novo_token = TokenRecuperacao(
                email=email,
                token=token,
                criado_em=datetime.now(),
                data_expiracao=valido_ate,  # Adicionando o campo data_expiracao
                valido_ate=valido_ate,
                usado=False
            )
            
            db.session.add(novo_token)
            db.session.commit()
            
            # Exibir token na tela
            return render_template('recuperar-senha.html', step='mostrar_token', email=email, token=token, valido_ate=valido_ate)
        
        # Etapa 2: Verificar token
        elif step == 'verificar':
            email = request.form.get('email')
            token = request.form.get('token')
            
            # Verificar se o token é válido
            token_recuperacao = TokenRecuperacao.query.filter_by(
                email=email,
                token=token,
                usado=False
            ).first()
            
            if not token_recuperacao:
                flash('Token inválido. Verifique e tente novamente.', 'error')
                return render_template('recuperar-senha.html', step='verificar', email=email)
            
            # Verificar se o token expirou
            if datetime.now() > token_recuperacao.valido_ate:
                flash('Token expirado. Solicite um novo token.', 'error')
                return render_template('recuperar-senha.html', step='solicitar')
            
            # Token válido, prosseguir para redefinição de senha
            return render_template('recuperar-senha.html', step='redefinir', email=email, token=token)
        
        # Etapa 3: Redefinir senha
        elif step == 'redefinir':
            email = request.form.get('email')
            token = request.form.get('token')
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            # Verificar se as senhas coincidem
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem. Tente novamente.', 'error')
                return render_template('recuperar-senha.html', step='redefinir', email=email, token=token)
            
            # Verificar se o token é válido
            token_recuperacao = TokenRecuperacao.query.filter_by(
                email=email,
                token=token,
                usado=False
            ).first()
            
            if not token_recuperacao or datetime.now() > token_recuperacao.valido_ate:
                flash('Token inválido ou expirado. Solicite um novo token.', 'error')
                return render_template('recuperar-senha.html', step='solicitar')
            
            # Atualizar senha do usuário
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                usuario.senha = generate_password_hash(nova_senha, method='pbkdf2:sha256')
                
                # Marcar token como usado
                token_recuperacao.usado = True
                
                db.session.commit()
                
                flash('Senha redefinida com sucesso! Faça login com sua nova senha.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Usuário não encontrado. Tente novamente.', 'error')
                return render_template('recuperar-senha.html', step='solicitar')
    
    # Método GET: exibir formulário inicial
    return render_template('recuperar-senha.html', step='solicitar')

# Rota para a tela cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        data_nascimento = request.form['data_nascimento']
        tipo_usuario = request.form['tipo_usuario']
        
        # Verificar se o email já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Email já cadastrado. Por favor, use outro email.')
            return render_template('cadastro.html')
        
        # Verificar se as senhas coincidem
        if senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.')
            return render_template('cadastro.html')
        
        # Criar novo usuário com hash de senha compatível com Werkzeug (pbkdf2:sha256)
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha, method='pbkdf2:sha256'),
            data_nascimento=data_nascimento,
            tipo_usuario=tipo_usuario
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.')
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

# Rota para a tela home
@app.route('/home', methods=['GET'])
@login_required
def home():
    # Obter parâmetros de busca
    titulo = request.args.get('titulo', '')
    turma = request.args.get('turma', '')
    modalidade = request.args.get('modalidade', '')
    curso = request.args.get('curso', '')
    
    # Iniciar com todos os trabalhos
    query = Trabalho.query
    
    # Aplicar filtros se fornecidos
    if titulo:
        query = query.filter(Trabalho.titulo.ilike(f'%{titulo}%'))
    if turma:
        query = query.filter(Trabalho.turma.ilike(f'%{turma}%'))
    # Filtro de modalidade aplicado através da relação com Curso
    if modalidade:
        query = query.join(Curso).filter(Curso.tipo.ilike(f'%{modalidade}%'))
    elif curso:  # Usar elif para evitar join duplicado se modalidade já foi aplicada
        query = query.join(Curso)
    
    # Aplicar filtro de curso se fornecido
    if curso:
        query = query.filter(Curso.nome.ilike(f'%{curso}%'))
    
    # Executar a consulta
    trabalhos = query.all()
    
    # Verificar se há filtros ativos para mostrar a seta
    filtros_ativos = any([titulo, turma, modalidade, curso])
    
    return render_template('home.html', trabalhos=trabalhos, filtros_ativos=filtros_ativos)

# Rota para apresentar um trabalho específico
@app.route('/apresentar-trabalho/<int:trabalho_id>')
@login_required
def apresentar_trabalho(trabalho_id):
    # Buscar o trabalho pelo ID
    trabalho = Trabalho.query.get_or_404(trabalho_id)
    
    # Buscar informações relacionadas
    usuario = Usuario.query.get(trabalho.usuario_id)
    curso = Curso.query.get(trabalho.curso_id)
    
    return render_template('apresentar-trabalho.html', trabalho=trabalho, usuario=usuario, curso=curso)

# Rota para a tela de cadastro de cursos
@app.route('/cadastrar-cursos', methods=['GET', 'POST'])
@login_required
def cadastrar_curso():
    # Verificar se o usuário é docente
    if current_user.tipo_usuario != 'docente':
        flash('Acesso restrito a docentes.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Capturar dados do formulário
        area = request.form['area']
        tipo = request.form['tipo']
        nome = request.form['nome']
        turma = request.form['turma']
        data_inicio = request.form['data_inicio']
        data_conclusao = request.form['data_conclusao']
        
        # Validar dados
        if not nome:
            mensagem_erro = "Por favor, preencha todos os campos obrigatórios!"
            return render_template('cadastrar-cursos.html', mensagem_erro=mensagem_erro)
        
        # Criar novo curso
        novo_curso = Curso(
            area=area,
            tipo=tipo,
            nome=nome,
            turma=turma,
            data_inicio=data_inicio,
            data_conclusao=data_conclusao
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_curso)
        db.session.commit()
        
        mensagem = "Curso cadastrado com sucesso!"
        return render_template('cadastrar-cursos.html', mensagem=mensagem)
    
    return render_template('cadastrar-cursos.html')

# Rota para a tela de cadastro de trabalhos
@app.route("/cadastrar-trabalho", methods=["GET", "POST"])
@login_required
def cadastrar_trabalho():
    # Verificar se o usuário é docente
    if current_user.tipo_usuario != 'docente':
        flash('Acesso restrito a docentes.')
        return redirect(url_for('home'))
    
    # Buscar cursos para o select
    cursos = Curso.query.all()
    
    if request.method == 'POST':
        # Captura os dados do formulário
        titulo = request.form['titulo']
        curso_id = request.form['id_curso']
        descricao = request.form['descricao']
        palavras_chave = request.form['palavras_chave']
        link = request.form['link']
        
        # Verificar se o curso existe
        curso = Curso.query.get(curso_id)
        if not curso:
            mensagem_erro = "Curso não encontrado. Verifique o ID do curso."
            return render_template('cadastrar-trabalhos.html', mensagem_erro=mensagem_erro, cursos=cursos)
        
        # Criar novo trabalho
        novo_trabalho = Trabalho(
            titulo=titulo,
            descricao=descricao,
            palavras_chave=palavras_chave,
            link=link,
            usuario_id=current_user.id,
            curso_id=curso_id
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_trabalho)
        db.session.commit()
        
        mensagem = "Trabalho cadastrado com sucesso!"
        return render_template('cadastrar-trabalhos.html', mensagem=mensagem, cursos=cursos)
    
    return render_template('cadastrar-trabalhos.html', cursos=cursos)

# Função para verificar e atualizar o formato das senhas
def verificar_formato_senhas():
    with app.app_context():
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            # Verifica se a senha não está no formato pbkdf2:sha256
            if not usuario.senha.startswith('pbkdf2:sha256'):
                print(f"AVISO: A senha do usuário {usuario.email} não está no formato pbkdf2:sha256.")
                print("Este usuário precisará redefinir sua senha no próximo login.")
                # Não podemos migrar automaticamente pois não temos acesso à senha original
                # O usuário precisará fazer login e redefinir a senha

# Função para gerar token de recuperação aleatório
def gerar_token_recuperacao():
    # Usando secrets para gerar um token seguro de 16 bytes (32 caracteres em hexadecimal)
    import secrets
    return secrets.token_urlsafe(16)

# Função para limpar tokens expirados
def limpar_tokens_expirados():
    try:
        # Remover todos os tokens expirados
        TokenRecuperacao.query.filter(TokenRecuperacao.valido_ate < datetime.now()).delete()
        db.session.commit()
        return True
    except Exception as e:
        print(f"Erro ao limpar tokens expirados: {e}")
        db.session.rollback()
        return False

# Inicializar o banco de dados
# Removido @app.before_first_request conforme Flask 3.x

if __name__ == "__main__":
    # Verificar se o diretório de uploads existe; se não, criar
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    # Verificar o formato das senhas existentes
    verificar_formato_senhas()

    # Porta dinâmica do Railway; padrão 5000 para ambiente local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)




