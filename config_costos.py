"""
Módulo para configuración de Costos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Costo, TipoCosto


class ConfigCostosWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurar Costos")
        self.root.geometry("900x700")

        # Variables
        self.current_costo = None
        self.current_tipo = TipoCosto.FIJO  # Por defecto

        # Crear interfaz
        self.create_widgets()

        # Cargar costos iniciales
        self.load_costos()

    def create_widgets(self):
        """Crea todos los widgets de la ventana"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # ========== SECCIÓN DE TIPO DE COSTO ==========
        tipo_frame = ttk.LabelFrame(main_frame, text="Tipo de Costo", padding="10")
        tipo_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))

        # Radio buttons para seleccionar tipo
        self.tipo_var = tk.StringVar(value=TipoCosto.FIJO.value)

        ttk.Radiobutton(
            tipo_frame,
            text="Costos Fijos",
            variable=self.tipo_var,
            value=TipoCosto.FIJO.value,
            command=self.cambiar_tipo_costo,
        ).pack(side=tk.LEFT, padx=20)

        ttk.Radiobutton(
            tipo_frame,
            text="Costos Variables",
            variable=self.tipo_var,
            value=TipoCosto.VARIABLE.value,
            command=self.cambiar_tipo_costo,
        ).pack(side=tk.LEFT, padx=20)

        # ========== SECCIÓN DE FORMULARIO ==========
        form_frame = ttk.LabelFrame(main_frame, text="Datos del Costo", padding="15")
        form_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        form_frame.columnconfigure(1, weight=1)

        # Campo: Nombre
        ttk.Label(form_frame, text="Nombre:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.nombre_entry = ttk.Entry(form_frame, width=40)
        self.nombre_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

        # Campo: Cantidad a Pagar
        ttk.Label(form_frame, text="Cantidad a Pagar:").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )

        cantidad_frame = ttk.Frame(form_frame)
        cantidad_frame.grid(row=1, column=1, pady=5, sticky=tk.W)

        self.cantidad_entry = ttk.Entry(cantidad_frame, width=15)
        self.cantidad_entry.pack(side=tk.LEFT)

        ttk.Label(cantidad_frame, text=" $").pack(side=tk.LEFT, padx=(5, 0))

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))

        ttk.Button(buttons_frame, text="Guardar", command=self.save_costo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Nuevo", command=self.new_costo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Cancelar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTAS ==========
        # Notebook (pestañas) para mostrar los dos tipos de costos
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Crear frames para cada tipo de costo
        self.fijo_frame = ttk.Frame(self.notebook, padding="5")
        self.variable_frame = ttk.Frame(self.notebook, padding="5")

        self.notebook.add(self.fijo_frame, text="Costos Fijos")
        self.notebook.add(self.variable_frame, text="Costos Variables")

        # Configurar frames
        for frame, tipo in [
            (self.fijo_frame, TipoCosto.FIJO),
            (self.variable_frame, TipoCosto.VARIABLE),
        ]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

            # Crear Treeview para este tipo
            tree = ttk.Treeview(
                frame, columns=("ID", "Nombre", "Cantidad"), show="headings", height=15
            )

            # Configurar columnas
            tree.heading("ID", text="ID")
            tree.heading("Nombre", text="Nombre")
            tree.heading("Cantidad", text="Cantidad ($)")

            tree.column("ID", width=50, anchor="center")
            tree.column("Nombre", width=250, anchor="w")
            tree.column("Cantidad", width=150, anchor="e")

            # Scrollbar
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            # Ubicar widgets
            tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

            # Guardar referencia al treeview
            if tipo == TipoCosto.FIJO:
                self.tree_fijos = tree
            else:
                self.tree_variables = tree

            # Bind para selección
            tree.bind(
                "<<TreeviewSelect>>", lambda e, t=tipo: self.on_costo_select(e, t)
            )

        # ========== SECCIÓN DE TOTALES ==========
        totales_frame = ttk.Frame(main_frame)
        totales_frame.grid(row=3, column=0, pady=(10, 0), sticky=(tk.W, tk.E))

        # Etiquetas para totales
        self.total_fijos_label = ttk.Label(
            totales_frame, text="Total Costos Fijos: $0.00", font=("Arial", 10, "bold")
        )
        self.total_fijos_label.pack(side=tk.LEFT, padx=(0, 30))

        self.total_variables_label = ttk.Label(
            totales_frame,
            text="Total Costos Variables: $0.00",
            font=("Arial", 10, "bold"),
        )
        self.total_variables_label.pack(side=tk.LEFT, padx=(0, 30))

        self.total_general_label = ttk.Label(
            totales_frame,
            text="Total General: $0.00",
            font=("Arial", 10, "bold", "underline"),
        )
        self.total_general_label.pack(side=tk.LEFT)

        # ========== BOTONES DE ACCIÓN ==========
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, pady=(10, 0))

        ttk.Button(action_frame, text="Editar", command=self.edit_costo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Eliminar", command=self.delete_costo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Actualizar Listas", command=self.load_costos
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cerrar", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def cambiar_tipo_costo(self):
        """Cambia el tipo de costo actual basado en los radio buttons"""
        self.current_tipo = TipoCosto(self.tipo_var.get())
        self.clear_form_campos()  # Solo limpia campos, no current_costo

    def clear_form_campos(self):
        """Limpia solo los campos del formulario, no current_costo"""
        self.nombre_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)

    def clear_form(self):
        """Limpia completamente el formulario (incluyendo current_costo)"""
        self.current_costo = None
        self.clear_form_campos()
        self.tipo_var.set(TipoCosto.FIJO.value)
        self.current_tipo = TipoCosto.FIJO
        self.nombre_entry.focus()

    def new_costo(self):
        """Prepara el formulario para un nuevo costo"""
        self.clear_form()

    def load_costos(self):
        """Carga todos los costos en los Treeviews correspondientes"""
        # Limpiar listas actuales
        for tree in [self.tree_fijos, self.tree_variables]:
            for item in tree.get_children():
                tree.delete(item)

        try:
            # Cargar costos fijos
            costos_fijos = Costo.get_by_tipo(TipoCosto.FIJO)
            total_fijos = 0.0

            for costo in costos_fijos:
                self.tree_fijos.insert(
                    "", tk.END, values=(costo.id, costo.nombre, f"{costo.cantidad:.2f}")
                )
                total_fijos += costo.cantidad

            # Cargar costos variables
            costos_variables = Costo.get_by_tipo(TipoCosto.VARIABLE)
            total_variables = 0.0

            for costo in costos_variables:
                self.tree_variables.insert(
                    "", tk.END, values=(costo.id, costo.nombre, f"{costo.cantidad:.2f}")
                )
                total_variables += costo.cantidad

            # Actualizar totales
            total_general = total_fijos + total_variables

            self.total_fijos_label.config(
                text=f"Total Costos Fijos: ${total_fijos:.2f}"
            )
            self.total_variables_label.config(
                text=f"Total Costos Variables: ${total_variables:.2f}"
            )
            self.total_general_label.config(text=f"Total General: ${total_general:.2f}")

        except Exception as e:
            print(f"Error al cargar costos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los costos: {str(e)}")

    def on_costo_select(self, event, tipo):
        """Cuando se selecciona un costo en la lista"""
        # Determinar qué treeview fue seleccionado
        if tipo == TipoCosto.FIJO:
            tree = self.tree_fijos
        else:
            tree = self.tree_variables

        selection = tree.selection()
        if selection:
            try:
                item = tree.item(selection[0])
                costo_id = item["values"][0]
                # Cargar el costo completo de la base de datos
                self.current_costo = Costo.get_by_id(costo_id)
                # Cambiar al tipo correcto
                self.current_tipo = self.current_costo.tipo
                self.tipo_var.set(self.current_tipo.value)
            except Exception as e:
                print(f"Error al cargar costo: {e}")
                self.current_costo = None

    def edit_costo(self):
        """Carga el costo seleccionado en el formulario para editar"""
        if not self.current_costo:
            messagebox.showwarning("Advertencia", "Seleccione un costo para editar")
            return

        try:
            # Guardar referencia antes de limpiar campos
            costo_a_editar = self.current_costo

            # Cargar datos frescos de la base de datos
            costo_actualizado = Costo.get_by_id(costo_a_editar.id)

            # Limpiar solo los campos, mantener current_costo
            self.nombre_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)

            # Cargar datos del costo
            self.nombre_entry.insert(0, costo_actualizado.nombre)
            self.cantidad_entry.insert(0, str(costo_actualizado.cantidad))

            # Establecer el tipo correcto
            self.current_tipo = costo_actualizado.tipo
            self.tipo_var.set(self.current_tipo.value)

            # Mantener la referencia
            self.current_costo = costo_actualizado

            # Cambiar a la pestaña correcta
            if self.current_tipo == TipoCosto.FIJO:
                self.notebook.select(0)
            else:
                self.notebook.select(1)

            self.nombre_entry.focus()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el costo: {str(e)}")

    def save_costo(self):
        """Guarda el costo (crea o actualiza)"""
        # Validar campos requeridos
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del costo es requerido")
            return

        try:
            # Obtener datos del formulario
            cantidad = float(self.cantidad_entry.get() or 0)

            # Validaciones básicas
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return

            # Obtener el tipo actual
            tipo_actual = TipoCosto(self.tipo_var.get())

            # DEBUG: Verificar current_costo
            print(f"DEBUG - save_costo: current_costo = {self.current_costo}")
            print(
                f"DEBUG - save_costo: tiene id? = {self.current_costo.id if self.current_costo else 'No hay current_costo'}"
            )

            if self.current_costo and self.current_costo.id:
                print(f"DEBUG - Actualizando costo ID: {self.current_costo.id}")
                # Actualizar costo existente
                self.current_costo.nombre = nombre
                self.current_costo.cantidad = cantidad
                self.current_costo.tipo = tipo_actual
                self.current_costo.save()
                messagebox.showinfo("Éxito", "Costo actualizado correctamente")
            else:
                print("DEBUG - Creando nuevo costo")
                # Crear nuevo costo
                nuevo_costo = Costo(nombre=nombre, cantidad=cantidad, tipo=tipo_actual)
                nuevo_costo.save()
                messagebox.showinfo("Éxito", "Costo creado correctamente")

            # Limpiar y actualizar
            self.clear_form()
            self.load_costos()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el costo: {str(e)}")

    def delete_costo(self):
        """Elimina el costo seleccionado"""
        if not self.current_costo:
            messagebox.showwarning("Advertencia", "Seleccione un costo para eliminar")
            return

        tipo_texto = "Fijo" if self.current_costo.tipo == TipoCosto.FIJO else "Variable"

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar el costo {tipo_texto} '{self.current_costo.nombre}'?",
        ):
            try:
                self.current_costo.delete()
                messagebox.showinfo("Éxito", "Costo eliminado correctamente")
                self.clear_form()
                self.load_costos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el costo: {str(e)}")


def main():
    root = tk.Tk()
    app = ConfigCostosWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
