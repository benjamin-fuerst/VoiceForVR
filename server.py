import socket
import whisper

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 1234
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5) #up to 5 connections
    
    model = whisper.load_model("tiny")
    
    while True:
        client, address = server.accept()
        print(f"Connection Established - {address[0]}:{address[1]}")
        
        filepath = client.recv(1024) #number of bytes to receive
        filepath = filepath.decode("utf-8")
        result = model.transcribe(filepath)
        client.send(bytes(result["text"], "utf-8"))
        client.close()
