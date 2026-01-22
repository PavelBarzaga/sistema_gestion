"""
Módulo de Contabilidad - Gestión de cuentas y estadísticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from database import (
    CuentaCobrar,
    CuentaPagar,
    get_total_compras_rango,
    get_total_ventas_rango,
)


class ContabilidadWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Contabilidad")
        self.root.geometry("1100x700")

        # Variables para cuentas
        self.current_cuenta_cobrar = None
        self.current_cuenta_pagar = None

        # Variables para estadísticas
        self.fecha_inicio = None
        self.fecha_fin = None

        # Crear interfaz
        self.create_widgets()

        # Cargar datos iniciales
        self.load_cuentas_cobrar()
        self.load_cuentas_pagar()

    def create_widgets(self):
        """Crea todos los widgets de la ventana"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ========== PESTAÑA 1: CUENTAS ==========
        cuentas_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(cuentas_frame, text="Cuentas")

        cuentas_frame.columnconfigure(0, weight=1)
        cuentas_frame.columnconfigure(1, weight=1)
        cuentas_frame.rowconfigure(1, weight=1)

        # ===== SECCIÓN IZQUIERDA: CUENTAS POR COBRAR =====
        cobrar_frame = ttk.LabelFrame(
            cuentas_frame, text="Cuentas por Cobrar", padding="10"
        )
        cobrar_frame.grid(
            row=0, column=0, padx=(0, 5), pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        cobrar_frame.columnconfigure(0, weight=1)
        cobrar_frame.rowconfigure(1, weight=1)

        # Formulario para cuentas por cobrar
        cobrar_form_frame = ttk.Frame(cobrar_frame)
        cobrar_form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        cobrar_form_frame.columnconfigure(1, weight=1)

        # Campos del formulario
        ttk.Label(cobrar_form_frame, text="Nombre Persona:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.cobrar_nombre_entry = ttk.Entry(cobrar_form_frame, width=25)
        self.cobrar_nombre_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(cobrar_form_frame, text="Cantidad ($):").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.cobrar_cantidad_entry = ttk.Entry(cobrar_form_frame, width=15)
        self.cobrar_cantidad_entry.grid(row=1, column=1, pady=5, sticky=tk.W)

        ttk.Label(cobrar_form_frame, text="Descripción:").grid(
            row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.cobrar_desc_entry = ttk.Entry(cobrar_form_frame, width=25)
        self.cobrar_desc_entry.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))

        # Botones para cuentas por cobrar
        cobrar_buttons_frame = ttk.Frame(cobrar_frame)
        cobrar_buttons_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(
            cobrar_buttons_frame, text="Agregar", command=self.save_cuenta_cobrar
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            cobrar_buttons_frame, text="Nuevo", command=self.new_cuenta_cobrar
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            cobrar_buttons_frame, text="Limpiar", command=self.clear_cuenta_cobrar
        ).pack(side=tk.LEFT, padx=2)

        # Lista de cuentas por cobrar
        cobrar_list_frame = ttk.Frame(cobrar_frame)
        cobrar_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        cobrar_list_frame.columnconfigure(0, weight=1)
        cobrar_list_frame.rowconfigure(0, weight=1)

        self.tree_cobrar = ttk.Treeview(
            cobrar_list_frame,
            columns=("ID", "Persona", "Cantidad", "Descripción"),
            show="headings",
            height=10,
        )

        self.tree_cobrar.heading("ID", text="ID")
        self.tree_cobrar.heading("Persona", text="Persona")
        self.tree_cobrar.heading("Cantidad", text="Cantidad ($)")
        self.tree_cobrar.heading("Descripción", text="Descripción")

        self.tree_cobrar.column("ID", width=50, anchor="center")
        self.tree_cobrar.column("Persona", width=150, anchor="w")
        self.tree_cobrar.column("Cantidad", width=100, anchor="e")
        self.tree_cobrar.column("Descripción", width=200, anchor="w")

        scrollbar_cobrar = ttk.Scrollbar(
            cobrar_list_frame, orient=tk.VERTICAL, command=self.tree_cobrar.yview
        )
        self.tree_cobrar.configure(yscrollcommand=scrollbar_cobrar.set)

        self.tree_cobrar.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_cobrar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.tree_cobrar.bind("<<TreeviewSelect>>", self.on_cuenta_cobrar_select)

        # Total cuentas por cobrar
        self.total_cobrar_label = ttk.Label(
            cobrar_frame, text="Total por Cobrar: $0.00", font=("Arial", 10, "bold")
        )
        self.total_cobrar_label.grid(row=3, column=0, pady=(10, 0))

        # ===== SECCIÓN DERECHA: CUENTAS POR PAGAR =====
        pagar_frame = ttk.LabelFrame(
            cuentas_frame, text="Cuentas por Pagar", padding="10"
        )
        pagar_frame.grid(
            row=0, column=1, padx=(5, 0), pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        pagar_frame.columnconfigure(0, weight=1)
        pagar_frame.rowconfigure(1, weight=1)

        # Formulario para cuentas por pagar
        pagar_form_frame = ttk.Frame(pagar_frame)
        pagar_form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        pagar_form_frame.columnconfigure(1, weight=1)

        # Campos del formulario
        ttk.Label(pagar_form_frame, text="Nombre Proveedor:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.pagar_nombre_entry = ttk.Entry(pagar_form_frame, width=25)
        self.pagar_nombre_entry.grid(row=0, column=1, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(pagar_form_frame, text="Cantidad ($):").grid(
            row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.pagar_cantidad_entry = ttk.Entry(pagar_form_frame, width=15)
        self.pagar_cantidad_entry.grid(row=1, column=1, pady=5, sticky=tk.W)

        ttk.Label(pagar_form_frame, text="Descripción:").grid(
            row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )
        self.pagar_desc_entry = ttk.Entry(pagar_form_frame, width=25)
        self.pagar_desc_entry.grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))

        # Botones para cuentas por pagar
        pagar_buttons_frame = ttk.Frame(pagar_frame)
        pagar_buttons_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(
            pagar_buttons_frame, text="Agregar", command=self.save_cuenta_pagar
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            pagar_buttons_frame, text="Nuevo", command=self.new_cuenta_pagar
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            pagar_buttons_frame, text="Limpiar", command=self.clear_cuenta_pagar
        ).pack(side=tk.LEFT, padx=2)

        # Lista de cuentas por pagar
        pagar_list_frame = ttk.Frame(pagar_frame)
        pagar_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        pagar_list_frame.columnconfigure(0, weight=1)
        pagar_list_frame.rowconfigure(0, weight=1)

        self.tree_pagar = ttk.Treeview(
            pagar_list_frame,
            columns=("ID", "Proveedor", "Cantidad", "Descripción"),
            show="headings",
            height=10,
        )

        self.tree_pagar.heading("ID", text="ID")
        self.tree_pagar.heading("Proveedor", text="Proveedor")
        self.tree_pagar.heading("Cantidad", text="Cantidad ($)")
        self.tree_pagar.heading("Descripción", text="Descripción")

        self.tree_pagar.column("ID", width=50, anchor="center")
        self.tree_pagar.column("Proveedor", width=150, anchor="w")
        self.tree_pagar.column("Cantidad", width=100, anchor="e")
        self.tree_pagar.column("Descripción", width=200, anchor="w")

        scrollbar_pagar = ttk.Scrollbar(
            pagar_list_frame, orient=tk.VERTICAL, command=self.tree_pagar.yview
        )
        self.tree_pagar.configure(yscrollcommand=scrollbar_pagar.set)

        self.tree_pagar.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_pagar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.tree_pagar.bind("<<TreeviewSelect>>", self.on_cuenta_pagar_select)

        # Total cuentas por pagar
        self.total_pagar_label = ttk.Label(
            pagar_frame, text="Total por Pagar: $0.00", font=("Arial", 10, "bold")
        )
        self.total_pagar_label.grid(row=3, column=0, pady=(10, 0))

        # ===== BOTONES DE ACCIÓN PARA AMBAS LISTAS =====
        action_frame = ttk.Frame(cuentas_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            action_frame,
            text="Editar Cuenta por Cobrar",
            command=self.edit_cuenta_cobrar,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame,
            text="Eliminar Cuenta por Cobrar",
            command=self.delete_cuenta_cobrar,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(action_frame, text=" | ").pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame, text="Editar Cuenta por Pagar", command=self.edit_cuenta_pagar
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            action_frame,
            text="Eliminar Cuenta por Pagar",
            command=self.delete_cuenta_pagar,
        ).pack(side=tk.LEFT, padx=5)

        # ========== PESTAÑA 2: ESTADÍSTICAS ==========
        stats_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(stats_frame, text="Estadísticas")

        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(1, weight=1)

        # ===== SELECTOR DE FECHAS =====
        fecha_frame = ttk.LabelFrame(
            stats_frame, text="Seleccionar Rango de Fechas", padding="15"
        )
        fecha_frame.grid(row=0, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        fecha_frame.columnconfigure(1, weight=1)
        fecha_frame.columnconfigure(3, weight=1)

        # Fecha Inicio
        ttk.Label(fecha_frame, text="Fecha Inicio:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )

        self.fecha_inicio_frame = ttk.Frame(fecha_frame)
        self.fecha_inicio_frame.grid(row=0, column=1, pady=5, sticky=tk.W)

        self.inicio_dia_var = tk.StringVar()
        self.inicio_mes_var = tk.StringVar()
        self.inicio_anio_var = tk.StringVar()

        # Establecer fecha inicial (hace 30 días)
        fecha_inicio_default = datetime.now().date() - timedelta(days=30)

        # Días (1-31)
        dias = [str(i).zfill(2) for i in range(1, 32)]
        self.inicio_dia_combo = ttk.Combobox(
            self.fecha_inicio_frame,
            textvariable=self.inicio_dia_var,
            values=dias,
            width=3,
            state="readonly",
        )
        self.inicio_dia_combo.set(str(fecha_inicio_default.day).zfill(2))
        self.inicio_dia_combo.pack(side=tk.LEFT)
        ttk.Label(self.fecha_inicio_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Meses (1-12)
        meses = [str(i).zfill(2) for i in range(1, 13)]
        self.inicio_mes_combo = ttk.Combobox(
            self.fecha_inicio_frame,
            textvariable=self.inicio_mes_var,
            values=meses,
            width=3,
            state="readonly",
        )
        self.inicio_mes_combo.set(str(fecha_inicio_default.month).zfill(2))
        self.inicio_mes_combo.pack(side=tk.LEFT)
        ttk.Label(self.fecha_inicio_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Años (2020-2030)
        anios = [str(i) for i in range(2020, 2031)]
        self.inicio_anio_combo = ttk.Combobox(
            self.fecha_inicio_frame,
            textvariable=self.inicio_anio_var,
            values=anios,
            width=5,
            state="readonly",
        )
        self.inicio_anio_combo.set(str(fecha_inicio_default.year))
        self.inicio_anio_combo.pack(side=tk.LEFT)

        # Fecha Fin
        ttk.Label(fecha_frame, text="Fecha Fin:").grid(
            row=0, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )

        self.fecha_fin_frame = ttk.Frame(fecha_frame)
        self.fecha_fin_frame.grid(row=0, column=3, pady=5, sticky=tk.W)

        self.fin_dia_var = tk.StringVar()
        self.fin_mes_var = tk.StringVar()
        self.fin_anio_var = tk.StringVar()

        # Establecer fecha fin (hoy)
        fecha_fin_default = datetime.now().date()

        # Días (1-31)
        self.fin_dia_combo = ttk.Combobox(
            self.fecha_fin_frame,
            textvariable=self.fin_dia_var,
            values=dias,
            width=3,
            state="readonly",
        )
        self.fin_dia_combo.set(str(fecha_fin_default.day).zfill(2))
        self.fin_dia_combo.pack(side=tk.LEFT)
        ttk.Label(self.fecha_fin_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Meses (1-12)
        self.fin_mes_combo = ttk.Combobox(
            self.fecha_fin_frame,
            textvariable=self.fin_mes_var,
            values=meses,
            width=3,
            state="readonly",
        )
        self.fin_mes_combo.set(str(fecha_fin_default.month).zfill(2))
        self.fin_mes_combo.pack(side=tk.LEFT)
        ttk.Label(self.fecha_fin_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Años (2020-2030)
        self.fin_anio_combo = ttk.Combobox(
            self.fecha_fin_frame,
            textvariable=self.fin_anio_var,
            values=anios,
            width=5,
            state="readonly",
        )
        self.fin_anio_combo.set(str(fecha_fin_default.year))
        self.fin_anio_combo.pack(side=tk.LEFT)

        # Botón para calcular
        ttk.Button(
            fecha_frame,
            text="Calcular Estadísticas",
            command=self.calcular_estadisticas,
        ).grid(row=1, column=0, columnspan=4, pady=(15, 0))

        # ===== RESULTADOS =====
        resultados_frame = ttk.LabelFrame(stats_frame, text="Resultados", padding="20")
        resultados_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        resultados_frame.columnconfigure(0, weight=1)

        # Etiquetas para resultados
        self.total_compras_label = ttk.Label(
            resultados_frame, text="Total Compras: $0.00", font=("Arial", 12)
        )
        self.total_compras_label.pack(pady=10)

        self.total_ventas_label = ttk.Label(
            resultados_frame, text="Total Ventas: $0.00", font=("Arial", 12)
        )
        self.total_ventas_label.pack(pady=10)

        self.balance_label = ttk.Label(
            resultados_frame,
            text="Balance (Ventas - Compras): $0.00",
            font=("Arial", 14, "bold"),
        )
        self.balance_label.pack(pady=20)

        # Línea separadora
        ttk.Separator(resultados_frame, orient="horizontal").pack(fill=tk.X, pady=20)

        # Nota informativa
        nota_label = ttk.Label(
            resultados_frame,
            text="Nota: Las ventas se calculan basándose en las semanas que "
            "caen dentro del rango de fechas seleccionado.",
            font=("Arial", 9),
            wraplength=600,
            justify=tk.LEFT,
        )
        nota_label.pack(pady=10)

        # ========== PESTAÑA 3: MARGEN NETO ==========
        margen_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(margen_frame, text="Margen Neto")

        margen_frame.columnconfigure(0, weight=1)
        margen_frame.rowconfigure(2, weight=1)

        # ===== SELECTOR DE SEMANAS =====
        selector_frame = ttk.LabelFrame(
            margen_frame, text="Seleccionar Período", padding="15"
        )
        selector_frame.grid(row=0, column=0, pady=(0, 20), sticky=(tk.W, tk.E))

        # Radio buttons para tipo de período
        self.tipo_periodo_var = tk.StringVar(value="semana")

        ttk.Radiobutton(
            selector_frame,
            text="Una Semana",
            variable=self.tipo_periodo_var,
            value="semana",
            command=self.cambiar_tipo_periodo,
        ).grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)

        ttk.Radiobutton(
            selector_frame,
            text="Rango de Semanas",
            variable=self.tipo_periodo_var,
            value="rango",
            command=self.cambiar_tipo_periodo,
        ).grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)

        # Frame para selección de semana única
        self.semana_unica_frame = ttk.Frame(selector_frame)
        self.semana_unica_frame.grid(
            row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E)
        )

        ttk.Label(self.semana_unica_frame, text="Seleccionar Semana:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.semana_unica_combo = ttk.Combobox(
            self.semana_unica_frame, state="readonly", width=40
        )
        self.semana_unica_combo.pack(side=tk.LEFT)

        # Frame para rango de semanas (inicialmente oculto)
        self.rango_semanas_frame = ttk.Frame(selector_frame)
        self.rango_semanas_frame.grid(
            row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E)
        )
        self.rango_semanas_frame.grid_remove()  # Oculto inicialmente

        ttk.Label(self.rango_semanas_frame, text="Semana Inicio:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.semana_inicio_combo = ttk.Combobox(
            self.rango_semanas_frame, state="readonly", width=30
        )
        self.semana_inicio_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(self.rango_semanas_frame, text="Semana Fin:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.semana_fin_combo = ttk.Combobox(
            self.rango_semanas_frame, state="readonly", width=30
        )
        self.semana_fin_combo.pack(side=tk.LEFT)

        # Botón para calcular
        ttk.Button(
            selector_frame,
            text="Calcular Margen Neto",
            command=self.calcular_margen_neto,
        ).grid(row=2, column=0, columnspan=2, pady=(15, 0))

        # ===== RESULTADOS =====
        resultados_frame = ttk.LabelFrame(
            margen_frame, text="Resultados del Margen Neto", padding="20"
        )
        resultados_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        resultados_frame.columnconfigure(0, weight=1)

        # Etiquetas para resultados
        self.ventas_label = ttk.Label(
            resultados_frame, text="Total Ventas: $0.00", font=("Arial", 11)
        )
        self.ventas_label.pack(pady=5)

        self.costos_fijos_label = ttk.Label(
            resultados_frame, text="Costos Fijos (asignados): $0.00", font=("Arial", 11)
        )
        self.costos_fijos_label.pack(pady=5)

        self.costos_variables_label = ttk.Label(
            resultados_frame,
            text="Costos Variables (estimados): $0.00",
            font=("Arial", 11),
        )
        self.costos_variables_label.pack(pady=5)

        self.margen_neto_label = ttk.Label(
            resultados_frame, text="Margen Neto: $0.00", font=("Arial", 14, "bold")
        )
        self.margen_neto_label.pack(pady=15)

        self.porcentaje_margen_label = ttk.Label(
            resultados_frame, text="Porcentaje de Margen: 0.0%", font=("Arial", 12)
        )
        self.porcentaje_margen_label.pack(pady=5)

        # Línea separadora
        ttk.Separator(resultados_frame, orient="horizontal").pack(fill=tk.X, pady=20)

        # Configuración de porcentaje de costos variables
        config_frame = ttk.Frame(resultados_frame)
        config_frame.pack(pady=10)

        ttk.Label(config_frame, text="Porcentaje Costos Variables:").pack(
            side=tk.LEFT, padx=(0, 10)
        )
        self.porcentaje_var = tk.StringVar(value="30")
        self.porcentaje_spinbox = ttk.Spinbox(
            config_frame, from_=0, to=100, textvariable=self.porcentaje_var, width=5
        )
        self.porcentaje_spinbox.pack(side=tk.LEFT)
        ttk.Label(config_frame, text="%").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(
            config_frame,
            text="Actualizar Cálculo",
            command=self.actualizar_porcentaje_costos,
        ).pack(side=tk.LEFT)

        # Nota informativa
        nota_label = ttk.Label(
            resultados_frame,
            text="Nota: Los costos fijos se distribuyen semanalmente (mes/4.33). "
            "Los costos variables se estiman como porcentaje de las ventas.",
            font=("Arial", 9),
            wraplength=600,
            justify=tk.LEFT,
        )
        nota_label.pack(pady=10)

        # Cargar semanas en los comboboxes
        self.cargar_semanas_comboboxes()

        # ===== BOTÓN CERRAR =====
        close_frame = ttk.Frame(main_frame)
        close_frame.grid(row=1, column=0, pady=(10, 0))

        ttk.Button(close_frame, text="Cerrar", command=self.root.destroy).pack()

    # ========== MÉTODOS PARA CUENTAS POR COBRAR ==========

    def new_cuenta_cobrar(self):
        """Prepara el formulario para una nueva cuenta por cobrar"""
        self.current_cuenta_cobrar = None
        self.clear_cuenta_cobrar()

    def clear_cuenta_cobrar(self):
        """Limpia el formulario de cuentas por cobrar"""
        self.cobrar_nombre_entry.delete(0, tk.END)
        self.cobrar_cantidad_entry.delete(0, tk.END)
        self.cobrar_desc_entry.delete(0, tk.END)
        self.cobrar_nombre_entry.focus()

    def load_cuentas_cobrar(self):
        """Carga todas las cuentas por cobrar en el Treeview"""
        # Limpiar lista actual
        for item in self.tree_cobrar.get_children():
            self.tree_cobrar.delete(item)

        try:
            cuentas = CuentaCobrar.get_all()
            total = 0.0

            for cuenta in cuentas:
                self.tree_cobrar.insert(
                    "",
                    tk.END,
                    values=(
                        cuenta.id,
                        cuenta.nombre_persona,
                        f"{cuenta.cantidad:.2f}",
                        cuenta.descripcion or "",
                    ),
                )
                total += cuenta.cantidad

            self.total_cobrar_label.config(text=f"Total por Cobrar: ${total:.2f}")

        except Exception as e:
            print(f"Error al cargar cuentas por cobrar: {e}")

    def on_cuenta_cobrar_select(self, event):
        """Cuando se selecciona una cuenta por cobrar en la lista"""
        selection = self.tree_cobrar.selection()
        if selection:
            try:
                item = self.tree_cobrar.item(selection[0])
                cuenta_id = item["values"][0]
                self.current_cuenta_cobrar = CuentaCobrar.get_by_id(cuenta_id)
            except Exception as e:
                print(f"Error al cargar cuenta por cobrar: {e}")
                self.current_cuenta_cobrar = None

    def edit_cuenta_cobrar(self):
        """Carga la cuenta por cobrar seleccionada en el formulario para editar"""
        if not self.current_cuenta_cobrar:
            messagebox.showwarning(
                "Advertencia", "Seleccione una cuenta por cobrar para editar"
            )
            return

        try:
            # Cargar datos frescos
            self.current_cuenta_cobrar = CuentaCobrar.get_by_id(
                self.current_cuenta_cobrar.id
            )

            # Limpiar y cargar formulario
            self.clear_cuenta_cobrar()
            self.cobrar_nombre_entry.insert(
                0, self.current_cuenta_cobrar.nombre_persona
            )
            self.cobrar_cantidad_entry.insert(
                0, str(self.current_cuenta_cobrar.cantidad)
            )
            self.cobrar_desc_entry.insert(
                0, self.current_cuenta_cobrar.descripcion or ""
            )

            self.cobrar_nombre_entry.focus()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar la cuenta por cobrar: {str(e)}"
            )

    def save_cuenta_cobrar(self):
        """Guarda la cuenta por cobrar (crea o actualiza)"""
        # Validar campos requeridos
        nombre = self.cobrar_nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning(
                "Advertencia", "El nombre de la persona es requerido"
            )
            return

        try:
            cantidad = float(self.cobrar_cantidad_entry.get() or 0)
            descripcion = self.cobrar_desc_entry.get().strip()

            # Validaciones básicas
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return

            if self.current_cuenta_cobrar and self.current_cuenta_cobrar.id:
                # Actualizar cuenta existente
                self.current_cuenta_cobrar.nombre_persona = nombre
                self.current_cuenta_cobrar.cantidad = cantidad
                self.current_cuenta_cobrar.descripcion = descripcion
                self.current_cuenta_cobrar.save()
                messagebox.showinfo(
                    "Éxito", "Cuenta por cobrar actualizada correctamente"
                )
            else:
                # Crear nueva cuenta
                nueva_cuenta = CuentaCobrar(
                    nombre_persona=nombre, cantidad=cantidad, descripcion=descripcion
                )
                nueva_cuenta.save()
                messagebox.showinfo("Éxito", "Cuenta por cobrar creada correctamente")

            # Actualizar
            self.new_cuenta_cobrar()
            self.load_cuentas_cobrar()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida")
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar la cuenta por cobrar: {str(e)}"
            )

    def delete_cuenta_cobrar(self):
        """Elimina la cuenta por cobrar seleccionada"""
        if not self.current_cuenta_cobrar:
            messagebox.showwarning(
                "Advertencia", "Seleccione una cuenta por cobrar para eliminar"
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la cuenta por cobrar de '{self.current_cuenta_cobrar.nombre_persona}'?",
        ):
            try:
                self.current_cuenta_cobrar.delete()
                messagebox.showinfo(
                    "Éxito", "Cuenta por cobrar eliminada correctamente"
                )
                self.new_cuenta_cobrar()
                self.load_cuentas_cobrar()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar la cuenta por cobrar: {str(e)}"
                )

    # ========== MÉTODOS PARA CUENTAS POR PAGAR ==========

    def new_cuenta_pagar(self):
        """Prepara el formulario para una nueva cuenta por pagar"""
        self.current_cuenta_pagar = None
        self.clear_cuenta_pagar()

    def clear_cuenta_pagar(self):
        """Limpia el formulario de cuentas por pagar"""
        self.pagar_nombre_entry.delete(0, tk.END)
        self.pagar_cantidad_entry.delete(0, tk.END)
        self.pagar_desc_entry.delete(0, tk.END)
        self.pagar_nombre_entry.focus()

    def load_cuentas_pagar(self):
        """Carga todas las cuentas por pagar en el Treeview"""
        # Limpiar lista actual
        for item in self.tree_pagar.get_children():
            self.tree_pagar.delete(item)

        try:
            cuentas = CuentaPagar.get_all()
            total = 0.0

            for cuenta in cuentas:
                self.tree_pagar.insert(
                    "",
                    tk.END,
                    values=(
                        cuenta.id,
                        cuenta.nombre_proveedor,
                        f"{cuenta.cantidad:.2f}",
                        cuenta.descripcion or "",
                    ),
                )
                total += cuenta.cantidad

            self.total_pagar_label.config(text=f"Total por Pagar: ${total:.2f}")

        except Exception as e:
            print(f"Error al cargar cuentas por pagar: {e}")

    def on_cuenta_pagar_select(self, event):
        """Cuando se selecciona una cuenta por pagar en la lista"""
        selection = self.tree_pagar.selection()
        if selection:
            try:
                item = self.tree_pagar.item(selection[0])
                cuenta_id = item["values"][0]
                self.current_cuenta_pagar = CuentaPagar.get_by_id(cuenta_id)
            except Exception as e:
                print(f"Error al cargar cuenta por pagar: {e}")
                self.current_cuenta_pagar = None

    def edit_cuenta_pagar(self):
        """Carga la cuenta por pagar seleccionada en el formulario para editar"""
        if not self.current_cuenta_pagar:
            messagebox.showwarning(
                "Advertencia", "Seleccione una cuenta por pagar para editar"
            )
            return

        try:
            # Cargar datos frescos
            self.current_cuenta_pagar = CuentaPagar.get_by_id(
                self.current_cuenta_pagar.id
            )

            # Limpiar y cargar formulario
            self.clear_cuenta_pagar()
            self.pagar_nombre_entry.insert(
                0, self.current_cuenta_pagar.nombre_proveedor
            )
            self.pagar_cantidad_entry.insert(0, str(self.current_cuenta_pagar.cantidad))
            self.pagar_desc_entry.insert(0, self.current_cuenta_pagar.descripcion or "")

            self.pagar_nombre_entry.focus()

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo cargar la cuenta por pagar: {str(e)}"
            )

    def save_cuenta_pagar(self):
        """Guarda la cuenta por pagar (crea o actualiza)"""
        # Validar campos requeridos
        nombre = self.pagar_nombre_entry.get().strip()
        if not nombre:
            messagebox.showwarning(
                "Advertencia", "El nombre del proveedor es requerido"
            )
            return

        try:
            cantidad = float(self.pagar_cantidad_entry.get() or 0)
            descripcion = self.pagar_desc_entry.get().strip()

            # Validaciones básicas
            if cantidad <= 0:
                messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a 0")
                return

            if self.current_cuenta_pagar and self.current_cuenta_pagar.id:
                # Actualizar cuenta existente
                self.current_cuenta_pagar.nombre_proveedor = nombre
                self.current_cuenta_pagar.cantidad = cantidad
                self.current_cuenta_pagar.descripcion = descripcion
                self.current_cuenta_pagar.save()
                messagebox.showinfo(
                    "Éxito", "Cuenta por pagar actualizada correctamente"
                )
            else:
                # Crear nueva cuenta
                nueva_cuenta = CuentaPagar(
                    nombre_proveedor=nombre, cantidad=cantidad, descripcion=descripcion
                )
                nueva_cuenta.save()
                messagebox.showinfo("Éxito", "Cuenta por pagar creada correctamente")

            # Actualizar
            self.new_cuenta_pagar()
            self.load_cuentas_pagar()

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida")
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo guardar la cuenta por pagar: {str(e)}"
            )

    def delete_cuenta_pagar(self):
        """Elimina la cuenta por pagar seleccionada"""
        if not self.current_cuenta_pagar:
            messagebox.showwarning(
                "Advertencia", "Seleccione una cuenta por pagar para eliminar"
            )
            return

        if messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la cuenta por pagar de '{self.current_cuenta_pagar.nombre_proveedor}'?",
        ):
            try:
                self.current_cuenta_pagar.delete()
                messagebox.showinfo("Éxito", "Cuenta por pagar eliminada correctamente")
                self.new_cuenta_pagar()
                self.load_cuentas_pagar()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar la cuenta por pagar: {str(e)}"
                )

    # ========== MÉTODOS PARA ESTADÍSTICAS ==========

    def get_fecha_from_selectores(self, dia_var, mes_var, anio_var):
        """Obtiene la fecha desde los selectores y la valida"""
        try:
            dia = dia_var.get()
            mes = mes_var.get()
            anio = anio_var.get()

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

    def calcular_estadisticas(self):
        """Calcula las estadísticas basadas en el rango de fechas"""
        try:
            # Obtener fechas desde selectores
            fecha_inicio = self.get_fecha_from_selectores(
                self.inicio_dia_var, self.inicio_mes_var, self.inicio_anio_var
            )
            fecha_fin = self.get_fecha_from_selectores(
                self.fin_dia_var, self.fin_mes_var, self.fin_anio_var
            )

            # Validar fechas
            if not fecha_inicio or not fecha_fin:
                messagebox.showwarning(
                    "Advertencia", "Por favor seleccione fechas válidas"
                )
                return

            if fecha_inicio > fecha_fin:
                messagebox.showwarning(
                    "Advertencia",
                    "La fecha de inicio debe ser anterior a la fecha de fin",
                )
                return

            # Calcular totales
            total_compras = get_total_compras_rango(fecha_inicio, fecha_fin)
            total_ventas = get_total_ventas_rango(fecha_inicio, fecha_fin)
            balance = total_ventas - total_compras

            # Actualizar etiquetas
            self.total_compras_label.config(text=f"Total Compras: ${total_compras:.2f}")
            self.total_ventas_label.config(text=f"Total Ventas: ${total_ventas:.2f}")

            # Determinar color del balance
            balance_color = "green" if balance >= 0 else "red"
            self.balance_label.config(
                text=f"Balance (Ventas - Compras): ${balance:.2f}",
                foreground=balance_color,
            )

            # Mostrar rango de fechas en el título
            self.notebook.tab(
                1,
                text=f"Estadísticas ({fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')})",
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron calcular las estadísticas: {str(e)}"
            )

    # ========== MÉTODOS ADICIONALES ==========

    def cargar_semanas_comboboxes(self):
        """Carga las semanas en los comboboxes del margen neto"""
        try:
            from database import Semana

            semanas = Semana.get_all()

            if semanas:
                semanas_info = []
                for semana in semanas:
                    # CAMBIO AQUÍ: Formato "Semana: DD/MM/YYYY - DD/MM/YYYY"
                    info = f"Semana: {semana.fecha_inicio.strftime('%d/%m/%Y')} - {semana.fecha_fin.strftime('%d/%m/%Y')}"  # CAMBIADO
                    semanas_info.append((semana.id, info))

                semanas_values = [info for _, info in semanas_info]

                # Cargar en ambos comboboxes
                self.semana_unica_combo["values"] = semanas_values
                self.semana_inicio_combo["values"] = semanas_values
                self.semana_fin_combo["values"] = semanas_values

                if semanas_values:
                    self.semana_unica_combo.current(0)
                    self.semana_inicio_combo.current(0)
                    self.semana_fin_combo.current(min(1, len(semanas_values) - 1))

        except Exception as e:
            print(f"Error al cargar semanas: {e}")

    def cambiar_tipo_periodo(self):
        """Cambia entre semana única y rango de semanas"""
        if self.tipo_periodo_var.get() == "semana":
            self.semana_unica_frame.grid()
            self.rango_semanas_frame.grid_remove()
        else:
            self.semana_unica_frame.grid_remove()
            self.rango_semanas_frame.grid()

    def get_semana_id_from_combo_text(self, combo_text):
        """Obtiene el ID de semana desde el texto del combobox"""
        try:
            from database import Semana

            semanas = Semana.get_all()

            for semana in semanas:
                # CAMBIO AQUÍ: Coincidir con el nuevo formato
                info = f"Semana: {semana.fecha_inicio.strftime('%d/%m/%Y')} - {semana.fecha_fin.strftime('%d/%m/%Y')}"  # CAMBIADO
                if info == combo_text:
                    return semana.id
            return None
        except:
            return None

    def calcular_margen_neto(self):
        """Calcula el margen neto según la selección"""
        try:
            from database import get_margen_neto_semana, get_margen_neto_rango

            if self.tipo_periodo_var.get() == "semana":
                # Una semana
                semana_text = self.semana_unica_combo.get()
                semana_id = self.get_semana_id_from_combo_text(semana_text)

                if not semana_id:
                    messagebox.showwarning(
                        "Advertencia", "Seleccione una semana válida"
                    )
                    return

                resultado = get_margen_neto_semana(semana_id)

                if resultado:
                    self.mostrar_resultados_margen(resultado)
                else:
                    messagebox.showwarning(
                        "Información", "No hay datos para calcular el margen neto"
                    )

            else:
                # Rango de semanas
                inicio_text = self.semana_inicio_combo.get()
                fin_text = self.semana_fin_combo.get()

                semana_inicio_id = self.get_semana_id_from_combo_text(inicio_text)
                semana_fin_id = self.get_semana_id_from_combo_text(fin_text)

                if not semana_inicio_id or not semana_fin_id:
                    messagebox.showwarning("Advertencia", "Seleccione semanas válidas")
                    return

                if semana_inicio_id > semana_fin_id:
                    messagebox.showwarning(
                        "Advertencia",
                        "La semana inicio debe ser anterior a la semana fin",
                    )
                    return

                resultado = get_margen_neto_rango(semana_inicio_id, semana_fin_id)

                if resultado:
                    self.mostrar_resultados_margen(resultado)
                else:
                    messagebox.showwarning(
                        "Información", "No hay datos para calcular el margen neto"
                    )

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo calcular el margen neto: {str(e)}"
            )

    def mostrar_resultados_margen(self, resultado):
        """Muestra los resultados del cálculo de margen neto"""
        try:
            # Actualizar etiquetas
            self.ventas_label.config(
                text=f"Total Ventas: ${resultado['total_ventas']:.2f}"
            )

            if "costos_fijos_semanales" in resultado:
                # Una semana
                self.costos_fijos_label.config(
                    text=f"Costos Fijos (asignados semanales): ${resultado['costos_fijos_semanales']:.2f}"
                )
                self.costos_variables_label.config(
                    text=f"Costos Variables (estimados): ${resultado['costos_variables_semanales']:.2f}"
                )
            else:
                # Rango de semanas
                self.costos_fijos_label.config(
                    text=f"Costos Fijos (asignados para {resultado['num_semanas']} semanas): ${resultado['costos_fijos_totales']:.2f}"
                )
                self.costos_variables_label.config(
                    text=f"Costos Variables (estimados): ${resultado['costos_variables_totales']:.2f}"
                )

            # Determinar color del margen neto
            margen_color = "green" if resultado["margen_neto"] >= 0 else "red"
            self.margen_neto_label.config(
                text=f"Margen Neto: ${resultado['margen_neto']:.2f}",
                foreground=margen_color,
            )

            self.porcentaje_margen_label.config(
                text=f"Porcentaje de Margen: {resultado['porcentaje_margen']:.1f}%"
            )

            # Actualizar spinbox con el porcentaje usado
            self.porcentaje_var.set(str(resultado["porcentaje_costos_variables"]))

        except Exception as e:
            print(f"Error al mostrar resultados: {e}")

    def actualizar_porcentaje_costos(self):
        """Actualiza el cálculo con nuevo porcentaje de costos variables"""
        # Aquí podrías implementar la actualización del porcentaje
        # y recalcular el margen neto
        messagebox.showinfo(
            "Configuración",
            "Para cambiar el porcentaje permanentemente, "
            "se necesita modificar la configuración del sistema.",
        )


def main():
    root = tk.Tk()
    app = ContabilidadWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
