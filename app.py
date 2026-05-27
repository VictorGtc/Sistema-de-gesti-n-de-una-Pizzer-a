from flask import Flask, request, jsonify
from src.usuarios import registrar_usuarios, validar_usuarios
from src.productos import registrar_producto, obtener_productos
from src.categorias import registrar_categoria, obtener_categorias
from src.recetas import registrar_recetas, obtener_receta
from src.inventario import registrar_inventario, obtener_inventario
import os
from werkzeug.utils import secure_filename



app=Flask(__name__)

union_productos = os.path.join(app.root_path,'static','uploads','productos')
union_categorias = os.path.join(app.root_path,'static','uploads','categorias')
app.config['CARPETA_PRODUCTOS']=union_productos
app.config['CARPETA_CATEGORIAS']=union_categorias

extensiones={'.png','.jpg','.jpeg'}

def validacion_imagen(imagen_insertada):
    nombre,extencion=os.path.splitext(imagen_insertada)

    if extencion.lower() in extensiones:
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
    id_producto=request.get_json('id_producto')
    id_inventario=request.get_json('id_inventario')
    cantidad=request.get_json('cantidad_requerida')

    resultado=registrar_recetas(id_producto,id_inventario,cantidad)

    if resultado is True:
        return jsonify({"mensaje" : "Receta registrada"}), 200
    else:
        return jsonify({"mensaje" : "Receta no registrada"}), 401

@app.route('/api/inventario', methods=['POST'])
def api_registrar_inventario():

    nombre_i=request.get_json("nombre_i")
    cantidad_i=request.get_json("cantidad_i")


    resultado=registrar_inventario(nombre_i,cantidad_i)

    if resultado is True:
        return jsonify({"mensaje" : "Ingrediente registrada"}), 200
    else:
        return jsonify({"mensaje" : "Ingrediente no registrada"}), 401

    
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
def api_obtener_receta():
    lista_productos= obtener_inventario()
    return jsonify(lista_productos),200



if __name__== '__main__':
    app.run(debug=True)
