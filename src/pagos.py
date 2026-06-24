from database.db import conectar_db
from flask import jsonify
from src.inventario import restar_stock_inventario
from datetime import datetime

def obtener_pagopendiente():
    db = conectar_db()
    if db is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = db.cursor(dictionary=True)
    try:
        # Traemos los pedidos que no han sido pagados aún
        consulta = """
            SELECT id_pedido, numero_mesa, total_p, estado, fecha_p 
            FROM pedidos 
            WHERE estado != 'Pagado'
            ORDER BY fecha_p DESC
        """
        cursor.execute(consulta)
        pedidos = cursor.fetchall()
        
        # Formatear fecha_p para evitar problemas de zona horaria en el frontend
        for p in pedidos:
            if isinstance(p['fecha_p'], datetime):
                p['fecha_p'] = p['fecha_p'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        db.close()
        return jsonify(pedidos), 200
    except Exception as e:
        print(f"Error al obtener pedidos activos: {e}")
        return jsonify({"error": "Error interno"}), 500
    
def registrar_pago_pedido(id_pedido, metodo_pago='efectivo'):
    db = conectar_db()
    if db is None: return jsonify({"error": "DB error"}), 500
    cursor = db.cursor(dictionary=True)
    try:
        # Verificar que el pedido haya sido cocinado/entregado antes de permitir el pago
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        pedido_actual = cursor.fetchone()
        if not pedido_actual:
            return jsonify({"error": "Pedido no encontrado"}), 404
            
        estado_actual = pedido_actual['estado'] or 'Pendiente'
        if estado_actual not in ['Listo', 'Entregado', 'Pagado']:
            return jsonify({"error": "La comida aún está en preparación. Espere a que cocina la despache o entrege."}), 400

        cursor.execute("UPDATE pedidos SET estado = 'Pagado', metodo_pago = %s WHERE id_pedido = %s", (metodo_pago, id_pedido))
        
        cursor.execute("SELECT id_producto, cantidad_v FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        items = cursor.fetchall()
        db.commit() 
        return jsonify({"mensaje": "Pago registrado y stock de venta guardado"}), 200
    except Exception as e:
        db.rollback() 
        print(f"Error crítico en el proceso de pago: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()