import socket
import pickle

def check_server(address, port):
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
        response = s.send(pickle.dumps({'type': 'get_maps'}))
        print(response)
        return True
    except:
        return False

if __name__ == '__main__':
    server_address = '10.20.204.86'
    server_port = 4010

    if check_server(server_address, server_port):
        print(f"The server at {server_address}:{server_port} is running")
    else:
        print(f"The server at {server_address}:{server_port} is not running")
