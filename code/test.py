import socket
import threading
import queue

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('127.0.0.1', 8000))

def udp_receive():
    while True:
        try:
            message, addr = server.recvfrom(2048)
            messages.put((message, addr))
        except:
            pass

def udp_broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[message.decode().index(":")+1:]
                        server.sendto(f"{name} joined!".encode(), client)
                    else:
                        server.sendto(message, client)
                except:
                    clients.remove(client)

t1 = threading.Thread(target=udp_receive)
t2 = threading.Thread(target=udp_broadcast)

t1.start()
t2.start()
