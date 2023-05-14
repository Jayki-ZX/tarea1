import socket
from struct import pack, unpack
import traceback
import time
import sys
from DatabaseWork import *

#Aun no se define para el protocolo 4
def protUnpack(protocol:int, data):
    protocol_unpack = ["<BBl", "<BBlBfBf", "<BBlBfBff", "<BBlBfBffffffff"]
    return unpack(protocol_unpack[protocol], data)

def headerUnpack(header):
    return unpack("<6B2BH", header)

def mainUnpackHeader(header):
    M1, M2, M3, M4, M5, M6, protocol, status, leng_msg = headerUnpack(header)
    MAC = ".".join([hex(x)[2:] for x in [M1, M2, M3, M4, M5, M6]])
    return {"mac":MAC, "protocol":protocol, "status":status, "length":leng_msg}

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
    
def mainUnpackPackage(package):
    header = package[0:10]
    data = package[10:]
    headerDict = mainUnpackHeader(header)
    dataDict = mainUnpackData(header["protocol"], data)
    return headerDict, dataDict

#Perdida de paquetes
lengmsg = [2, 6, 16, 20, 44, 12016]
def dataLength(protocol):
    return lengmsg[protocol]-1

def messageLength(protocol):
    return 1+12+dataLength(protocol)

#Funcion que calcula la perdida de paquetes
def perdida(data, protocol):
    messageLength(protocol) - sys.getsizeof(data)

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
        timestampServer = int(time.time())
        guardarlogs(headerDict, timestampServer)
        print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
        #while True:
        #Solo recibe 5 paquete, para pruebas
        for i in range(5):
            configActual = consultarconfig(i) #este i debe corresponder al numero de iteracion en que estamos actualmente
            protocol = configActual[0][0]
            transport_layer = configActual(i)[0][1]
            conn.send(configActual)
            try:
                data = conn.recv(1024)
                timestampServer = int(time.time())
                if data == b'':
                    break
            # except KeyboardInterrupt:
                # break
            except ConnectionResetError:
                break
            headerDict, dataDict = mainUnpackPackage(data)
            guardardatos(headerDict, dataDict["timestamp"], dataDict)
            guardarLoss(timestampServer - dataDict["timestamp"], perdida(data, headerDict["protocol"]))
            # print("%d" % data[0:4])
            #print(type(data))
            #print(unpack("<ii", data)[0])
            #print(unpack("<ii", data)[1])
            #print("%d" % int.from_bytes(data, 'little'))
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
