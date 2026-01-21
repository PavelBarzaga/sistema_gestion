"""
Configuración de la base de datos y modelos de la aplicación
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Tuple


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


# Instancia global de la base de datos
db = Database()
