import socket
import pickle
import sys

class Network:
    '''
    Network object acts as middleware for the client

    Sockets:
        - server: tcp socket to the main server
        - tcp_client: tcp socket to the room server
        - udp_client: udp socket to the room server
    '''

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = '127.0.0.1'
        self.server_port = 6000
        self.udp_client.bind(('127.0.0.1', 0))  # binding the client udp socket
        self.player = self.connect_server()

    def connect_server(self):
        '''
        Establish tcp connection to server
        '''

        try:
            self.server.connect((self.server_ip, self.server_port))
            return self.server.recv(2048)
        except socket.error as e:
            print("Socket error:", e)
        except Exception as e:
            print("Error: ", e)

    def connect_tcp(self, tcp_port):
        '''
        Establish tcp connection to the room

        Parameters:
            - tcp_port: tcp port of the room
        '''

        try:
            print("CONNECTING TO PORT:", tcp_port)
            self.tcp_client.connect((self.server_ip, tcp_port))
            self.chat_client.connect((self.server_ip, tcp_port))
            self.tcp_client.recv(2048)
            self.chat_client.recv(2048)
            return
        except socket.error as e:
            print("Socket error:", e)
        except Exception as e:
            print("Error:", e)

    def send_server(self, data, timeout=10):
        '''
        Send data to the main server using the server socket

        Parameters:
            - data: data to send
            - timeout: time after which to raise timeout, default 10 s

        Returns:
            - response: unserialized response from server
        '''

        try:
            data = pickle.dumps(data)
            self.server.send(data)
            self.server.settimeout(timeout)
            response = pickle.loads(self.server.recv(2048))
            return response

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print("Socket error:", e)
        except Exception as e:
            print("Error:", e)

    def send_tcp(self, data, timeout=20):
        '''
        Send data to the room server using the tcp_client socket

        Parameters:
            - data: data to send
            - timeout: time after which to raise timeout, default 20 s

        Returns:
            - response: unserialized response from server
        '''

        try:
            data = pickle.dumps(data)
            self.tcp_client.send(data)
            self.tcp_client.settimeout(timeout)
            response = pickle.loads(self.tcp_client.recv(2048))
            return response

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print("Socket error:", e)
        except Exception as e:
            print("Error:", e)

    def send_udp(self, data, timeout=10):
        '''
        Send data to the room server using the udp_client socket

        Parameters:
            - data: data to send
            - timeout: time after which to raise timeout, default 10 s

        Returns:
            - response: unserialized response from server
        '''

        try:
            data = pickle.dumps(data)
            self.udp_client.settimeout(timeout)
            self.udp_client.sendto(data, (self.server_ip, self.udp_port))
            response, _ = self.udp_client.recvfrom(2048)
            return pickle.loads(response)

        except socket.timeout:
            print("Server timed out")
        except socket.error as e:
            print("Socket error:", e)
        except Exception as e:
            print("Error:", e)

    def get_chat(self, timeout):
        try:
            self.chat_client.settimeout(timeout)
            return pickle.loads(self.chat_client.recv(2048))
        except socket.timeout:
            pass
        except Exception as e:
            print("Error:", e)
            sys.exit()

    def close_tcp(self):
        '''
        Close tcp socket connected to room server
        '''

        self.tcp_client.close()
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close_udp(self):
        '''
        Close udp socket to room server
        '''

        self.udp_client.close()
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close_chat(self):
        self.chat_client.close()
        self.chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    n = Network()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5010))
    print(pickle.loads(s.recv(2048)))
    s.send(pickle.dumps({'type': 'get_maps'}))
    print(pickle.loads(s.recv(2048)))
