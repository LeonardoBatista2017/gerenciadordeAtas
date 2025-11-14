# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from views.login_screen import LoginScreen
from views.cadastro_screen import CadastroScreen
from views.main_screen import MainScreen

class AtaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.usuario_logado = None
        sm.creds = None
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CadastroScreen(name='cadastro'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    AtaApp().run()