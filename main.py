"""
Ventana principal de la aplicación - Sistema de Gestión
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
from pathlib import Path


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión")
        self.root.geometry("800x600")

        # Configurar estilo
        self.setup_styles()

        # Crear interfaz
        self.create_widgets()

    def setup_styles(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use("clam")

        # Configurar colores y fuentes
        style.configure("Title.TLabel", font=("Arial", 24, "bold"))
        style.configure("Button.TButton", font=("Arial", 12), padding=10)
        style.configure(
            "Disabled.TButton", font=("Arial", 12), padding=10, foreground="gray"
        )

    def create_widgets(self):
        """Crea todos los widgets de la ventana principal"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión de la ventana
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Título/Encabezado
        title_label = ttk.Label(
            main_frame, text="Sistema de Gestión", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, pady=(0, 30))

        # Frame para los botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        buttons_frame.columnconfigure(0, weight=1)

        # Lista de módulos con su estado (habilitado/deshabilitado)
        # Formato: (nombre, archivo, habilitado)
        modulos = [
            ("Categorías", "categorias.py", True),
            ("Productos", "productos.py", True),
            ("Clientes", None, False),
            ("Proveedores", None, False),
            ("Ventas", None, False),
            ("Inventario", None, False),
        ]

        # Crear botones
        self.buttons = []
        for i, (nombre, archivo, habilitado) in enumerate(modulos):
            btn = ttk.Button(
                buttons_frame,
                text=nombre,
                command=lambda a=archivo: self.abrir_modulo(a) if a else None,
                style="Button.TButton" if habilitado else "Disabled.TButton",
                state=tk.NORMAL if habilitado else tk.DISABLED,
            )
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            self.buttons.append(btn)

    def abrir_modulo(self, archivo):
        """
        Abre una ventana de módulo específico
        Esta función es reutilizable para cualquier módulo
        """
        try:
            # Usar subprocess para ejecutar el archivo del módulo
            script_path = Path(__file__).parent / archivo
            subprocess.Popen([sys.executable, str(script_path)])
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
