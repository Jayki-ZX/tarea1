import socket
from struct import pack, unpack
import traceback
from DatabaseWork import *

#Aun no se define para el protocolo 4
def protUnpack(protocol:int, data):
    protocol_unpack = ["<BBl", "<BBlBfBf", "<BBlBfBff", "<BBlBfBffffffff"]
    return unpack(protocol_unpack[protocol], data)

def headerUnpack(header):
    return unpack("<6B2BH", header)

def mainUnpackData(protocol:int, data):
    if protocol not in [0, 1, 2, 3, 4]:
        print("Error: protocol doesnt exist")
        return None
    def protFunc(protocol, keys):
        def p(data):
            unp = protUnpack(protocol, data)
            return {key:val for (key,val) in zip(keys, unp)}
        return p
    p0 = ["Val", "Batt_level", "Timestamp"]
    p1 = ["Val", "Batt_level", "Timestamp", "Temp", "Pres", "Hum", "Co"]
    p2 = ["Val", "Batt_level", "Timestamp", "Temp", "Pres", "Hum", "Co", "RMS"]
    p3 = ["Val", "Batt_level", "Timestamp", "Temp", "Pres", "Hum", "Co", "RMS", "Ampx", "Frecx", "Ampy", "Frecy", "Ampz", "Frecz"]
    p4 = ["Val", "Batt_level", "Timestamp", "Temp", "Pres", "Hum", "Co", "AccX", "AccY", "AccZ"]
    p = [p0, p1, p2, p3, p4]

    try:
        return protFunc(protocol, p[protocol])(data)
    except Exception:
        print("Data unpacking Error:", traceback.format_exc())
        return None
# "192.168.5.177"  # Standard loopback interface address (localhost)
#HOST = "" #"10.13.0.114"#"localhost"
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, #internet
                  socket.SOCK_STREAM) #TCP
s.bind(('', PORT))
s.listen(5)
print(f"Listening on {''}:{PORT}")
while True:
    try:
        conn, addr = s.accept()
        print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
        #while True:
        #Solo recibe 5 paquete, para pruebas
        for i in range(5):
            try:
                data = conn.recv(1024)
                if data == b'':
                    break
            # except KeyboardInterrupt:
                # break
            except ConnectionResetError:
                break
            # print("%d" % data[0:4])
            print(type(data))
            print(unpack("<ii", data)[0])
            print(unpack("<ii", data)[1])
            print("%d" % int.from_bytes(data, 'little'))
            # print(((data[3] << 24) | (data[2] << 16) | (data[1] << 8) | data[0]))
            print(f"Recibido {data}")
            # if data == b'CONF_REQ':
                # # First byte -> 0=TCP, 1=UDP
                # # Second byte -> Protocol Number
                # conn.send(b'02')
            # else:
                # conn.send(b'unknown')
            conn.send(data)

        conn.close()
        print('Desconectado')
    except KeyboardInterrupt:
        conn.close()
        break
