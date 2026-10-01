import socket
import threading
import json
import importlib

DEFAULT_PORT = 5555

def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class LANServer:
    def __init__(self, host='0.0.0.0', port=DEFAULT_PORT, max_clients=4, use_online_tunnel=False):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.use_online_tunnel = use_online_tunnel
        self.public_host = None
        self.public_port = None
        self.ngrok_tunnel = None

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.player_metadata = []
        self.colors = ["RED", "GREEN", "YELLOW", "BLUE"]
        self.running = False

    def start(self) -> tuple[str, int]:
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_clients)
        self.running = True

        if self.use_online_tunnel:
            try:
                ngrok = importlib.import_module("pyngrok").ngrok
                # Open public TCP tunnel forwarding to our local port
                self.ngrok_tunnel = ngrok.connect(self.port, "tcp")
                # e.g., tcp://0.tcp.ngrok.io:12345
                pub_url = self.ngrok_tunnel.public_url.replace("tcp://", "")
                self.public_host, p_str = pub_url.split(":")
                self.public_port = int(p_str)
            except Exception as e:
                print(f"Online tunnel initialization failed: {e}. Falling back to local LAN.")
                self.public_host = get_local_ip()
                self.public_port = self.port
        else:
            self.public_host = get_local_ip()
            self.public_port = self.port

        threading.Thread(target=self._accept_clients, daemon=True).start()
        return self.public_host, self.public_port

    def _accept_clients(self):
        while self.running and len(self.clients) < self.max_clients:
            try:
                conn, addr = self.server.accept()
                assigned_color = self.colors[len(self.clients)]
                is_host = (len(self.clients) == 0)
                self.clients.append(conn)

                init_msg = {
                    "type": "INIT",
                    "assigned_color": assigned_color,
                    "is_host": is_host
                }
                conn.sendall((json.dumps(init_msg) + "\n").encode('utf-8'))
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, conn):
        buffer = ""
        while self.running:
            try:
                data = conn.recv(2048).decode('utf-8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        msg = json.loads(line)
                        if msg.get("type") == "JOIN_METADATA":
                            self.player_metadata.append({
                                "name": msg.get("name", "Player"),
                                "color": msg.get("color"),
                                "is_host": msg.get("is_host", False)
                            })
                            self.broadcast({
                                "type": "LOBBY_UPDATE",
                                "slots": self.player_metadata
                            })
                        else:
                            self.broadcast(msg)
            except Exception:
                break
        if conn in self.clients:
            self.clients.remove(conn)
        conn.close()

    def broadcast(self, data: dict):
        payload = (json.dumps(data) + "\n").encode('utf-8')
        for c in list(self.clients):
            try:
                c.sendall(payload)
            except Exception:
                if c in self.clients:
                    self.clients.remove(c)

    def stop(self):
        self.running = False
        if self.ngrok_tunnel:
            try:
                ngrok = importlib.import_module("pyngrok").ngrok
                ngrok.disconnect(self.ngrok_tunnel.public_url)
            except Exception:
                pass
        for c in self.clients:
            try:
                c.close()
            except Exception:
                pass
        try:
            self.server.close()
        except Exception:
            pass

class LANClient:
    def __init__(self, message_callback):
        self.client = None
        self.assigned_color = None
        self.is_host = False
        self.callback = message_callback
        self.connected = False

    def connect(self, host: str, port: int = DEFAULT_PORT) -> bool:
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            self.connected = True
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except Exception:
            self.connected = False
            return False

    def send_action(self, action_dict: dict):
        if self.connected and self.client:
            try:
                payload = (json.dumps(action_dict) + "\n").encode('utf-8')
                self.client.sendall(payload)
            except Exception:
                self.connected = False

    def _listen(self):
        buffer = ""
        while self.connected:
            try:
                data = self.client.recv(2048).decode('utf-8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        msg = json.loads(line)
                        if msg.get("type") == "INIT":
                            self.assigned_color = msg.get("assigned_color")
                            self.is_host = msg.get("is_host", False)
                        self.callback(msg)
            except Exception:
                break
        self.connected = False

    def disconnect(self):
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass