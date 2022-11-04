import socket

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 1234
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5) #up to 5 connections
    
    while True:
        client, address = server.accept()
        print(f"Connection Established - {address[0]}:{address[1]}")
        
        string = client.recv(1024) #number of bytes to receive
        string = string.decode("utf-8")
        string = string.upper()
        client.send(bytes(string, "utf-8"))
        client.close()