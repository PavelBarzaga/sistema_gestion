"""
Módulo para gestión de Compras - CRUD completo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Compra


class ComprasWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Compras")
        self.root.geometry("1000x600")

        # Variables
        self.current_compra = None

        # Crear interfaz
        self.create_widgets()

        # Cargar compras iniciales
        self.load_compras()

    def create_widgets(self):
        """Crea todos los widgets de la ventana"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # ========== SECCIÓN DE FORMULARIO ==========
        form_frame = ttk.LabelFrame(main_frame, text="Datos de la Compra", padding="15")
        form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Campo: Nombre del Producto
        ttk.Label(form_frame, text="Nombre del Producto:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.producto_entry = ttk.Entry(form_frame, width=30)
        self.producto_entry.grid(
            row=0, column=1, pady=5, sticky=(tk.W, tk.E), columnspan=3
        )

        # Campos: Costo Total y Cantidad de Elementos
        ttk.Label(form_frame, text="Costo Total:").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.costo_entry = ttk.Entry(form_frame, width=15)
        self.costo_entry.grid(row=1, column=1, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text="Cantidad de Elementos:").grid(
            row=1, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )
        self.cantidad_entry = ttk.Entry(form_frame, width=15)
        self.cantidad_entry.grid(row=1, column=3, pady=5, sticky=tk.W)

        # Campos: Merma y Fecha de Compra
        ttk.Label(form_frame, text="Merma:").grid(
            row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.merma_entry = ttk.Entry(form_frame, width=15)
        self.merma_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        ttk.Label(form_frame, text="(cantidad en mal estado)").grid(
            row=2, column=1, padx=(90, 0), pady=5, sticky=tk.W
        )

        ttk.Label(form_frame, text="Fecha de Compra:").grid(
            row=2, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )

        # Frame para el selector de fecha
        fecha_frame = ttk.Frame(form_frame)
        fecha_frame.grid(row=2, column=3, pady=5, sticky=tk.W)

        # Crear comboboxes para día, mes y año
        self.dia_var = tk.StringVar()
        self.mes_var = tk.StringVar()
        self.anio_var = tk.StringVar()

        # Obtener fecha actual
        hoy = datetime.now()

        # Días (1-31)
        dias = [str(i).zfill(2) for i in range(1, 32)]
        self.dia_combo = ttk.Combobox(
            fecha_frame,
            textvariable=self.dia_var,
            values=dias,
            width=3,
            state="readonly",
        )
        self.dia_combo.set(str(hoy.day).zfill(2))
        self.dia_combo.pack(side=tk.LEFT)
        ttk.Label(fecha_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Meses (1-12)
        meses = [str(i).zfill(2) for i in range(1, 13)]
        self.mes_combo = ttk.Combobox(
            fecha_frame,
            textvariable=self.mes_var,
            values=meses,
            width=3,
            state="readonly",
        )
        self.mes_combo.set(str(hoy.month).zfill(2))
        self.mes_combo.pack(side=tk.LEFT)
        ttk.Label(fecha_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Años (2020-2030)
        anios = [str(i) for i in range(2020, 2031)]
        self.anio_combo = ttk.Combobox(
            fecha_frame,
            textvariable=self.anio_var,
            values=anios,
            width=5,
            state="readonly",
        )
        self.anio_combo.set(str(hoy.year))
        self.anio_combo.pack(side=tk.LEFT)

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=(15, 0))

        ttk.Button(buttons_frame, text="Guardar", command=self.save_compra).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Nuevo", command=self.new_compra).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Cancelar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTA ==========
        # Frame para la lista
        lista_frame = ttk.LabelFrame(main_frame, text="Lista de Compras", padding="10")
        lista_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        # Treeview (tabla) para mostrar compras
        columns = (
            "ID",
            "Producto",
            "Costo Total",
            "Cantidad",
            "Costo Unit",
            "Merma",
            "Pérdidas",
            "Fecha",
        )

        self.tree = ttk.Treeview(
            lista_frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_configs = [
            ("ID", 50, "center"),
            ("Producto", 150, "w"),
            ("Costo Total", 100, "e"),
            ("Cantidad", 80, "e"),
            ("Costo Unit", 100, "e"),
            ("Merma", 80, "e"),
            ("Pérdidas", 100, "e"),
            ("Fecha", 100, "center"),
        ]

        for col_name, width, anchor in column_configs:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, anchor=anchor)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            lista_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Ubicar widgets
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind para selección
        self.tree.bind("<<TreeviewSelect>>", self.on_compra_select)

        # ========== BOTONES DE ACCIÓN ==========
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(action_frame, text="Editar", command=self.edit_compra).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Eliminar", command=self.delete_compra).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Actualizar Lista", command=self.load_compras
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cerrar", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def get_fecha_from_selectores(self):
        """Obtiene la fecha desde los selectores y la valida"""
        try:
            dia = self.dia_var.get()
            mes = self.mes_var.get()
            anio = self.anio_var.get()

            # Validar que todos los campos tengan valores
            if not (dia and mes and anio):
                return None

            # Formatear fecha como YYYY-MM-DD
            fecha_str = f"{anio}-{mes}-{dia}"

            # Validar que sea una fecha válida
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            return fecha_obj

        except ValueError:
            return None

    def set_fecha_in_selectores(self, fecha):
        """Establece la fecha en los selectores desde un objeto datetime/string"""
        try:
            if isinstance(fecha, str):
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            else:
                fecha_obj = fecha

            self.dia_var.set(str(fecha_obj.day).zfill(2))
            self.mes_var.set(str(fecha_obj.month).zfill(2))
            self.anio_var.set(str(fecha_obj.year))

        except (ValueError, AttributeError):
            # Si hay error, establecer fecha actual
            hoy = datetime.now()
            self.dia_var.set(str(hoy.day).zfill(2))
            self.mes_var.set(str(hoy.month).zfill(2))
            self.anio_var.set(str(hoy.year))

    def clear_form(self):
        """Limpia solo los campos del formulario, no current_compra"""
        # Solo limpia los campos de entrada, no cambia current_compra
        self.producto_entry.delete(0, tk.END)
        self.costo_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        self.merma_entry.delete(0, tk.END)

        # Establecer fecha actual en los selectores
        hoy = datetime.now()
        self.set_fecha_in_selectores(hoy)

    def new_compra(self):
        """Prepara el formulario para una nueva compra"""
        self.current_compra = None  # Importante: establecer a None para nuevo
        self.clear_form()
        self.producto_entry.focus()

    def load_compras(self):
        """Carga todas las compras en el Treeview"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            compras = Compra.get_all()

            if not compras:
                return

            for compra in compras:
                # Calcular valores para mostrar (costo unitario y pérdidas)
                costo_unitario = (
                    compra.costo_total / compra.cantidad_elementos
                    if compra.cantidad_elementos > 0
                    else 0
                )
                perdidas = costo_unitario * compra.merma

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        compra.id,
                        compra.producto_nombre,
                        f"{compra.costo_total:.2f}",
                        compra.cantidad_elementos,
                        f"{costo_unitario:.2f}",
                        compra.merma,
                        f"{perdidas:.2f}",
                        compra.fecha_compra,
                    ),
                )

        except Exception as e:
            print(f"Error al cargar compras: {e}")
            messagebox.showerror(
                "Error", f"No se pudieron cargar las compras: {str(e)}"
            )

    def on_compra_select(self, event):
        """Cuando se selecciona una compra en la lista"""
        selection = self.tree.selection()
        if selection:
            try:
                item = self.tree.item(selection[0])
                compra_id = item["values"][0]
                # Cargar la compra completa de la base de datos
                self.current_compra = Compra.get_by_id(compra_id)
            except Exception as e:
                print(f"Error al cargar compra: {e}")
                self.current_compra = None

    def edit_compra(self):
        """Carga la compra seleccionada en el formulario para editar"""
        if not self.current_compra:
            messagebox.showwarning("Advertencia", "Seleccione una compra para editar")
            return

        try:
            # Guardar referencia antes de limpiar campos
            compra_a_editar = self.current_compra

            # Cargar datos frescos de la base de datos
            compra_actualizada = Compra.get_by_id(compra_a_editar.id)

            # Limpiar solo los campos, mantener current_compra
            self.producto_entry.delete(0, tk.END)
            self.costo_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
            self.merma_entry.delete(0, tk.END)

            # Cargar datos de la compra
            self.producto_entry.insert(0, compra_actualizada.producto_nombre)
            self.costo_entry.insert(0, str(compra_actualizada.costo_total))
            self.cantidad_entry.insert(0, str(compra_actualizada.cantidad_elementos))
            self.merma_entry.insert(0, str(compra_actualizada.merma))

            # Establecer fecha en los selectores
            self.set_fecha_in_selectores(compra_actualizada.fecha_compra)

            # Mantener la referencia
            self.current_compra = compra_actualizada
            self.producto_entry.focus()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la compra: {str(e)}")

    def save_compra(self):
        """Guarda la compra (crea o actualiza)"""
        # Validar campos requeridos
        producto_nombre = self.producto_entry.get().strip()
        if not producto_nombre:
            messagebox.showwarning("Advertencia", "El nombre del producto es requerido")
            return

        try:
            # Obtener datos del formulario
            costo_total = float(self.costo_entry.get() or 0)
            cantidad_elementos = int(self.cantidad_entry.get() or 0)
            merma = int(self.merma_entry.get() or 0)

            # Obtener fecha desde selectores
            fecha_compra = self.get_fecha_from_selectores()
            if fecha_compra is None:
                messagebox.showwarning(
                    "Advertencia",
                    "Fecha inválida. Por favor seleccione una fecha válida.",
                )
                return

            # Validaciones básicas
            if costo_total <= 0:
                messagebox.showwarning(
                    "Advertencia", "El costo total debe ser mayor a 0"
                )
                return

            if cantidad_elementos <= 0:
                messagebox.showwarning(
                    "Advertencia", "La cantidad de elementos debe ser mayor a 0"
                )
                return

            if merma < 0:
                messagebox.showwarning("Advertencia", "La merma no puede ser negativa")
                return

            if merma > cantidad_elementos:
                if not messagebox.askyesno(
                    "Confirmar",
                    f"La merma ({merma}) es mayor que la cantidad total ({cantidad_elementos}). ¿Desea continuar?",
                ):
                    return

            # DEBUG: Verificar current_compra
            print(f"DEBUG - save_compra: current_compra = {self.current_compra}")
            print(
                f"DEBUG - save_compra: tiene id? = {self.current_compra.id if self.current_compra else 'No hay current_compra'}"
            )

            if self.current_compra and self.current_compra.id:
                print(f"DEBUG - Actualizando compra ID: {self.current_compra.id}")
                # Actualizar compra existente
                self.current_compra.producto_nombre = producto_nombre
                self.current_compra.costo_total = costo_total
                self.current_compra.cantidad_elementos = cantidad_elementos
                self.current_compra.merma = merma
                self.current_compra.fecha_compra = fecha_compra
                self.current_compra.save()
                messagebox.showinfo("Éxito", "Compra actualizada correctamente")
            else:
                print("DEBUG - Creando nueva compra")
                # Crear nueva compra
                nueva_compra = Compra(
                    producto_nombre=producto_nombre,
                    costo_total=costo_total,
                    cantidad_elementos=cantidad_elementos,
                    merma=merma,
                    fecha_compra=fecha_compra,
                )
                nueva_compra.save()
                messagebox.showinfo("Éxito", "Compra creada correctamente")

            # Limpiar y actualizar
            self.current_compra = None  # Limpiar referencia después de guardar
            self.clear_form()
            self.load_compras()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la compra: {str(e)}")

    def delete_compra(self):
        """Elimina la compra seleccionada"""
        if not self.current_compra:
            messagebox.showwarning("Advertencia", "Seleccione una compra para eliminar")
            return

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la compra de '{self.current_compra.producto_nombre}'?",
        ):
            try:
                # Si el producto que vamos a eliminar es el current_compra, limpiarlo
                if self.current_compra:
                    self.current_compra.delete()
                    self.current_compra = None
                    self.clear_form()

                messagebox.showinfo("Éxito", "Compra eliminada correctamente")
                self.load_compras()  # Recargar la lista
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar la compra: {str(e)}"
                )


def main():
    root = tk.Tk()
    app = ComprasWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
