import json
import sqlite3 as sql

# Documentación https://docs.python.org/3/library/sqlite3.html

def dataSave(header, data):
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        cur.execute('''insert into Info (MAC, Status, Protocol, Data1) values (?, ?, ?, ?)''', (header["MAC"], header["status"], header["protocol"], json.dumps(data)))
        con.commit()

# Esta funcion consulta la base de datos segun su nombre y devuelve sus primeras cinco entradas
# Su uso es para debugging
def consultarconfig(nombre):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {nombre} LIMIT 5")
        return cur.fetchall()
    