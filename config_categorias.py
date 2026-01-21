"""
Módulo para gestión de Categorías - CRUD completo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Categoria


class CategoriasWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Categorías")
        self.root.geometry("600x500")

        # Variable para almacenar la categoría actual (para edición)
        self.current_categoria = None

        # Crear interfaz
        self.create_widgets()

        # Cargar categorías iniciales
        self.load_categorias()

    def create_widgets(self):
        """Crea todos los widgets de la ventana"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ========== SECCIÓN DE FORMULARIO ==========
        form_frame = ttk.LabelFrame(main_frame, text="Datos de Categoría", padding="10")
        form_frame.grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E)
        )
        form_frame.columnconfigure(1, weight=1)

        # Campo: Nombre
        ttk.Label(form_frame, text="Nombre:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.nombre_entry = ttk.Entry(form_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(buttons_frame, text="Guardar", command=self.save_categoria).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Nuevo", command=self.new_categoria).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Cancelar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTA ==========
        list_frame = ttk.LabelFrame(
            main_frame, text="Lista de Categorías", padding="10"
        )
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión de la lista
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview (tabla) para mostrar categorías
        columns = ("ID", "Nombre")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nombre", width=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Ubicar widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind para selección
        self.tree.bind("<<TreeviewSelect>>", self.on_categoria_select)

        # ========== BOTONES DE ACCIÓN ==========
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(action_frame, text="Editar", command=self.edit_categoria).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Eliminar", command=self.delete_categoria).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Actualizar Lista", command=self.load_categorias
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cerrar", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def load_categorias(self):
        """Carga todas las categorías en el Treeview"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener y mostrar categorías
        try:
            categorias = Categoria.get_all()
            for cat in categorias:
                self.tree.insert("", tk.END, values=(cat.id, cat.nombre))
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar las categorías: {str(e)}"
            )

    def clear_form(self):
        """Limpia el formulario"""
        self.current_categoria = None
        self.nombre_entry.delete(0, tk.END)
        # Limpiar selección del treeview
        self.tree.selection_remove(self.tree.selection())

    def new_categoria(self):
        """Prepara el formulario para una nueva categoría"""
        self.clear_form()
        self.nombre_entry.focus()

    def on_categoria_select(self, event):
        """Cuando se selecciona una categoría en la lista"""
        selection = self.tree.selection()
        if selection:
            try:
                item = self.tree.item(selection[0])
                categoria_id = item["values"][0]
                # Cargar la categoría completa de la base de datos
                self.current_categoria = Categoria.get_by_id(categoria_id)
            except Exception as e:
                print(f"Error al cargar categoría: {e}")
                self.current_categoria = None

    def edit_categoria(self):
        """Carga la categoría seleccionada en el formulario para editar"""
        if self.current_categoria and self.current_categoria.id:
            # Guardar una referencia a la categoría antes de limpiar
            categoria_a_editar = self.current_categoria

            # Limpiar solo el campo de texto
            self.nombre_entry.delete(0, tk.END)

            # Insertar el nombre de la categoría
            self.nombre_entry.insert(0, categoria_a_editar.nombre)
            self.nombre_entry.focus()

            # Nota: No establecemos self.current_categoria = None aquí
            # porque queremos mantener la referencia para guardar
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione una categoría para editar"
            )

    def save_categoria(self):
        """Guarda la categoría (crea o actualiza)"""
        nombre = self.nombre_entry.get().strip()

        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es requerido")
            return

        try:
            if self.current_categoria and self.current_categoria.id:
                # Actualizar categoría existente
                self.current_categoria.nombre = nombre
                self.current_categoria.save()
                messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
            else:
                # Crear nueva categoría
                nueva_cat = Categoria(nombre=nombre)
                nueva_cat.save()
                messagebox.showinfo("Éxito", "Categoría creada correctamente")

            # Limpiar formulario y actualizar lista
            self.clear_form()
            self.load_categorias()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la categoría: {str(e)}")

    def delete_categoria(self):
        """Elimina la categoría seleccionada"""
        if not self.current_categoria:
            messagebox.showwarning(
                "Advertencia", "Seleccione una categoría para eliminar"
            )
            return

        # Verificar si es la categoría por defecto "Sin Categoría"
        if self.current_categoria.nombre == "Sin Categoría":
            messagebox.showwarning(
                "Advertencia", "La categoría 'Sin Categoría' no se puede eliminar"
            )
            return

        try:
            # Verificar si hay productos
            count_productos = self.current_categoria.get_count_productos()

            if count_productos > 0:
                # Preguntar al usuario qué hacer
                respuesta = messagebox.askyesnocancel(
                    "Categoría con productos",
                    f"La categoría '{self.current_categoria.nombre}' tiene {count_productos} producto(s).\n\n"
                    f"¿Qué desea hacer?\n\n"
                    f"Sí: Mover productos a 'Sin Categoría' y eliminar\n"
                    f"No: Solo eliminar (fallará si hay productos)\n"
                    f"Cancelar: No hacer nada",
                )

                if respuesta is None:  # Cancelar
                    return
                elif respuesta:  # Sí - Mover a categoría por defecto
                    if messagebox.askyesno(
                        "Confirmar",
                        f"¿Mover {count_productos} producto(s) a 'Sin Categoría' y eliminar '{self.current_categoria.nombre}'?",
                    ):
                        self.current_categoria.delete(mover_a_default=True)
                        messagebox.showinfo(
                            "Éxito",
                            f"Categoría eliminada. {count_productos} producto(s) movidos a 'Sin Categoría'.",
                        )
                        self.clear_form()
                        self.load_categorias()
                else:  # No - Intentar eliminar normalmente (fallará)
                    try:
                        self.current_categoria.delete()
                        messagebox.showinfo(
                            "Éxito", "Categoría eliminada correctamente"
                        )
                        self.clear_form()
                        self.load_categorias()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
            else:
                # No hay productos, eliminar directamente
                if messagebox.askyesno(
                    "Confirmar",
                    f"¿Eliminar la categoría '{self.current_categoria.nombre}'?",
                ):
                    self.current_categoria.delete()
                    messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
                    self.clear_form()
                    self.load_categorias()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la categoría: {str(e)}")


def main():
    root = tk.Tk()
    app = CategoriasWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
