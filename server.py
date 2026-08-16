from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

messages = []
users = []
FAMILY_PASSWORD = "Mini2012"  # Замените на свой пароль

# Получаем путь к текущей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                index_path = os.path.join(BASE_DIR, 'index.html')
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/icon.png' or self.path == '/icon-180.png' or self.path == '/icon-192.png' or self.path == '/icon-512.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                icon_file = self.path.lstrip('/')
                with open(icon_file, 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/manifest.json':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open('manifest.json', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/icon.png' or self.path == '/icon-180.png' or self.path == '/icon-192.png' or self.path == '/icon-512.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                icon_file = self.path.lstrip('/')
                with open(icon_file, 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/manifest.json':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open('manifest.json', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/messages':
                # Получаем имя пользователя из заголовка
                username = self.headers.get('X-Username', '')
                
                # Фильтруем сообщения - только где пользователь участник
                filtered = [msg for msg in messages if 
                    msg.get('sender') == username or 
                    msg.get('recipient') == username]
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                response = json.dumps({'messages': filtered, 'users': users})
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"GET error: {e}")

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/send':
                messages.append(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            
            elif self.path == '/join':
                username = data.get('username')
                password = data.get('password', '')
                
                if password == FAMILY_PASSWORD:
                    if username and username not in users:
                        users.append(username)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
                else:
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'Неверный пароль'}).encode('utf-8'))
            
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"POST error: {e}")

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f'Server started on port {port}')
    server = HTTPServer(('0.0.0.0', port), ChatHandler)
    server.serve_forever()
