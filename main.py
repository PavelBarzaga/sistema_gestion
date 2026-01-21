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
        style.configure("MainButton.TButton", font=("Arial", 12), padding=15)
        style.configure("SubButton.TButton", font=("Arial", 10), padding=8)
        style.configure(
            "Disabled.TButton", font=("Arial", 12), padding=15, foreground="gray"
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

        # Frame para los botones principales
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        buttons_frame.columnconfigure(0, weight=1)

        # Lista de módulos principales
        # Formato: (nombre, archivo, habilitado, es_submenu)
        modulos_principales = [
            ("Configuraciones", None, True, True),  # Este abre submenú
            ("Productos", "productos.py", True, False),
            ("Compras", "compras.py", True, False),
            ("Ventas", None, False, False),
            ("Reportes", None, False, False),
        ]

        # Crear botones principales
        self.buttons = []
        for i, (nombre, archivo, habilitado, es_submenu) in enumerate(
            modulos_principales
        ):
            if es_submenu:
                # Botón para abrir ventana de configuraciones
                btn = ttk.Button(
                    buttons_frame,
                    text=nombre,
                    command=self.abrir_configuraciones,
                    style="MainButton.TButton" if habilitado else "Disabled.TButton",
                    state=tk.NORMAL if habilitado else tk.DISABLED,
                )
            else:
                # Botón normal que abre un módulo
                btn = ttk.Button(
                    buttons_frame,
                    text=nombre,
                    command=lambda a=archivo: self.abrir_modulo(a) if a else None,
                    style="MainButton.TButton" if habilitado else "Disabled.TButton",
                    state=tk.NORMAL if habilitado else tk.DISABLED,
                )

            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            self.buttons.append(btn)

        # Botón Cerrar
        ttk.Button(
            buttons_frame,
            text="Cerrar",
            command=self.root.quit,
            style="MainButton.TButton",
        ).grid(
            row=len(modulos_principales), column=0, pady=(20, 0), sticky=(tk.W, tk.E)
        )

    def abrir_modulo(self, archivo):
        """
        Abre una ventana de módulo específico
        """
        try:
            # Usar subprocess para ejecutar el archivo del módulo
            script_path = Path(__file__).parent / archivo
            subprocess.Popen([sys.executable, str(script_path)])
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo abrir el módulo: {str(e)}")

    def abrir_configuraciones(self):
        """
        Abre la ventana de configuraciones con opciones específicas
        """
        try:
            # Crear ventana emergente de configuraciones
            config_window = tk.Toplevel(self.root)
            config_window.title("Configuraciones del Sistema")
            config_window.geometry("500x400")
            config_window.transient(self.root)  # Hacerla hija de la ventana principal
            config_window.grab_set()  # Modal

            # Centrar ventana
            config_window.update_idletasks()
            width = config_window.winfo_width()
            height = config_window.winfo_height()
            x = (config_window.winfo_screenwidth() // 2) - (width // 2)
            y = (config_window.winfo_screenheight() // 2) - (height // 2)
            config_window.geometry(f"{width}x{height}+{x}+{y}")

            # Título
            ttk.Label(
                config_window, text="Configuraciones", font=("Arial", 16, "bold")
            ).pack(pady=(20, 30))

            # Frame para botones de configuración
            config_frame = ttk.Frame(config_window, padding="20")
            config_frame.pack(expand=True, fill=tk.BOTH)
            config_frame.columnconfigure(0, weight=1)

            # Botones de configuración
            configuraciones = [
                ("Categorías", "config_categorias.py"),
                ("Costos", None),  # Futuro módulo
                ("Semanas", None),  # Futuro módulo
            ]

            for i, (nombre, archivo) in enumerate(configuraciones):
                if archivo:
                    btn = ttk.Button(
                        config_frame,
                        text=nombre,
                        command=lambda a=archivo: self.abrir_config_desde_submenu(
                            config_window, a
                        ),
                        style="SubButton.TButton",
                        width=25,
                    )
                else:
                    btn = ttk.Button(
                        config_frame,
                        text=nombre,
                        state=tk.DISABLED,
                        style="Disabled.TButton",
                        width=25,
                    )

                btn.grid(row=i, column=0, pady=8, ipady=10)

        except Exception as e:
            tk.messagebox.showerror(
                "Error", f"No se pudo abrir configuraciones: {str(e)}"
            )

    def abrir_config_desde_submenu(self, parent_window, archivo):
        """
        Abre un módulo de configuración desde el submenú y cierra la ventana de configuraciones
        """
        parent_window.destroy()  # Cerrar ventana de configuraciones
        self.abrir_modulo(archivo)  # Abrir el módulo específico


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
