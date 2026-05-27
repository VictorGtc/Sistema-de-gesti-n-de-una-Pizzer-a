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

    consultar_sql="SELECT id_producto, nombre_pr, precio_pr, imagen_pr, id_categoria FROM productos"
    try:
        cursor.execute(consultar_sql)
        categorias=cursor.fetchall()
        return categorias
    except Exception as e:
        print(f"Erro al consultar productos: {e} ")
        return []
    finally:
        cursor.close()
        db.close()