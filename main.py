from kivy.app import App
from kivy.core.window import Window
from ui import LivrosFeraApp

class MainApp(App):
    def build(self):
        Window.size = (360, 640)  # Resolução padrão de celular
        return LivrosFeraApp()

if __name__ == "__main__":
    MainApp().run()
