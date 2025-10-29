import os

class Config:
    # Configuração do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-para-desenvolvimento'
    
    # Configuração do SQLAlchemy para MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:raf167725@127.0.0.1:3307/acervo_digital'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuração do Flask-Login
    LOGIN_VIEW = 'login'
    
    # Configuração de upload de arquivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = False  # Definir como True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600  # 1 hora