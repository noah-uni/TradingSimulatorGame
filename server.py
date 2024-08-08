import socket
import threading
import json
import time

class GameServer:
    def __init__(self, host='localhost', port=12346):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.players = {}
        self.profits = {}
        self.countdown = 60
        self.game_running = True

    def counting(self, countdown):
        remaining_time = countdown
        while remaining_time >= 0:
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
                    if data['type'] == "shutdown":
                        client_socket.close()
                    elif data['type'] == "lobby":
                        player_name = data['name']
                        if player_name not in self.players:
                            self.players[player_name] = {'ready': False}
                            self.update_player_list()
                    elif data['type'] == "ready":
                        player_name = data['name']
                        if player_name in self.players:
                            self.players[player_name]['ready'] = True
                            self.update_player_list()

                            if all(player['ready'] for player in self.players.values()):
                                start_message = {
                                    'start_game': True
                                }
                                time.sleep(1)
                                self.game_running = True
                                self.broadcast(json.dumps(start_message))

                                x = threading.Thread(target=self.counting, args=(self.countdown,))
                                x.start()
                    elif data['type'] == "game" and self.game_running:
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

    def update_player_list(self):
        player_names = list(self.players.keys())
        playerlist = {
            'players': player_names
        }
        self.broadcast(json.dumps(playerlist))

    def broadcast_results(self):
        print("sending data to everyone")
        data = {
            'type': "game over",
            'profit': self.profits
        }
        results = json.dumps(data)
        for client_socket in self.clients:
            client_socket.send(results.encode('utf-8'))
        self.game_running = False
        self.players = self.profits = {}

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
