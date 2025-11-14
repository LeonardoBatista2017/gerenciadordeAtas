from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
import os

from controllers.controllers_usuario import cadastrar_usuario

class CadastroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ── Fundo branco ─────────────
        with self.canvas.before:
            Color(1, 1, 1, 1)  # branco
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text="Cadastro", color=(0,0,1,1), font_size=22, bold=True))  # título azul

        self.nome_input = TextInput(hint_text='Nome', multiline=False)
        layout.add_widget(self.nome_input)

        self.email_input = TextInput(hint_text='Email', multiline=False)
        layout.add_widget(self.email_input)

        self.senha_input = TextInput(hint_text='Senha', password=True, multiline=False)
        layout.add_widget(self.senha_input)

        self.status_label = Label(text="Nenhum arquivo selecionado.", color=(0,0,0,1))  # texto preto
        layout.add_widget(self.status_label)

        selecionar_btn = Button(
            text='Selecionar credentials.json',
            background_color=(0,0,1,1),   # azul
            color=(1,1,1,1)               # texto branco
        )
        selecionar_btn.bind(on_press=self.abrir_seletor_arquivo)
        layout.add_widget(selecionar_btn)

        cadastrar_btn = Button(
            text='Cadastrar',
            background_color=(0,0,0.8,1),
            color=(1,1,1,1)
        )
        cadastrar_btn.bind(on_press=self.cadastrar)
        layout.add_widget(cadastrar_btn)

        voltar_btn = Button(
            text='Voltar para Login',
            background_color=(0.2,0.2,1,1),
            color=(1,1,1,1)
        )
        voltar_btn.bind(on_press=self.ir_para_login)
        layout.add_widget(voltar_btn)

        self.add_widget(layout)

        self.selected_file = None
        self.popup = None

    def _update_bg(self, *args):
        """Atualiza o fundo ao redimensionar a tela"""
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def abrir_seletor_arquivo(self, instance):
        filechooser = FileChooserListView(filters=['*.json'])
        filechooser.size_hint = (1, 1)
        filechooser.bind(selection=self.on_file_selected)

        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.add_widget(filechooser)

        self.popup = Popup(title="Selecione o arquivo credentials.json",
                      content=scrollview,
                      size_hint=(0.9, 0.9))
        self.popup.open()

    def on_file_selected(self, instance, value):
        if value and len(value) > 0:
            self.selected_file = value[0]
            self.status_label.text = f"Arquivo selecionado: {os.path.basename(self.selected_file)}"
            if self.popup:
                self.popup.dismiss()
        else:
            self.selected_file = None
            self.status_label.text = "Nenhum arquivo selecionado."

    def cadastrar(self, instance):
        nome = self.nome_input.text.strip()
        email = self.email_input.text.strip()
        senha = self.senha_input.text.strip()

        if not nome or not email or not senha or not self.selected_file:
            self.status_label.text = "Todos os campos são obrigatórios, incluindo o arquivo credentials.json."
            return

        user = cadastrar_usuario(nome, email, senha, self.selected_file)
        if user:
            self.status_label.text = "Cadastro realizado com sucesso!"
            self.manager.current = 'login'
        else:
            self.status_label.text = "Erro ao cadastrar usuário."

    def ir_para_login(self, instance):
        self.manager.current = 'login'
