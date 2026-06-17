from database.db import conectar_db
from flask import jsonify

def registrar_inventario(nombre,cantidad_inicial,cantidad_minima,unidad):
    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    if unidad == 'Kg' or unidad == 'Litros':
        cantidad_inicial=cantidad_inicial*1000
        cantidad_minima=cantidad_minima*1000

        unidad='g' if unidad=='Kg' else 'ml'

    try:
        consulta_sql="INSERT INTO inventario (nombre_i,stock_inicial,stock_minimo,unidad_registrada) VALUES (%s,%s,%s,%s)"
        valores=(nombre,cantidad_inicial,cantidad_minima,unidad)

        cursor.execute(consulta_sql,valores)
        db.commit()

        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        cursor.close()
        db.close()
        return False


def obtener_inventario():
    db=conectar_db()
    cursor=db.cursor(dictionary=True)

    consultar_sql="SELECT id_inventario,nombre_i,stock_inicial,stock_minimo,unidad_registrada,activo FROM inventario"
    try:
        cursor.execute(consultar_sql)
        categorias=cursor.fetchall()
        return categorias
    except Exception as e:
        print(f"Error al consultar el inventario: {e} ")
        return []
    finally:
        cursor.close()
        db.close()


def cambiar_estado_ingrediente(id_inventario, nuevo_estado):
    db = conectar_db()
    if db is None: return False
    
    cursor = db.cursor()
    try:
        # Hacemos un UPDATE en lugar de un DELETE
        sql = "UPDATE inventario SET activo = %s WHERE id_inventario = %s"
        cursor.execute(sql, (nuevo_estado, id_inventario))
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error al cambiar estado en BD: {e}")
        cursor.close()
        db.close()
        return False


def actualizar_inventario(id_inventario, nombre, cantidad_inicial, cantidad_minima, unidad):
    db = conectar_db()
    if db is None:
        return False
    
    cursor = db.cursor()
    if unidad == 'Kg' or unidad == 'Litros':
        cantidad_inicial = cantidad_inicial * 1000
        cantidad_minima = cantidad_minima * 1000
        unidad = 'g' if unidad == 'Kg' else 'ml'

    try:
        consulta_sql = """
            UPDATE inventario 
            SET nombre_i = %s, stock_inicial = %s, stock_minimo = %s, unidad_registrada = %s 
            WHERE id_inventario = %s
        """
        valores = (nombre, cantidad_inicial, cantidad_minima, unidad, id_inventario)

        cursor.execute(consulta_sql, valores)
        db.commit()
        
        exito = cursor.rowcount > 0
        return exito
    except Exception as e:
        print(f"Error al actualizar inventario en BD: {str(e)}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()