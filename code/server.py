import socket
from _thread import start_new_thread
import sys
from util import read_pos, make_pos

server = "192.168.1.8"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Server Started")

pos = [(450, 450), (550, 550)]

def threaded_client(connection, player):
    connection.send(str.encode(make_pos(pos[player])))
    reply = ""
    while True:
        try:
            data = read_pos(connection.recv(2048).decode())
            pos[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = pos[0]
                else:
                    reply = pos[1]

                print("Recieved:", data)
                print("Sending:", reply)

            connection.sendall(str.encode(make_pos(reply)))

        except:
            break

    print("Lost connection")

current_player = 0

while True:
    connection, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (connection, current_player))
    current_player += 1
