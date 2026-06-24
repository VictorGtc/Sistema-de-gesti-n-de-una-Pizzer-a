import mysql.connector
from database.db import conectar_db
from werkzeug.security import generate_password_hash, check_password_hash


def registrar_clientes(nombre, apellido, correo, password, telefono, direccion):
    db=conectar_db()
    if db is None:
        return False
    
    cursor=db.cursor()
    try:
        # Verificar duplicados en clientes
        cursor.execute("SELECT id_cliente FROM clientes WHERE correo_cl = %s", (correo,))
        if cursor.fetchone():
            return False
            
        # Verificar duplicados en usuarios
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo_u = %s", (correo,))
        if cursor.fetchone():
            return False

        pass_hasheado=generate_password_hash(password)
        consulta_sql="INSERT INTO clientes (nombre_cl, apellido_cl, correo_cl, contraseña_cl, telefono_cl, direccion) VALUES (%s,%s,%s,%s,%s,%s)"
        valores=(nombre,apellido,correo,pass_hasheado,telefono,direccion)
        cursor.execute(consulta_sql,valores)

        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error al registrar cliente: {e}")
        cursor.close()
        db.close()
        return False


def validar_clientes(correo, password):
    db = conectar_db()
    if db is None:
        return False, "Error de conexión"
    
    cursor = db.cursor()
    datos_usuarios = None
    es_valido = False
    mensaje = "Credenciales incorrectas"
    
    try:
        consulta_sql = 'SELECT id_cliente, nombre_cl, apellido_cl, correo_cl, contraseña_cl, direccion FROM clientes WHERE correo_cl = %s'
        valores = (correo,)
        cursor.execute(consulta_sql, valores)

        resultado = cursor.fetchone()

        if resultado is not None:
            if check_password_hash(resultado[4], password):
                datos_usuarios = {
                    'id_cliente': resultado[0],
                    'Nombre': resultado[1], 
                    'Apellido': resultado[2],
                    'Correo': resultado[3], 
                    'Direccion': resultado[5]
                }
                es_valido = True
                mensaje = "Éxito"
            else:
                es_valido = False
                mensaje = "Credenciales incorrectas"
        else:
            es_valido = False
            mensaje = "Credenciales incorrectas"
            
    except Exception as e:
        print(f"Error en base de datos: {e}")
        es_valido = False
        mensaje = "Error interno"
        
    finally:
        if cursor:
            cursor.fetchall() 
            cursor.close()
        if db:
            db.close()
            
    return es_valido, datos_usuarios if es_valido else mensaje