import sqlite3

def connect():
    conn = sqlite3.connect("livrosfera.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        genre TEXT NOT NULL,
                        total_pages INTEGER NOT NULL,
                        pages_read INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

def add_book(title, author, genre, total_pages, pages_read):
    conn = sqlite3.connect("livrosfera.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, genre, total_pages, pages_read) VALUES (?, ?, ?, ?, ?)",
                   (title, author, genre, total_pages, pages_read))
    conn.commit()
    conn.close()

def get_books():
    conn = sqlite3.connect("livrosfera.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def remove_book(book_id):
    conn = sqlite3.connect("livrosfera.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

def update_book(book_id, title=None, author=None, genre=None, total_pages=None, pages_read=None):
    conn = sqlite3.connect("livrosfera.db")
    cursor = conn.cursor()
    if title is not None:
        cursor.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
    if author is not None:
        cursor.execute("UPDATE books SET author = ? WHERE id = ?", (author, book_id))
    if genre is not None:
        cursor.execute("UPDATE books SET genre = ? WHERE id = ?", (genre, book_id))
    if total_pages is not None:
        cursor.execute("UPDATE books SET total_pages = ? WHERE id = ?", (total_pages, book_id))
    if pages_read is not None:
        cursor.execute("UPDATE books SET pages_read = ? WHERE id = ?", (pages_read, book_id))
    conn.commit()
    conn.close()
