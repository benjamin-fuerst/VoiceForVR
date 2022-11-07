from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import whisper
from io import BytesIO

HOST = "127.0.0.1"
PORT = 8000

class WhisperHTTP(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.wfile.write(bytes("<html><body><h1>HELLO WORLD</h1></body></html>", "utf-8"))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        filepath = self.rfile.read(content_length)
        filepath = filepath.decode("utf-8")
        result = model.transcribe(filepath)
        
        self.send_response(200)
        self.end_headers()
        
        response = f"This is a POST request. Received: {result['text']}"
        
        self.wfile.write(bytes(response, "utf-8"))
        

if __name__ == "__main__":
    model = whisper.load_model("tiny")
    
    server = HTTPServer((HOST, PORT), WhisperHTTP)
    print(f"Server  running at http://{HOST}:{PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    
    server.server_close()
    print("Server stopped")