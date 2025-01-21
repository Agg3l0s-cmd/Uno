import socket
import threading
import time


class GameServer:
    def __init__(self, host="localhost", port=12345, decks=1):
        self.DECKS = decks
        self.CARDS = {'blue\\b0.png': self.DECKS, 'blue\\b1.png': self.DECKS, 'blue\\b2.png': self.DECKS, 'blue\\b3.png': self.DECKS, 'blue\\b1.png': self.DECKS, 'blue\\b5.png': self.DECKS, 'blue\\b6.png': self.DECKS, 'blue\\b7.png': self.DECKS, 'blue\\b8.png': self.DECKS, 'blue\\b9.png': self.DECKS, 'blue\\bs.png': self.DECKS, 'blue\\bd.png': self.DECKS, 'blue\\br.png': self.DECKS,
                      'green\\g0.png': self.DECKS, 'green\\g1.png': self.DECKS, 'green\\g2.png': self.DECKS, 'green\\g3.png': self.DECKS, 'green\\g1.png': self.DECKS, 'green\\g5.png': self.DECKS, 'green\\g6.png': 1 *
                      self.DECKS, 'green\\g7.png': self.DECKS, 'green\\g8.png': self.DECKS, 'green\\g9.png': self.DECKS, 'green\\gs.png': self.DECKS, 'green\\gd.png': self.DECKS, 'green\\gr.png': self.DECKS,
                      'red\\r0.png': self.DECKS, 'red\\r1.png': self.DECKS, 'red\\r2.png': self.DECKS, 'red\\r3.png': self.DECKS, 'red\\r1.png': self.DECKS, 'red\\r5.png': self.DECKS, 'red\\r6.png': 1 *
                      self.DECKS, 'red\\r7.png': self.DECKS, 'red\\r8.png': self.DECKS, 'red\\r9.png': self.DECKS, 'red\\rs.png': self.DECKS, 'red\\rd.png': self.DECKS, 'red\\rr.png': self.DECKS,
                      'yellow\\y0.png': self.DECKS, 'yellow\\y1.png': self.DECKS, 'yellow\\y2.png': self.DECKS, 'yellow\\y3.png': self.DECKS, 'yellow\\y1.png': self.DECKS, 'yellow\\y5.png': self.DECKS, 'yellow\\y6.png': 1 *
                      self.DECKS, 'yellow\\y7.png': self.DECKS, 'yellow\\y8.png': self.DECKS, 'yellow\\y9.png': self.DECKS, 'yellow\\ys.png': self.DECKS, 'yellow\\yd.png': self.DECKS, 'yellow\\yr.png': self.DECKS,
                      'extra\\e0.png': 4*self.DECKS, 'extra\\e1.png': 2*self.DECKS}

        self.ids = [1, 2]
        self.clientAdresses = []
        self.pid = {}
        self.turn = 0

        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # List of connected clients
        self.clientsToSend = []
        self.lock = threading.Lock()  # Ensure thread-safe operations
        self.mid = self.getCard()  # Get a card for the middle
        print(self.mid)

        self.mid_color = self.mid.split("\\")[0]
        self.mid_value = self.mid.split("\\")[1].split(".")[0]

        print(f"Middle card: {self.mid_color} {self.mid_value}")

    def start(self):
        """Start the server and accept client connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)  # Accept up to two clients
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            with self.lock:
                self.clientAdresses.append(client_address)
                self.clients.append(client_socket)
                self.clientsToSend.append(client_socket)
            print(f"Client connected: {client_address}")

            # Start a thread to handle this client
            threading.Thread(target=self.process_manager, args=(
                client_socket, len(self.clients)), daemon=True).start()

    def process_manager(self, client_socket, client_id):
        """Process manager for each client."""
        try:
            # Send a unique welcome message based on client ID
            for _, client in enumerate(self.clientsToSend):
                client.sendall(f"You are Player {client_id}".encode("utf-8"))
                time.sleep(0.1)
                # Send deck to user with ! prefix and id and remove him from the list to send
                cards = f"!{self.getCard(7)}\n"
                client.sendall(cards.encode("utf-8"))
                print(f"Sent to Player {client_id}: {cards}")
                # client.sendall("\n".encode("utf-8"))

                time.sleep(0.15)
                id = f"@{self.giveID()}"
                client.sendall(id.encode("utf-8"))
                self.pid[int(id[1])] = self.clients[client_id-1]
                print(f"Sent to Player {client_id}: {id}")

                time.sleep(0.1)
                middle = f"?cards\\{self.mid}"
                client.sendall(middle.encode("utf-8"))
                print(f"Sent middle card to Player {client_id}: {middle}")

                self.clientsToSend.remove(client)
                # for client in self.clients:
                #     print(self.clientAdresses[0][1])

            if len(self.clients) == 2:
                print(self.pid)
                print(self.clients)
                print("Both clients connected, sending start signal.")
                for client in self.clients:
                    # Send start signal
                    start_signal = "START"
                    client.sendall(start_signal.encode("utf-8"))
                    time.sleep(0.1)
                    client.sendall(f"MIDVALS|{self.mid_color}|{
                                   self.mid_value}".encode("utf-8"))

            # Handle messages from the client
            while True:
                if len(self.clients) == 2:
                    for client in self.clients:
                        client.sendall(f"TURN {self.turn}".encode("utf-8"))

                message: str = client_socket.recv(1024).decode("utf-8").strip()
                if message:
                    print(f"Received from Player {client_id}: {message}")
                    # Send back the played card so it can render in the middle
                    if message.startswith("?"):
                        self.sendBack(message)

                    if message.startswith("!"):
                        self.mid_color = message.split("|")[0][1:]
                        self.mid_value = message.split("|")[1]
                        print("NEW CARD: ", self.mid_color,
                              self.mid_value)

                    # Update each user's hand after a card was played
                    if message.startswith("%"):
                        try:
                            senderID = int(message.split(",")[1])
                            action = int(message.split(",")[0][1:])
                            print(f"YO: {senderID} {action}")
                            sendTo = 1
                            if senderID == 1:
                                sendTo = 2
                            else:
                                sendTo = 1

                            print("SENDING TO: ", sendTo, "FROM: ", senderID)
                            self.pid[sendTo].sendall(
                                f"%{action}".encode("utf-8"))

                            # time.sleep(.05)
                            if action == 1:
                                self.pid[senderID].sendall(
                                    f"!{self.getCard()}".encode("utf-8"))

                        except ValueError as ve:
                            print(ve)
                            continue

                    # Update turn
                    if message == "UPDATE":
                        for client in self.clients:
                            client.sendall(
                                f"MIDVALS|{self.mid_color}|{self.mid_value}".encode("utf-8"))
                        self.turn += 1

        except Exception as e:
            print(f"Error with Player {client_id}: {e}")
        finally:
            with self.lock:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"Player {client_id} disconnected.")
            for client in self.clients:
                client.sendall("STOP".encode("utf-8"))

            self.reset()

    def shutdown(self):
        """Shutdown the server and close all connections."""
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except Exception as e:
                    print(f"Error closing client connection: {e}")
        self.server_socket.close()
        print("Server shut down.")

    def sendBack(self, message):
        for client in self.clients:
            client.sendall(message.encode("utf-8"))

    def getCard(self, size=1) -> str:
        import random

        hand = []
        keys = list(self.CARDS.keys())

        i = 0
        while i < size:
            card = random.choice(keys)
            if self.CARDS[card] > 0:
                self.CARDS[card] -= 1
                hand.append(card)
                i += 1

        if size > 1:
            return ",".join(hand)
        return hand[0]

    def giveID(self) -> int:
        import random

        res = random.choice(self.ids)
        self.ids.remove(res)
        return res

    def reset(self):
        if len(self.clients) == 0:
            self.ids = [1, 2]
            self.turn = 0
            print("resetted params")


# Example usage
if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down the server.")
        server.shutdown()
