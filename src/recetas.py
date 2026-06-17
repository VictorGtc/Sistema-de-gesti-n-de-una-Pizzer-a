from database.db import conectar_db

def registrar_recetas(id_producto,id_inventario,cantidad_requerida):

    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql=("INSERT INTO recetas (id_producto,id_inventario,cantidad_requerida) VALUES (%s,%s,%s)")
    valores=(id_producto,id_inventario,cantidad_requerida)

    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True


def obtener_receta():
    db=conectar_db()
    cursor=db.cursor(dictionary=True)

    consultar_sql="""SELECT 
            r.id_producto, 
            r.id_inventario, 
            r.cantidad_requerida,
            i.nombre_i,         
            i.unidad_registrada
        FROM recetas r
        INNER JOIN inventario i ON r.id_inventario = i.id_inventario"""
    try:
        cursor.execute(consultar_sql)
        categorias=cursor.fetchall()
        return categorias
    except Exception as e:
        print(f"Error al consultar la receta: {e} ")
        return []
    finally:
        cursor.close()
        db.close()

def borrar_ingrediente_de_receta(id_producto, id_inventario):
    db = conectar_db()
    if db is None:
        return False
        
    cursor = db.cursor()
    consulta_sql = "DELETE FROM recetas WHERE id_producto = %s AND id_inventario = %s"
    valores = (id_producto, id_inventario)
    
    try:
        cursor.execute(consulta_sql, valores)
        db.commit()
        # Si afectó a una o más filas, significa que se eliminó correctamente
        exito = cursor.rowcount > 0
        return exito
    except Exception as e:
        print(f"Error al eliminar ingrediente de la receta: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()
