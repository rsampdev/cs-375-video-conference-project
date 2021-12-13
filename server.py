import json
import socket
import select

FORMAT = "utf-8"
HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 8888

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

print(f"Listening for connections on {IP}:{PORT}...")

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode(FORMAT).strip())

        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print("Accepted new connection from {}:{}, username: {}".format(*client_address, user["data"].decode(FORMAT)))
        else:
            message = receive_message(notified_socket)

            if message is False:
                print("Closed connection from: {}".format(clients[notified_socket]["data"].decode(FORMAT)))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            data = json.loads(message["data"])

            for client_socket in clients:
                if client_socket != notified_socket:
                    if (data["type"] == "connect"):
                        connect_data = json.dumps({"type":"connect", "data":"Joined the room!"}).encode(FORMAT)
                        connect_header = f"{len(connect_data):<{HEADER_LENGTH}}".encode(FORMAT)

                        client_socket.send(user["header"] + user["data"] + connect_header + connect_data)

                    if (data["type"] == "video"):
                        client_socket.send(user["header"] + user["data"] + message["header"] + message["data"])
                    elif (data["type"] == "audio"):
                        pass
                    elif (data["type"] == "text"):
                        client_socket.send(user["header"] + user["data"] + message["header"] + message["data"])