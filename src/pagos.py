from database.db import conectar_db
from flask import jsonify

def obtener_pagopendiente():
    db = conectar_db()
    if db is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = db.cursor(dictionary=True)
    try:
        # Traemos los pedidos que no han sido pagados aún
        consulta = """
            SELECT id_pedido, numero_mesa, tipo_p, total_p, estado_p, fecha_p 
            FROM pedidos 
            WHERE estado_p != 'Pagado'
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
    if db is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cursor = db.cursor()
    try:
        consulta = "UPDATE pedidos SET estado_p = 'Pagado' WHERE id_pedido = %s"
        cursor.execute(consulta, (id_pedido,))
        db.commit()
        
        cursor.close()
        db.close()
        return jsonify({"mensaje": "Pedido pagado y registrado con éxito"}), 200
    except Exception as e:
        print(f"Error al procesar el pago en DB: {e}")
        return jsonify({"error": "No se pudo procesar el pago"}), 500
