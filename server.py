from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

# Подключение к PostgreSQL через HTTP API Render
DATABASE_URL = "postgresql://coldphone:CS3FSP5WakTuabPnANYq2LkVCYjaDWHi@dpg-da1v0d7lk1mc73adp28g-a/coldphone"

# Используем простой способ - храним в памяти + файл
messages = []
users = []
HISTORY_FILE = 'history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history():
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(messages, f, ensure_ascii=False)
    except:
        pass

messages = load_history()

# Загружаем список пользователей
USERS_FILE = 'users.json'
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except:
        users = []
else:
    users = []
FAMILY_PASSWORD = "Mini2012"

class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/icon-180.png' or self.path == '/icon-192.png' or self.path == '/icon-512.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                icon_file = self.path.lstrip('/')
                if os.path.exists(icon_file):
                    with open(icon_file, 'rb') as f:
                        self.wfile.write(f.read())
            elif self.path == '/manifest.json':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open('manifest.json', 'rb') as f:
                    self.wfile.write(f.read())
            elif self.path == '/messages':
                username = self.headers.get('X-Username', '')
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
                save_history()
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
                        with open(USERS_FILE, 'w') as f:
                            json.dump(users, f, ensure_ascii=False)
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
    print(f'History loaded: {len(messages)} messages')
    server = HTTPServer(('0.0.0.0', port), ChatHandler)
    server.serve_forever()
