from database.db import conectar_db

def registrar_categoria(nombre,imagen):
    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql=("INSERT INTO categorias (nombre_c,imagen_c) VALUES (%s,%s)")
    valores=(nombre, imagen)

    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True


def obtener_categorias():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    consultar_sql = "SELECT id_categoria, nombre_c, imagen_c, activo_c FROM categorias"
    try:
        cursor.execute(consultar_sql)
        categorias = cursor.fetchall()
        return categorias 
    except Exception as e:
        print(f"Error al consultar todas las categorías: {e}")
        return []
    finally:
        cursor.close()
        db.close()


def obtener_categorias_publicas():
    db = conectar_db()
    cursor = db.cursor(dictionary=True)
    
    consultar_sql = "SELECT id_categoria, nombre_c, imagen_c FROM categorias WHERE activo_c = 1"
    try:
        cursor.execute(consultar_sql)
        categorias = cursor.fetchall()
        return categorias
    except Exception as e:
        print(f"Error al consultar categorías públicas: {e}")
        return []
    finally:
        cursor.close()
        db.close()

def actualizar_categoria(id_categoria, nombre, imagen):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        if imagen:
            sql = "UPDATE categorias SET nombre_c = %s, imagen_c = %s WHERE id_categoria = %s"
            valores = (nombre, imagen, id_categoria)
        else:
            sql = "UPDATE categorias SET nombre_c = %s WHERE id_categoria = %s"
            valores = (nombre, id_categoria)
            
        cursor.execute(sql, valores)
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar categoría: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

def cambiar_estado_categoria(id_categoria, nuevo_estado):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        sql = "UPDATE categorias SET activo_c = %s WHERE id_categoria = %s"
        cursor.execute(sql, (int(nuevo_estado), int(id_categoria)))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al cambiar estado de la categoría en BD: {e}")
        return False
    finally:
        cursor.close()
        db.close()