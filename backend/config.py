import os


def _normalize_db_url(url: str) -> str:
    """Converte URLs mysql:// para mysql+pymysql:// para o SQLAlchemy."""
    if url and url.startswith("mysql://"):
        return "mysql+pymysql://" + url[len("mysql://"):]
    return url


# URL padrão do Railway (pode ser sobrescrita por variáveis de ambiente)
RAILWAY_DB_URL = "mysql://root:PMdlxllXwlmqeXqMTTJNtOdLIRLXBtaK@maglev.proxy.rlwy.net:38829/acervo_digital"

# Prioriza variáveis de ambiente fornecidas pelo Railway
DB_URL = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("MYSQL_URL")
    or RAILWAY_DB_URL
)


class Config:
    # Configuração do Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-secreta-padrao-para-desenvolvimento"

    # Configuração do SQLAlchemy (MySQL via PyMySQL)
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(DB_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Segurança
    SESSION_COOKIE_SECURE = False  # Defina True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600  # 1 hora