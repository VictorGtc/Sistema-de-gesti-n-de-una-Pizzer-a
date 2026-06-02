from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from src.usuarios import registrar_usuarios, validar_usuarios
from src.productos import registrar_producto, obtener_productos
from src.categorias import registrar_categoria, obtener_categorias
from src.recetas import registrar_recetas, obtener_receta
from src.inventario import registrar_inventario, obtener_inventario
from src.pedidos import registrar_pedidos_mesa,obtener_pedido,registrar_pedido_domicilio, actualizar_pedidos
from src.clientes import registrar_clientes, validar_clientes


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

@app.route('/')

def home ():
    return 'Bienvenidos a la pagina principal de la pizzeria'   

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

@app.route('/login',methods=['POST'])

def api_login():
    datos=request.get_json()
    correo=datos.get('correo')
    contraseña=datos.get('contraseña')

    resultado, info =validar_usuarios(correo,contraseña)

    if resultado is True:
        return jsonify({"mensaje" : "Inicio exitoso","Usuario": info}), 200
    else:
        return jsonify({"mensaje" :info}), 401
    

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
    datos=request.get_json()
    id_producto=datos.get('id_producto')
    id_inventario=datos.get('id_inventario')
    cantidad=datos.get('cantidad_requerida')

    resultado=registrar_recetas(id_producto,id_inventario,cantidad)

    if resultado is True:
        return jsonify({"mensaje" : "Receta registrada"}), 200
    else:
        return jsonify({"mensaje" : "Receta no registrada"}), 401

@app.route('/api/inventario', methods=['POST'])
def api_registrar_inventario():
    datos=request.get_json()
    nombre_i=datos.get("nombre_i")
    cantidad_i=datos.get("cantidad_i")


    resultado=registrar_inventario(nombre_i,cantidad_i)

    if resultado is True:
        return jsonify({"mensaje" : "Ingrediente registrada"}), 200
    else:
        return jsonify({"mensaje" : "Ingrediente no registrada"}), 401
    


@app.route('/api/pedido_local', methods=['POST'])
def api_registrar_pedido_local():
    datos=request.get_json()
    numero_mesa=datos.get('numero_mesa')
    id_usuario=datos.get('id_usuario')
    lita_productos= datos.get('productos')

    if not numero_mesa or not id_usuario or not lita_productos:
        return jsonify({"mensaje": "Faltan compos obligatorios para este procedimiento"})

    resultado=registrar_pedidos_mesa(numero_mesa,id_usuario,lita_productos)

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


@app.route('/api/login_cliente', methods=['POST'])
def api_login_cliente():
    datos = request.get_json()
    correo = datos.get('correo')
    password = datos.get('password')

    exito, resultado = validar_clientes(correo, password)
    
    if exito:
        return jsonify({"mensaje": "Login correcto", "cliente": resultado}), 200
    else:
        return jsonify({"error": resultado}), 401




#=====================

@app.route('/api/pedido_domicilio', methods=['POST'])
def api_pedido_domicilio():
    datos = request.get_json()
    
    id_cliente = datos.get('id_cliente')
    productos = datos.get('productos') 
    if not id_cliente or not productos:
        return jsonify({"error": "Faltan datos obligatorios (cliente o productos)"}), 400

    exito = registrar_pedido_domicilio(id_cliente, None, productos)
    
    if exito:
        return jsonify({"mensaje": "Pedido a domicilio guardado con éxito"}), 201
    else:
        return jsonify({"error": "No se pudo procesar el pedido a domicilio"}), 500




    
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
    

@app.route('/api/productos/actualizar/<int:id_producto>',methods=['POST'])
def api_actualizar_producto():
    nombre=request.form.get('nombre')
    precio=request.form.get('precio')
    id_categoria=request.form.get('id_categoria')
    archivo_foto=request.files.get('imagen_route')

    nombre_limpio=None

    if archivo_foto and archivo_foto.filename != '':
        if not validacion_imagen(archivo_foto.filename):
            return jsonify({"Mensaje":"Formato de imagen no permitida"}), 400
        nombre_limpio=secure_filename(archivo_foto.filename)
        ruta_segura= os.path.join(app.config['CARPETA PRODUCTOS'],nombre_limpio)
        archivo_foto.save(ruta_segura)

    resultado = actualizar_producto(id_producto, nombre, precio, nombre_limpio, id_categoria)

    if resultado is True:
        return jsonify({"mensaje": "El producto ha sido actualizado exitosamente"}), 200
    else:
        return jsonify({"mensaje": "El producto no pudo ser actualizado"}), 500




# ===== rutas de las vistas 

@app.route('/login', methods=['GET'])
def vista_login():
    return render_template('login.html')

@app.route('/index', methods=['GET'])
def vista_index():
    return render_template('index.html')

@app.route('/cocina', methods=['GET'])
def vista_cocina():
    return render_template('cocina.html')






if __name__== '__main__':
    app.run(debug=True)
