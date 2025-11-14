from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from controllers.controllers_usuario import login_user, buscar_senha_por_email


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fundo branco
        Window.clearcolor = (1, 1, 1, 1)

        # Layout principal (vertical)
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # --- TOPO: Logotipo ---
        try:
            logo = Image(
                source='assets/logo_luft.png',  # coloque a imagem nesta pasta
                size_hint=(1, 0.10),
                allow_stretch=True,
                keep_ratio=True
            )
            main_layout.add_widget(logo)
        except Exception as e:
            print("Erro ao carregar logo:", e)

        # --- CENTRO: Área do formulário ---
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.size_hint = (0.7, 0.6)
        layout.pos_hint = {'center_x': 0.5}

        # Títulos
        titulo = Label(
            text="Gerador de Atas Google Meet",
            font_size=32,
            color=(0, 0, 1, 1),
            size_hint_y=None,
            height=50
        )
        subtitulo = Label(
            text="Inovadores da Luft",
            font_size=18,
            color=(0, 0, 0.6, 1),
            size_hint_y=None,
            height=30
        )

        layout.add_widget(titulo)
        layout.add_widget(subtitulo)

        # Campos de entrada
        self.email = TextInput(
            hint_text="Email",
            multiline=False,
            size_hint_y=None,
            height=40,
            foreground_color=(0, 0, 0, 1),
            background_color=(0.9, 0.9, 1, 1)
        )
        self.senha = TextInput(
            hint_text="Senha",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40,
            foreground_color=(0, 0, 0, 1),
            background_color=(0.9, 0.9, 1, 1)
        )

        layout.add_widget(self.email)
        layout.add_widget(self.senha)

        # Botão Login
        btn_login = Button(
            text="Entrar",
            size_hint_y=None,
            height=50,
            background_color=(0, 0, 1, 1),
            color=(1, 1, 1, 1)
        )
        btn_login.bind(on_press=self.fazer_login)
        layout.add_widget(btn_login)

        # Botão Cadastro
        btn_cadastro = Button(
            text="Cadastrar",
            size_hint_y=None,
            height=40,
            background_color=(0, 0, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        btn_cadastro.bind(on_press=self.ir_cadastro)
        layout.add_widget(btn_cadastro)

        # Botão Recuperar Senha
        btn_recuperar = Button(
            text="Recuperar Senha",
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.2, 1, 1),
            color=(1, 1, 1, 1)
        )
        btn_recuperar.bind(on_press=self.abrir_popup_recuperar)
        layout.add_widget(btn_recuperar)

        # Adiciona o layout principal
        main_layout.add_widget(layout)

        # --- RODAPÉ ---
        rodape = Label(
            text="Autor: [b]Leonardo Batista[/b] - Analista em Suporte - Luft Healthcare",
            markup=True,
            font_size=14,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(rodape)

        self.add_widget(main_layout)

    # ---------------------------------------------------------------
    # Funções de controle
    # ---------------------------------------------------------------
    def fazer_login(self, instance):
        user = login_user(self.email.text, self.senha.text)
        if user:
            self.manager.usuario_logado = user
            self.manager.current = 'main'
        else:
            popup = Popup(
                title="Erro",
                content=Label(text="Email ou senha inválidos."),
                size_hint=(0.6, 0.4)
            )
            popup.open()

    def ir_cadastro(self, instance):
        self.manager.current = 'cadastro'

    def abrir_popup_recuperar(self, instance):
        """Abre popup para recuperar senha pelo email"""
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)

        email_input = TextInput(hint_text="Digite seu email", multiline=False, size_hint_y=None, height=40)
        status_label = Label(text="", color=(0, 0, 0, 1))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        ok_btn = Button(text="OK", background_color=(0, 0, 1, 1), color=(1, 1, 1, 1))
        cancelar_btn = Button(text="Cancelar", background_color=(0.5, 0.5, 0.5, 1), color=(1, 1, 1, 1))

        box.add_widget(Label(text="Recuperar Senha", color=(1, 1, 1, 1)))
        box.add_widget(email_input)
        box.add_widget(status_label)
        box.add_widget(btns)

        popup = Popup(title="Recuperar Senha", content=box, size_hint=(0.8, 0.5))

        def confirmar(instance):
            email = email_input.text.strip()
            if not email:
                status_label.text = "Informe um email!"
                return
            senha = buscar_senha_por_email(email)
            if senha:
                status_label.text = f"Sua senha é: {senha}"
            else:
                status_label.text = "Email não encontrado."

        ok_btn.bind(on_press=confirmar)
        cancelar_btn.bind(on_press=lambda x: popup.dismiss())
        btns.add_widget(ok_btn)
        btns.add_widget(cancelar_btn)

        popup.open()
