import socket
from struct import pack, unpack
import traceback
import time
import sys
from DatabaseWork import *
from juntarFragm import *

#Aun no se define para el protocolo 4
def protUnpack(protocol:int, data):
    protocol_unpack = ["<BBl", "<BBlBfBf", "<BBlBfBff", "<BBlBfBffffffff", "<BBlBlBl2000f2000f2000f"]
    return unpack(protocol_unpack[protocol], data)

def headerUnpack(header):
    return unpack("<h6BBBH", header)

def mainUnpackHeader(header):
    id_device, M1, M2, M3, M4, M5, M6, transport_layer, protocol, leng_msg = headerUnpack(header)
    MAC = ".".join([hex(x)[2:] for x in [M1, M2, M3, M4, M5, M6]])
    return {"id_device": id_device, "mac":MAC, "protocol":protocol, "transport_layer":transport_layer, "length":leng_msg}

def mainUnpackData(protocol:int, data):
    print(data)
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
    header = package[0:12]
    data = package[12:]
    headerDict = mainUnpackHeader(header)
    dataDict = mainUnpackData(headerDict["protocol"], data)
    return headerDict, dataDict

#Perdida de paquetes
lengmsg = [6, 16, 20, 44, 12016]
def dataLength(protocol):
    return lengmsg[protocol]

def messageLength(protocol):
    return 12+dataLength(protocol)

#Funcion que calcula la perdida de paquetes
def perdida(data, protocol):
    messageLength(protocol) - sys.getsizeof(data)


# "192.168.5.177"  # Standard loopback interface address (localhost)
#HOST = "" #"10.13.0.114"#"localhost

PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

def tcp_receive(protocol):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 5001))
    server.listen(5)
    print("Waiting for data ...")
    print(f"Listening on {''}:{5001}")
    # open tcp server
    while True:
        conn2, addr = server.accept()
        print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
        print("Recibiendo datos del protocolo {}".format(protocol))
        # handle the receive process
        package = conn2.recv(1024) # ojo si necesita mas
        print("Received {} bytes of data".format(len(package)-12))
        headerDict, dataDict = mainUnpackPackage(package)
        guardardatos(headerDict, dataDict["Timestamp"], dataDict)
        guardarLoss(timestampServer - dataDict["Timestamp"], perdida(package, headerDict["protocol"]))
        print(f"Recibido el paquete {package}")
        conn2.close()
        break

def udp_receive(protocol):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('', 5002))
    print(f"Listening on {''}:{5002}")
    print("Waiting for data ...")
    # open tcp server
    while True:
        package, client_address = server.recvfrom(4096) #ojo si necesita mas
        print("Received {} from {}".format(package, client_address))
        headerDict, dataDict = mainUnpackPackage(package)
        guardardatos(headerDict, dataDict["Timestamp"], dataDict)
        guardarLoss(timestampServer - dataDict["Timestamp"], perdida(package, headerDict["protocol"]))
        # sent = server.sendto(package, client_address)
        break

def start_communication(protocol, transport_layer):
    print("Starting protocol {} via {}".format(protocol, transport_layer))
    if transport_layer == 0: # TCP
        tcp_receive(protocol)
    elif transport_layer == 1: # UDP
        udp_receive(protocol)
    else:
        print("Layer not recognized")


s = socket.socket(socket.AF_INET, #internet
                  socket.SOCK_STREAM) #TCP
s.bind(('', PORT))
s.listen(5)
print(f"Listening on {''}:{PORT}")

while True:
    conn, addr = s.accept()
    timestampServer = int(time.time())
    # guardarlogs(headerDict, timestampServer)
    print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
    i = 0
    while True:
        configActual = consultarconfig(i) #este i debe corresponder al numero de iteracion en que estamos actualmente
        protocol = configActual[0][0]
        transport_layer = configActual[0][1]
        i = (i+1) % 8
        config = bytearray()
        config.append(protocol)
        config.append(transport_layer)
        print("sent protocol {} via layer {}".format(protocol, transport_layer))
        conn.send(config)
        if transport_layer == 0:
            tcp_receive(protocol)
        elif transport_layer == 1:
            udp_receive(protocol)
    conn.close()
