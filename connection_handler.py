import socket
import threading
import time
import Card


class ConnectionHandler:
    def __init__(self, server_ip="localhost", server_port=12345):
        """Initialize the connection handler with server details."""
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.listener_thread = None

        self._hand = []
        self.id = None
        self.started = False
        self.myTurn = True
        self.middle = None
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

                    # Handle received hand in the beginning
                    if message.startswith("!"):
                        for i in message[1::].split(','):
                            card = Card.Card(f"cards\\{i}")
                            self._hand.append(card)

                    # Hangle unique id received from server
                    if message.startswith("@"):
                        self.id = int(message[1:])

                    # Handle card to render for the middle
                    if message.startswith("?"):
                        self.middle = message[1:]

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
                        self.can_draw = True

                    if self.on_message_received:
                        # Pass the message to the callback
                        self.on_message_received(message)
            except Exception as e:
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


# Example usage
# if __name__ == "__main__":
#     def handle_game_message(message):
#         """Handle game-specific logic for incoming messages."""
#         print(f"Game logic processing: {message}")

#     # Create and configure the connection handler
#     conn = ConnectionHandler(server_ip="localhost", server_port=12345)
#     conn.on_message_received = handle_game_message  # Set the callback for incoming messages

#     # Connect to the server
#     conn.connect_to_server()

#     # Simulate sending game data
#     while conn.connected:
#         user_input = input("Enter a message to send (or 'quit' to exit): ")
#         if user_input.lower() == "quit":
#             break
#         conn.send_message(user_input)

#     # Close the connection
#     conn.close()
