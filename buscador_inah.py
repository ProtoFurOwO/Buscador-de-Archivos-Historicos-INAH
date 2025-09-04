import os
import sqlite3
import subprocess
import threading
from tkinter import Tk, Label, Entry, Button, Frame, Scrollbar, Toplevel, messagebox, filedialog
from tkinter.ttk import Treeview, Style

# --- Configuración de Base de Datos ---
DB_NAME = "inah_documentos.db"

# --- Funciones de Lógica y Base de Datos ---

def crear_tabla_si_no_existe():
    """
    Se conecta a la base de datos y crea la tabla 'documentos' 
    si esta no existe previamente.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_documento TEXT NOT NULL,
            nombre_edificio TEXT NOT NULL,
            nombre_municipio TEXT NOT NULL,
            ruta_completa TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'documentos' verificada/creada.")

def indexar_archivos_background(app_instance, ruta_base):
    """
    Recorre un directorio base, extrae metadatos de las rutas de los archivos PDF
    y los inserta en la base de datos. Se ejecuta en un hilo secundario para no
    bloquear la interfaz de usuario.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("DELETE FROM documentos")
    conn.commit()
    
    documentos_a_insertar = []
    archivos_procesados = 0

    app_instance.status_label.config(text=f"Iniciando indexación desde: {ruta_base}. Esto puede tardar...", fg="#ffcc00")
    app_instance.update_idletasks()

    try:
        for root, dirs, files in os.walk(ruta_base):
            try:
                relative_path = os.path.relpath(root, ruta_base)
                path_components = relative_path.split(os.sep)
                
                nombre_municipio = "Desconocido"
                nombre_edificio = "Desconocido"

                if len(path_components) >= 2 and path_components[-1] != '' and path_components[-2] != '':
                    nombre_edificio = path_components[-1]
                    nombre_municipio = path_components[-2]
                elif len(path_components) == 1 and path_components[0] != '.':
                    nombre_municipio = path_components[0]
                    nombre_edificio = "N/A"
                else:
                    nombre_edificio = os.path.basename(root)
                    nombre_municipio = "Desconocido"
            
            except Exception as e:
                print(f"Error al parsear ruta: {root}. Error: {e}")
                parts = root.split(os.sep)
                if len(parts) >= 2:
                    nombre_edificio = parts[-1]
                    nombre_municipio = parts[-2]
                else:
                    nombre_municipio = "Desconocido"
                    nombre_edificio = "Desconocido"

            for file in files:
                if file.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(root, file)
                    documentos_a_insertar.append((file, nombre_edificio, nombre_municipio, ruta_completa))
                    archivos_procesados += 1
                    if archivos_procesados % 100 == 0:
                        app_instance.status_label.config(text=f"Procesando archivo {archivos_procesados}...", fg="#add8e6")
                        app_instance.update_idletasks()
        
        c.executemany("INSERT OR REPLACE INTO documentos (nombre_documento, nombre_edificio, nombre_municipio, ruta_completa) VALUES (?, ?, ?, ?)",
                      documentos_a_insertar)
        
        conn.commit()
        conn.close()
        app_instance.status_label.config(text=f"Indexación completada. Se procesaron {archivos_procesados} documentos.", fg="#98fb98")
        messagebox.showinfo("Indexación Completa", f"Se han encontrado y registrado {archivos_procesados} documentos.")
        app_instance.search_entry.delete(0, 'end')
        app_instance.perform_search()

    except Exception as e:
        conn.close()
        app_instance.status_label.config(text="Error durante la indexación.", fg="#ff6347")
        messagebox.showerror("Error de Indexación", f"Ocurrió un error durante la indexación:\n{e}")
        print(f"Error durante la indexación: {e}")

def buscar_documentos(query):
    """
    Busca en la base de datos los documentos que coincidan con el término de búsqueda
    en el nombre del documento, edificio o municipio.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    query_lower = query.lower()

    c.execute("""
        SELECT nombre_documento, nombre_edificio, nombre_municipio, ruta_completa 
        FROM documentos 
        WHERE LOWER(nombre_documento) LIKE ? 
          OR LOWER(nombre_edificio) LIKE ? 
          OR LOWER(nombre_municipio) LIKE ?
        ORDER BY nombre_municipio, nombre_edificio, nombre_documento
    """, (f"%{query_lower}%", f"%{query_lower}%", f"%{query_lower}%"))
    
    resultados = c.fetchall()
    conn.close()
    return resultados

def abrir_pdf(ruta_pdf):
    """
    Abre un archivo PDF utilizando la aplicación predeterminada del sistema operativo.
    Es compatible con Windows, macOS y Linux.
    """
    try:
        if os.path.exists(ruta_pdf):
            if os.name == 'nt':
                os.startfile(ruta_pdf)
            elif os.uname().sysname == 'Darwin':
                subprocess.Popen(['open', ruta_pdf])
            else:
                subprocess.Popen(['xdg-open', ruta_pdf])
            print(f"Abriendo PDF: {ruta_pdf}.")
        else:
            messagebox.showerror("Error", f"El archivo no existe en la ruta:\n'{ruta_pdf}'\nPor favor, re-indexe los archivos.")
            print(f"Error: Archivo no encontrado en la ruta: {ruta_pdf}")
    except Exception as e:
        messagebox.showerror("Error", f"No se puede abrir el archivo PDF:\n'{ruta_pdf}'\nError: {e}")
        print(f"Error al intentar abrir PDF: {ruta_pdf}. Error: {e}")


# --- Clase Principal de la Aplicación ---

class AplicacionINAH(Tk):
    """
    Clase principal que encapsula toda la funcionalidad y la interfaz
    gráfica de la aplicación de búsqueda de archivos.
    """
    def __init__(self):
        super().__init__()
        self.title("Buscador de Archivos Históricos INAH")
        self.geometry("1000x700")
        self.configure(bg="#2c2c2c")
        self.root_path = ""
        self.db_name = DB_NAME
        self.sort_order = {"municipio": False, "edificio": False, "documento": False}
        
        self.configurar_estilos()
        self.crear_widgets()
        self.center_window()
        crear_tabla_si_no_existe()

    def configurar_estilos(self):
        """Configura los estilos visuales para los widgets de la aplicación."""
        style = Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#3c3c3c", 
                        foreground="#ffffff", 
                        rowheight=25, 
                        fieldbackground="#3c3c3c",
                        font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', '#5a0000')], foreground=[('selected', '#ffffff')])
        
        style.configure("Treeview.Heading", 
                        font=('Segoe UI', 11, 'bold'), 
                        background="#1a1a1a", 
                        foreground="#ffcc00")

    def center_window(self):
        """Centra la ventana principal en la pantalla del usuario."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def crear_widgets(self):
        """Crea y organiza todos los componentes de la interfaz gráfica."""
        main_frame = Frame(self, bg="#2c2c2c", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        title_label = Label(main_frame, text="Explorador de Monumentos INAH", 
                            font=('Consolas', 24, 'bold'), fg="#ffcc00", bg="#2c2c2c")
        title_label.pack(pady=15)

        search_frame = Frame(main_frame, bg="#3c3c3c", padx=10, pady=10, relief="groove", bd=2)
        search_frame.pack(pady=10, fill="x")

        path_frame = Frame(search_frame, bg="#3c3c3c")
        path_frame.pack(pady=5, fill="x")
        
        path_label = Label(path_frame, text="Carpeta Raíz:", font=('Segoe UI', 12, 'bold'), fg="#ffffff", bg="#3c3c3c")
        path_label.pack(side="left", padx=5)

        self.path_entry = Entry(path_frame, font=('Segoe UI', 10), bg="#4a4a4a", fg="#ffffff", state='readonly', width=60)
        self.path_entry.pack(side="left", padx=5, expand=True, fill="x")

        select_button = Button(path_frame, text="📁 Seleccionar Carpeta", command=self.select_root_folder, font=('Segoe UI', 10), bg="#004d40", fg="#ffffff", activebackground="#006655", activeforeground="#ffffff")
        select_button.pack(side="left", padx=5)
        
        search_label = Label(search_frame, text="Buscar:", font=('Segoe UI', 12, 'bold'), fg="#ffffff", bg="#3c3c3c")
        search_label.pack(side="left", padx=5)

        self.search_entry = Entry(search_frame, width=50, font=('Segoe UI', 12), bg="#4a4a4a", fg="#ffffff", insertbackground="#ffcc00")
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.search_entry.bind("<Return>", self.perform_search)

        search_button = Button(search_frame, text="🔎 Buscar", command=self.perform_search, font=('Segoe UI', 12, 'bold'), bg="#5a0000", fg="#ffffff", activebackground="#7b0000", activeforeground="#ffffff")
        search_button.pack(side="left", padx=5)

        index_button = Button(search_frame, text="🔄 Re-Indexar Archivos", command=self.start_indexing, font=('Segoe UI', 10), bg="#004d40", fg="#ffffff", activebackground="#006655", activeforeground="#ffffff")
        index_button.pack(side="right", padx=5)
        
        self.status_label = Label(main_frame, text="", font=('Segoe UI', 10, 'italic'), fg="#aaaaaa", bg="#2c2c2c")
        self.status_label.pack(pady=5)

        columns = ("municipio", "edificio", "documento")
        self.results_tree = Treeview(main_frame, columns=columns, show="headings", selectmode="browse")
        
        self.results_tree.heading("municipio", text="Municipio", anchor="w", command=lambda: self.sort_column("municipio"))
        self.results_tree.heading("edificio", text="Edificio / Lugar", anchor="w", command=lambda: self.sort_column("edificio"))
        self.results_tree.heading("documento", text="Documento", anchor="w", command=lambda: self.sort_column("documento"))

        self.results_tree.column("municipio", width=200, stretch=True, minwidth=150)
        self.results_tree.column("edificio", width=350, stretch=True, minwidth=250)
        self.results_tree.column("documento", width=300, stretch=True, minwidth=200)

        vsb = Scrollbar(main_frame, orient="vertical", command=self.results_tree.yview)
        hsb = Scrollbar(main_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.results_tree.pack(fill="both", expand=True, pady=10)

        self.results_tree.bind("<Double-1>", self.on_double_click)
        
        info_button = Button(main_frame, text="ℹ️ Información", command=self.show_info, font=('Segoe UI', 10), bg="#8B008B", fg="#ffffff", activebackground="#A020F0", activeforeground="#ffffff")
        info_button.pack(side="left", padx=5, pady=5)
        
        self.results_count_label = Label(main_frame, text="Resultados: 0", font=('Segoe UI', 10), fg="#aaaaaa", bg="#2c2c2c")
        self.results_count_label.pack(side="right", padx=5, pady=5)

    def select_root_folder(self):
        """
        Abre un diálogo para que el usuario seleccione la carpeta raíz de los archivos
        y actualiza la interfaz con la ruta seleccionada.
        """
        selected_path = filedialog.askdirectory(title="Selecciona la Carpeta Raíz de los Archivos del INAH")
        if selected_path:
            self.root_path = selected_path
            self.path_entry.config(state='normal')
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, self.root_path)
            self.path_entry.config(state='readonly')
            messagebox.showinfo("Carpeta Seleccionada", f"Carpeta seleccionada.\nAhora haz clic en 'Re-Indexar Archivos' para comenzar.")

    def perform_search(self, event=None):
        """
        Obtiene el texto del campo de búsqueda, consulta la base de datos
        y puebla la tabla de resultados con las coincidencias.
        """
        query = self.search_entry.get().strip()
        
        self.status_label.config(text="Buscando documentos, por favor espere...", fg="#add8e6")
        self.update_idletasks()

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        resultados = buscar_documentos(query)
        
        if not resultados:
            self.status_label.config(text=f"No se encontraron resultados para '{query}'.", fg="#ff6347")
            self.results_count_label.config(text="Resultados: 0")
            return

        for doc, edif, mun, ruta in resultados:
            self.results_tree.insert("", "end", iid=ruta, values=(mun, edif, doc))
        
        self.results_count_label.config(text=f"Resultados: {len(resultados)}")
        self.status_label.config(text=f"Búsqueda completada. Encontrados {len(resultados)} resultados.", fg="#98fb98")

    def on_double_click(self, event):
        """
        Manejador para el evento de doble clic en un elemento de la tabla de resultados.
        Abre el archivo PDF correspondiente.
        """
        item_id = self.results_tree.selection()
        if item_id:
            ruta_pdf = self.results_tree.item(item_id, "iid")
            if ruta_pdf:
                abrir_pdf(ruta_pdf)

    def sort_column(self, col):
        """
        Ordena los datos en la tabla de resultados según la columna en la que el
        usuario hizo clic, alternando entre orden ascendente y descendente.
        """
        data = [(self.results_tree.item(item, 'values'), item) for item in self.results_tree.get_children('')]
        
        column_index_map = {"municipio": 0, "edificio": 1, "documento": 2}
        col_idx = column_index_map.get(col)
        
        if col_idx is None: return

        reverse = not self.sort_order.get(col, False)
        self.sort_order[col] = reverse

        data.sort(key=lambda x: str(x[0][col_idx]).lower(), reverse=reverse)

        for c in self.results_tree["columns"]:
            current_text = self.results_tree.heading(c, "text").split(" ")[0]
            self.results_tree.heading(c, text=current_text)
        
        arrow = " 🔽" if reverse else " 🔼"
        self.results_tree.heading(col, text=f"{self.results_tree.heading(col, 'text').split(' ')[0]}{arrow}")

        for item in self.results_tree.get_children(''):
            self.results_tree.delete(item)

        for values, item_id in data:
            self.results_tree.insert("", "end", iid=item_id, values=values)

    def start_indexing(self):
        """
        Inicia el proceso de indexación de archivos en un hilo separado
        para evitar que la interfaz de usuario se congele.
        """
        if not self.root_path:
            messagebox.showerror("Error de Ruta", "Por favor, primero seleccione la carpeta raíz de los archivos.")
            return
            
        confirm = messagebox.askyesno("Confirmar Indexación", 
                                      "La indexación puede tardar un poco y sobrescribirá los datos existentes.\n¿Desea continuar?",
                                      icon='warning')
        if not confirm:
            return

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results_count_label.config(text="Resultados: 0")
        self.status_label.config(text="Iniciando indexación, esto puede tardar...", fg="#ffcc00")
        self.update_idletasks()

        indexing_thread = threading.Thread(target=indexar_archivos_background, args=(self, self.root_path))
        indexing_thread.daemon = True
        indexing_thread.start()

    def show_info(self):
        """
        Muestra una ventana emergente con información sobre cómo usar la aplicación.
        """
        info_window = Toplevel(self)
        info_window.title("Información del Buscador")
        info_window.geometry("500x350")
        info_window.resizable(False, False)
        info_window.configure(bg="#202020")
        
        info_text = """
        Buscador de Archivos Históricos INAH
        
        Desarrollado con Python (Tkinter, SQLite).
        
        Instrucciones:
        1. Haga clic en 'Seleccionar Carpeta' para elegir la carpeta raíz.
        2. Haga clic en 'Re-Indexar Archivos' para que el programa
           encuentre todos los PDFs y cree la base de datos.
        3. Escriba su búsqueda (municipio, edificio o documento)
           y presione Enter o el botón 'Buscar'.
        4. Haga doble clic en un resultado para abrir el PDF.
        5. Haga clic en los encabezados de las columnas
           para ordenar los resultados alfabéticamente.
        
        Esperamos que esta herramienta le sea de gran ayuda.
        """
        info_label = Label(info_window, text=info_text, font=('Segoe UI', 10), fg="#e0e0e0", bg="#202020", justify="left")
        info_label.pack(padx=20, pady=20, expand=True)

        close_button = Button(info_window, text="Cerrar", command=info_window.destroy, 
                              font=('Segoe UI', 10, 'bold'), bg="#5a0000", fg="#ffffff")
        close_button.pack(pady=10)


# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    crear_tabla_si_no_existe()
    app = AplicacionINAH()
    app.mainloop()
