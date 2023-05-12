import socket
from struct import pack, unpack

# "192.168.5.177"  # Standard loopback interface address (localhost)
HOST = "192.168.0.8"#"localhost"
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, #internet
                  socket.SOCK_STREAM) #TCP
s.bind((HOST, PORT))
s.listen(5)
print(f"Listening on {HOST}:{PORT}")
while True:
    try:
        conn, addr = s.accept()
        print(f'Conectado por alguien ({addr[0]}) desde el puerto {addr[1]}')
        while True:
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
