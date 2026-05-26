from database.db import conectar_db

def registrar_cotegoria(nombre,imagen):
    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql=("INSERT INTO productos (nombre_c, imagen_c) VALUES (%s,%s)")
    valores=(nombre, imagen)

    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True