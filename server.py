import socket
import threading
import json
import time

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.players = []
        self.profits = {}
        self.countdown = 10
        self.waiting = {}

    def counting(self, countdown):
        remaining_time = countdown
        while remaining_time > 0:
            mins, secs = divmod(remaining_time, 60)
            timer_text = f'{mins:02d}:{secs:02d}'
            timemessage = {
                'type': 'timer',
                'time': timer_text
            }
            self.broadcast(json.dumps(timemessage))
            time.sleep(1)
            remaining_time -= 1
        
        self.broadcast_results()

    def handle_client(self, client_socket, addr):
        print(f"New connection from {addr}")
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                data = json.loads(message)
                if data['type'] != None:
                    #Wenn die Message 'Shutdown' ist, wird die Verbindung abgebrochen
                    if data['type'] == "shutdown":
                        client_socket.close()
                    elif data['type'] == "lobby":
                        if not data['name'] in self.players:
                            self.players.append(data['name'])
                            playerlist = {
                                'players': self.players
                            }
                        self.broadcast(json.dumps(playerlist))
                        if len(self.players) > 1:
                            start_message = {
                                'start_game': True
                            }
                            #Kleine Pause bevor das Spiel startet
                            time.sleep(1)
                            self.broadcast(json.dumps(start_message))

                            x = threading.Thread(target=self.counting, args=(self.countdown,))
                            x.start()
                    elif data['type'] == "game":
                        player_id = data['player_id']
                        profit = data['profit']
                        self.profits[player_id] = profit
                        print(self.profits)
            except ConnectionResetError:
                break

        client_socket.close()
        self.clients.remove(client_socket)
        print(f"Connection closed from {addr}")

    def broadcast(self, message):
        for client_socket in self.clients:
            client_socket.send(message.encode('utf-8'))

    def start_game(self):
        message = "start game"
        for client_socket in self.clients:
            client_socket.send(message.encode('utf-8'))

    def broadcast_results(self):
        print("sending data to everyone")
        data = {
            'type': "game over",
            'profit': self.profits
        }
        results = json.dumps(data)
        for client_socket in self.clients:
            client_socket.send(results.encode('utf-8'))
        self.players = []
        self.profits = {}

    def start(self):
        print("Server started...")

        while True:
            client_socket, addr = self.server.accept()
            self.clients.append(client_socket)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_handler.start()

if __name__ == "__main__":
    server = GameServer()
    server.start()