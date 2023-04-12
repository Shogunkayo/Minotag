import socket

def check_server(address, port):
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) # Set timeout to 5 seconds
        s.connect((address, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False

if __name__ == '__main__':
    server_address = '192.168.1.8'
    server_port = 8010

    if check_server(server_address, server_port):
        print(f"The server at {server_address}:{server_port} is running")
    else:
        print(f"The server at {server_address}:{server_port} is not running")
