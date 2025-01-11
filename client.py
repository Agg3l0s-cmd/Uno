import pygame
import os
import Card
import connection_handler

class Client:
    def __init__(self, window_width=1000, window_height=900, num_cards=7, spacing=1):
        # Constants
        self.CARD_WIDTH = 100
        self.CARD_HEIGHT = 170
        self.NUM_CARDS = num_cards
        self.SPACING = spacing
        self.window_width = window_width
        self.window_height = window_height
        self.center_card = None
        self.can_play = 0
        self.backCardPath = "cards\\back.png"

        # Store card rectangles for click detection
        self.bottom_card_rects = []

        # Store side card rectangle for click detection
        self.side_card_rect = None

        # Create the connection handler
        self.conn = connection_handler.ConnectionHandler()
        self.conn.connect_to_server()

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height))
        pygame.display.set_caption('Uno')

        # Make opponent's deck
        self.op = [Card.Card(self.backCardPath) for _ in self.conn._hand]

        # Store card rectangles for click detection
        self.bottom_card_rects = []

        # Store side card rectangle for click detection
        self.side_card_rect = None

    def load_card_image(self, image_path: str):
        """Load a PNG image and return the Pygame Surface."""
        image_path = image_path.strip()
        if os.path.exists(image_path):
            return pygame.image.load(image_path)
        else:
            print(f"Image not found: {image_path}")
            return None

    def display_user_cards(self):
        """Display the user's cards at the bottom of the screen with centered rows."""
        try:
            self.bottom_card_rects = self._render_cards(
                y_offset=self.window_height - self.CARD_HEIGHT - 20, hand=self.conn._hand, enable_hover=True)
        except Exception as e:
            pass

    def display_op_cards(self):
        """Display the opponent's cards at the top of the screen with centered rows."""
        self._render_cards(y_offset=20, hand=self.op)

    def _render_cards(self, y_offset, hand, max_rows=2, enable_hover=False):
        """
        Render cards with overlap, support multiple rows, and enlarge hovered cards.

        Args:
            y_offset (int): Vertical position for the first row.
            hand (list): List of card images to display.
            max_rows (int): Maximum number of rows to display.
        """
        mouse_pos = pygame.mouse.get_pos()  # Get current mouse position
        total_cards = len(hand)
        overlap_width = self.CARD_WIDTH // 3  # Amount of overlap between cards
        max_cards_per_row = (self.window_width -
                             self.CARD_WIDTH) // overlap_width + 1

        # Initialize position variables
        card_rects = []
        row_height = self.CARD_HEIGHT + 20  # Space between rows

        # Track the hovered card index
        hovered_card_index = None

        # Determine hovered card first to avoid overlapping issues
        for i in range(total_cards - 1, -1, -1):  # Check from topmost to bottommost
            row = i // max_cards_per_row
            if row >= max_rows:
                continue
            col = i % max_cards_per_row

            cards_in_this_row = min(
                max_cards_per_row, total_cards - row * max_cards_per_row)
            row_start_x = (self.window_width - (cards_in_this_row - 1)
                           * overlap_width - self.CARD_WIDTH) // 2
            x_pos = row_start_x + col * overlap_width
            y_pos = y_offset + row * row_height

            rect = pygame.Rect(
                x_pos, y_pos, self.CARD_WIDTH, self.CARD_HEIGHT)
            if rect.collidepoint(mouse_pos):
                hovered_card_index = i
                break

        # Draw cards with hover effect applied to the topmost hovered card
        for i, card in enumerate(hand):
            # print(card)
            # print(card.getPath())
            if card:
                card_width = self.CARD_WIDTH
                card_height = self.CARD_HEIGHT

                row = i // max_cards_per_row
                if row >= max_rows:
                    break
                col = i % max_cards_per_row

                cards_in_this_row = min(
                    max_cards_per_row, total_cards - row * max_cards_per_row)
                row_start_x = (
                    self.window_width - (cards_in_this_row - 1) * overlap_width - card_width) // 2
                x_pos = row_start_x + col * overlap_width
                y_pos = y_offset + row * row_height

                if i == hovered_card_index and enable_hover:
                    # Enlarge the hovered card
                    scale_factor = 1.2
                    scaled_width = int(card_width * scale_factor)
                    scaled_height = int(card_height * scale_factor)
                    scaled_x = x_pos - (scaled_width - card_width) // 2
                    scaled_y = y_pos - (scaled_height - card_height) // 2
                    self.screen.blit(
                        pygame.transform.scale(
                            self.load_card_image(card.getPath()), (scaled_width, scaled_height)),
                        (scaled_x, scaled_y)
                    )
                else:
                    # Render card at normal size
                    self.screen.blit(
                        pygame.transform.scale(
                            self.load_card_image(card.getPath()), (card_width, card_height)),
                        (x_pos, y_pos)
                    )

                # Store the rect for click detection
                card_rects.append(pygame.Rect(
                    x_pos, y_pos, card_width, card_height))

        return card_rects

    def display_card_center(self, card_image):
        """Display a single card at the center of the screen."""
        if card_image:
            card_width = self.CARD_WIDTH
            card_height = self.CARD_HEIGHT

            # Calculate the position to center the card
            center_x = (self.window_width - card_width) // 2
            center_y = (self.window_height - card_height) // 2

            # Render the card
            self.screen.blit(
                pygame.transform.scale(self.load_card_image(
                    card_image), (card_width, card_height)),
                (center_x, center_y)
            )

    def display_card_side(self):
        # Calculate the position to center the card
        x_pos = self.CARD_WIDTH - 60
        y_pos = (self.window_height - self.CARD_HEIGHT) // 2

        self.side_card_rect = pygame.Rect(
            x_pos, y_pos, self.CARD_WIDTH, self.CARD_HEIGHT)
        mouse_pos = pygame.mouse.get_pos()

        if self.side_card_rect.collidepoint(mouse_pos):
            scale_factor = 1.1
            card_width = self.CARD_WIDTH * scale_factor
            card_height = self.CARD_HEIGHT * scale_factor
        else:
            card_width = self.CARD_WIDTH
            card_height = self.CARD_HEIGHT

        # Render the card
        self.screen.blit(
            pygame.transform.scale(self.load_card_image(
                self.backCardPath), (card_width*1.3, card_height*1.3)),
            (x_pos, y_pos)
        )

    def draw_gradient_background(self):
        """Draw a smooth gradient background with blended Uno colors."""
        # Define the start and end colors for the gradient
        start_color = (255, 0, 0)   # Red
        end_color = (0, 0, 255)     # Blue
        mid_color1 = (255, 255, 0)  # Yellow
        mid_color2 = (0, 255, 0)    # Green

        # Create a list of colors for smooth interpolation
        gradient_colors = [start_color, mid_color1, mid_color2, end_color]
        gradient_height = self.window_height // (len(gradient_colors) - 1)

        for i in range(len(gradient_colors) - 1):
            self._draw_gradient_segment(
                gradient_colors[i],
                gradient_colors[i + 1],
                i * gradient_height,
                (i + 1) * gradient_height
            )

    def _draw_gradient_segment(self, start_color, end_color, start_y, end_y):
        """Draw a single segment of the gradient."""
        for y in range(start_y, end_y):
            # Interpolate between start_color and end_color
            # Interpolation factor (0 to 1)
            t = (y - start_y) / (end_y - start_y)
            r = int(start_color[0] + t * (end_color[0] - start_color[0]))
            g = int(start_color[1] + t * (end_color[1] - start_color[1]))
            b = int(start_color[2] + t * (end_color[2] - start_color[2]))

            pygame.draw.line(self.screen, (r, g, b),
                             (0, y), (self.window_width, y))

    def handle_click(self, pos):
        """Handle mouse click events. Remove the clicked card and render it in the center."""
        for index, rect in enumerate(self.bottom_card_rects):
            if rect.collidepoint(pos):
                # Remove the clicked card from the hand
                clicked_card = self.conn._hand[index]
                self.conn._hand.pop(index)

                # Remove the clicked card's rect from the bottom card rectangles
                self.bottom_card_rects.pop(index)

                # Set the clicked card as the center card
                self.conn.send_message("?"+clicked_card.getPath())
                # self.conn.middle = clicked_card
                # self.center_card = clicked_card
                pygame.display.flip()

                # Re-render the bottom cards after removal
                self.display_user_cards()

                # Send the card click to the server
                self.conn.send_message(f"%-1, {self.conn.id}")
                # time.sleep(.2)
                self.conn.send_message("UPDATE")

                # Reset the turn for current user and if he can draw a card
                # self.conn.myTurn = False

                break  # Exit after the first card click to avoid multiple removals

        if self.side_card_rect.collidepoint(pos) and self.conn.can_draw:
            # # Send signal to server to increment opponents hand and update deck
            self.conn.send_message(f"%1, {self.conn.id}")

            # Update screen
            pygame.display.update()

            # # Player can't draw anymore
            self.conn.can_draw = False

    def run(self):
        """Main game loop to run the viewer."""
        running = True
        clock = pygame.time.Clock()  # Add a clock to control framerate
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # del self.hand
                    self.conn.close()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.conn.started and self.conn.myTurn:
                    self.handle_click(event.pos)

            # Draw the gradient background
            self.draw_gradient_background()

            # print("TURN: ", self.conn.myTurn)

            # Display user's hand
            self.display_user_cards()

            # Updated opponent's hand after play
            if self.conn.newCard == -1:
                if len(self.op):
                    self.op.pop()
                    self.conn.newCard = 0

            if self.conn.newCard == 1:
                if len(self.op):
                    self.op.append(Card.Card(self.backCardPath))
                    self.conn.newCard = 0

            # Display opponent's hand
            self.display_op_cards()

            # Display middle card
            if self.conn.middle:
                self.display_card_center(self.conn.middle)

            # Display side deck
            self.display_card_side()

            # Update the display
            pygame.display.flip()

            # Control the framerate
            clock.tick(60)  # 60 FPS


# Main Execution
if __name__ == "__main__":
    os.system("cls")
    client = Client()
    client.run()  # Run the game in the main thread
