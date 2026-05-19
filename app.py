from flask import Flask, request, jsonify
from src.usuarios import registrar_usuarios, validar_usuarios


app=Flask(__name__)

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
        return jsonify({"mensaje" : "Inicio exitoso"}), 200
    else:
        return jsonify({"mensaje" : "Inicio fallido"}), 200
    


if __name__== '__main__':
    app.run(debug=True)
