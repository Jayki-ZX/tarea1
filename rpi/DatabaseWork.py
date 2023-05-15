import json
import sqlite3 as sql

# Documentación https://docs.python.org/3/library/sqlite3.html

# Esta funcion consulta la base de datos segun su nombre y devuelve sus primeras cinco entradas
# Su uso es para debugging
def consultartabla(nombre):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {nombre}")
        return cur.fetchall()
    
def guardardatos(headerDict, timestamp, dataDict):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO datos (timestamp, data, id_device, mac) VALUES (?, ?, ?, ?)", (timestamp, json.dumps(dataDict), headerDict["id_device"], headerDict["mac"]))
        conn.commit()

def guardarlogs(headerDict, timestamp):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO logs (id_device, transport_layer, protocol, timestamp) VALUES (?, ?, ?, ?)", (headerDict["id_device"], headerDict["transport_layer"], headerDict["protocol"], timestamp))
        conn.commit()

#Para cambiar el orden y protocolo con que manda datos el cliente
def guardarconfig(headerDict):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO config (protocol, transport_layer) VALUES (?, ?)", (headerDict["protocol"], headerDict["transport_layer"]))
        conn.commit()

def guardarLoss(connection_delay, packet_loss):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO loss (connection_delay, packet_loss) VALUES (?, ?)", (connection_delay, 0))
        conn.commit()

#funcion que retorna el valor de protocol y transport layer de la i esima entrada de la tabla config
def consultarconfig(i):
    with sql.connect("tarea.sqlite") as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM config LIMIT 1 OFFSET {i}")
        return cur.fetchall()
