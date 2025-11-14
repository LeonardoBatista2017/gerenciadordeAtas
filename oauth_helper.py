# oauth_helper.py
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from kivy.clock import Clock
from google_auth_oauthlib.flow import Flow

# Escopos corrigidos (sem espaços!)
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Variáveis globais para comunicação
oauth_code = None
oauth_error = None
oauth_server = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global oauth_code, oauth_error, oauth_server
        if self.path.startswith('/callback'):
            query = urlparse(self.path).query
            params = parse_qs(query)
            if 'code' in params:
                oauth_code = params['code'][0]
                response_html = b"<h2>Autentica&ccedil;&atilde;o conclu&iacute;da!</h2><p>Pode fechar esta janela.</p>"
            elif 'error' in params:
                oauth_error = params['error'][0]
                response_html = f"<h2>Erro: {oauth_error}</h2>".encode()
            else:
                oauth_error = "unknown_error"
                response_html = b"<h2>Erro desconhecido.</h2>"

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(response_html)

            # Para o servidor em outro thread
            threading.Thread(target=oauth_server.shutdown).start()
        else:
            self.send_response(404)
            self.end_headers()

def start_oauth_server(port=5000):
    global oauth_server
    oauth_server = HTTPServer(('127.0.0.1', port), OAuthCallbackHandler)
    oauth_server.serve_forever()

def iniciar_oauth_kivy(callback):
    """
    Inicia o fluxo OAuth com servidor local.
    Chama callback(creds, error) quando terminar.
    """
    global oauth_code, oauth_error
    oauth_code = None
    oauth_error = None

    # Inicia servidor em background
    server_thread = threading.Thread(target=start_oauth_server, daemon=True)
    server_thread.start()

    # Cria o fluxo OAuth
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:5000/callback'
    )
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    # Abre navegador
    import webbrowser
    webbrowser.open(auth_url)

    # Função para verificar o código periodicamente
    def check_code(dt):
        global oauth_code, oauth_error
        if oauth_code:
            Clock.unschedule(check_code)
            try:
                flow.fetch_token(code=oauth_code)
                callback(flow.credentials, None)
            except Exception as e:
                callback(None, str(e))
        elif oauth_error:
            Clock.unschedule(check_code)
            callback(None, oauth_error)

    Clock.schedule_interval(check_code, 0.5)