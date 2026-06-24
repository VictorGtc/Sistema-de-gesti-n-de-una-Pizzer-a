from database.db import conectar_db
from datetime import datetime

def registrar_pedidos_mesa (numero_mesa, id_usuario, lista_producto):
    db=conectar_db()
    if db is None:
        return False
    cursor=db.cursor()

    total_pedido= round(sum(item['cantidad'] * item['precio_unitario'] for item in lista_producto) * 1.15, 2)

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
    db = conectar_db()
    if db is None:
        return []
    cursor = db.cursor(dictionary=True)

    # Seleccionamos las columnas nuevas y detalles de clientes
    consulta_sql = """SELECT 
                        pe.id_pedido, 
                        pe.numero_mesa, 
                        pe.fecha_p, 
                        pe.total_p, 
                        pe.id_usuario, 
                        pe.id_cliente, 
                        pe.estado,
                        pe.metodo_pago,
                        pe.direccion_entrega,
                        pe.telefono_entrega,
                        pe.cedula_ruc,
                        cl.nombre_cl, 
                        cl.apellido_cl,
                        cl.telefono_cl,
                        cl.direccion as cliente_direccion,
                        p.id_producto, 
                        p.nombre_pr, 
                        dp.cantidad_v, 
                        dp.precio_unitario 
                    FROM pedidos pe
                    LEFT JOIN detalle_pedido dp ON pe.id_pedido = dp.id_pedido
                    LEFT JOIN productos p ON p.id_producto = dp.id_producto
                    LEFT JOIN clientes cl ON cl.id_cliente = pe.id_cliente
                    ORDER BY pe.id_pedido DESC"""

    pedidos_agrupados = {}

    try:
        cursor.execute(consulta_sql)
        pedido = cursor.fetchall()
        for fila in pedido:
            id_actual = fila['id_pedido']
            if id_actual is None: continue
            
            if id_actual not in pedidos_agrupados:
                nombre_cliente = fila['nombre_cl'] or 'Mesa'
                apellido_cliente = fila['apellido_cl'] or ''
                
                # Usamos los datos del pedido o en su defecto los del perfil del cliente
                telefono_cliente = fila['telefono_entrega'] or fila['telefono_cl'] or ''
                direccion_cliente = fila['direccion_entrega'] or fila['cliente_direccion'] or ''
                
                if fila['numero_mesa']:
                    origen = f"Mesa {fila['numero_mesa']}"
                else:
                    origen = f"Domicilio ({nombre_cliente} {apellido_cliente})".strip()
                
                pedidos_agrupados[id_actual] = {
                    'id_pedido': id_actual,
                    'numero_mesa': fila['numero_mesa'],
                    'id_cliente': fila['id_cliente'], 
                    'origen_pedido': origen,
                    'fecha_p': fila['fecha_p'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(fila['fecha_p'], datetime) else fila['fecha_p'],
                    'total_p': fila['total_p'],
                    'id_usuario': fila['id_usuario'],
                    'estado': fila['estado'],
                    'metodo_pago': fila['metodo_pago'] or 'efectivo',
                    'direccion_entrega': direccion_cliente,
                    'telefono_entrega': telefono_cliente,
                    'cedula_ruc': fila['cedula_ruc'] or '9999999999',
                    'cliente_nombre': f"{nombre_cliente} {apellido_cliente}".strip(),
                    'productos': []
                }
            
            if fila['id_producto'] is not None:
                pedidos_agrupados[id_actual]['productos'].append({
                    'id_producto': fila['id_producto'],
                    'nombre_pr': fila['nombre_pr'],
                    'cantidad_v': fila['cantidad_v'],
                    'precio_unitario': fila['precio_unitario']
                })
        
        return list(pedidos_agrupados.values())
                 
    except Exception as e:
        print(f"Error al consultar el pedido {e}")
        return []
    finally:
        cursor.close()
        db.close()


def registrar_pedido_domicilio(id_cliente, id_usuario, lista_producto, metodo_pago='efectivo', direccion_entrega=None, telefono_entrega=None, cedula_ruc='9999999999'):
    db = conectar_db()
    if db is None:
        return False
    cursor = db.cursor(dictionary=True)

    total_pedido = round(sum(item['cantidad'] * item['precio_unitario'] for item in lista_producto) * 1.15, 2)
    fecha_actual = datetime.now()
    
    try: 
        print(f"DEBUG: Registrando pedido para cliente: {id_cliente} y usuario: {id_usuario}")
        db.start_transaction()

        # Insertamos el pedido con los nuevos campos de facturación y entrega
        sql_pedido = """
            INSERT INTO pedidos (id_cliente, numero_mesa, fecha_p, total_p, id_usuario, estado, metodo_pago, direccion_entrega, telefono_entrega, cedula_ruc) 
            VALUES (%s, NULL, %s, %s, %s, 'Pendiente', %s, %s, %s, %s)
        """
        valores_pedidos = (id_cliente, fecha_actual, total_pedido, id_usuario, metodo_pago, direccion_entrega, telefono_entrega, cedula_ruc)
        cursor.execute(sql_pedido, valores_pedidos)

        id_pedido_generado = cursor.lastrowid

        # 2. Registrar detalles y descontar inventario inmediatamente
        sql_detalle = """
            INSERT INTO detalle_pedido (id_producto, id_pedido, cantidad_v, precio_unitario) 
            VALUES (%s, %s, %s, %s)
        """

        for item in lista_producto:
            # Insertar detalle
            cursor.execute(sql_detalle, (item['id_producto'], id_pedido_generado, item['cantidad'], item['precio_unitario']))
            
            # Descontar inventario
            cursor.execute("SELECT id_inventario, cantidad_requerida FROM recetas WHERE id_producto = %s", (item['id_producto'],))
            ingredientes = cursor.fetchall()
            for ing in ingredientes:
                if ing['cantidad_requerida'] is not None:
                    total_a_restar = ing['cantidad_requerida'] * item['cantidad']
                    cursor.execute("UPDATE inventario SET stock_inicial = stock_inicial - %s WHERE id_inventario = %s", 
                                   (total_a_restar, ing['id_inventario']))
        
        db.commit()
        return id_pedido_generado
    except Exception as e: 
        db.rollback()
        print(f"Error crítico en registro y stock: {e}")
        return None
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


def obtener_pedidos_caja():
    todos_los_pedidos = obtener_pedido()
    pedidos_para_caja = []
    
    for pedido in todos_los_pedidos:
        estado = pedido.get('estado') or 'Pendiente'
        # Permitimos pedidos activos de mesas y a domicilio que ya pasaron por la cocina (Listo, Entregado, etc.)
        if estado not in ['Pendiente', 'Cocinado', 'Cancelado', 'Pagado']:
            if pedido['total_p'] is not None:
                pedido['total_p'] = float(pedido['total_p'])
            for prod in pedido['productos']:
                if prod['precio_unitario'] is not None:
                    prod['precio_unitario'] = float(prod['precio_unitario'])
            pedidos_para_caja.append(pedido)
            
    return pedidos_para_caja