import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import time
import shutil

class FileExplorer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Файловый менеджер")
        self.geometry("1000x600")

        # История для кнопок "Назад" и "Вперед"
        self.history = []
        self.history_index = -1

        # Навигационная панель для выбора дисков и папок
        self.nav_tree = ttk.Treeview(self, columns=("Name"), show="tree")
        self.nav_tree.heading("#0", text="Диски и Папки")
        self.nav_tree.column("#0", width=50)
        self.nav_tree.pack(side="left", fill="y")

        # Добавление дисков в навигационную панель
        self.load_drives()

        # Панель выбора директории
        self.path_label = tk.Label(self, text="Текущий каталог:")
        self.path_label.pack(anchor="nw", padx=10, pady=5)

        self.path_entry = tk.Entry(self, width=80)
        self.path_entry.pack(anchor="nw", padx=10, pady=5)
        self.path_entry.insert(0, os.getcwd())

        # Событие нажатия Enter для открытия директории
        self.path_entry.bind("<Return>", self.on_path_entry_enter)

        # Кнопки для навигации и управления файлами
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(anchor="nw", padx=10, pady=5)

        self.back_button = tk.Button(self.nav_frame, text="Назад", command=self.go_back)
        self.back_button.pack(side="left")

        self.forward_button = tk.Button(self.nav_frame, text="Вперед", command=self.go_forward)
        self.forward_button.pack(side="left")

        self.refresh_button = tk.Button(self.nav_frame, text="Обновить", command=self.refresh_directory)
        self.refresh_button.pack(side="left")

        self.create_button = tk.Button(self.nav_frame, text="Создать файл", command=self.create_file)
        self.create_button.pack(side="left")

        self.delete_button = tk.Button(self.nav_frame, text="Удалить файл", command=self.delete_file)
        self.delete_button.pack(side="left")

        self.properties_button = tk.Button(self.nav_frame, text="Свойства файла", command=self.show_properties)
        self.properties_button.pack(side="left")

        # Древовидная структура файлов и папок
        self.tree = ttk.Treeview(self, columns=("Name", "Size", "Type", "Modified"), show="headings")
        self.tree.heading("Name", text="Название файла")
        self.tree.heading("Size", text="Размер файла")
        self.tree.heading("Type", text="Тип файла")
        self.tree.heading("Modified", text="Дата изменения")

        self.tree.column("Name", width=300, anchor="w")
        self.tree.column("Size", width=100, anchor="e")
        self.tree.column("Type", width=100, anchor="center")
        self.tree.column("Modified", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Заполнение содержимого текущей директории
        self.load_directory(os.getcwd())

        # Обработка двойного щелчка для открытия папок/файлов и нажатия на элементы навигации
        self.tree.bind("<Double-1>", self.on_double_click)
        self.nav_tree.bind("<<TreeviewSelect>>", self.on_nav_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Контекстное меню
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Создать файл", command=self.create_file)
        self.context_menu.add_command(label="Удалить файл", command=self.delete_file)
        self.context_menu.add_command(label="Свойства файла", command=self.show_properties)

    def load_drives(self):
        """Загрузка доступных дисков"""
        if os.name == 'nt':  # Windows
            for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive_path = f"{drive}:\\"
                if os.path.exists(drive_path):
                    # Добавляем диск в дерево как узел без дочерних элементов
                    self.nav_tree.insert("", "end", drive_path, text=drive_path)
        else:  # macOS, Linux
            self.nav_tree.insert("", "end", "/", text="/")
            for folder in os.listdir("/"):
                folder_path = os.path.join("/", folder)
                if os.path.isdir(folder_path):
                    self.nav_tree.insert("/", "end", folder_path, text=folder, values=(folder_path))

    def load_directory(self, path):
        """Загрузка файлов и папок из указанного пути"""
        self.tree.delete(*self.tree.get_children())  # Очистка дерева
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

        # Обновляем историю
        if not (self.history and self.history[self.history_index] == path):
            self.history = self.history[:self.history_index + 1]
            self.history.append(path)
            self.history_index += 1

        if not os.path.isdir(path):
            return

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    item_type = "Folder"
                    item_size = ""
                else:
                    item_type = os.path.splitext(item)[1][1:].upper() or "File"  # Отображаем расширение в верхнем регистре
                    item_size = f"{os.path.getsize(item_path)} bytes"
                item_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(item_path)))

                # Добавление в древовидную структуру
                self.tree.insert("", "end", values=(item, item_size, item_type, item_mtime), iid=item_path)
        except Exception:
            pass  # Пропускаем ошибки

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_directory(self.history[self.history_index])

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_directory(self.history[self.history_index])

    def refresh_directory(self):
        """Перезагрузка текущей директории"""
        current_path = self.path_entry.get()
        self.load_directory(current_path)

    def on_path_entry_enter(self, event):
        """Обработка нажатия Enter в поле пути для перехода к указанной директории"""
        path = self.path_entry.get()
        if os.path.isdir(path):
            self.load_directory(path)
        else:
            messagebox.showerror("Ошибка", f"Каталог '{path}' не существует.")

    def on_double_click(self, event):
        """Обработка двойного щелчка для открытия папок или открытия файлов"""
        selected_item = self.tree.selection()
        if selected_item:
            item_path = selected_item[0]
            if os.path.isdir(item_path):
                self.load_directory(item_path)
            else:
                self.open_file(item_path)

    def on_nav_select(self, event):
        """Обработка выбора элемента в навигационной панели"""
        selected_item = self.nav_tree.selection()
        if selected_item:
            folder_path = selected_item[0]
            if os.path.isdir(folder_path):
                self.load_directory(folder_path)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        self.context_menu.post(event.x_root, event.y_root)

    def open_file(self, file_path):
        """Открытие файла с помощью системного приложения"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS, Linux
                os.system(f'open "{file_path}"' if sys.platform == 'darwin' else f'xdg-open "{file_path}"')
        except Exception:
            pass

    def create_file(self):
        """Создание нового текстового файла"""
        new_file = filedialog.asksaveasfilename(title="Создать файл", defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if new_file:
            with open(new_file, "w") as f:
                f.write("")

            self.load_directory(self.path_entry.get())

    def delete_file(self):
        """Удаление выбранного файла в корзину"""
        selected_item = self.tree.selection()
        if selected_item:
            file_path = selected_item[0]
            try:
                if os.name == 'nt':  # Windows
                    import send2trash
                    send2trash.send2trash(file_path)
                else:
                    shutil.move(file_path, os.path.expanduser("~/.local/share/Trash/files/"))
                self.load_directory(self.path_entry.get())
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить файл: {e}")

    def show_properties(self):
        """Показать свойства файла"""
        selected_item = self.tree.selection()
        if selected_item:
            file_path = selected_item[0]
            try:
                file_info = os.stat(file_path)
                file_size = f"{file_info.st_size} bytes"
                modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_info.st_mtime))
                properties_message = f"Путь: {file_path}\nРазмер: {file_size}\nДата изменения: {modified_time}"
                messagebox.showinfo("Свойства файла", properties_message)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось получить свойства файла: {e}")

if __name__ == "__main__":
    app = FileExplorer()
    app.mainloop()
