from database.db import conectar_db

def registrar_recetas(id_producto,id_inventario,cantidad_requerida):

    db=conectar_db

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

    consultar_sql="SELECT id_producto,id_inventario,cantidad_requerida FROM recetas"
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