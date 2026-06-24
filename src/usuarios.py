import mysql.connector
from database.db import conectar_db
from werkzeug.security import generate_password_hash, check_password_hash



def registrar_usuarios(nombre, apellido, correo, password, telefono, rol):
    db=conectar_db()
    if db is None:
        return False
    
    cursor=db.cursor()
    try:
        # Verificar duplicados en usuarios
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo_u = %s", (correo,))
        if cursor.fetchone():
            return False
            
        # Verificar duplicados en clientes
        cursor.execute("SELECT id_cliente FROM clientes WHERE correo_cl = %s", (correo,))
        if cursor.fetchone():
            return False

        pass_hasheado=generate_password_hash(password)
        consulta_sql="INSERT INTO usuarios (nombre_u, apellido_u, correo_u, contraseña_u, telefono_u, rol, activo) VALUES (%s,%s,%s,%s,%s,%s,1)"
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
    
    consulta_sql ='SELECT id_usuario, nombre_u, apellido_u, correo_u, contraseña_u AS password, telefono_u, rol, activo FROM usuarios WHERE correo_u = %s'
    valores=(correo,)
    cursor.execute(consulta_sql,valores)

    resultado=cursor.fetchone()

    if resultado is not None:
        # Validar si el usuario está suspendido
        if resultado.get('activo') == 0:
            cursor.close()
            db.close()
            return False, "Esta cuenta ha sido suspendida. Contacte al administrador."

        if check_password_hash(resultado['password'],password):
            datos_usuarios = {'id_usuario': resultado['id_usuario'], 'Nombre':resultado['nombre_u'], 'Apellido': resultado['apellido_u'],'Correo': resultado['correo_u'], 'Rol': resultado['rol']}
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



def actualizar_usuario_completo(id_usuario, nombre_u, apellido_u, correo_u, rol, telefono_u):
    db = conectar_db()
    if db is None:
        return False
    
    cursor = db.cursor()
    try:
        consulta_sql = """
            UPDATE usuarios 
            SET nombre_u = %s, 
                apellido_u = %s, 
                correo_u = %s, 
                rol = %s, 
                telefono_u = %s 
            WHERE id_usuario = %s
        """
        valores = (nombre_u, apellido_u, correo_u, rol, telefono_u, id_usuario)
        cursor.execute(consulta_sql, valores)
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar usuario en BD: {str(e)}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

def cambiar_estado_usuario(id_usuario, nuevo_estado):
    db = conectar_db()
    if db is None:
        return False
    cursor = db.cursor()
    try:
        sql = "UPDATE usuarios SET activo = %s WHERE id_usuario = %s"
        cursor.execute(sql, (nuevo_estado, id_usuario))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al cambiar estado del usuario en BD: {e}")
        return False
    finally:
        cursor.close()
        db.close()