import os
import sys
import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, validates
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


# Detecta se o app está rodando empacotado com PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # pasta temporária usada pelo PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(BASE_DIR, '.env')

if not os.path.exists(ENV_PATH):
    # tenta achar um .env na raiz do projeto (modo debug)
    fallback = os.path.join(os.path.dirname(BASE_DIR), '.env')
    if os.path.exists(fallback):
        ENV_PATH = fallback
    else:
        raise FileNotFoundError(f"Arquivo .env não encontrado em: {ENV_PATH}")

load_dotenv(ENV_PATH)


# ----------------------------
# Variáveis do banco
# ----------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")

if not DB_USER or not DB_NAME:
    raise ValueError(
        "Variáveis de ambiente obrigatórias não definidas!\n"
        "Verifique o arquivo .env:\n"
        "DB_USER=seu_usuario_mysql\nDB_PASSWORD=sua_senha_mysql\n"
        "DB_HOST=localhost\nDB_NAME=nome_do_banco"
    )

# ----------------------------
# Configuração do SQLAlchemy
# ----------------------------
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# ✅ Exporte APENAS a fábrica de sessões, não uma sessão ativa
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ----------------------------
# Pasta para salvar arquivos
# ----------------------------
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
# ❌ NÃO crie diretórios no nível do módulo — faça isso em funções
# (mas manter a variável está ok)

# ----------------------------
# Modelo de Usuário
# ----------------------------
class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    senha = Column(String(200), nullable=False)
    google_token = Column(Text, nullable=True)

    def set_password(self, senha: str) -> None:
        self.senha = generate_password_hash(senha)

    def check_password(self, senha: str) -> bool:
        return check_password_hash(self.senha, senha)

    @validates("google_token")
    def validate_google_token(self, key, value):
        if value:
            try:
                json.loads(value)
            except Exception as e:
                raise ValueError(f"google_token inválido: {e}")
        return value

# ----------------------------
# Criar tabelas
# ----------------------------
try:
    Base.metadata.create_all(engine)
    print("[INFO] Tabelas criadas/verificadas com sucesso.")
except Exception as e:
    print("[ERRO] Não foi possível criar/verificar tabelas:", e)

# ----------------------------
# Função auxiliar para obter sessão (boa prática)
# ----------------------------
def get_db_session():
    """Retorna uma nova sessão do banco. Use em contextos com `with` ou feche manualmente."""
    return SessionLocal()

# ----------------------------
# Função para testar conexão
# ----------------------------
def testar_conexao():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("[INFO] Conexão com o MySQL bem-sucedida!")
    except Exception as e:
        print("[ERRO] Falha ao conectar no MySQL:", e)

if __name__ == "__main__":
    testar_conexao()