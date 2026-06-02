import mysql.connector
from database.db import conectar_db
from werkzeug.security import generate_password_hash, check_password_hash


def registrar_clientes(nombre, apellido, correo, password, telefono, direccion):
    pass_hasheado=generate_password_hash(password)

    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()

    consulta_sql="INSERT INTO clientes (nombre_cl, apellido_cl, correo_cl, contraseña_cl, telefono_cl, direccion) VALUES (%s,%s,%s,%s,%s,%s)"
    valores=(nombre,apellido,correo,pass_hasheado,telefono,direccion)
    cursor.execute(consulta_sql,valores)

    db.commit()

    cursor.close()
    db.close()

    return True


def validar_clientes(correo, password):
    db=conectar_db()

    if db is None:
        return False
    
    cursor = db.cursor()
    
    consulta_sql ='SELECT id_cliente, nombre_cl, apellido_cl, correo_cl, contraseña_cl, direccion FROM clientes WHERE correo_cl = %s'
    valores=(correo,)
    cursor.execute(consulta_sql,valores)

    resultado=cursor.fetchone()

    if resultado is not None:

        if check_password_hash(resultado[4],password):
            datos_usuarios = {
                'id_cliente':resultado[0],
                'Nombre':resultado[1], 
                'Apellido': resultado[2],
                'Correo': resultado[3], 
                'Direccion': resultado[5]}
            cursor.close()
            db.close()
            return True, datos_usuarios  
        else :
            cursor.close()
            db.close()
            return False, "Credenciales incorrectas"

    else:
        cursor.close()
        db.close()
        return False, "Credenciales incorrectas "

