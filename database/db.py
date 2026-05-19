import mysql.connector 
from config import Config
import sys
sys.path.append(".")

def conectar_db():
    try:
        conexion=mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB)
        
        return conexion
    
    except TypeError:
        print('Error al conectar a la base de datos')
        return None
