# auth.py
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from models.models_usuario import get_db_session, Usuario  # ✅ Importação corrigida

def salvar_token_google(user_id, creds):
    """Salva token do Google associado ao usuário."""
    session = get_db_session()
    try:
        user = session.query(Usuario).get(user_id)
        if user:
            user.google_token = creds.to_json()
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def carregar_token_google(user_id):
    """Carrega e atualiza token do Google, se possível."""
    session = get_db_session()
    try:
        user = session.query(Usuario).get(user_id)
        if not user or not user.google_token:
            return None

        try:
            creds = Credentials.from_authorized_user_info(json.loads(user.google_token))
            if creds.valid:
                return creds
            elif creds.expired and creds.refresh_token:
                creds.refresh(Request())
                user.google_token = creds.to_json()
                session.commit()
                return creds
        except Exception as e:
            print("Erro ao carregar/refresh token:", e)
            return None
        return None
    finally:
        session.close()