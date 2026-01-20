"""
Configuración de la base de datos y modelos de la aplicación
"""

import sqlite3
from pathlib import Path
from typing import List, Optional


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

            # Crear índices para mejorar el rendimiento
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id)"
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


# Instancia global de la base de datos
db = Database()
