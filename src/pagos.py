from database.db import conectar_db
from flask import jsonify
from src.inventario import restar_stock_inventario

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
        
        cursor.close()
        db.close()
        return jsonify(pedidos), 200
    except Exception as e:
        print(f"Error al obtener pedidos activos: {e}")
        return jsonify({"error": "Error interno"}), 500
    
def registrar_pago_pedido(id_pedido):
    db = conectar_db()
    if db is None: return jsonify({"error": "DB error"}), 500
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("UPDATE pedidos SET estado = 'Pagado' WHERE id_pedido = %s", (id_pedido,))
        
        cursor.execute("SELECT id_producto, cantidad_v FROM detalle_pedido WHERE id_pedido = %s", (id_pedido,))
        items = cursor.fetchall()
        db.commit() 
        return jsonify({"mensaje": "Pago registrado y stock actualizado"}), 200
    except Exception as e:
        db.rollback() 
        print(f"Error crítico en el proceso de pago: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()