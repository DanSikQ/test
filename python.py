import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from bs4 import BeautifulSoup
import psycopg2

DB_CONFIG = {'host': 'localhost',
             'port': '5433',
             'database': 'hh_test',
             'user': 'postgres',
             'password': '123'}



def parser(pathway):
    data = []

    with open(pathway, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    for i, load_vac in enumerate(soup.find_all(class_ = 'resume-card-content--pA9euQ2yPckXrBh1')):

        main_info = load_vac.find(class_ = 'column-content--q3SfppwQANVUv38P')

        url_find = main_info.find('a')['href']
        info_about_time_to_be = main_info.find(class_ = 'magritte-text___pbpft_4-1-1 magritte-text_style-secondary___1IU11_4-1-1 magritte-text_typography-label-3-regular___Nhtlp_4-1-1')
        
        a = info_about_time_to_be.find(string = lambda t: 'Был' in t)
        if a:
            date = a.find_next('span').text
            full_text = a + ' ' + date
        else:
            full_text = None
        
        data.append((url_find, full_text))

    return data

def load_db(data):
    try: 
        with psycopg2.connect(**DB_CONFIG) as connect:
            with connect.cursor() as cur:

                cur.execute('''CREATE TABLE IF NOT EXISTS info_res (
                        id SERIAL PRIMARY KEY,
                        full_url TEXT,
                        visit_time TEXT)''')
                cur.executemany('INSERT INTO info_res (full_url, visit_time) VALUES (%s, %s)', data)
                connect.commit()

            return True
        
    except Exception as e:
        print(f'Ошибка {e}')
        return False



def create_file_loader():
    # Создаем главное окно
    root = tk.Tk()
    root.title("Парсер вакансий HH")
    root.geometry("500x300")
    root.configure(bg='#f0f0f0')

    # Стилизация
    bold_font = Font(family="Arial", size=8, weight="bold")
    normal_font = Font(family="Arial", size=7)

    # Фрейм для основной области
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Заголовок
    ttk.Label(
        main_frame,
        text="Загрузчик HTML файлов",
        font=Font(family="Arial", size=12, weight="bold"),
        foreground="#333"
    ).pack(pady=(0, 20))

    # Фрейм для выбора файла
    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill=tk.X, pady=10)

    # Поле для отображения пути
    file_path_var = tk.StringVar()
    file_entry = ttk.Entry(
        file_frame,
        textvariable=file_path_var,
        font=normal_font,
        width=40,
        state='readonly'
    )
    file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    # Стильная кнопка Browse
    browse_btn = ttk.Button(
        file_frame,
        text="Browse",
        command=lambda: select_file(file_path_var),
        style='Accent.TButton',
        width=10,
        
    )
    browse_btn.pack(side=tk.RIGHT)

    # Статус бар
    status_var = tk.StringVar()
    status_bar = ttk.Label(
        main_frame,
        textvariable=status_var,
        relief=tk.SUNKEN,
        anchor=tk.W,
        font=normal_font
    )
    status_bar.pack(fill=tk.X, pady=(20, 0))

    # Настраиваем стиль для акцентной кнопки
    style = ttk.Style()
    style.configure('Accent.TButton', font=bold_font, foreground='black', background="#000000")

    return root, file_path_var, status_var

def select_file(file_path_var):
    """Функция выбора файла"""
    filetypes = (
        ('HTML files', '*.html'),
        ('All files', '*.*')
    )
    
    filename = filedialog.askopenfilename(
        title='Выберите файл',
        initialdir='/',
        filetypes=filetypes
    )
    
    if filename:
        file_path_var.set(filename)
        status_var.set(f"Выбран файл: {filename}")
    else:
        status_var.set("Файл не выбран")

def load_all(file_path_var):
    try:
        data = parser(file_path_var)
        if load_db(data):
            status_var.set(f"Успешно! Загружено {len(data)} записей")
        else:
            status_var.set("Ошибка при сохранении в БД")
    except Exception as e:
        status_var.set(f"Ошибка: {str(e)}")

# Создаем интерфейс
root, file_path_var, status_var = create_file_loader()

# Кнопка для обработки (пример)
process_btn = ttk.Button(
    root,
    text="Обработать файл",
    command = lambda: load_all(file_path_var.get()),
    style='Accent.TButton',
    width=10
)
process_btn.pack(pady=20)

# Запускаем приложение
root.mainloop()