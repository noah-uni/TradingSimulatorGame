import socket
import threading
import json
import time

class GameServer:
    #Initialisierung der Variablen
    def __init__(self, host='localhost', port=12346):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.players = {}
        self.profits = {}
        self.countdown = 60
        self.game_running = True

    #Der Timer wird runtergezählt
    # Nach dem countdown wird das Spiel beendet mit broadcast_results und alle Variablen zurückgesetzt
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

    #Wird für jeden Client/Spieler seperat ausgeführt
    def handle_client(self, client_socket, addr):
        print(f"New connection from {addr}")
        while True:
            try:
                #Es wird auf eine Message vom Spieler gewartet
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                data = json.loads(message)
                #Fallunterscheidung für die Art der Message
                if data['type'] != None:
                    if data['type'] == "shutdown":
                        client_socket.close()
                    #Wenn der Spieler einer Lobby beitritt, wird sein Name in Self.player hinzugefügt und jedem Client geschickt
                    elif data['type'] == "lobby":
                        player_name = data['name']
                        if player_name not in self.players:
                            self.players[player_name] = {'ready': False}
                            self.update_player_list()
                    #Ist ein Spieler ready, wird die self.players aktualisiert. Beispiel: {Player1: {ready: True}, Player2: {ready: False}}
                    elif data['type'] == "ready":
                        player_name = data['name']
                        if player_name in self.players:
                            self.players[player_name]['ready'] = True
                            self.update_player_list()
                            #Wenn alle Spieler ready sind, wird kurz gewartet, bevor das Spiel begonnen wird
                            if all(player['ready'] for player in self.players.values()):
                                start_message = {
                                    'start_game': True
                                }
                                time.sleep(1)
                                self.game_running = True
                                self.broadcast(json.dumps(start_message))

                                x = threading.Thread(target=self.counting, args=(self.countdown,))
                                x.start()
                    #Ist das Spiel am Laufen und die Art ist "game", enthält die Message Infos über den erspielten Gewinn des Spielers
                    elif data['type'] == "game" and self.game_running:
                        player_id = data['player_id']
                        profit = data['profit']
                        self.profits[player_id] = profit
                        print(self.profits)
            except ConnectionResetError:
                break
        # Bricht die Loop ab, weil der Client sich getrennt hat, wird die Verbindung getrennt und der Spieler aus der Clientliste entfernt
        client_socket.close()
        self.clients.remove(client_socket)
        print(f"Connection closed from {addr}")

    #Sendet eine Nachricht an jeden Spieler, der mit dem Server verbunden ist
    def broadcast(self, message):
        for client_socket in self.clients:
            client_socket.send(message.encode('utf-8'))

    #Sendet jedem Spieler eine Liste der Spieler, die sich in der Lobby befinden
    def update_player_list(self):
        player_names = list(self.players.keys())
        playerlist = {
            'players': player_names
        }
        self.broadcast(json.dumps(playerlist))

    #Beendet das Spiel und sendet jedem Spieler eine Liste mit dem Gewinn, den jeder Spieler am Ende des Spiels vorzuzeigen hat
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

    #startet den Server und initiert einen seperaten Thread für jeden Client/Spieler, der sich verbindet
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
