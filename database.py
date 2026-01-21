"""
Configuración de la base de datos y modelos de la aplicación
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Tuple
from dataclasses import dataclass


class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent / "app_database.db"
        self.init_database()
        self.ensure_default_categoria()

    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        # Habilitar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de categorías
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE
                )
            """
            )

            # Tabla de productos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    categoria_id INTEGER NOT NULL,
                    costo REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    cantidad INTEGER NOT NULL,
                    margen_bruto REAL NOT NULL,
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
                )
            """
            )

            # Tabla de compras
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_nombre TEXT NOT NULL,
                    costo_total REAL NOT NULL,
                    cantidad_elementos INTEGER NOT NULL,
                    merma INTEGER NOT NULL DEFAULT 0,
                    fecha_compra DATE NOT NULL,
                    costo_unitario REAL GENERATED ALWAYS AS (costo_total / cantidad_elementos) VIRTUAL,
                    perdidas REAL GENERATED ALWAYS AS ((costo_total / cantidad_elementos) * merma) VIRTUAL
                )
            """
            )

            # Tabla de semanas
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS semanas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    UNIQUE(fecha_inicio, fecha_fin)
                )
            """
            )
            # Tabla de costos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS costos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN ('fijo', 'variable'))
                )
            """
            )
            # Tabla de ventas
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    semana_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad_vendida INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    FOREIGN KEY (semana_id) REFERENCES semanas(id) ON DELETE CASCADE,
                    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
                )
            """
            )

            # Crear índices para mejorar el rendimiento
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha_compra)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_compras_producto ON compras(producto_nombre)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_semanas_inicio ON semanas(fecha_inicio)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_semanas_fin ON semanas(fecha_fin)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_costos_tipo ON costos(tipo)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_costos_nombre ON costos(nombre)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ventas_semana ON ventas(semana_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ventas_producto ON ventas(producto_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ventas_fecha_producto ON ventas(semana_id, producto_id)"
            )

            conn.commit()

    def ensure_default_categoria(self):
        """Asegura que exista una categoría por defecto 'Sin Categoría'"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Buscar si ya existe la categoría "Sin Categoría"
                cursor.execute(
                    "SELECT id FROM categorias WHERE nombre = 'Sin Categoría'"
                )
                if not cursor.fetchone():
                    # Crear categoría por defecto
                    cursor.execute(
                        "INSERT INTO categorias (nombre) VALUES ('Sin Categoría')"
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error al crear categoría por defecto: {e}")

    @staticmethod
    def get_default_categoria_id():
        """Obtiene el ID de la categoría por defecto 'Sin Categoría'"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM categorias WHERE nombre = 'Sin Categoría'"
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error al obtener categoría por defecto: {e}")
            return None


class Categoria:
    """Modelo para la tabla Categorias"""

    def __init__(self, nombre, id=None):
        self.id = id
        self.nombre = nombre

    @staticmethod
    def get_all():
        """Obtiene todas las categorías"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
                rows = cursor.fetchall()
                return [Categoria(nombre=row[1], id=row[0]) for row in rows]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_id(categoria_id):
        """Obtiene una categoría por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, nombre FROM categorias WHERE id = ?", (categoria_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Categoria(nombre=row[1], id=row[0])
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    def get_productos(self):
        """Obtiene todos los productos de esta categoría"""
        return Producto.get_by_categoria(self.id)

    def get_total_productos(self):
        """Obtiene la suma total de cantidad de productos en esta categoría"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT SUM(cantidad) FROM productos WHERE categoria_id = ?",
                    (self.id,),
                )
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except Exception as e:
            print(f"Error en get_total_productos: {e}")
            return 0

    def save(self):
        """Guarda la categoría en la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                if self.id:  # Actualizar
                    cursor.execute(
                        "UPDATE categorias SET nombre = ? WHERE id = ?",
                        (self.nombre, self.id),
                    )
                else:  # Insertar
                    cursor.execute(
                        "INSERT INTO categorias (nombre) VALUES (?)", (self.nombre,)
                    )
                    self.id = cursor.lastrowid
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            raise Exception("Ya existe una categoría con ese nombre")
        except Exception as e:
            raise Exception(f"Error al guardar: {str(e)}")

    def get_count_productos(self):
        """Obtiene la cantidad de productos en esta categoría"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM productos WHERE categoria_id = ?", (self.id,)
                )
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error en get_count_productos: {e}")
            return 0

    def mover_productos_a_categoria(self, nueva_categoria_id):
        """Mueve todos los productos de esta categoría a otra categoría"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE productos SET categoria_id = ? WHERE categoria_id = ?",
                    (nueva_categoria_id, self.id),
                )
                conn.commit()
                return cursor.rowcount  # Retorna cuántos productos fueron movidos
        except Exception as e:
            raise Exception(f"Error al mover productos: {str(e)}")

    def delete(self, mover_a_default=False):
        """Elimina la categoría de la base de datos"""
        try:
            # Verificar si hay productos en esta categoría
            count_productos = self.get_count_productos()

            if count_productos > 0:
                if mover_a_default:
                    # Mover productos a categoría por defecto
                    default_cat_id = Database.get_default_categoria_id()
                    if default_cat_id:
                        self.mover_productos_a_categoria(default_cat_id)
                    else:
                        raise Exception("No se encontró la categoría por defecto")
                else:
                    raise Exception(
                        f"No se puede eliminar la categoría '{self.nombre}' porque tiene {count_productos} producto(s) asociado(s). "
                        f"Por favor, mueva o elimine primero los productos."
                    )

            # Ahora sí eliminar la categoría
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categorias WHERE id = ?", (self.id,))
                conn.commit()
                return True

        except Exception as e:
            raise Exception(f"Error al eliminar categoría: {str(e)}")

    def __str__(self):
        return f"Categoria(id={self.id}, nombre='{self.nombre}')"


class Producto:
    """Modelo para la tabla Productos"""

    def __init__(self, nombre, categoria_id, costo, precio_venta, cantidad, id=None):
        self.id = id
        self.nombre = nombre
        self.categoria_id = categoria_id
        self.costo = costo
        self.precio_venta = precio_venta
        self.cantidad = cantidad
        self.margen_bruto = precio_venta - costo

    @staticmethod
    def calcular_margen(costo, precio_venta):
        """Calcula el margen bruto"""
        return precio_venta - costo

    @property
    def categoria(self):
        """Obtiene el objeto Categoria asociado"""
        return Categoria.get_by_id(self.categoria_id)

    @staticmethod
    def get_all():
        """Obtiene todos los productos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, categoria_id, costo, precio_venta, cantidad 
                    FROM productos ORDER BY nombre
                """
                )
                rows = cursor.fetchall()
                return [
                    Producto(
                        nombre=row[1],
                        categoria_id=row[2],
                        costo=row[3],
                        precio_venta=row[4],
                        cantidad=row[5],
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_categoria(categoria_id):
        """Obtiene todos los productos de una categoría específica"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, categoria_id, costo, precio_venta, cantidad 
                    FROM productos 
                    WHERE categoria_id = ? 
                    ORDER BY nombre
                """,
                    (categoria_id,),
                )
                rows = cursor.fetchall()
                return [
                    Producto(
                        nombre=row[1],
                        categoria_id=row[2],
                        costo=row[3],
                        precio_venta=row[4],
                        cantidad=row[5],
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_by_categoria: {e}")
            return []

    @staticmethod
    def get_by_id(producto_id):
        """Obtiene un producto por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, categoria_id, costo, precio_venta, cantidad 
                    FROM productos WHERE id = ?
                """,
                    (producto_id,),
                )
                row = cursor.fetchone()
                if row:
                    return Producto(
                        nombre=row[1],
                        categoria_id=row[2],
                        costo=row[3],
                        precio_venta=row[4],
                        cantidad=row[5],
                        id=row[0],
                    )
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    @staticmethod
    def get_productos_agrupados_por_categoria():
        """Obtiene todos los productos agrupados por categoría"""
        productos = Producto.get_all()
        categorias_dict = {}

        for producto in productos:
            categoria_id = producto.categoria_id
            if categoria_id not in categorias_dict:
                categorias_dict[categoria_id] = []
            categorias_dict[categoria_id].append(producto)

        # Convertir a lista de tuplas (categoria, productos)
        resultado = []
        for categoria_id, productos_list in categorias_dict.items():
            categoria = Categoria.get_by_id(categoria_id)
            if categoria:
                resultado.append((categoria, productos_list))

        # Ordenar por nombre de categoría
        resultado.sort(key=lambda x: x[0].nombre)
        return resultado

    def save(self):
        """Guarda el producto en la base de datos"""
        try:
            # Recalcular margen bruto
            self.margen_bruto = self.precio_venta - self.costo

            with Database().get_connection() as conn:
                cursor = conn.cursor()
                if self.id:  # Actualizar
                    cursor.execute(
                        """
                        UPDATE productos 
                        SET nombre = ?, categoria_id = ?, costo = ?, 
                            precio_venta = ?, cantidad = ?, margen_bruto = ?
                        WHERE id = ?
                    """,
                        (
                            self.nombre,
                            self.categoria_id,
                            self.costo,
                            self.precio_venta,
                            self.cantidad,
                            self.margen_bruto,
                            self.id,
                        ),
                    )
                else:  # Insertar
                    cursor.execute(
                        """
                        INSERT INTO productos 
                        (nombre, categoria_id, costo, precio_venta, cantidad, margen_bruto) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            self.nombre,
                            self.categoria_id,
                            self.costo,
                            self.precio_venta,
                            self.cantidad,
                            self.margen_bruto,
                        ),
                    )
                    self.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al guardar producto: {str(e)}")

    def delete(self):
        """Elimina el producto de la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM productos WHERE id = ?", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al eliminar producto: {str(e)}")

    def __str__(self):
        return f"Producto(id={self.id}, nombre='{self.nombre}', categoria_id={self.categoria_id})"


class Compra:
    """Modelo para la tabla Compras"""

    def __init__(
        self,
        producto_nombre,
        costo_total,
        cantidad_elementos,
        merma=0,
        fecha_compra=None,
        id=None,
    ):
        self.id = id
        self.producto_nombre = producto_nombre
        self.costo_total = costo_total
        self.cantidad_elementos = cantidad_elementos
        self.merma = merma
        self.fecha_compra = fecha_compra if fecha_compra else datetime.now().date()

        # Calcular valores derivados
        self.costo_unitario = (
            costo_total / cantidad_elementos if cantidad_elementos > 0 else 0
        )
        self.perdidas = self.costo_unitario * merma

    @staticmethod
    def get_all():
        """Obtiene todas las compras ordenadas por fecha descendente"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, producto_nombre, costo_total, cantidad_elementos, 
                           merma, fecha_compra 
                    FROM compras 
                    ORDER BY fecha_compra DESC, id DESC
                """
                )
                rows = cursor.fetchall()
                return [
                    Compra(
                        producto_nombre=row[1],
                        costo_total=row[2],
                        cantidad_elementos=row[3],
                        merma=row[4],
                        fecha_compra=row[5],
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_id(compra_id):
        """Obtiene una compra por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, producto_nombre, costo_total, cantidad_elementos, 
                           merma, fecha_compra 
                    FROM compras WHERE id = ?
                """,
                    (compra_id,),
                )
                row = cursor.fetchone()
                if row:
                    return Compra(
                        producto_nombre=row[1],
                        costo_total=row[2],
                        cantidad_elementos=row[3],
                        merma=row[4],
                        fecha_compra=row[5],
                        id=row[0],
                    )
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    def save(self):
        """Guarda la compra en la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                if self.id:  # Actualizar
                    cursor.execute(
                        """
                        UPDATE compras 
                        SET producto_nombre = ?, costo_total = ?, cantidad_elementos = ?, 
                            merma = ?, fecha_compra = ?
                        WHERE id = ?
                    """,
                        (
                            self.producto_nombre,
                            self.costo_total,
                            self.cantidad_elementos,
                            self.merma,
                            self.fecha_compra,
                            self.id,
                        ),
                    )
                else:  # Insertar
                    cursor.execute(
                        """
                        INSERT INTO compras 
                        (producto_nombre, costo_total, cantidad_elementos, merma, fecha_compra) 
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            self.producto_nombre,
                            self.costo_total,
                            self.cantidad_elementos,
                            self.merma,
                            self.fecha_compra,
                        ),
                    )
                    self.id = cursor.lastrowid
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al guardar compra: {str(e)}")

    def delete(self):
        """Elimina la compra de la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM compras WHERE id = ?", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al eliminar compra: {str(e)}")

    def calcular_perdidas(self):
        """Calcula las pérdidas basadas en la merma"""
        if self.cantidad_elementos > 0:
            self.costo_unitario = self.costo_total / self.cantidad_elementos
            self.perdidas = self.costo_unitario * self.merma
        else:
            self.costo_unitario = 0
            self.perdidas = 0
        return self.perdidas

    def __str__(self):
        return f"Compra(id={self.id}, producto='{self.producto_nombre}', costo_total={self.costo_total})"


class Semana:
    """Modelo para la tabla Semanas"""

    def __init__(self, fecha_inicio: date, fecha_fin: date, id: int = None):
        self.id = id
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.numero = self.calcular_numero_semana()

    @staticmethod
    def calcular_numero_semana_para_fecha(fecha: date) -> int:
        """Calcula el número de semana ISO para una fecha dada"""
        return fecha.isocalendar()[1]

    def calcular_numero_semana(self) -> int:
        """Calcula el número de semana basado en la fecha de inicio"""
        return self.calcular_numero_semana_para_fecha(self.fecha_inicio)

    @staticmethod
    def get_all() -> List["Semana"]:
        """Obtiene todas las semanas ordenadas por fecha de inicio"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, fecha_inicio, fecha_fin 
                    FROM semanas 
                    ORDER BY fecha_inicio DESC
                """
                )
                rows = cursor.fetchall()
                return [
                    Semana(
                        fecha_inicio=datetime.strptime(row[1], "%Y-%m-%d").date(),
                        fecha_fin=datetime.strptime(row[2], "%Y-%m-%d").date(),
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_id(semana_id: int) -> Optional["Semana"]:
        """Obtiene una semana por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, fecha_inicio, fecha_fin 
                    FROM semanas WHERE id = ?
                """,
                    (semana_id,),
                )
                row = cursor.fetchone()
                if row:
                    return Semana(
                        fecha_inicio=datetime.strptime(row[1], "%Y-%m-%d").date(),
                        fecha_fin=datetime.strptime(row[2], "%Y-%m-%d").date(),
                        id=row[0],
                    )
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    @staticmethod
    def verificar_solapamiento(
        fecha_inicio: date, fecha_fin: date, excluir_id: int = None
    ) -> Tuple[bool, Optional["Semana"]]:
        """
        Verifica si hay solapamiento con semanas existentes

        Returns:
            Tuple[bool, Optional[Semana]]: (hay_solapamiento, semana_solapada)
        """
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()

                # Query para verificar solapamiento
                if excluir_id:
                    cursor.execute(
                        """
                        SELECT id, fecha_inicio, fecha_fin 
                        FROM semanas 
                        WHERE id != ? AND (
                            (fecha_inicio <= ? AND fecha_fin >= ?) OR  -- Nueva semana dentro de existente
                            (fecha_inicio >= ? AND fecha_inicio <= ?) OR  -- Inicio en rango existente
                            (fecha_fin >= ? AND fecha_fin <= ?)  -- Fin en rango existente
                        )
                        LIMIT 1
                    """,
                        (
                            excluir_id,
                            fecha_fin,
                            fecha_inicio,
                            fecha_inicio,
                            fecha_fin,
                            fecha_inicio,
                            fecha_fin,
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, fecha_inicio, fecha_fin 
                        FROM semanas 
                        WHERE (
                            (fecha_inicio <= ? AND fecha_fin >= ?) OR
                            (fecha_inicio >= ? AND fecha_inicio <= ?) OR
                            (fecha_fin >= ? AND fecha_fin <= ?)
                        )
                        LIMIT 1
                    """,
                        (
                            fecha_fin,
                            fecha_inicio,
                            fecha_inicio,
                            fecha_fin,
                            fecha_inicio,
                            fecha_fin,
                        ),
                    )

                row = cursor.fetchone()
                if row:
                    semana_solapada = Semana(
                        fecha_inicio=datetime.strptime(row[1], "%Y-%m-%d").date(),
                        fecha_fin=datetime.strptime(row[2], "%Y-%m-%d").date(),
                        id=row[0],
                    )
                    return True, semana_solapada
                return False, None

        except Exception as e:
            print(f"Error en verificar_solapamiento: {e}")
            return (
                True,
                None,
            )  # Por seguridad, asumir que hay solapamiento en caso de error

    def save(self) -> bool:
        """Guarda la semana en la base de datos"""
        try:
            # Verificar que fecha_inicio <= fecha_fin
            if self.fecha_inicio > self.fecha_fin:
                raise Exception(
                    "La fecha de inicio debe ser anterior o igual a la fecha de fin"
                )

            # Verificar solapamiento
            hay_solapamiento, semana_solapada = self.verificar_solapamiento(
                self.fecha_inicio, self.fecha_fin, self.id
            )

            if hay_solapamiento:
                raise Exception(
                    f"La semana se solapa con la semana existente: "
                    f"{semana_solapada.fecha_inicio} - {semana_solapada.fecha_fin}"
                )

            with Database().get_connection() as conn:
                cursor = conn.cursor()
                if self.id:  # Actualizar (aunque no permitiremos editar normalmente)
                    cursor.execute(
                        """
                        UPDATE semanas 
                        SET fecha_inicio = ?, fecha_fin = ?
                        WHERE id = ?
                    """,
                        (
                            self.fecha_inicio.strftime("%Y-%m-%d"),
                            self.fecha_fin.strftime("%Y-%m-%d"),
                            self.id,
                        ),
                    )
                else:  # Insertar
                    cursor.execute(
                        """
                        INSERT INTO semanas (fecha_inicio, fecha_fin) 
                        VALUES (?, ?)
                    """,
                        (
                            self.fecha_inicio.strftime("%Y-%m-%d"),
                            self.fecha_fin.strftime("%Y-%m-%d"),
                        ),
                    )
                    self.id = cursor.lastrowid

                conn.commit()
                return True

        except Exception as e:
            raise Exception(f"Error al guardar semana: {str(e)}")

    def delete(self) -> bool:
        """Elimina la semana de la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM semanas WHERE id = ?", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al eliminar semana: {str(e)}")

    def __str__(self) -> str:
        return f"Semana(id={self.id}, inicio={self.fecha_inicio}, fin={self.fecha_fin}, num={self.numero})"


class TipoCosto(Enum):
    """Enum para los tipos de costo"""

    FIJO = "fijo"
    VARIABLE = "variable"


class Costo:
    """Modelo para la tabla Costos"""

    def __init__(self, nombre: str, cantidad: float, tipo: TipoCosto, id: int = None):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.tipo = tipo

    @staticmethod
    def get_all() -> List["Costo"]:
        """Obtiene todos los costos ordenados por tipo y nombre"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, cantidad, tipo 
                    FROM costos 
                    ORDER BY tipo, nombre
                """
                )
                rows = cursor.fetchall()
                return [
                    Costo(
                        nombre=row[1],
                        cantidad=row[2],
                        tipo=TipoCosto(row[3]),
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_tipo(tipo: TipoCosto) -> List["Costo"]:
        """Obtiene todos los costos de un tipo específico"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, cantidad, tipo 
                    FROM costos 
                    WHERE tipo = ? 
                    ORDER BY nombre
                """,
                    (tipo.value,),
                )
                rows = cursor.fetchall()
                return [
                    Costo(
                        nombre=row[1],
                        cantidad=row[2],
                        tipo=TipoCosto(row[3]),
                        id=row[0],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_by_tipo: {e}")
            return []

    @staticmethod
    def get_total_por_tipo(tipo: TipoCosto) -> float:
        """Obtiene la suma total de costos de un tipo específico"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT SUM(cantidad) 
                    FROM costos 
                    WHERE tipo = ?
                """,
                    (tipo.value,),
                )
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0.0
        except Exception as e:
            print(f"Error en get_total_por_tipo: {e}")
            return 0.0

    @staticmethod
    def get_total_general() -> float:
        """Obtiene la suma total de todos los costos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(cantidad) FROM costos")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0.0
        except Exception as e:
            print(f"Error en get_total_general: {e}")
            return 0.0

    @staticmethod
    def get_by_id(costo_id: int) -> Optional["Costo"]:
        """Obtiene un costo por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, nombre, cantidad, tipo 
                    FROM costos WHERE id = ?
                """,
                    (costo_id,),
                )
                row = cursor.fetchone()
                if row:
                    return Costo(
                        nombre=row[1],
                        cantidad=row[2],
                        tipo=TipoCosto(row[3]),
                        id=row[0],
                    )
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    def save(self) -> bool:
        """Guarda el costo en la base de datos"""
        try:
            # Validaciones básicas
            if not self.nombre.strip():
                raise Exception("El nombre del costo no puede estar vacío")

            if self.cantidad <= 0:
                raise Exception("La cantidad debe ser mayor a 0")

            with Database().get_connection() as conn:
                cursor = conn.cursor()
                if self.id:  # Actualizar
                    cursor.execute(
                        """
                        UPDATE costos 
                        SET nombre = ?, cantidad = ?, tipo = ?
                        WHERE id = ?
                    """,
                        (self.nombre.strip(), self.cantidad, self.tipo.value, self.id),
                    )
                else:  # Insertar
                    cursor.execute(
                        """
                        INSERT INTO costos (nombre, cantidad, tipo) 
                        VALUES (?, ?, ?)
                    """,
                        (self.nombre.strip(), self.cantidad, self.tipo.value),
                    )
                    self.id = cursor.lastrowid

                conn.commit()
                return True

        except Exception as e:
            raise Exception(f"Error al guardar costo: {str(e)}")

    def delete(self) -> bool:
        """Elimina el costo de la base de datos"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM costos WHERE id = ?", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Error al eliminar costo: {str(e)}")

    def __str__(self) -> str:
        return f"Costo(id={self.id}, nombre='{self.nombre}', cantidad={self.cantidad}, tipo={self.tipo.value})"


@dataclass
class Venta:
    """Modelo para la tabla Ventas"""

    id: int = None
    semana_id: int = None
    producto_id: int = None
    cantidad_vendida: int = 0
    monto: float = 0.0

    @property
    def semana(self):
        """Obtiene el objeto Semana asociado"""
        return Semana.get_by_id(self.semana_id) if self.semana_id else None

    @property
    def producto(self):
        """Obtiene el objeto Producto asociado"""
        return Producto.get_by_id(self.producto_id) if self.producto_id else None

    @staticmethod
    def get_all() -> List["Venta"]:
        """Obtiene todas las ventas ordenadas por semana y producto"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, semana_id, producto_id, cantidad_vendida, monto 
                    FROM ventas 
                    ORDER BY semana_id DESC, producto_id
                """
                )
                rows = cursor.fetchall()
                return [
                    Venta(
                        id=row[0],
                        semana_id=row[1],
                        producto_id=row[2],
                        cantidad_vendida=row[3],
                        monto=row[4],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    @staticmethod
    def get_by_semana(semana_id: int) -> List["Venta"]:
        """Obtiene todas las ventas de una semana específica"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, semana_id, producto_id, cantidad_vendida, monto 
                    FROM ventas 
                    WHERE semana_id = ?
                    ORDER BY producto_id
                """,
                    (semana_id,),
                )
                rows = cursor.fetchall()
                return [
                    Venta(
                        id=row[0],
                        semana_id=row[1],
                        producto_id=row[2],
                        cantidad_vendida=row[3],
                        monto=row[4],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_by_semana: {e}")
            return []

    @staticmethod
    def get_by_producto(producto_id: int) -> List["Venta"]:
        """Obtiene todas las ventas de un producto específico"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, semana_id, producto_id, cantidad_vendida, monto 
                    FROM ventas 
                    WHERE producto_id = ?
                    ORDER BY semana_id DESC
                """,
                    (producto_id,),
                )
                rows = cursor.fetchall()
                return [
                    Venta(
                        id=row[0],
                        semana_id=row[1],
                        producto_id=row[2],
                        cantidad_vendida=row[3],
                        monto=row[4],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error en get_by_producto: {e}")
            return []

    @staticmethod
    def get_by_id(venta_id: int) -> Optional["Venta"]:
        """Obtiene una venta por su ID"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, semana_id, producto_id, cantidad_vendida, monto 
                    FROM ventas WHERE id = ?
                """,
                    (venta_id,),
                )
                row = cursor.fetchone()
                if row:
                    return Venta(
                        id=row[0],
                        semana_id=row[1],
                        producto_id=row[2],
                        cantidad_vendida=row[3],
                        monto=row[4],
                    )
                return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    @staticmethod
    def get_total_monto_semana(semana_id: int) -> float:
        """Obtiene el monto total de ventas de una semana"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT SUM(monto) 
                    FROM ventas 
                    WHERE semana_id = ?
                """,
                    (semana_id,),
                )
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0.0
        except Exception as e:
            print(f"Error en get_total_monto_semana: {e}")
            return 0.0

    @staticmethod
    def get_total_cantidad_producto(producto_id: int) -> int:
        """Obtiene la cantidad total vendida de un producto"""
        try:
            with Database().get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT SUM(cantidad_vendida) 
                    FROM ventas 
                    WHERE producto_id = ?
                """,
                    (producto_id,),
                )
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
        except Exception as e:
            print(f"Error en get_total_cantidad_producto: {e}")
            return 0

    def _actualizar_inventario(
        self, operacion: str, cantidad_anterior: int = 0, conn=None
    ):
        """Actualiza el inventario del producto después de una operación"""
        try:
            # Usar conexión proporcionada o crear una nueva
            close_conn = False
            if conn is None:
                conn = Database().get_connection()
                close_conn = True

            cursor = conn.cursor()

            # Obtener producto con la misma conexión
            cursor.execute(
                """
                SELECT id, nombre, categoria_id, costo, precio_venta, cantidad, margen_bruto
                FROM productos WHERE id = ?
            """,
                (self.producto_id,),
            )
            row = cursor.fetchone()

            if not row:
                raise Exception("Producto no encontrado")

            # Crear objeto Producto
            producto = Producto(
                nombre=row[1],
                categoria_id=row[2],
                costo=row[3],
                precio_venta=row[4],
                cantidad=row[5],
                id=row[0],
            )

            if operacion == "crear":
                # Restar cantidad vendida del inventario
                if producto.cantidad < self.cantidad_vendida:
                    raise Exception(
                        f"Inventario insuficiente. Solo hay {producto.cantidad} unidades disponibles"
                    )
                producto.cantidad -= self.cantidad_vendida

            elif operacion == "actualizar":
                # Calcular diferencia
                diferencia = self.cantidad_vendida - cantidad_anterior

                # Si la nueva cantidad es mayor, verificar inventario
                if diferencia > 0 and producto.cantidad < diferencia:
                    raise Exception(
                        f"Inventario insuficiente para actualizar. Solo hay {producto.cantidad} unidades disponibles"
                    )

                # Ajustar inventario
                producto.cantidad -= diferencia

            elif operacion == "eliminar":
                # Devolver cantidad al inventario
                producto.cantidad += self.cantidad_vendida

            # Actualizar producto en la misma conexión
            producto.margen_bruto = producto.precio_venta - producto.costo
            cursor.execute(
                """
                UPDATE productos 
                SET cantidad = ?, margen_bruto = ?
                WHERE id = ?
            """,
                (producto.cantidad, producto.margen_bruto, producto.id),
            )

            if close_conn:
                conn.commit()
                conn.close()

        except Exception as e:
            if conn and close_conn:
                conn.close()
            raise Exception(f"Error al actualizar inventario: {str(e)}")

    def save(self, es_actualizacion: bool = False, cantidad_anterior: int = 0) -> bool:
        """Guarda la venta en la base de datos y actualiza el inventario"""
        conn = None
        try:
            # Validaciones básicas
            if not self.semana_id:
                raise Exception("Debe seleccionar una semana")

            if not self.producto_id:
                raise Exception("Debe seleccionar un producto")

            if self.cantidad_vendida <= 0:
                raise Exception("La cantidad vendida debe ser mayor a 0")

            if self.monto <= 0:
                raise Exception("El monto debe ser mayor a 0")

            # Usar UNA sola conexión para toda la operación
            conn = Database().get_connection()
            cursor = conn.cursor()

            # Iniciar transacción
            conn.execute("BEGIN TRANSACTION")

            if self.id:  # Actualizar
                # Primero actualizar inventario
                self._actualizar_inventario("actualizar", cantidad_anterior, conn)

                # Luego actualizar venta
                cursor.execute(
                    """
                    UPDATE ventas 
                    SET semana_id = ?, producto_id = ?, cantidad_vendida = ?, monto = ?
                    WHERE id = ?
                """,
                    (
                        self.semana_id,
                        self.producto_id,
                        self.cantidad_vendida,
                        self.monto,
                        self.id,
                    ),
                )

            else:  # Insertar
                # Primero verificar inventario
                cursor.execute(
                    "SELECT cantidad FROM productos WHERE id = ?", (self.producto_id,)
                )
                row = cursor.fetchone()
                if not row:
                    raise Exception("Producto no encontrado")

                inventario_actual = row[0]
                if inventario_actual < self.cantidad_vendida:
                    raise Exception(
                        f"Inventario insuficiente. Solo hay {inventario_actual} unidades disponibles"
                    )

                # Insertar venta
                cursor.execute(
                    """
                    INSERT INTO ventas (semana_id, producto_id, cantidad_vendida, monto) 
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        self.semana_id,
                        self.producto_id,
                        self.cantidad_vendida,
                        self.monto,
                    ),
                )
                self.id = cursor.lastrowid

                # Luego actualizar inventario
                self._actualizar_inventario("crear", 0, conn)

            # Commit de la transacción
            conn.commit()
            return True

        except Exception as e:
            # Rollback en caso de error
            if conn:
                conn.rollback()
            raise Exception(f"Error al guardar venta: {str(e)}")
        finally:
            # Siempre cerrar la conexión
            if conn:
                conn.close()

    def delete(self) -> bool:
        """Elimina la venta de la base de datos y devuelve el inventario"""
        conn = None
        try:
            # Usar UNA sola conexión
            conn = Database().get_connection()
            cursor = conn.cursor()

            # Iniciar transacción
            conn.execute("BEGIN TRANSACTION")

            # Primero devolver inventario
            self._actualizar_inventario("eliminar", 0, conn)

            # Luego eliminar la venta
            cursor.execute("DELETE FROM ventas WHERE id = ?", (self.id,))

            # Commit de la transacción
            conn.commit()
            return True
        except Exception as e:
            # Rollback en caso de error
            if conn:
                conn.rollback()
            raise Exception(f"Error al eliminar venta: {str(e)}")
        finally:
            # Siempre cerrar la conexión
            if conn:
                conn.close()

    def __str__(self) -> str:
        semana_info = (
            self.semana.fecha_inicio.strftime("%d/%m/%Y") if self.semana else "N/A"
        )
        producto_info = self.producto.nombre if self.producto else "N/A"
        return f"Venta(id={self.id}, semana={semana_info}, producto='{producto_info}', cantidad={self.cantidad_vendida}, monto={self.monto})"


# Instancia global de la base de datos
db = Database()
