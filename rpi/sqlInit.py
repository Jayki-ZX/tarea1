import sqlite3 as sql



# Funcion que elimina las tablas creadas
def drop_tables():
    conn = sql.connect("tarea.sqlite")
    cur = conn.cursor()
    cur.execute("DROP TABLE data")
    cur.execute("DROP TABLE logs")
    cur.execute("DROP TABLE config")
    cur.execute("DROP TABLE loss")
    conn.commit()
    conn.close()

drop_tables()

create_table_data = '''CREATE TABLE data (
    timestamp STRING,
    data STRING,
    id_device STRING,
    mac STRING
);'''

create_table_logs = '''CREATE TABLE logs (
    id_device STRING,
    transport_layer STRING,
    protocol STRING,
    timestamp STRING
);'''

create_table_config = '''CREATE TABLE config (
    protocol STRING,
    transport_layer STRING
);'''

create_table_loss = '''CREATE TABLE loss (
    connection_delay STRING,
    packet_loss STRING
);'''

conn = sql.connect("tarea.sqlite")
cur = conn.cursor()
try:
    r1 = cur.execute(create_table_data)
    r2 = cur.execute(create_table_logs)
    r3 = cur.execute(create_table_config)
    r4 = cur.execute(create_table_loss)
except Exception:
    pass

cur.execute('INSERT INTO logs values("id", "tcp", "1", "now"), ("id2", "udp", "2", "ma;")')
cur.execute('''INSERT INTO config values("0", "UDP"), ("1", "UDP"), ("2", "UDP"), ("3", "UDP"), ("4", "UDP"),
("0", "TCP"), ("1", "TCP"), ("2", "TCP"), ("3", "TCP"), ("4", "TCP")
''')
print(cur.execute("SELECT * FROM config").fetchall())
conn.commit()
conn.close()


# inicializa la BDD