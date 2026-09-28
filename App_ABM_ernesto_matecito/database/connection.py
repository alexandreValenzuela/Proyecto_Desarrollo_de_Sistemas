import os
import sqlite3

def obtener_conexion():
    nombre_bbdd = 'database'
    if not os.path.exists(nombre_bbdd):
        os.mkdir(nombre_bbdd)
        print('Se creó la carpeta database con éxito')
        
    conexion = sqlite3.connect('database/app_abm.db')
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion
