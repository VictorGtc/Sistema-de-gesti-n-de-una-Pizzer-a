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
    db=conectar_db()
    cursor=db.cursor(dictionary=True)

    consultar_sql="SELECT id_categoria, nombre_c, imagen_c FROM categorias"
    try:
        cursor.execute(consultar_sql)
        categorias=cursor.fetchall()
        return categorias
    except Exception as e:
        print(f"Erro al consultar categorias: {e} ")
        return []
    finally:
        cursor.close()
        db.close()