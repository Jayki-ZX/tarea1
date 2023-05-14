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
    # dataDict = mainUnpackData(header["protocol"], data)
    dataDict = mainUnpackData(header[9], data)
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
#HOST = "" #"10.13.0.114"#"localhost

PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

def tcp_receive(protocol):
    # fragment
    if protocol == 4:
        pass
    else:
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
            #header, data = mainUnpackPackage(package)
            print(f"Recibido el paquete {package}")
            #print(header)
            #print(data) 
            conn2.close()
            break

def udp_receive(protocol):
    # fragment
    if protocol == 4:
        pass
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(('', 5002))
        print(f"Listening on {''}:{5002}")
        print("Waiting for data ...")
        # open tcp server
        while True:
            payload, client_address = server.recvfrom(4096) #ojo si necesita mas
            print("Received {} from {}".format(payload, client_address))
            # sent = server.sendto(payload, client_address)
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
    print("conn is")
    print(conn)
    timestampServer = int(time.time())
    # guardarlogs(headerDict, timestampServer)
    print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
    i = 0
    while True:
        configActual = consultarconfig(i) #este i debe corresponder al numero de iteracion en que estamos actualmente
        protocol = configActual[0][0]
        if protocol == 4:
            protocol-=1
        transport_layer = configActual[0][1]
        i = (i+1) % 10
        config = bytearray()
        config.append(protocol)
        config.append(transport_layer)
        print("sent {}".format(config))
        print("sent protocol {} via layer {}".format(protocol, transport_layer))
        print("conn is")
        print(conn)
        conn.send(config)
        print("waiting {} bytes of data".format(messageLength(protocol)))
        if transport_layer == 0:
            tcp_receive(protocol)
        elif transport_layer == 1:
            udp_receive(protocol)
        # data = conn.recv(1024)
        # print(f"Recibido {data}, {len(data)} bytes of data")
        # conn.send(configActual)
        # start_communication(protocol, transport_layer)
        # try:
        #     data = conn.recv(1024)
        #     timestampServer = int(time.time())
        #     if data == b'':
        #         break
        # # except KeyboardInterrupt:
        #     # break
        # except ConnectionResetError:
        #     break
        # headerDict, dataDict = mainUnpackPackage(data)
        # guardardatos(headerDict, dataDict["timestamp"], dataDict)
        # guardarLoss(timestampServer - dataDict["timestamp"], perdida(data, headerDict["protocol"]))
        # print(f"Recibido {data}")
        # conn.send(data)
    conn.close()
