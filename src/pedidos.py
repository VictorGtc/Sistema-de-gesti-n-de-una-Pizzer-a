from database.db import conectar_db
from datetime import datetime

def registrar_pedidos_mesa (numero_mesa, id_usuario, lista_producto):
    db=conectar_db()
    if db is None:
        return False
    cursor=db.cursor()

    total_pedido= sum(item['cantidad'] * item['precio_unitario'] for item in lista_producto)

    fecha_actual= datetime.now()
    try: 
        db.start_transaction()

        sql_pedido="INSERT INTO pedidos (id_cliente, numero_mesa, fecha_p, total_p, id_usuario, estado) VALUES (NULL,%s,%s,%s,%s,'Pendiente')"

        valores_pedidos= (numero_mesa, fecha_actual,total_pedido,id_usuario)

        cursor.execute(sql_pedido,valores_pedidos)

        id_pedido_generado= cursor.lastrowid

        sql_detalle="INSERT INTO detalle_pedido(id_producto, id_pedido, cantidad_v, precio_unitario) VALUES (%s,%s,%s,%s)"

        for item in lista_producto:
            valores_detalle=(
                item['id_producto'],
                id_pedido_generado,
                item['cantidad'],
                item['precio_unitario']
            )
            cursor.execute(sql_detalle,valores_detalle)
        
        db.commit()
        return True
    except Exception as e: 
        db.rollback()
        print(f"Error en critico al realizar el pedido {e}")
        return False
    finally:
        cursor.close()
        db.close()

def obtener_pedido():
    db=conectar_db()
    if db is None:
        return []
    cursor=db.cursor(dictionary=True)

    consulta_sql="""SELECT 
                        pe.id_pedido, 
                        pe.numero_mesa, 
                        pe.fecha_p, 
                        pe.total_p, 
                        pe.id_usuario, 
                        pe.estado,
                        IFNULL (cl.nombre_cl,'Mesa') as cliente_nombre,
                        p.id_producto, 
                        p.nombre_pr, 
                        dp.cantidad_v, 
                        dp.precio_unitario 
                    from detalle_pedido dp
                    LEFT JOIN productos p on p.id_producto=dp.id_producto
                    LEFT JOIN pedidos pe on pe.id_pedido=dp.id_pedido
                    LEFT JOIN clientes cl ON cl.id_cliente = pe.id_cliente"""
    pedidos_agrupados={}

    try:
        cursor.execute(consulta_sql)
        pedido=cursor.fetchall()
        for fila in pedido:
            if fila['id_pedido'] is None:
                continue
            id_actual=fila['id_pedido']
            if id_actual not in pedidos_agrupados:
                origen = f"Mesa {fila['numero_mesa']}" if fila['numero_mesa'] else f"Domicilio ({fila['cliente_nombre']})"
                pedidos_agrupados[id_actual]={
                    'id_pedido':id_actual,
                    'numero_mesa':fila['numero_mesa'],
                    'origen_pedido': origen,
                    'fecha_p':fila['fecha_p'],
                    'total_p':fila['total_p'],
                    'id_usuario':fila['id_usuario'],
                    'estado': fila['estado'],
                    'productos':[]
                }
            if fila['id_producto'] is not None:
                pedidos_agrupados[id_actual]['productos'].append({
                    'id_producto':fila['id_producto'],
                    'nombre_pr':fila['nombre_pr'],
                    'cantidad_v':fila['cantidad_v'],
                    'precio_unitario':fila['precio_unitario']
    })
        return list(pedidos_agrupados.values())
                
    except Exception as e:
        print(f"Error al consultar el pedido {e}")
        return []
    finally:
        cursor.close()
        db.close()


def registrar_pedido_domicilio(id_cliente, id_usuario, lista_producto):
    db = conectar_db()
    if db is None:
        return False
    cursor = db.cursor()

    total_pedido = sum(item['cantidad'] * item['precio_unitario'] for item in lista_producto)
    fecha_actual = datetime.now()
    if id_usuario is None:
        id_usuario = 1
    try: 
        db.start_transaction()

        sql_pedido = """
            INSERT INTO pedidos (id_cliente, numero_mesa, fecha_p, total_p, id_usuario, estado) 
            VALUES (%s, NULL, %s, %s, %s, %s)
        """
        valores_pedidos = (id_cliente, fecha_actual, total_pedido, id_usuario, 'Pendiente')
        cursor.execute(sql_pedido, valores_pedidos)

        id_pedido_generado = cursor.lastrowid

        sql_detalle = """
            INSERT INTO detalle_pedido (id_producto, id_pedido, cantidad_v, precio_unitario) 
            VALUES (%s, %s, %s, %s)
        """

        for item in lista_producto:
            valores_detalle = (
                item['id_producto'],
                id_pedido_generado,
                item['cantidad'],
                item['precio_unitario']
            )
            cursor.execute(sql_detalle, valores_detalle)
        
        db.commit()
        return True
    except Exception as e: 
        db.rollback()
        print(f"Error crítico en pedido a domicilio: {e}")
        return False
    finally:
        cursor.close()
        db.close()


def actualizar_pedidos(id_pedido, nuevo_estado):
    db = conectar_db()
    if db is None:
        return False
    
    try: 
        cursor = db.cursor()

        consulta_sql="UPDATE pedidos SET estado= %s WHERE id_pedido=%s"
        values=(nuevo_estado,id_pedido)
        
        cursor.execute(consulta_sql,values)

        db.commit()

        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error en la actualizacion de datos {e} ")
        if db:
            db.rollback()
        return False


def actualizar_prodcuto(id_producto, nombre, precio, imagen, id_categoria):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        # Si viene una nueva imagen se actualiza, si no, se mantiene la anterior
        if imagen:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, imagen_pr = %s, id_categoria = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, imagen, id_categoria, id_producto)
        else:
            sql = """UPDATE productos 
                        SET nombre_pr = %s, precio_pr = %s, id_categoria = %s 
                        WHERE id_producto = %s"""
            valores = (nombre, precio, id_categoria, id_producto)
            
        cursor.execute(sql, valores)
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

def eliminar_producto(id_producto):
    db = conectar_db()
    if db is None: return False
    cursor = db.cursor()
    try:
        # NOTA: Asegúrate de que no haya dependencias activas en detalle_pedido o maneja el borrado lógico
        sql = "DELETE FROM productos WHERE id_producto = %s"
        cursor.execute(sql, (id_producto,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()
