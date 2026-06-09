import mysql.connector
from database.db import conectar_db
from werkzeug.security import generate_password_hash, check_password_hash



def registrar_usuarios(nombre, apellido, correo, password, telefono, rol):
    pass_hasheado=generate_password_hash(password)

    db=conectar_db()

    if db is None:
        return False
    
    cursor=db.cursor()
    try:
        consulta_sql="INSERT INTO usuarios (nombre_u, apellido_u, correo_u, contraseña_u, telefono_u, rol) VALUES (%s,%s,%s,%s,%s,%s)"
        valores=(nombre,apellido,correo,pass_hasheado,telefono,rol)
        cursor.execute(consulta_sql,valores)

        db.commit()

        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        cursor.close()
        db.close()
        return False




def validar_usuarios(correo, password):
    db=conectar_db()

    if db is None:
        return False
    
    cursor = db.cursor(dictionary=True)
    
    consulta_sql ='SELECT nombre_u, apellido_u, correo_u, contraseña_u AS password, telefono_u, rol FROM usuarios WHERE correo_u = %s'
    valores=(correo,)
    cursor.execute(consulta_sql,valores)

    resultado=cursor.fetchone()

    if resultado is not None:

        if check_password_hash(resultado['password'],password):
            datos_usuarios = {'Nombre':resultado['nombre_u'], 'Apellido': resultado['apellido_u'],'Correo': resultado['correo_u'], 'Rol': resultado['rol']}
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

def obtener_usuario():
    db=conectar_db()

    if db is None:
        return  []
    
    cursor = db.cursor(dictionary=True)

    consulta_sql="SELECT * from usuarios"

    try:
        cursor.execute(consulta_sql)
        usuarios=cursor.fetchall()
        return usuarios
    except Exception as e:
        print(f"Error al realizar la consulta {e}")
        return []
    finally:
        db.close()
        cursor.close()