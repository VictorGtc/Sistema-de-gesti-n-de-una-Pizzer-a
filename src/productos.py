from database.db import conectar_db

def registrar_producto (nombre, precio, imagen, id_categoria):

    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql=("INSERT INTO productos (nombre_pr, precio_pr, imagen_pr, id_categoria) VALUES (%s,%s,%s,%s)")
    valores=(nombre,precio,imagen,id_categoria)

    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True

def obtener_productos():
    db=conectar_db()
    cursor=db.cursor(dictionary=True)

    consultar_sql="SELECT id_producto, nombre_pr, precio_pr, imagen_pr, id_categoria FROM productos WHERE activo_p=1"
    try:
        cursor.execute(consultar_sql)
        productos=cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Erro al consultar productos: {e} ")
        return []
    finally:
        cursor.close()
        db.close()

def actualizar_producto(id_producto, nombre, precio, imagen, id_categoria):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        # Si viene una nueva imagen se actualiza, si no, se mantiene la anterior
        if imagen:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, imagen_pr = %s, id_categoria = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, imagen, id_categoria, id_producto)
        else:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, id_categoria = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, id_categoria, id_producto)
            
        cursor.execute(sql, valores)
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

def eliminar_producto(id_producto):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        # NOTA: Asegúrate de que no haya dependencias activas en detalle_pedido o maneja el borrado lógico
        sql = "DELETE FROM productos WHERE id_producto = %s"
        cursor.execute(sql, (id_producto,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()


