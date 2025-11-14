# views/main_screen_safe.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
import threading
import webbrowser
import os
from kivy.graphics import Color, Rectangle
from datetime import datetime

from controllers.controllers_usuario import processar_ata, ata_status, listar_reunioes, get_user_upload_folder, gerar_resumo_texto
from auth import carregar_token_google, salvar_token_google
from oauth_helper import iniciar_oauth_kivy
from kivy.uix.popup import Popup


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fundo branco
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg_rect, pos=self._update_bg_rect)

        # Dados e paginação
        self.todos_eventos = []
        self.eventos_filtrados = []
        self.pagina_atual = 0
        self.itens_por_pagina = 10
        self._search_trigger = None

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
         # Label de status
        self.label = Label(
            text="Carregando...",
            size_hint_y=None,
            height=40,
            color=(0.1, 0.2, 0.6, 1)
        )
        layout.add_widget(self.label)
      
        # Botão autenticação Google
        self.auth_btn = Button(
            text="Autenticar Google",
            size_hint_y=None,
            height=50,
            background_color=(0.10, 0.46, 0.82, 1),
            color=(1, 1, 1, 1)
        )
        self.auth_btn.bind(on_press=self.auth_google)
        layout.add_widget(self.auth_btn)

        # Linha de busca
        busca_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)

        self.search_input = TextInput(
            hint_text="Buscar reuniões (título, descrição, organizador)...",
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.2, 0.6, 1),
            cursor_color=(0.1, 0.2, 0.6, 1)
        )
        self.search_input.bind(text=self.on_search_text)
        busca_layout.add_widget(self.search_input)

        # Campo data início
        self.data_inicio_input = TextInput(
            hint_text="Data início (dd/mm/aaaa)",
            size_hint_x=0.3,
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.2, 0.6, 1),
        )
        self.data_inicio_input.bind(text=self.on_search_text)
        busca_layout.add_widget(self.data_inicio_input)

        # Campo data fim
        self.data_fim_input = TextInput(
            hint_text="Data fim (dd/mm/aaaa)",
            size_hint_x=0.3,
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.2, 0.6, 1),
        )
        self.data_fim_input.bind(text=self.on_search_text)
        busca_layout.add_widget(self.data_fim_input)

        layout.add_widget(busca_layout)

        # Scroll e grid
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        # Paginação
        pag_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        self.btn_anterior = Button(text="◀ Anterior", size_hint_x=0.2)
        self.pagina_label = Label(text="Página 1 de 1", size_hint_x=0.6, color=(0, 0, 0, 1))
        self.btn_proximo = Button(text="Próxima ▶", size_hint_x=0.2)
        self.btn_anterior.bind(on_release=self.pagina_anterior)
        self.btn_proximo.bind(on_release=self.pagina_proxima)
        pag_layout.add_widget(self.btn_anterior)
        pag_layout.add_widget(self.pagina_label)
        pag_layout.add_widget(self.btn_proximo)
        layout.add_widget(pag_layout)

               # --- Botão de Voltar para Login ---
        btn_voltar = Button(
            text="⟵ Voltar para Login",
            size_hint_y=None,
            height=40,
            background_color=(0.8, 0.1, 0.1, 1),  # vermelho claro
            color=(1, 1, 1, 1)
        )
        btn_voltar.bind(on_press=self.voltar_login)
        layout.add_widget(btn_voltar)
        # -----------------------------------

       


        self.add_widget(layout)

    def _update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

       

    # ----------------------------
    # Autenticação Google
    # ----------------------------
    def auth_google(self, instance):
        self.label.text = "Abrindo navegador para autenticação..."
        iniciar_oauth_kivy(self.on_oauth_result)

    def on_oauth_result(self, creds, error):
        if error:
            self.label.text = f"Erro na autenticação: {error}"
            return
        salvar_token_google(self.manager.usuario_logado.id, creds)
        self.manager.creds = creds
        self.label.text = "Google autenticado com sucesso!"
        self.carregar_reunioes()

    # ----------------------------
    # Carregar reuniões
    # ----------------------------
    def carregar_reunioes(self):
        if not hasattr(self.manager, "creds") or not self.manager.creds:
            self.label.text = "Autentique-se para carregar reuniões."
            return
        threading.Thread(target=self._carregar_reunioes_thread, daemon=True).start()

    def _carregar_reunioes_thread(self):
        try:
            events = listar_reunioes(self.manager.creds)
            self.todos_eventos = events if events else []
            self.eventos_filtrados = self.todos_eventos[:]
            self.pagina_atual = 0
            self.atualizar_reunioes()
            self.label.text = f"{len(self.todos_eventos)} reuniões carregadas."
        except Exception as e:
            self.label.text = f"Erro ao carregar reuniões: {e}"
            self.todos_eventos = []
            self.eventos_filtrados = []
            self.atualizar_reunioes()

    # ----------------------------
    # Filtro de reuniões
    # ----------------------------
    def on_search_text(self, instance, value):
        if self._search_trigger:
            self._search_trigger.cancel()
        self._search_trigger = Clock.schedule_once(lambda dt: self.filtrar_eventos(), 0.3)

    def filtrar_eventos(self):
        termo = (self.search_input.text or "").lower().strip()
        data_inicio_txt = (self.data_inicio_input.text or "").strip()
        data_fim_txt = (self.data_fim_input.text or "").strip()

        def parse_data_br(txt):
            try:
                return datetime.strptime(txt, "%d/%m/%Y").date()
            except Exception:
                return None

        data_inicio = parse_data_br(data_inicio_txt)
        data_fim = parse_data_br(data_fim_txt)

        filtrados = []
        for e in self.todos_eventos:
            summary = (e.get('summary') or "").lower()
            description = (e.get('description') or "").lower()
            organizer = (e.get('organizer', {}).get('email') or "").lower()

            start_obj = e.get('start', {})
            start_str = start_obj.get('dateTime') or start_obj.get('date') or ""
            data_evento_date = None
            if start_str:
                try:
                    data_evento_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
                except Exception:
                    pass

            cond_texto = not termo or (termo in summary or termo in description or termo in organizer)
            cond_data = True
            if data_inicio and data_fim and data_evento_date:
                cond_data = data_inicio <= data_evento_date <= data_fim
            elif data_inicio and data_evento_date:
                cond_data = data_evento_date >= data_inicio
            elif data_fim and data_evento_date:
                cond_data = data_evento_date <= data_fim
            elif (data_inicio or data_fim) and not data_evento_date:
                cond_data = False

            if cond_texto and cond_data:
                filtrados.append(e)

        self.eventos_filtrados = filtrados
        self.pagina_atual = 0
        self.atualizar_reunioes()

    # ----------------------------
    # Atualizar interface
    # ----------------------------
    @mainthread
    def atualizar_reunioes(self):
        self.grid.clear_widgets()
        total = len(self.eventos_filtrados)
        total_paginas = max(1, (total + self.itens_por_pagina - 1) // self.itens_por_pagina)
        inicio = self.pagina_atual * self.itens_por_pagina
        fim = inicio + self.itens_por_pagina
        pagina_eventos = self.eventos_filtrados[inicio:fim]

        for e in pagina_eventos:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
            start_str = e.get('start', {}).get('dateTime') or e.get('start', {}).get('date') or ""
            data_mostrada = ""
            if start_str:
                try:
                    data_mostrada = datetime.strptime(start_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    data_mostrada = start_str

            title_text = f"{e.get('summary', 'Sem título')} — {data_mostrada}"
            label = Label(text=title_text, size_hint_x=0.4, color=(0, 0, 0, 1))
            box.add_widget(label)

            status_label = Label(text="", size_hint_x=0.2, color=(0, 0, 0, 1))
            box.add_widget(status_label)

            gerar_btn = Button(text="Gerar ATA", size_hint_x=0.15)
            resumo_btn = Button(text="Resumo ATA", size_hint_x=0.15, disabled=True)
            download_btn = Button(text="Baixar DOCX", size_hint_x=0.15, disabled=True)

            def abrir_docx(inst):
                path = getattr(inst, 'docx_path', None)
                if path and os.path.exists(path):
                    import subprocess, sys
                    try:
                        if sys.platform == "win32":
                            os.startfile(path)
                        elif sys.platform == "darwin":
                            subprocess.run(["open", path])
                        else:
                            subprocess.run(["xdg-open", path])
                    except Exception as ex:
                        print(f"Erro ao abrir arquivo: {ex}")

            download_btn.bind(on_release=abrir_docx)

            gerar_btn.bind(
                on_release=lambda inst, ev=e, lbl=status_label, d_btn=download_btn, r_btn=resumo_btn:
                self.gerar_ata(ev, lbl, d_btn, r_btn)
            )
            resumo_btn.bind(on_release=lambda inst, ev=e: self.mostrar_resumo_ata(ev))

            box.add_widget(gerar_btn)
            box.add_widget(resumo_btn)
            box.add_widget(download_btn)
            self.grid.add_widget(box)

        self.pagina_label.text = f"Página {self.pagina_atual + 1} de {total_paginas}"
        self.btn_anterior.disabled = self.pagina_atual == 0
        self.btn_proximo.disabled = self.pagina_atual >= (total_paginas - 1)

    # ----------------------------
    # Paginação
    # ----------------------------
    def pagina_anterior(self, instance):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self.atualizar_reunioes()

    def pagina_proxima(self, instance):
        total_paginas = max(1, (len(self.eventos_filtrados) + self.itens_por_pagina - 1) // self.itens_por_pagina)
        if self.pagina_atual < (total_paginas - 1):
            self.pagina_atual += 1
            self.atualizar_reunioes()

    # ----------------------------
    # Gerar ATA (Whisper)
    # ----------------------------
    def gerar_ata(self, event, status_label, download_btn, resumo_btn):
        if not hasattr(self.manager, "usuario_logado") or not self.manager.usuario_logado:
            status_label.text = "Usuário não logado"
            return

        @mainthread
        def callback(event_id, docx_path=None):
            status = ata_status.get(event_id, {})
            status_label.text = status.get("mensagem", "")
            if status.get("ready") and docx_path:
                download_btn.disabled = False
                resumo_btn.disabled = False
                download_btn.docx_path = docx_path

        status_label.text = "Processando..."
        download_btn.disabled = True
        resumo_btn.disabled = True
        download_btn.docx_path = None

        threading.Thread(
            target=processar_ata,
            args=(event, self.manager.creds, self.manager.usuario_logado.email, callback),
            daemon=True
        ).start()

    # ----------------------------
    # Resumo da ATA (popup)
    # ----------------------------
    def mostrar_resumo_ata(self, event):
        event_id = event.get("id")
        resumo = ata_status.get(event_id, {}).get("resumo", "Resumo ainda não disponível.")

        label = Label(
            text=resumo,
            color=(1, 1, 1, 1),
            halign="left",
            valign="top",
            text_size=(500, None)
        )
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(label)

        popup = Popup(
            title="Resumo da ATA",
            content=scroll,
            size_hint=(0.8, 0.8),
            auto_dismiss=True
        )
        popup.open()

    def voltar_login(self, instance):
        if self.manager:
            self.manager.current = "login"
