from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex
from database import connect, add_book, get_books, remove_book, update_book
import os

class ImageButton(ButtonBehavior, Image):
    pass

class LivrosFeraApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        connect()

        self.search_input = TextInput(
            size_hint_y=None, height=40, hint_text="Pesquisar livro, autor ou gênero...",
            background_color="#222222", foreground_color="#ffffff", cursor_color="#ffffff"
        )
        self.search_input.bind(text=self.update_books_from_search)
        self.add_widget(self.search_input)

        self.scroll = ScrollView()
        self.books_layout = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        self.books_layout.bind(minimum_height=self.books_layout.setter('height'))
        self.scroll.add_widget(self.books_layout)
        self.add_widget(self.scroll)

        add_button = Button(
            text="Adicionar Livro", size_hint_y=None, height=50,
            background_color="#333333", color="#ffffff"
        )
        add_button.bind(on_press=self.open_add_popup)
        self.add_widget(add_button)

        self.load_books()

    def open_add_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        title_input = TextInput(hint_text="Nome")
        author_input = TextInput(hint_text="Autor")
        genre_input = TextInput(hint_text="Gênero")
        total_pages_input = TextInput(hint_text="Páginas Totais", input_filter='int')
        pages_read_input = TextInput(hint_text="Páginas Lidas (opcional)", input_filter='int')

        popup_layout.add_widget(title_input)
        popup_layout.add_widget(author_input)
        popup_layout.add_widget(genre_input)
        popup_layout.add_widget(total_pages_input)
        popup_layout.add_widget(pages_read_input)

        save_button = Button(text="Salvar")
        popup = Popup(title="Adicionar Livro", content=popup_layout, size_hint=(0.9, 0.9))
        save_button.bind(on_press=lambda x: self.save_book(popup, title_input.text, author_input.text,
                                                            genre_input.text, total_pages_input.text,
                                                            pages_read_input.text))
        popup_layout.add_widget(save_button)
        popup.open()

    def save_book(self, popup, title, author, genre, total_pages, pages_read):
        if not (title and author and genre and total_pages.isdigit()):
            return

        total_pages = int(total_pages)
        pages_read = int(pages_read) if pages_read.isdigit() else 0
        pages_read = min(pages_read, total_pages)

        add_book(title, author, genre, total_pages, pages_read)
        popup.dismiss()
        self.load_books()

    def load_books(self, query=""):
        self.books_layout.clear_widgets()
        books = get_books()

        if query:
            query = query.lower()
            books = [book for book in books if
                     query in book[1].lower() or query in book[2].lower() or query in book[3].lower()]
            books.sort(key=lambda b: b[1].lower())

        for book in books:
            title, author, genre, total, lidas = book[1], book[2], book[3], book[4], book[5]
            perc_lidas = (lidas / total) * 100 if total > 0 else 0
            btn = Button(
                text=f"{title} ({perc_lidas:.2f}% lido)",
                size_hint_y=None,
                height=60,
                background_color="#444444",
                color="#ffffff",
                on_press=lambda instance, b=book: self.show_book_details(b)
            )
            self.books_layout.add_widget(btn)

    def update_books_from_search(self, instance, value):
        self.load_books(query=value)

    def show_book_details(self, book):
        book_id, title, author, genre, total, lidas = book
        perc_lidas = (lidas / total) * 100 if total > 0 else 0
        perc_restante = 100 - perc_lidas

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        def create_row(label_text, value_text, edit_callback):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            row.add_widget(Label(text=f"{label_text}: {value_text}", size_hint_x=0.85))
            edit_icon = ImageButton(source=os.path.join("resources", "edit.png"), size_hint_x=0.15)
            edit_icon.bind(on_press=edit_callback)
            row.add_widget(edit_icon)
            return row

        content.add_widget(create_row("Título", title, lambda x: self.edit_field("Título", title, lambda new_val: update_book(book_id, title=new_val), self.load_books)))
        content.add_widget(create_row("Autor", author, lambda x: self.edit_field("Autor", author, lambda new_val: update_book(book_id, author=new_val), self.load_books)))
        content.add_widget(create_row("Gênero", genre, lambda x: self.edit_field("Gênero", genre, lambda new_val: update_book(book_id, genre=new_val), self.load_books)))
        content.add_widget(create_row("Páginas", f"{lidas}/{total}", lambda x: self.edit_pages(book_id, total, lidas)))

        content.add_widget(Label(text=f"Lido: {perc_lidas:.2f}%"))
        content.add_widget(Label(text=f"Restante: {perc_restante:.2f}%"))

        remove_button = Button(text="Remover Livro", background_color="#aa3333", color="#ffffff", size_hint_y=None, height=40)
        close_button = Button(text="Fechar", background_color="#333333", color="#ffffff", size_hint_y=None, height=40)

        remove_button.bind(on_press=lambda x: (remove_book(book_id), popup.dismiss(), self.load_books()))
        close_button.bind(on_press=lambda x: popup.dismiss())

        content.add_widget(remove_button)
        content.add_widget(close_button)

        popup = Popup(title="Detalhes do Livro", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def edit_field(self, title, current_value, save_callback, refresh_callback=None):
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        input_field = TextInput(text=current_value)
        popup_layout.add_widget(input_field)

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        confirm_btn = Button(text="Confirmar", background_color="#228822", color="#ffffff")
        cancel_btn = Button(text="Cancelar", background_color="#555555", color="#ffffff")

        popup_layout.add_widget(btns)
        btns.add_widget(confirm_btn)
        btns.add_widget(cancel_btn)

        popup = Popup(title=f"Editar {title}", content=popup_layout, size_hint=(0.8, 0.5))

        confirm_btn.bind(on_press=lambda x: (save_callback(input_field.text), popup.dismiss(), refresh_callback() if refresh_callback else None))
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()

    def edit_pages(self, book_id, total, lidas):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        total_input = TextInput(text=str(total), hint_text="Páginas Totais", input_filter='int')
        lidas_input = TextInput(text=str(lidas), hint_text="Páginas Lidas", input_filter='int')

        layout.add_widget(total_input)
        layout.add_widget(lidas_input)

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        confirm_btn = Button(text="Confirmar", background_color="#228822", color="#ffffff")
        cancel_btn = Button(text="Cancelar", background_color="#555555", color="#ffffff")
        btns.add_widget(confirm_btn)
        btns.add_widget(cancel_btn)

        layout.add_widget(btns)

        popup = Popup(title="Editar Páginas", content=layout, size_hint=(0.8, 0.6))

        def confirmar(_):
            if not total_input.text.isdigit():
                return
            new_total = int(total_input.text)
            new_lidas = int(lidas_input.text) if lidas_input.text.isdigit() else 0
            new_lidas = min(new_lidas, new_total)
            update_book(book_id, total_pages=new_total, pages_read=new_lidas)
            popup.dismiss()
            self.load_books()

        confirm_btn.bind(on_press=confirmar)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()
