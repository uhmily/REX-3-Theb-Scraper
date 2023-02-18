import websocket
import socket_based
import threading
import time
import os
import sys


class HeartBeat(socket_based.SocketBased):
    
    def __init__(self, socket: websocket.WebSocket):
        super().__init__(socket)
    
    def start(self):
        self.socket.connect("wss://gateway.discord.gg/?v=6&encording=json")
        event = self.receive_json_response()
        
        self.heartbeat_interval = event['d']['heartbeat_interval'] / 1000
        self.main_thread = threading.Thread(target=HeartBeat.loop, args=(self,))
        self.main_thread.start()
    
    def loop(self):
        print('\n--------------------------------------------------\n\nREX3 SCRAPETRACKER\nby zetexfake and GDNewbie')
        while True:
            time.sleep(self.heartbeat_interval)
            heartbeatJSON = {
                "op": 1,
                "d": "null"
            }
            try:
                self.send_json_request(heartbeatJSON)
                print("\nheartbeat sent after " + str(self.heartbeat_interval) + "s")
            except Exception as err:
                # SHITTY FIX 2
                print(err)
                os.execl(sys.executable, 'python', "main.py")
