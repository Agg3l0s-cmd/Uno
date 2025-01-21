import socket
import threading
import time
import Card
import os
import datetime


class ConnectionHandler:
    def __init__(self, server_ip="localhost", server_port=12345):
        """Initialize the connection handler with server details."""
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.listener_thread = None

        self.hand = []
        self.id = None
        self.started = False
        self.myTurn = True

        self.middle = None
        self.middle_color = None
        self.middle_value = None

        self.newCard = 0
        self.can_draw = True

        # Callback function to handle received messages
        self.on_message_received = None

    def connect_to_server(self):
        """Establish a connection to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print(f"Connected to the server at {
                  self.server_ip}:{self.server_port}")

            # Start a thread to listen for incoming messages
            self.listener_thread = threading.Thread(
                target=self.listen_for_messages, daemon=True)
            self.listener_thread.start()
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def listen_for_messages(self):
        """Listen for messages from the server."""
        while self.connected:
            try:
                message = self.socket.recv(1024).decode("utf-8").strip()
                if message:
                    print(f"Message received: {message}")
                    log(f"COLOR: {self.middle_color}, VALUE: {
                        self.middle_value}")

                    # Handle received hand in the beginning
                    if message.startswith("!"):
                        for i in message[1::].split(','):
                            card = Card.Card(f"cards\\{i}")
                            self.hand.append(card)

                    # Hangle unique id received from server
                    if message.startswith("@"):
                        self.id = int(message[1:])

                    # Handle card to render for the middle
                    if message.startswith("?"):
                        print("MESSAGE: ", message)
                        self.middle = Card.Card(message[1:])

                    if message.startswith("MIDVALS"):
                        self.middle_color = message.split("|")[1]
                        self.middle_value = message.split("|")[2]

                    # Handle either to add or remove card from opponent's hand
                    if message.startswith("%"):
                        self.newCard = int(message[1:])

                    # Flag to start game when both users connect
                    if message == "START":
                        self.started = True

                    # Flag to stop game when either disconnects
                    if message == "STOP":
                        self.started = False

                    # Check if it's current user's turn depending on what turn is the server on
                    if message.startswith("TURN"):
                        self.myTurn = int(message[-1]) % 2 == int(self.id) - 1
                        print(self.myTurn)
                        self.can_draw = True

                    if self.on_message_received:
                        # Pass the message to the callback
                        self.on_message_received(message)

                message = ""
            except Exception:
                # print(f"Error receiving message: {e}")
                self.connected = False
                break

    def send_message(self, message: str):
        """Send a message to the server."""
        time.sleep(.05)
        if self.connected and self.socket:
            try:
                self.socket.sendall(message.encode("utf-8"))
                print(f"Message sent to server: {message}")
            except Exception as e:
                print(f"Failed to send message: {e}")
        else:
            print("Not connected to the server. Please connect first.")

    def close(self):
        """Close the connection to the server."""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
                print("Connection closed.")
            except Exception as e:
                print(f"Error closing the connection: {e}")


def log(message):
    os.system(f"echo CONNECTION HANDLER {
              datetime.datetime.now()} {message} >> log.txt")

