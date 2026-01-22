"""
Módulo para configuración de Semanas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from database import Semana


class ConfigSemanasWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurar Semanas")
        self.root.geometry("800x500")

        # Variables
        self.current_semana = None

        # Crear interfaz
        self.create_widgets()

        # Cargar semanas iniciales
        self.load_semanas()

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
        form_frame = ttk.LabelFrame(main_frame, text="Crear Nueva Semana", padding="15")
        form_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Campos: Fecha Inicio y Fecha Fin
        ttk.Label(form_frame, text="Fecha Inicio:").grid(
            row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W
        )

        inicio_frame = ttk.Frame(form_frame)
        inicio_frame.grid(row=0, column=1, pady=5, sticky=tk.W)

        # Selectores para fecha inicio
        self.inicio_dia_var = tk.StringVar()
        self.inicio_mes_var = tk.StringVar()
        self.inicio_anio_var = tk.StringVar()

        # Días (1-31)
        dias = [str(i).zfill(2) for i in range(1, 32)]
        self.inicio_dia_combo = ttk.Combobox(
            inicio_frame,
            textvariable=self.inicio_dia_var,
            values=dias,
            width=3,
            state="readonly",
        )
        self.inicio_dia_combo.pack(side=tk.LEFT)
        ttk.Label(inicio_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Meses (1-12)
        meses = [str(i).zfill(2) for i in range(1, 13)]
        self.inicio_mes_combo = ttk.Combobox(
            inicio_frame,
            textvariable=self.inicio_mes_var,
            values=meses,
            width=3,
            state="readonly",
        )
        self.inicio_mes_combo.pack(side=tk.LEFT)
        ttk.Label(inicio_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Años (2020-2030)
        anios = [str(i) for i in range(2020, 2031)]
        self.inicio_anio_combo = ttk.Combobox(
            inicio_frame,
            textvariable=self.inicio_anio_var,
            values=anios,
            width=5,
            state="readonly",
        )
        self.inicio_anio_combo.pack(side=tk.LEFT)

        # Botón para fecha actual
        ttk.Button(inicio_frame, text="Hoy", command=self.set_fecha_inicio_hoy).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        ttk.Label(form_frame, text="Fecha Fin:").grid(
            row=0, column=2, padx=(20, 10), pady=5, sticky=tk.W
        )

        fin_frame = ttk.Frame(form_frame)
        fin_frame.grid(row=0, column=3, pady=5, sticky=tk.W)

        # Selectores para fecha fin
        self.fin_dia_var = tk.StringVar()
        self.fin_mes_var = tk.StringVar()
        self.fin_anio_var = tk.StringVar()

        # Días (1-31)
        self.fin_dia_combo = ttk.Combobox(
            fin_frame,
            textvariable=self.fin_dia_var,
            values=dias,
            width=3,
            state="readonly",
        )
        self.fin_dia_combo.pack(side=tk.LEFT)
        ttk.Label(fin_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Meses (1-12)
        self.fin_mes_combo = ttk.Combobox(
            fin_frame,
            textvariable=self.fin_mes_var,
            values=meses,
            width=3,
            state="readonly",
        )
        self.fin_mes_combo.pack(side=tk.LEFT)
        ttk.Label(fin_frame, text="/").pack(side=tk.LEFT, padx=2)

        # Años (2020-2030)
        self.fin_anio_combo = ttk.Combobox(
            fin_frame,
            textvariable=self.fin_anio_var,
            values=anios,
            width=5,
            state="readonly",
        )
        self.fin_anio_combo.pack(side=tk.LEFT)

        # Botón para fecha actual + 6 días (semana completa)
        ttk.Button(fin_frame, text="+6 días", command=self.set_fecha_fin_semana).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # Información
        info_frame = ttk.Frame(form_frame)
        info_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))

        ttk.Label(
            info_frame, text="Nota: Las semanas no se pueden editar una vez creadas."
        ).pack()
        ttk.Label(
            info_frame,
            text="Cada semana debe tener 7 días y no puede solaparse con otras semanas.",
        ).pack()

        # Botones del formulario
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))

        ttk.Button(buttons_frame, text="Crear Semana", command=self.create_semana).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="Limpiar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # ========== SECCIÓN DE LISTA ==========
        # Frame para la lista
        lista_frame = ttk.LabelFrame(
            main_frame, text="Semanas Registradas", padding="10"
        )
        lista_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar expansión
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        # Treeview (tabla) para mostrar semanas
        columns = ("Fecha Inicio", "Fecha Fin", "Días")

        self.tree = ttk.Treeview(
            lista_frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_configs = [
            ("Fecha Inicio", 120, "center"),
            ("Fecha Fin", 120, "center"),
            ("Días", 80, "center"),
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
        self.tree.bind("<<TreeviewSelect>>", self.on_semana_select)

        # ========== BOTONES DE ACCIÓN ==========
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=(10, 0))

        # NO hay botón de Editar (intencionalmente)
        ttk.Button(action_frame, text="Eliminar", command=self.delete_semana).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Actualizar Lista", command=self.load_semanas
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cerrar", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

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

    def set_fecha_inicio_hoy(self):
        """Establece la fecha de inicio como hoy"""
        hoy = datetime.now().date()
        self.inicio_dia_var.set(str(hoy.day).zfill(2))
        self.inicio_mes_var.set(str(hoy.month).zfill(2))
        self.inicio_anio_var.set(str(hoy.year))

    def set_fecha_fin_semana(self):
        """Establece la fecha fin como inicio + 6 días (semana completa)"""
        # Primero obtener fecha inicio
        fecha_inicio = self.get_fecha_from_selectores(
            self.inicio_dia_var, self.inicio_mes_var, self.inicio_anio_var
        )

        if fecha_inicio:
            # Calcular fecha fin (inicio + 6 días)
            fecha_fin = fecha_inicio + timedelta(days=6)
            self.fin_dia_var.set(str(fecha_fin.day).zfill(2))
            self.fin_mes_var.set(str(fecha_fin.month).zfill(2))
            self.fin_anio_var.set(str(fecha_fin.year))
        else:
            # Si no hay fecha inicio, usar hoy + 6 días
            hoy = datetime.now().date()
            fecha_fin = hoy + timedelta(days=6)
            self.fin_dia_var.set(str(fecha_fin.day).zfill(2))
            self.fin_mes_var.set(str(fecha_fin.month).zfill(2))
            self.fin_anio_var.set(str(fecha_fin.year))

    def clear_form(self):
        """Limpia el formulario"""
        self.current_semana = None

        # Limpiar fecha inicio
        self.inicio_dia_var.set("")
        self.inicio_mes_var.set("")
        self.inicio_anio_var.set("")

        # Limpiar fecha fin
        self.fin_dia_var.set("")
        self.fin_mes_var.set("")
        self.fin_anio_var.set("")

    def load_semanas(self):
        """Carga todas las semanas en el Treeview"""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            semanas = Semana.get_all()

            if not semanas:
                return

            for semana in semanas:
                # Calcular número de días
                dias = (semana.fecha_fin - semana.fecha_inicio).days + 1

                # Formatear fechas
                inicio_str = semana.fecha_inicio.strftime("%d/%m/%Y")
                fin_str = semana.fecha_fin.strftime("%d/%m/%Y")

                # CAMBIO AQUÍ: Solo mostrar fechas y días, no ID ni número
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        # semana.id,  # REMOVIDO
                        # semana.numero,  # REMOVIDO
                        inicio_str,  # Ahora es columna 0
                        fin_str,  # Ahora es columna 1
                        f"{dias} días",  # Ahora es columna 2
                    ),
                )

        except Exception as e:
            print(f"Error al cargar semanas: {e}")
            messagebox.showerror(
                "Error", f"No se pudieron cargar las semanas: {str(e)}"
            )

    def on_semana_select(self, event):
        """Cuando se selecciona una semana en la lista"""
        selection = self.tree.selection()
        if selection:
            try:
                item = self.tree.item(selection[0])
                semana_id = item["values"][0]
                # Cargar la semana completa de la base de datos
                self.current_semana = Semana.get_by_id(semana_id)
            except Exception as e:
                print(f"Error al cargar semana: {e}")
                self.current_semana = None

    def create_semana(self):
        """Crea una nueva semana"""
        try:
            # Obtener fechas desde selectores
            fecha_inicio = self.get_fecha_from_selectores(
                self.inicio_dia_var, self.inicio_mes_var, self.inicio_anio_var
            )
            fecha_fin = self.get_fecha_from_selectores(
                self.fin_dia_var, self.fin_mes_var, self.fin_anio_var
            )

            # Validaciones básicas
            if fecha_inicio is None or fecha_fin is None:
                messagebox.showwarning(
                    "Advertencia", "Por favor complete ambas fechas correctamente"
                )
                return

            if fecha_inicio > fecha_fin:
                messagebox.showwarning(
                    "Advertencia",
                    "La fecha de inicio debe ser anterior o igual a la fecha de fin",
                )
                return

            # Calcular días de diferencia
            dias_diferencia = (fecha_fin - fecha_inicio).days + 1

            # Verificar que sea una semana completa (7 días)
            if dias_diferencia != 7:
                respuesta = messagebox.askyesno(
                    "Confirmar",
                    f"La semana tiene {dias_diferencia} días (no 7). ¿Desea continuar de todos modos?",
                )
                if not respuesta:
                    return

            # Crear objeto Semana
            nueva_semana = Semana(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

            # Guardar (esto verificará automáticamente solapamientos)
            nueva_semana.save()

            messagebox.showinfo(
                "Éxito",
                f"Semana creada correctamente:\n"
                f"Número: {nueva_semana.numero}\n"
                f"Del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}",
            )

            # Limpiar y actualizar
            self.clear_form()
            self.load_semanas()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la semana: {str(e)}")

    def delete_semana(self):
        """Elimina la semana seleccionada"""
        if not self.current_semana:
            messagebox.showwarning("Advertencia", "Seleccione una semana para eliminar")
            return

        # Mostrar información de la semana a eliminar
        semana_info = (
            f"Semana {self.current_semana.numero}\n"
            f"Del {self.current_semana.fecha_inicio.strftime('%d/%m/%Y')} "
            f"al {self.current_semana.fecha_inicio.strftime('%d/%m/%Y')}"
        )

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la siguiente semana?\n\n{semana_info}\n\n"
            f"Esta acción no se puede deshacer.",
        ):
            try:
                self.current_semana.delete()
                messagebox.showinfo("Éxito", "Semana eliminada correctamente")
                self.clear_form()
                self.load_semanas()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo eliminar la semana: {str(e)}"
                )


def main():
    root = tk.Tk()
    app = ConfigSemanasWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
