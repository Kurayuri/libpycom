import queue
import time
import threading
import websocket


class WebSocketClient:
    # TODO
    _on_message = None

    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.ws = None
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.connect()

    def connect(self):
        self.ws = websocket.WebSocketApp(self.uri,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.thread = threading.Thread(target=self.ws.run_forever, kwargs=self.kwargs)
        self.thread.daemon = True
        self.thread.start()

        time.sleep(1)

    def run_forever(self):
        while True:
            time.sleep(1)

    def on_open(self, ws):
        self.logout("Connection opened")

    def on_message(self, ws, message):
        self.logout(f"Received: {message}")
        if self._on_message:
            self._on_message()

    def on_error(self, ws, error):
        self.logout(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.logout(
            f"Connection closed with status code {close_status_code}, reason: {close_msg}")
        self.logout("Attempting to reconnect...")
        self.reconnect()

    def reconnect(self):
        time.sleep(0.2)
        self.connect()
        # 重新发送未发送的消息
        with self.lock:
            while not self.message_queue.empty():
                message = self.message_queue.get()
                self.send(message)

    def send(self, message):
        with self.lock:
            try:
                if self.ws.sock and self.ws.sock.connected:
                    self.ws.send(message)
                    self.logout(f"Sent: {message}")
                else:
                    self.logout("WebSocket is not connected, queueing message")
                    self.message_queue.put(message)
            except websocket.WebSocketConnectionClosedException:
                self.logout("WebSocket is closed, queueing message")
                self.message_queue.put(message)

    def logout(self, *values, **kwargs):
        print("WS:", *values, **kwargs)
