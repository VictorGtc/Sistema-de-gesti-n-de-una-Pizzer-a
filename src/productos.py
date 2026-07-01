from database.db import conectar_db

def registrar_producto (nombre, precio, imagen, id_categoria, descripcion=None):

    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql=("INSERT INTO productos (nombre_pr, precio_pr, imagen_pr, id_categoria, descripcion) VALUES (%s,%s,%s,%s,%s)")
    valores=(nombre,precio,imagen,id_categoria,descripcion)

    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True

def obtener_productos():
    db=conectar_db()
    cursor=db.cursor(dictionary=True)

    consultar_sql="SELECT id_producto, nombre_pr, precio_pr, imagen_pr, id_categoria, activo_p, descripcion FROM productos "
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


def obtener_productos_publicos():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)

    consultar_sql = "SELECT id_producto, nombre_pr, precio_pr, imagen_pr, id_categoria, descripcion FROM productos WHERE activo_p = 1"
    try:
        cursor.execute(consultar_sql)
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error al consultar productos públicos: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def actualizar_producto(id_producto, nombre, precio, imagen, id_categoria, descripcion=None):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        # Si viene una nueva imagen se actualiza, si no, se mantiene la anterior
        if imagen:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, imagen_pr = %s, id_categoria = %s, descripcion = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, imagen, id_categoria, descripcion, id_producto)
        else:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, id_categoria = %s, descripcion = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, id_categoria, descripcion, id_producto)
            
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



def cambiar_estado_producto(id_producto,nuevo_estado):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        sql="UPDATE productos SET activo_p = %s WHERE id_producto = %s"
        cursor.execute(sql,(nuevo_estado,id_producto))
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e: 
        print(f"Error al cambiar estado en BD: {e}")
        cursor.close()
        db.close()
        return False


