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
        self.profits = {}
        self.countdown = 4

    def counting(self, countdown):
        time.sleep(countdown)
        self.broadcast_results()

    def handle_client(self, client_socket, addr):
        print(f"New connection from {addr}")
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                data = json.loads(message)
                if data == "shutdown":
                    client_socket.close()
                player_id = data['player_id']
                profit = data['profit']
                self.profits[player_id] = profit
                print(self.profits)
            except ConnectionResetError:
                break

        client_socket.close()
        self.clients.remove(client_socket)
        print(f"Connection closed from {addr}")

    def broadcast_results(self):
        print("sending data to everyone")
        data = {
            'gamestatus': "over",
            'profit': self.profits
        }
        results = json.dumps(data)
        for client_socket in self.clients:
            client_socket.send(results.encode('utf-8'))

    def start(self):
        print("Server started...")

        while True:
            client_socket, addr = self.server.accept()
            x = threading.Thread(target=self.counting, args=(self.countdown,))
            x.start()
            self.clients.append(client_socket)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            client_handler.start()

if __name__ == "__main__":
    server = GameServer()
    server.start()