"""
Módulo para gestión de Productos - CRUD completo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Producto, Categoria


class ProductosWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Productos")
        self.root.geometry("1000x700")

        # Variables
        self.current_producto = None
        self.categorias = Categoria.get_all()

        # Crear interfaz
        self.create_widgets()

        # Cargar productos iniciales
        self.load_productos()

    def create_widgets(self):
        """Crea todos los widgets de la ventana"""

        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # ========== SECCIÓN DE FORMULARIO ==========
        form_frame = ttk.LabelFrame(main_frame, text="Datos del Producto", padding="15")
        form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Campo: Nombre
        ttk.Label(form_frame, text="Nombre del Producto:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.nombre_entry = ttk.Entry(form_frame, width=30)
        self.nombre_entry.grid(
            row=0, column=1, pady=5, sticky=(tk.W, tk.E), columnspan=3
        )

        # Campo: Categoría
        ttk.Label(form_frame, text="Categoría:").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.categoria_combo = ttk.Combobox(form_frame, state="readonly", width=27)
        self.categoria_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        self.load_categorias_combo()

        # Campos: Costo, Precio de Venta y Cantidad en la misma línea
        ttk.Label(form_frame, text="Costo:").grid(
            row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.costo_entry = ttk.Entry(form_frame, width=15)
        self.costo_entry.grid(row=2, column=1, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text="Precio de Venta:").grid(
            row=2, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )
        self.precio_entry = ttk.Entry(form_frame, width=15)
        self.precio_entry.grid(row=2, column=3, pady=5, sticky=tk.W)

        ttk.Label(form_frame, text="Cantidad:").grid(
            row=3, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.cantidad_entry = ttk.Entry(form_frame, width=15)
        self.cantidad_entry.grid(row=3, column=1, pady=5, sticky=tk.W)

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=4, column=0, columnspan=4, pady=(15, 0))

        ttk.Button(buttons_frame, text="Guardar", command=self.save_producto).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Nuevo", command=self.new_producto).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Cancelar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTA ==========
        # Frame con scrollbar para la lista
        lista_container = ttk.Frame(main_frame)
        lista_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lista_container.columnconfigure(0, weight=1)
        lista_container.rowconfigure(0, weight=1)

        # Canvas y scrollbar para lista larga
        canvas = tk.Canvas(lista_container)
        scrollbar = ttk.Scrollbar(
            lista_container, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Ubicar widgets
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Lista de productos agrupados por categoría
        self.lista_frame = scrollable_frame
        self.lista_frame.columnconfigure(0, weight=1)

    def load_categorias_combo(self):
        """Carga las categorías en el combobox"""
        categorias_nombres = [cat.nombre for cat in self.categorias]
        self.categoria_combo["values"] = categorias_nombres
        if categorias_nombres:
            self.categoria_combo.current(0)

    def clear_form(self):
        """Limpia solo los campos del formulario, mantiene current_producto si existe"""
        # Solo limpia los campos de entrada, no cambia current_producto
        self.nombre_entry.delete(0, tk.END)
        self.costo_entry.delete(0, tk.END)
        self.precio_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        if self.categorias:
            self.categoria_combo.current(0)

    def new_producto(self):
        """Prepara el formulario para un nuevo producto"""
        self.current_producto = None  # Importante: establecer a None para nuevo
        self.clear_form()
        self.nombre_entry.focus()

    def load_productos(self):
        """Carga y muestra todos los productos agrupados por categoría"""

        # Limpiar lista actual
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        try:
            # Obtener productos agrupados por categoría
            productos_agrupados = Producto.get_productos_agrupados_por_categoria()

            if not productos_agrupados:
                ttk.Label(
                    self.lista_frame,
                    text="No hay productos registrados",
                    font=("Arial", 12),
                ).grid(row=0, column=0, pady=20)
                return

            row_index = 0

            for categoria, productos in productos_agrupados:
                # Calcular total de productos en esta categoría
                total_categoria = sum(p.cantidad for p in productos)

                # Frame para la categoría
                cat_frame = ttk.LabelFrame(
                    self.lista_frame,
                    text=f"{categoria.nombre} - Total de Productos: {total_categoria}",
                    padding="10",
                )
                cat_frame.grid(
                    row=row_index, column=0, sticky=(tk.W, tk.E), pady=(0, 15)
                )
                cat_frame.columnconfigure(0, weight=1)

                # Encabezados de la tabla
                headers_frame = ttk.Frame(cat_frame)
                headers_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

                # Configurar anchos de columnas y alineación
                # Columna 0: Nombre (25 caracteres)
                ttk.Label(
                    headers_frame,
                    text="Nombre",
                    font=("Arial", 10, "bold"),
                    width=25,
                    anchor="w",
                ).grid(row=0, column=0, padx=5, sticky=tk.W)

                # Columna 1: Costo (12 caracteres, centrado)
                ttk.Label(
                    headers_frame,
                    text="Costo",
                    font=("Arial", 10, "bold"),
                    width=12,
                    anchor="center",
                ).grid(row=0, column=1, padx=5, sticky=tk.EW)

                # Columna 2: Precio Venta (12 caracteres, centrado)
                ttk.Label(
                    headers_frame,
                    text="Precio Venta",
                    font=("Arial", 10, "bold"),
                    width=12,
                    anchor="center",
                ).grid(row=0, column=2, padx=5, sticky=tk.EW)

                # Columna 3: Margen Bruto (12 caracteres, centrado)
                ttk.Label(
                    headers_frame,
                    text="Margen Bruto",
                    font=("Arial", 10, "bold"),
                    width=12,
                    anchor="center",
                ).grid(row=0, column=3, padx=5, sticky=tk.EW)

                # Columna 4: Cantidad (10 caracteres, centrado)
                ttk.Label(
                    headers_frame,
                    text="Cantidad",
                    font=("Arial", 10, "bold"),
                    width=10,
                    anchor="center",
                ).grid(row=0, column=4, padx=5, sticky=tk.EW)

                # Columna 5: Acciones (20 caracteres, centrado)
                ttk.Label(
                    headers_frame,
                    text="Acciones",
                    font=("Arial", 10, "bold"),
                    width=20,
                    anchor="center",
                ).grid(row=0, column=5, padx=5, sticky=tk.EW)

                # Configurar expansión uniforme de columnas
                for i in range(6):
                    headers_frame.columnconfigure(i, weight=1, uniform="headers")

                # Productos de esta categoría
                for i, producto in enumerate(productos, 1):
                    prod_frame = ttk.Frame(cat_frame)
                    prod_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)

                    # Configurar expansión uniforme para las columnas del producto
                    for col in range(6):
                        prod_frame.columnconfigure(col, weight=1, uniform="prod_cols")

                    # Nombre (alineado a la izquierda)
                    nombre_label = ttk.Label(
                        prod_frame, text=producto.nombre, width=25, anchor="w"
                    )
                    nombre_label.grid(row=0, column=0, padx=5, sticky=tk.W)

                    # Costo (alineado a la derecha para números)
                    costo_text = f"{producto.costo:.2f}"
                    costo_label = ttk.Label(
                        prod_frame, text=costo_text, width=12, anchor="e"
                    )
                    costo_label.grid(row=0, column=1, padx=5, sticky=tk.E)

                    # Precio de venta (alineado a la derecha)
                    precio_text = f"{producto.precio_venta:.2f}"
                    precio_label = ttk.Label(
                        prod_frame, text=precio_text, width=12, anchor="e"
                    )
                    precio_label.grid(row=0, column=2, padx=5, sticky=tk.E)

                    # Margen bruto (alineado a la derecha)
                    margen = producto.precio_venta - producto.costo
                    margen_text = f"{margen:.2f}"
                    margen_label = ttk.Label(
                        prod_frame, text=margen_text, width=12, anchor="e"
                    )
                    margen_label.grid(row=0, column=3, padx=5, sticky=tk.E)

                    # Cantidad (alineado a la derecha)
                    cantidad_label = ttk.Label(
                        prod_frame, text=str(producto.cantidad), width=10, anchor="e"
                    )
                    cantidad_label.grid(row=0, column=4, padx=5, sticky=tk.E)

                    # Botones de acciones (centrados)
                    actions_frame = ttk.Frame(prod_frame)
                    actions_frame.grid(row=0, column=5, padx=5, sticky=tk.EW)

                    # Centrar los botones en el frame
                    actions_frame.columnconfigure(0, weight=1)
                    actions_frame.columnconfigure(1, weight=1)

                    edit_btn = ttk.Button(
                        actions_frame,
                        text="Editar",
                        width=8,
                        command=lambda p=producto: self.edit_producto_from_list(p),
                    )
                    edit_btn.grid(row=0, column=0, padx=2)

                    delete_btn = ttk.Button(
                        actions_frame,
                        text="Eliminar",
                        width=8,
                        command=lambda p=producto: self.delete_producto_from_list(p),
                    )
                    delete_btn.grid(row=0, column=1, padx=2)

                row_index += 1

        except Exception as e:
            print(f"Error al cargar productos: {e}")
            messagebox.showerror(
                "Error", f"No se pudieron cargar los productos: {str(e)}"
            )

    def edit_producto_from_list(self, producto):
        """Carga un producto de la lista en el formulario para editar"""
        # Primero guardamos la referencia al producto que vamos a editar
        self.current_producto = producto

        # Limpiar solo los campos del formulario (sin afectar current_producto)
        self.nombre_entry.delete(0, tk.END)
        self.costo_entry.delete(0, tk.END)
        self.precio_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)

        # Cargar datos del producto
        self.nombre_entry.insert(0, producto.nombre)
        self.costo_entry.insert(0, str(producto.costo))
        self.precio_entry.insert(0, str(producto.precio_venta))
        self.cantidad_entry.insert(0, str(producto.cantidad))

        # Seleccionar categoría en combobox
        categoria = producto.categoria
        if categoria:
            for i, cat in enumerate(self.categorias):
                if cat.id == categoria.id:
                    self.categoria_combo.current(i)
                    break

        # Enfocar el campo de nombre
        self.nombre_entry.focus()

        # Opcional: mostrar mensaje
        # messagebox.showinfo("Producto cargado", f"Producto '{producto.nombre}' cargado para edición")

    def delete_producto_from_list(self, producto):
        """Elimina un producto directamente desde la lista"""
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{producto.nombre}'?",
        ):
            try:
                # Si el producto que vamos a eliminar es el current_producto, limpiarlo
                if self.current_producto and self.current_producto.id == producto.id:
                    self.current_producto = None
                    self.clear_form()

                producto.delete()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.load_productos()  # Recargar la lista
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar el producto: {str(e)}"
                )

    def save_producto(self):
        """Guarda el producto (crea o actualiza) - margen se calcula automáticamente"""
        # Validar campos requeridos
        nombre = self.nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del producto es requerido")
            return

        try:
            # Obtener datos del formulario
            categoria_nombre = self.categoria_combo.get()
            categoria = next(
                (c for c in self.categorias if c.nombre == categoria_nombre), None
            )

            if not categoria:
                messagebox.showwarning("Advertencia", "Seleccione una categoría válida")
                return

            costo = float(self.costo_entry.get() or 0)
            precio_venta = float(self.precio_entry.get() or 0)
            cantidad = int(self.cantidad_entry.get() or 0)

            # Validaciones básicas
            if costo < 0 or precio_venta < 0 or cantidad < 0:
                messagebox.showwarning(
                    "Advertencia", "Los valores no pueden ser negativos"
                )
                return

            if precio_venta < costo:
                if not messagebox.askyesno(
                    "Confirmar",
                    "El precio de venta es menor que el costo. ¿Desea continuar?",
                ):
                    return

            # DEBUG: Verificar current_producto
            print(f"DEBUG - save_producto: current_producto = {self.current_producto}")
            print(
                f"DEBUG - save_producto: tiene id? = {self.current_producto.id if self.current_producto else 'No hay current_producto'}"
            )

            if self.current_producto and self.current_producto.id:
                print(f"DEBUG - Actualizando producto ID: {self.current_producto.id}")
                # Actualizar producto existente
                self.current_producto.nombre = nombre
                self.current_producto.categoria_id = categoria.id
                self.current_producto.costo = costo
                self.current_producto.precio_venta = precio_venta
                self.current_producto.cantidad = cantidad
                self.current_producto.save()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            else:
                print("DEBUG - Creando nuevo producto")
                # Crear nuevo producto - margen se calcula automáticamente en __init__
                nuevo_producto = Producto(
                    nombre=nombre,
                    categoria_id=categoria.id,
                    costo=costo,
                    precio_venta=precio_venta,
                    cantidad=cantidad,
                )
                nuevo_producto.save()
                messagebox.showinfo("Éxito", "Producto creado correctamente")

            # Limpiar y actualizar
            self.current_producto = None  # Limpiar referencia después de guardar
            self.clear_form()
            self.load_productos()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {str(e)}")

    def delete_producto(self):
        """Elimina el producto seleccionado desde el botón principal"""
        if not self.current_producto:
            messagebox.showwarning(
                "Advertencia", "Primero seleccione un producto de la lista"
            )
            return

        self.delete_producto_from_list(self.current_producto)


def main():
    root = tk.Tk()
    app = ProductosWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
