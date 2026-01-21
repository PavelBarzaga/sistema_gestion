"""
Módulo para gestión de Ventas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Venta, Semana, Producto


class VentasWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Ventas")
        self.root.geometry("1000x700")

        # Variables
        self.current_venta = None
        self.cantidad_anterior = 0  # Para manejar actualizaciones de inventario
        self.semanas = Semana.get_all()
        self.productos = Producto.get_all()

        # Inicializar widgets primero
        self.info_label = None
        self.inventario_label = None

        # Crear interfaz
        self.create_widgets()

        # Cargar ventas iniciales
        self.load_ventas()

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
        form_frame = ttk.LabelFrame(main_frame, text="Datos de la Venta", padding="15")
        form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Campo: Semana
        ttk.Label(form_frame, text="Semana:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )

        self.semana_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.semana_combo.grid(row=0, column=1, pady=5, sticky=tk.W)

        # Campo: Producto
        ttk.Label(form_frame, text="Producto:").grid(
            row=0, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )

        self.producto_combo = ttk.Combobox(form_frame, state="readonly", width=30)
        self.producto_combo.grid(row=0, column=3, pady=5, sticky=tk.W)

        # Cargar datos en comboboxes
        self.load_semanas_combo()
        self.load_productos_combo()

        # Campo: Cantidad Vendida
        ttk.Label(form_frame, text="Cantidad Vendida:").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )

        cantidad_frame = ttk.Frame(form_frame)
        cantidad_frame.grid(row=1, column=1, pady=5, sticky=tk.W)

        self.cantidad_entry = ttk.Entry(cantidad_frame, width=15)
        self.cantidad_entry.pack(side=tk.LEFT)

        # Etiqueta de inventario disponible
        self.inventario_label = ttk.Label(cantidad_frame, text="(Disponible: 0)")
        self.inventario_label.pack(side=tk.LEFT, padx=(10, 0))

        # Campo: Monto (Ganancia Total)
        ttk.Label(form_frame, text="Monto (Ganancia Total):").grid(
            row=1, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )

        monto_frame = ttk.Frame(form_frame)
        monto_frame.grid(row=1, column=3, pady=5, sticky=tk.W)

        self.monto_entry = ttk.Entry(monto_frame, width=15)
        self.monto_entry.pack(side=tk.LEFT)

        ttk.Label(monto_frame, text=" $").pack(side=tk.LEFT, padx=(5, 0))

        # Información del producto seleccionado
        self.info_frame = ttk.Frame(form_frame)
        self.info_frame.grid(
            row=2, column=0, columnspan=4, pady=(10, 0), sticky=(tk.W, tk.E)
        )

        self.info_label = ttk.Label(
            self.info_frame,
            text="Seleccione un producto para ver detalles",
            font=("Arial", 9),
        )
        self.info_label.pack()

        # Bind para cambio de producto
        self.producto_combo.bind("<<ComboboxSelected>>", self.on_producto_selected)

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=(15, 0))

        ttk.Button(buttons_frame, text="Guardar", command=self.save_venta).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Nuevo", command=self.new_venta).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Cancelar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTA ==========
        # Frame para la lista
        lista_frame = ttk.LabelFrame(
            main_frame, text="Ventas Registradas", padding="10"
        )
        lista_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        # Treeview (tabla) para mostrar ventas
        columns = (
            "ID",
            "Semana",
            "Producto",
            "Cantidad",
            "Monto",
            "Inventario Restante",
        )

        self.tree = ttk.Treeview(
            lista_frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_configs = [
            ("ID", 50, "center"),
            ("Semana", 120, "center"),
            ("Producto", 200, "w"),
            ("Cantidad", 100, "e"),
            ("Monto", 120, "e"),
            ("Inventario Restante", 120, "e"),
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
        self.tree.bind("<<TreeviewSelect>>", self.on_venta_select)

        # ========== BOTONES DE ACCIÓN ==========
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(action_frame, text="Editar", command=self.edit_venta).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Eliminar", command=self.delete_venta).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Actualizar Lista", command=self.load_ventas
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cerrar", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def load_semanas_combo(self):
        """Carga las semanas en el combobox"""
        if self.semanas:
            semanas_info = []
            for semana in self.semanas:
                info = f"Semana {semana.numero}: {semana.fecha_inicio.strftime('%d/%m/%Y')} - {semana.fecha_fin.strftime('%d/%m/%Y')}"
                semanas_info.append((semana.id, info))

            self.semana_combo["values"] = [info for _, info in semanas_info]
            if semanas_info:
                self.semana_combo.current(0)
        else:
            self.semana_combo["values"] = ["No hay semanas configuradas"]

    def load_productos_combo(self):
        """Carga los productos en el combobox"""
        if self.productos:
            productos_info = []
            for producto in self.productos:
                info = f"{producto.nombre} (Stock: {producto.cantidad}, Precio: ${producto.precio_venta:.2f})"
                productos_info.append((producto.id, info))

            self.producto_combo["values"] = [info for _, info in productos_info]
            if productos_info:
                self.producto_combo.current(0)
                # Actualizar información del primer producto
                self.actualizar_info_producto(self.productos[0])
        else:
            self.producto_combo["values"] = ["No hay productos registrados"]

    def on_producto_selected(self, event):
        """Cuando se selecciona un producto en el combobox"""
        producto_id = self.get_producto_id_from_combo()
        if producto_id:
            producto = Producto.get_by_id(producto_id)
            if producto:
                self.actualizar_info_producto(producto)

    def get_semana_id_from_combo(self):
        """Obtiene el ID de la semana seleccionada en el combobox"""
        try:
            selected_text = self.semana_combo.get()
            for semana in self.semanas:
                info = f"Semana {semana.numero}: {semana.fecha_inicio.strftime('%d/%m/%Y')} - {semana.fecha_fin.strftime('%d/%m/%Y')}"
                if info == selected_text:
                    return semana.id
            return None
        except:
            return None

    def get_producto_id_from_combo(self):
        """Obtiene el ID del producto seleccionado en el combobox"""
        try:
            selected_text = self.producto_combo.get()
            for producto in self.productos:
                info = f"{producto.nombre} (Stock: {producto.cantidad}, Precio: ${producto.precio_venta:.2f})"
                if info == selected_text:
                    return producto.id
            return None
        except:
            return None

    def actualizar_info_producto(self, producto):
        """Actualiza la información del producto seleccionado"""
        if producto and hasattr(self, "info_label") and self.info_label:
            info_text = (
                f"Producto: {producto.nombre} | "
                f"Categoría: {producto.categoria.nombre if producto.categoria else 'N/A'} | "
                f"Costo: ${producto.costo:.2f} | "
                f"Precio Venta: ${producto.precio_venta:.2f} | "
                f"Margen: ${producto.precio_venta - producto.costo:.2f}"
            )
            self.info_label.config(text=info_text)

            if hasattr(self, "inventario_label") and self.inventario_label:
                self.inventario_label.config(text=f"(Disponible: {producto.cantidad})")

    def clear_form_campos(self):
        """Limpia solo los campos del formulario, no current_venta"""
        self.cantidad_entry.delete(0, tk.END)
        self.monto_entry.delete(0, tk.END)
        self.cantidad_anterior = 0

        # Restaurar selecciones por defecto
        if self.semanas:
            self.semana_combo.current(0)
        if self.productos:
            self.producto_combo.current(0)
            self.actualizar_info_producto(self.productos[0])

    def clear_form(self):
        """Limpia completamente el formulario"""
        self.current_venta = None
        self.cantidad_anterior = 0
        self.clear_form_campos()

    def new_venta(self):
        """Prepara el formulario para una nueva venta"""
        self.clear_form()

    def load_ventas(self):
        """Carga todas las ventas en el Treeview"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            ventas = Venta.get_all()

            if not ventas:
                return

            for venta in ventas:
                # Obtener información de semana y producto
                semana = venta.semana
                producto = venta.producto

                if semana and producto:
                    semana_info = f"Semana {semana.numero}"
                    producto_info = producto.nombre
                    inventario_restante = producto.cantidad

                    self.tree.insert(
                        "",
                        tk.END,
                        values=(
                            venta.id,
                            semana_info,
                            producto_info,
                            venta.cantidad_vendida,
                            f"${venta.monto:.2f}",
                            inventario_restante,
                        ),
                    )

        except Exception as e:
            print(f"Error al cargar ventas: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar las ventas: {str(e)}")

    def on_venta_select(self, event):
        """Cuando se selecciona una venta en la lista"""
        selection = self.tree.selection()
        if selection:
            try:
                item = self.tree.item(selection[0])
                venta_id = item["values"][0]
                # Cargar la venta completa de la base de datos
                self.current_venta = Venta.get_by_id(venta_id)
            except Exception as e:
                print(f"Error al cargar venta: {e}")
                self.current_venta = None

    def edit_venta(self):
        """Carga la venta seleccionada en el formulario para editar"""
        if not self.current_venta:
            messagebox.showwarning("Advertencia", "Seleccione una venta para editar")
            return

        try:
            # Guardar referencia y cantidad anterior
            venta_a_editar = self.current_venta
            self.cantidad_anterior = venta_a_editar.cantidad_vendida

            # Cargar datos frescos de la base de datos
            venta_actualizada = Venta.get_by_id(venta_a_editar.id)

            # Limpiar solo los campos, mantener current_venta
            self.cantidad_entry.delete(0, tk.END)
            self.monto_entry.delete(0, tk.END)

            # Cargar datos de la venta
            self.cantidad_entry.insert(0, str(venta_actualizada.cantidad_vendida))
            self.monto_entry.insert(0, str(venta_actualizada.monto))

            # Seleccionar semana en combobox
            semana = venta_actualizada.semana
            if semana and self.semanas:
                for i, s in enumerate(self.semanas):
                    if s.id == semana.id:
                        self.semana_combo.current(i)
                        break

            # Seleccionar producto en combobox y mostrar información
            producto = venta_actualizada.producto
            if producto and self.productos:
                # Primero actualizar la lista de productos (por si cambió el inventario)
                self.productos = Producto.get_all()
                self.load_productos_combo()

                # Buscar el producto en la lista actualizada
                for i, p in enumerate(self.productos):
                    if p.id == producto.id:
                        self.producto_combo.current(i)
                        self.actualizar_info_producto(p)
                        break

            # Mantener la referencia
            self.current_venta = venta_actualizada
            self.cantidad_entry.focus()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la venta: {str(e)}")

    def save_venta(self):
        """Guarda la venta (crea o actualiza)"""
        try:
            # Obtener IDs desde los comboboxes
            semana_id = self.get_semana_id_from_combo()
            producto_id = self.get_producto_id_from_combo()

            # Validaciones básicas
            if not semana_id:
                messagebox.showwarning("Advertencia", "Seleccione una semana válida")
                return

            if not producto_id:
                messagebox.showwarning("Advertencia", "Seleccione un producto válido")
                return

            # Obtener datos del formulario
            try:
                cantidad_vendida = int(self.cantidad_entry.get() or 0)
                monto = float(self.monto_entry.get() or 0)
            except ValueError:
                messagebox.showerror(
                    "Error", "Por favor ingrese valores numéricos válidos"
                )
                return

            # Validaciones
            if cantidad_vendida <= 0:
                messagebox.showwarning(
                    "Advertencia", "La cantidad vendida debe ser mayor a 0"
                )
                return

            if monto <= 0:
                messagebox.showwarning("Advertencia", "El monto debe ser mayor a 0")
                return

            # DEBUG: Verificar current_venta
            print(f"DEBUG - save_venta: current_venta = {self.current_venta}")
            print(
                f"DEBUG - save_venta: tiene id? = {self.current_venta.id if self.current_venta else 'No hay current_venta'}"
            )
            print(f"DEBUG - save_venta: cantidad_anterior = {self.cantidad_anterior}")

            if self.current_venta and self.current_venta.id:
                print(f"DEBUG - Actualizando venta ID: {self.current_venta.id}")
                # Actualizar venta existente
                self.current_venta.semana_id = semana_id
                self.current_venta.producto_id = producto_id
                self.current_venta.cantidad_vendida = cantidad_vendida
                self.current_venta.monto = monto

                self.current_venta.save(
                    es_actualizacion=True, cantidad_anterior=self.cantidad_anterior
                )
                messagebox.showinfo("Éxito", "Venta actualizada correctamente")
            else:
                print("DEBUG - Creando nueva venta")
                # Crear nueva venta
                nueva_venta = Venta(
                    semana_id=semana_id,
                    producto_id=producto_id,
                    cantidad_vendida=cantidad_vendida,
                    monto=monto,
                )
                nueva_venta.save()
                messagebox.showinfo("Éxito", "Venta creada correctamente")

            # Refrescar datos
            self.refrescar_datos()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la venta: {str(e)}")

    def refrescar_datos(self):
        """Refresca todos los datos después de una operación"""
        try:
            # Actualizar listas
            self.semanas = Semana.get_all()
            self.productos = Producto.get_all()

            # Actualizar comboboxes
            self.load_semanas_combo()
            self.load_productos_combo()

            # Limpiar formulario
            self.clear_form()

            # Recargar lista de ventas
            self.load_ventas()

        except Exception as e:
            print(f"Error al refrescar datos: {e}")
            # Continuar aunque haya error en refresco

    def delete_venta(self):
        """Elimina la venta seleccionada"""
        if not self.current_venta:
            messagebox.showwarning("Advertencia", "Seleccione una venta para eliminar")
            return

        # Obtener información para el mensaje de confirmación
        producto = self.current_venta.producto
        semana = self.current_venta.semana

        producto_nombre = producto.nombre if producto else "Desconocido"
        semana_info = f"Semana {semana.numero}" if semana else "Desconocida"

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar la venta de '{producto_nombre}' de la {semana_info}?\n\n"
            f"Cantidad: {self.current_venta.cantidad_vendida} | Monto: ${self.current_venta.monto:.2f}\n\n"
            f"Nota: La cantidad será devuelta al inventario.",
        ):
            try:
                self.current_venta.delete()
                messagebox.showinfo("Éxito", "Venta eliminada correctamente")

                # Refrescar datos
                self.refrescar_datos()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la venta: {str(e)}")


def main():
    root = tk.Tk()
    app = VentasWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
