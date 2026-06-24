from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from src.usuarios import registrar_usuarios, validar_usuarios,obtener_usuario,actualizar_usuario_completo
from src.productos import registrar_producto, obtener_productos, actualizar_producto, cambiar_estado_producto,obtener_productos_publicos
from src.categorias import registrar_categoria, obtener_categorias, actualizar_categoria, obtener_categorias_publicas, cambiar_estado_categoria
from src.recetas import registrar_recetas, obtener_receta, borrar_ingrediente_de_receta
from src.inventario import registrar_inventario, obtener_inventario,cambiar_estado_ingrediente, actualizar_inventario, sumar_stock_db
from src.pedidos import registrar_pedidos_mesa,obtener_pedido,registrar_pedido_domicilio, actualizar_pedidos,obtener_pedidos_caja, registrar_pedido_domicilio
from src.clientes import registrar_clientes, validar_clientes
from src.pagos import obtener_pagopendiente,registrar_pago_pedido

import os
from werkzeug.utils import secure_filename



app=Flask(__name__)
CORS(app)

union_productos = os.path.join(app.root_path,'static','uploads','productos')
union_categorias = os.path.join(app.root_path,'static','uploads','categorias')
app.config['CARPETA_PRODUCTOS']=union_productos
app.config['CARPETA_CATEGORIAS']=union_categorias

extensiones={'.png','.jpg','.jpeg'}

def validacion_imagen(imagen_insertada):
    nombre,extension=os.path.splitext(imagen_insertada)

    if extension.lower() in extensiones:
        return True
    else:
        return False


@app.route('/registrar', methods=['POST'])

def api_usuarios():
    datos=request.get_json()
    nombre=datos.get('nombre')
    apellido=datos.get('apellido')
    correo=datos.get('correo')
    password=datos.get('password')
    telefono=datos.get('telefono')
    rol=datos.get('rol')

    resultado=registrar_usuarios(nombre,apellido,correo,password,telefono,rol)

    if resultado is True:
        return jsonify({"mensaje": "Usuario Guardado"}), 201
    else:
        return jsonify({"mensaje": "Error del servidor"}), 500

@app.route('/login', methods=['POST'])
def api_login():
    datos = request.get_json()
    correo = datos.get('correo')
    password = datos.get('password') 

    if not correo or not password:
        return jsonify({"mensaje": "Faltan datos requeridos"}), 400

    # 1. Intentamos validar primero si es un Empleado (Usuario interno)
    es_usuario, info_usuario = validar_usuarios(correo, password)
    if es_usuario:
        return jsonify({
            "mensaje": "Inicio exitoso",
            "perfil": {
                "Nombre": info_usuario.get('Nombre'),
                "Correo": info_usuario.get('Correo'),
                "Rol": info_usuario.get('Rol'),  # admin, cocina, mesero
                "Tipo": "empleado"
            }
        }), 200
    elif info_usuario == "Esta cuenta ha sido suspendida. Contacte al administrador.":
        return jsonify({"mensaje": info_usuario}), 403

    # 2. Si no es empleado, buscamos en la tabla de Clientes
    es_cliente, info_cliente = validar_clientes(correo, password)
    if es_cliente:
        return jsonify({
            "mensaje": "Inicio exitoso",
            "perfil": {
                "Nombre": info_cliente.get('Nombre'),
                "Correo": info_cliente.get('Correo'),
                "Rol": "cliente",  
                "Tipo": "cliente",
                "id_cliente": info_cliente.get('id_cliente'),
                "Direccion": info_cliente.get('Direccion')
            }
        }), 200

    # 3. Si no coincide en ninguna de las dos tablas
    return jsonify({"mensaje": "El correo o la contraseña son incorrectos"}), 401

@app.route('/api/productos', methods=['POST'])

def api_regis_producto():
    nombre=request.form.get('nombre')
    precio=request.form.get('precio')
    id_categori=request.form.get('id_categoria')
    archivo_foto=request.files.get('imagen_route')

    if not archivo_foto or archivo_foto.filename == '':
        return jsonify({"mensaje" :"La imagen no fue subida"}), 400
        
    if not validacion_imagen(archivo_foto.filename):
        return jsonify({"mensaje" :"Formato no permitido"}), 400
    
    nombre_limpio=secure_filename(archivo_foto.filename)

    ruta_segura = os.path.join(app.config['CARPETA_PRODUCTOS'],nombre_limpio)

    archivo_foto.save(ruta_segura)

    resultado=registrar_producto(nombre, precio, nombre_limpio, id_categori)

    if resultado is True:
        return jsonify({"mensaje" : "El producto ha sido ingresado exitosamente" }), 200
    else:
        return jsonify({"mensaje" : "El producto no pudo ser registrado"}), 401

@app.route('/api/categorias', methods=['POST'])
def api_registrar_categoria():
    nombre=request.form.get('nombre')
    foto_categoria=request.files.get('image_route')

    if not foto_categoria or foto_categoria.filename == '':
        return jsonify({"mensaje" :"La imagen no fue subida"}), 400
        
    if not validacion_imagen(foto_categoria.filename):
        return jsonify({"mensaje" :"Formato no permitido"}), 400
    
    nombre_limpio=secure_filename(foto_categoria.filename)

    ruta_segura = os.path.join(app.config['CARPETA_CATEGORIAS'],nombre_limpio)

    foto_categoria.save(ruta_segura)

    resultado=registrar_categoria(nombre,nombre_limpio)
    if resultado is True:
        return jsonify({"mensaje" : "El producto ha sido ingresado exitosamente" }), 200
    else:
        return jsonify({"mensaje" : "El producto no pudo ser registrado"}), 401
    

@app.route('/api/recetas', methods=['POST'])
def api_registrar_recetas():
    datos = request.get_json()
    id_producto = datos.get('id_producto')
    lista_ingredientes = datos.get('ingredientes')

    if not id_producto or not lista_ingredientes:
        return jsonify({"mensaje": "Faltan datos obligatorios"}), 400
    hubo_error = False
    for ing in lista_ingredientes:
        id_inventario = ing.get('id_inventario')
        cantidad = ing.get('cantidad_requerida')
        resultado = registrar_recetas(id_producto, id_inventario, cantidad)
        if not resultado:
            hubo_error = True

    if not hubo_error:
        return jsonify({"mensaje": "Receta registrada con éxito"}), 200
    else:
        return jsonify({"mensaje": "Error al registrar algunos ingredientes"}), 500
    



@app.route('/api/inventario', methods=['POST'])
def api_registrar_inventario():
    datos=request.get_json()
    nombre_i=datos.get("nombre_i")
    
    stock_inicial=float(datos.get('stock_actual',0))
    stock_minimo=float(datos.get('stock_minimo',0))
    unidad_registrada=datos.get('unidad_registrada')
    
    resultado=registrar_inventario(nombre_i,stock_inicial,stock_minimo,unidad_registrada)

    if resultado == True:
        return jsonify({"mensaje" : "Inventario registrado"}), 200
    else:
        return jsonify({"mensaje" : "Inventario no registrada"}), 500



@app.route('/api/pedido_local', methods=['POST'])
def api_registrar_pedido_local():
    datos=request.get_json()
    numero_mesa=datos.get('numero_mesa')
    id_usuario=datos.get('id_usuario')
    lita_productos= datos.get('lista_producto')
    
    id_cliente = datos.get('id_cliente')
    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    direccion = datos.get('direccion')
    telefono = datos.get('telefono')
    cedula_ruc = datos.get('cedula_ruc', '9999999999')
    metodo_pago = datos.get('metodo_pago', 'efectivo')

    if not numero_mesa or not id_usuario or not lita_productos:
        return jsonify({"mensaje": "Faltan compos obligatorios para este procedimiento"})

    resultado=registrar_pedidos_mesa(
        numero_mesa, 
        id_usuario, 
        lita_productos, 
        id_cliente=id_cliente, 
        nombre=nombre, 
        apellido=apellido, 
        direccion=direccion, 
        telefono=telefono, 
        cedula_ruc=cedula_ruc, 
        metodo_pago=metodo_pago
    )

    if resultado is True:
        return jsonify({"mensaje" : "El pedido ha sido registrado exitosamente"}), 200
    else:
        return jsonify({"mensaje" : "El pedido no pudo ser registrado"}), 401



#----------------
@app.route('/api/registrar_cliente', methods=['POST'])
def api_registrar_cliente():
    datos = request.get_json()
    
    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    correo = datos.get('correo')
    password = datos.get('password')
    telefono = datos.get('telefono')
    direccion = datos.get('direccion')

    exito = registrar_clientes(nombre, apellido, correo, password, telefono, direccion)
    
    if exito:
        return jsonify({"mensaje": "Cliente registrado con éxito"}), 201
    else:
        return jsonify({"error": "No se pudo registrar al cliente"}), 500






#=====================

@app.route('/api/pedido_domicilio', methods=['POST'])
def api_pedido_domicilio():
    datos = request.get_json()
    
    id_cliente = datos.get('id_cliente')
    productos = datos.get('productos') 
    metodo_pago = datos.get('metodo_pago', 'efectivo')
    numero_tarjeta = datos.get('numero_tarjeta', '')
    direccion = datos.get('direccion', '')
    telefono = datos.get('telefono', '')
    cedula_ruc = datos.get('cedula_ruc', '9999999999')

    if not id_cliente or not productos:
        return jsonify({"error": "Faltan datos obligatorios (cliente o productos)"}), 400
    estado_pago_simulado = 'Pendiente'

    if metodo_pago == 'tarjeta':
        tarjeta_limpia = numero_tarjeta.replace(" ", "")
        
        if tarjeta_limpia == '4242424242424242':
            estado_pago_simulado = 'Pagado'
        else:
            return jsonify({
                "error": "Transacción rechazada: La tarjeta simulada no cuenta con fondos suficientes o es inválida. Usa la tarjeta de pruebas."
            }), 402

    exito = registrar_pedido_domicilio(
        id_cliente, None, productos,
        metodo_pago=metodo_pago,
        direccion_entrega=direccion,
        telefono_entrega=telefono,
        cedula_ruc=cedula_ruc
    )
    
    if exito:
        return jsonify({
            "mensaje": "Pedido a domicilio procesado con éxito",
            "estado_pago": estado_pago_simulado
        }), 201
    else:
        return jsonify({"error": "No se pudo procesar el pedido a domicilio"}), 500


@app.route('/api/usuarios/registrar_empleado', methods=['POST'])
def api_registrar_empleado():
    datos = request.get_json()
    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    correo = datos.get('correo')
    password = datos.get('password')
    telefono = datos.get('telefono')
    rol = datos.get('rol') # Capturamos el rol elegido por el admin

    if not all([nombre,apellido, correo, password, telefono, rol]):
        return jsonify({"mensaje": "Todos los campos son obligatorios"}), 400

    # Llamamos a la función de tu módulo con el nuevo parámetro 'rol'
    exito = registrar_usuarios(nombre,apellido, correo, password, telefono, rol)

    if exito:
        return jsonify({"mensaje": "Empleado registrado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "El correo ya está registrado o hubo un error"}), 500



@app.route('/api/productos/actualizar/<int:id_producto>', methods=['POST'])
def api_actualizar_producto(id_producto):
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    id_categoria = request.form.get('id_categoria')
    archivo_foto = request.files.get('imagen_route') 
    nombre_limpio = None

    if archivo_foto and archivo_foto.filename != '':
        if not validacion_imagen(archivo_foto.filename): 
            return jsonify({"mensaje": "Formato de imagen no permitido"}), 400
        
        nombre_limpio = secure_filename(archivo_foto.filename)
        ruta_segura = os.path.join(app.config['CARPETA_PRODUCTOS'], nombre_limpio)
        archivo_foto.save(ruta_segura)
    resultado = actualizar_producto(id_producto, nombre, precio, nombre_limpio, id_categoria)

    if resultado is True:
        return jsonify({"mensaje": "El producto ha sido actualizado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "El producto no pudo ser actualizado"}), 500
    

@app.route('/api/categorias/actualizar/<int:id_categoria>', methods=['POST'])
def api_actualizar_categoria(id_categoria):
    nombre = request.form.get('nombre')
    foto_categoria = request.files.get('image_route') # Mismo nombre de tu registrar_categoria

    nombre_limpio = None
    if foto_categoria and foto_categoria.filename != '':
        if not validacion_imagen(foto_categoria.filename):
            return jsonify({"mensaje": "Formato de imagen no permitido"}), 400
        
        nombre_limpio = secure_filename(foto_categoria.filename)
        ruta_segura = os.path.join(app.config['CARPETA_CATEGORIAS'], nombre_limpio)
        foto_categoria.save(ruta_segura)

    resultado = actualizar_categoria(id_categoria, nombre, nombre_limpio)

    if resultado is True:
        return jsonify({"mensaje": "La categoría ha sido actualizada exitosamente"}), 200
    else:
        return jsonify({"mensaje": "La categoría no pudo ser actualizada"}), 500


@app.route('/api/pagar_pedido/<int:id_pedido>', methods=['POST'])
def finalizar_cobro(id_pedido):
    datos = request.get_json() or {}
    metodo_pago = datos.get('metodo_pago', 'efectivo')
    return registrar_pago_pedido(id_pedido, metodo_pago)
    



@app.route('/api/pagar_domicilio', methods=['POST'])
def api_pagar_domicilio():
    datos = request.json
    id_cliente = datos.get('id_cliente')
    lista_producto = datos.get('lista_producto')
    id_usuario = datos.get('id_usuario', None) 
    metodo_pago = datos.get('metodo_pago', 'efectivo')
    numero_tarjeta = datos.get('numero_tarjeta', '')
    direccion = datos.get('direccion', '')
    telefono = datos.get('telefono', '')
    cedula_ruc = datos.get('cedula_ruc', '9999999999')

    estado_pago_simulado = 'Pendiente'
    if metodo_pago == 'tarjeta':
        tarjeta_limpia = numero_tarjeta.replace(" ", "")
        if tarjeta_limpia == '4242424242424242':
            estado_pago_simulado = 'Pagado'
        else:
            return jsonify({
                "error": "Transacción rechazada: La tarjeta simulada no cuenta con fondos suficientes o es inválida. Usa la tarjeta de pruebas."
            }), 402

    id_pedido = registrar_pedido_domicilio(
        id_cliente, id_usuario, lista_producto,
        metodo_pago=metodo_pago,
        direccion_entrega=direccion,
        telefono_entrega=telefono,
        cedula_ruc=cedula_ruc
    )
    
    if id_pedido:
        # Retornamos éxito sin llamar a registrar_pago_pedido para que el estado de preparación
        # siga en 'Pendiente' y la cocina pueda cocinarlo. El método de pago queda registrado.
        return jsonify({
            "mensaje": "Pedido a domicilio registrado con éxito",
            "id_pedido": id_pedido,
            "estado_pago": estado_pago_simulado
        }), 201
    else:
        return jsonify({"error": "Error al registrar pedido"}), 500


# ==== Rutas GET 


@app.route('/api/obtener_categorias_publicas', methods=['GET'])
def api_obtener_categorias_publicas():
    categorias = obtener_categorias_publicas() 
    return jsonify(categorias)

@app.route('/api/obtener_productos_publicos', methods=['GET'])
def api_obtener_productos_publicos():

    productos = obtener_productos_publicos()  
    return jsonify(productos)

@app.route('/api/categoria/estado', methods=['PUT'])
def api_cambiar_estado_categoria():
    datos = request.get_json()
    
    # OJO: Validamos que las llaves correspondan exactamente a lo enviado por JS
    id_categoria = datos.get('id_categoria')
    nuevo_estado = datos.get('activo_c')

    if id_categoria is None or nuevo_estado is None:
        return jsonify({"mensaje": "Datos incompletos"}), 400
        
    exito = cambiar_estado_categoria(id_categoria, nuevo_estado)
    if exito:
        mensaje = "Estado de categoría actualizado"
        return jsonify({"mensaje": mensaje}), 200
    else:
        return jsonify({"mensaje": "No se pudo cambiar el estado en la base de datos"}), 500
    

@app.route('/api/mis_pedidos_activos', methods=['GET'])
def api_mis_pedidos_activos():
    try:
        id_cliente = request.args.get('id_cliente')
        numero_mesa = request.args.get('numero_mesa')
        todos_los_pedidos = obtener_pedido()
        
        if not todos_los_pedidos:
            return jsonify([]), 200

        pedidos_filtrados = []
        for p in todos_los_pedidos:
            estado_crudo = p.get('estado') or p.get('estado_p')
            estado_p = str(estado_crudo).strip() if estado_crudo is not None else 'Pendiente'
        
            # Solo procesamos estados activos (no pagados/cancelados)
            if estado_p not in ['Pagado', 'Cancelado']:
                
                id_p_cliente = p.get('id_cliente')
                p_mesa = p.get('numero_mesa')
                
                if id_cliente and id_p_cliente is not None:
                    if str(id_p_cliente).strip() == str(id_cliente).strip():
                        pedidos_filtrados.append(p)
                elif numero_mesa and p_mesa is not None:
                    if str(p_mesa).strip() == str(numero_mesa).strip():
                        pedidos_filtrados.append(p)

        return jsonify(pedidos_filtrados), 200

    except Exception as e:
        print(f"Error crítico en API mis_pedidos_activos: {e}")
        return jsonify({"mensaje": "Error interno al procesar los pedidos"}), 500
    

@app.route('/api/admin/historial_ventas', methods=['GET'])
def api_historial_ventas():
    try:
        todos_los_pedidos = obtener_pedido()
        
        if not todos_los_pedidos:
            return jsonify([]), 200

        historial = []
        for p in todos_los_pedidos:
            estado_crudo = p.get('estado') or p.get('estado_p')
            estado = str(estado_crudo).strip() if estado_crudo is not None else 'Pendiente'
            if estado in ['Pagado', 'Cancelado']:
                historial.append({
                    "id_pedido": p.get('id_pedido'),
                    "origen_pedido": p.get('origen_pedido', 'No especificado'),
                    "fecha_p": p.get('fecha_p'),
                    "total_p": p.get('total_p', 0),
                    "estado": estado,
                    "productos": p.get('productos', [])
                })
        historial.sort(key=lambda x: x['id_pedido'], reverse=True)
        return jsonify(historial), 200

    except Exception as e:
        print(f"Error en API historial_ventas: {e}")
        return jsonify({"mensaje": "Error interno al procesar el historial"}), 500

@app.route('/api/obtener_categorias', methods=['GET'])
def api_obtener_categorias():
    lista_categorias= obtener_categorias()
    
    return jsonify(lista_categorias),200

@app.route('/api/obtener_productos', methods=['GET'])
def api_obtener_productos():
    lista_productos= obtener_productos()
    return jsonify(lista_productos),200
    

@app.route('/api/obtener_receta', methods=['GET'])
def api_obtener_receta():
    lista_productos= obtener_receta()
    return jsonify(lista_productos),200

@app.route('/api/obtener_inventario', methods=['GET'])
def api_obtener_ingrediente():
    lista_productos= obtener_inventario()
    return jsonify(lista_productos),200

@app.route('/api/obtener_pedido', methods=['GET'])
def api_obtener_pedidos():
    lista_pedidos=obtener_pedido()
    if not lista_pedidos:
        return jsonify({"mensaje":"No hay pedidos para hoy"}),200
    else:
        return jsonify(lista_pedidos),200

@app.route('/api/obtener_usuario', methods=['GET'])
def api_obtener_usuario():
    lista_usuarios=obtener_usuario()
    if not lista_usuarios:
        return jsonify({"mensaje":"No hay usuarios existentes"}),200
    else:
        return jsonify(lista_usuarios),200
    

@app.route('/api/pedidos/activos', methods=['GET'])
def api_obtener_pedidos_activos():
    pedidos=obtener_pedidos_caja()
    return jsonify(pedidos),200









#=========== ACTUALIZACIONES ====================




@app.route('/api/actualizar_estado', methods=['PUT'])
def api_actualizar_estado_pedido():
    datos=request.get_json()
    id_pedido=datos.get('id_pedido')
    nuevo_estado=datos.get('nuevo_estado')

    if not id_pedido or not nuevo_estado:
        return jsonify({"Error": "Faltan datos obligatorios (id o el estado)"} ), 400
    resultado=actualizar_pedidos(id_pedido,nuevo_estado)

    if resultado:
        return jsonify({"Mensaje":f"El pedido #{id_pedido} se actualizo al estado {nuevo_estado}"}), 200
    else: 
        return jsonify({"Mensaje":f"El pedido #{id_pedido} no pudo actualizarse su estado"}), 500
    

@app.route('/api/inventario/estado', methods=['PUT'])
def api_cambiar_estado_inventario():
    datos = request.get_json()
    id_inventario = datos.get('id_inventario')
    nuevo_estado = datos.get('activo') 
    
    if id_inventario is None or nuevo_estado is None:
        return jsonify({"mensaje": "Datos incompletos"}), 400
        
    exito = cambiar_estado_ingrediente(id_inventario, nuevo_estado)
    
    if exito:
        mensaje = "Ingrediente deshabilitado" if nuevo_estado == 0 else "Ingrediente habilitado"
        return jsonify({"mensaje": mensaje}), 200
    else:
        return jsonify({"mensaje": "No se pudo cambiar el estado"}), 500

@app.route('/api/pedidos/pagar/<int:id_pedido>', methods=['PUT'])
def api_pagar_pedido(id_pedido):

    resultado = actualizar_pedidos(id_pedido, 'Pagado')
    
    if resultado is True:
        return jsonify({"mensaje": "El pedido ha sido pagado y cerrado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "No se pudo registrar el pago del pedido"}), 500


@app.route('/api/producto/estado', methods=['PUT'])
def api_cambiar_estado_producto():
    datos = request.get_json()
    id_producto = datos.get('id_producto')
    nuevo_estado = datos.get('activo_p')
    if id_producto is None or nuevo_estado is None:
        return jsonify({"mensaje": "Datos incompletos"}), 400
    exito = cambiar_estado_producto(id_producto,nuevo_estado)
    if exito:
        mensaje = "Producto deshabilitado" if nuevo_estado == 0 else "Producto habilitado"
        return jsonify({"mensaje": mensaje}), 200
    else:
        return jsonify({"mensaje": "No se pudo cambiar el estado"}), 500


@app.route('/api/inventario/actualizar', methods=['PUT'])
def api_actualizar_inventario():
    try:
        datos = request.get_json()
        id_inventario = datos.get('id_inventario')
        nombre = datos.get('nombre')
        cantidad_inicial = datos.get('cantidad_inicial')
        cantidad_minima = datos.get('cantidad_minima')
        unidad = datos.get('unidad')

        # Validación rápida de seguridad
        if not all([id_inventario, nombre, cantidad_inicial is not None, cantidad_minima is not None, unidad]):
            return jsonify({"mensaje": "Datos del insumo incompletos"}), 400

        # Convertir a tipos numéricos correctos
        exito = actualizar_inventario(
            int(id_inventario), 
            nombre, 
            float(cantidad_inicial), 
            float(cantidad_minima), 
            unidad
        )

        if exito:
            return jsonify({"mensaje": "Insumo actualizado con éxito en el inventario"}), 200
        else:
            return jsonify({"mensaje": "No se pudo actualizar el insumo o no sufrió cambios"}), 404

    except Exception as e:
        print(f"Error en API api_actualizar_inventario: {e}")
        return jsonify({"mensaje": "Error interno del servidor"}), 500


@app.route('/api/usuarios/actualizar', methods=['PUT'])
def api_actualizar_usuario_completo():
    try:
        datos = request.get_json()
        id_usuario = datos.get('id_usuario')
        nombre = datos.get('nombre')
        apellido = datos.get('apellido')
        usuario = datos.get('usuario')
        rol = datos.get('rol')
        telefono = datos.get('telefono')


        if not all([id_usuario, nombre, apellido, usuario, rol, telefono]):
            return jsonify({"mensaje": "Datos del empleado incompletos"}), 400

        exito = actualizar_usuario_completo(int(id_usuario), nombre, apellido, usuario, rol, telefono)

        if exito:
            return jsonify({"mensaje": "Empleado actualizado con éxito"}), 200
        else:
            return jsonify({"mensaje": "No se pudo actualizar el empleado o no sufrió cambios"}), 404
    except Exception as e:
        print(f"Error en API api_actualizar_usuario_completo: {e}")
        return jsonify({"mensaje": "Error interno del servidor"}), 500
    


@app.route('/api/inventario/sumar/<int:id>', methods=['PUT'])
def api_sumar_inventario(id):
    datos = request.json
    cantidad = float(datos.get('cantidad'))
    unidad = datos.get('unidad') # Capturamos la unidad que llega desde el select
    
    # Lógica de conversión (Ajusta esto según tu unidad base: si guardas todo en gramos/ml)
    cantidad_final = cantidad
    
    if unidad == 'kg':
        cantidad_final = cantidad * 1000
    elif unidad == 'l':
        cantidad_final = cantidad * 1000
    # Si es 'g', 'ml' o 'unid', se queda igual
    
    if cantidad_final <= 0:
        return jsonify({"mensaje": "Cantidad inválida"}), 400
    
    try:
        # Pasamos la cantidad ya convertida a la base de datos
        resultado = sumar_stock_db(id, cantidad_final)
        return jsonify({"mensaje": "Stock sumado exitosamente"}), 200
    except Exception as e:
        print(f"--- ERROR DETECTADO ---: {e}") 
        return jsonify({"mensaje": f"Error interno: {str(e)}"}), 500

# ===== rutas de las vistas 

@app.route('/', methods=['GET'])
def vista_login():
    return render_template('login.html')

@app.route('/index', methods=['GET'])
def vista_index():
    return render_template('index.html')

@app.route('/cocina', methods=['GET'])
def vista_cocina():
    return render_template('cocina.html')

@app.route('/registro', methods=['GET'])
def vista_registro():
    return render_template('registro.html')

@app.route('/admin', methods=['GET'])
def vista_admin():
    return render_template('admin.html')

@app.route('/cajero', methods=['GET'])
def vista_cajero():
    return render_template('cajero.html')

@app.route('/menu', methods=['GET'])
def vista_menu_qr():
    numero_mesa = request.args.get('mesa')
    return render_template('index.html', mesa=numero_mesa)

@app.route('/mesero', methods=['GET'])
def vista_mesero():
    return render_template('mesero.html')

@app.route('/api/mis_pedidos_historial', methods=['GET'])
def api_mis_pedidos_historial():
    try:
        id_cliente = request.args.get('id_cliente')
        numero_mesa = request.args.get('numero_mesa')
        todos_los_pedidos = obtener_pedido()
        
        if not todos_los_pedidos:
            return jsonify([]), 200

        pedidos_filtrados = []
        for p in todos_los_pedidos:
            estado_crudo = p.get('estado') or p.get('estado_p')
            estado_p = str(estado_crudo).strip() if estado_crudo is not None else 'Pendiente'
        
            # Pedidos completados (pagados/cancelados)
            if estado_p in ['Pagado', 'Cancelado']:
                id_p_cliente = p.get('id_cliente')
                p_mesa = p.get('numero_mesa')
                
                if id_cliente and id_p_cliente is not None:
                    if str(id_p_cliente).strip() == str(id_cliente).strip():
                        pedidos_filtrados.append(p)
                elif numero_mesa and p_mesa is not None:
                    if str(p_mesa).strip() == str(numero_mesa).strip():
                        pedidos_filtrados.append(p)

        return jsonify(pedidos_filtrados), 200
    except Exception as e:
        print(f"Error en API mis_pedidos_historial: {e}")
        return jsonify({"mensaje": "Error interno al obtener el historial"}), 500

@app.route('/api/usuarios/estado', methods=['PUT'])
def api_cambiar_estado_usuario():
    try:
        datos = request.get_json()
        id_usuario = datos.get('id_usuario')
        nuevo_estado = datos.get('activo')
        
        if id_usuario is None or nuevo_estado is None:
            return jsonify({"mensaje": "Datos incompletos"}), 400
            
        from src.usuarios import cambiar_estado_usuario
        exito = cambiar_estado_usuario(int(id_usuario), int(nuevo_estado))
        
        if exito:
            mensaje = "Empleado suspendido con éxito" if int(nuevo_estado) == 0 else "Empleado habilitado con éxito"
            return jsonify({"mensaje": mensaje}), 200
        else:
            return jsonify({"mensaje": "No se pudo cambiar el estado del empleado"}), 500
    except Exception as e:
        print(f"Error en API cambiar_estado_usuario: {e}")
        return jsonify({"mensaje": "Error interno del servidor"}), 500



# ============== funciones de eliminaciones 

@app.route('/api/recetas/eliminar/<int:id_producto>/<int:id_inventario>', methods=['DELETE'])
def eliminar_ingrediente_receta(id_producto, id_inventario):
    try:
        exito = borrar_ingrediente_de_receta(id_producto, id_inventario)
        
        if exito:
            return jsonify({"mensaje": "Ingrediente removido con éxito de la receta"}), 200
        else:
            return jsonify({"mensaje": "No se pudo encontrar el ingrediente especificado"}), 404
    except Exception as e:
        print(f"Error en API eliminar_ingrediente_receta: {e}")
        return jsonify({"mensaje": "Error interno en el servidor"}), 500


if __name__== '__main__':
    app.run(debug=True)
