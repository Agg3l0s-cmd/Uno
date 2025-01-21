import pygame
import os
import Card
import connection_handler
import datetime
import time


class Client:
    def __init__(self, window_width=1000, window_height=900, num_cards=7, spacing=1):
        # Create the connection handler
        self.conn = connection_handler.ConnectionHandler()
        self.conn.connect_to_server()

        # Constants
        self.CARD_WIDTH = 100
        self.CARD_HEIGHT = 170
        self.NUM_CARDS = num_cards
        self.SPACING = spacing
        self.window_width = window_width
        self.window_height = window_height
        self.id = self.conn.id
        self.can_play = 0
        self.backCardPath = "cards\\back.png"

        self.COLORMAP = {"red": (255, 0, 0), "blue": (
            0, 0, 255), "green": (0, 255, 0), "yellow": (255, 255, 0)}

        # Store card rectangles for click detection
        self.bottom_card_rects = []

        # Store side card rectangle for click detection
        self.side_card_rect = None

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height))
        pygame.display.set_caption(f'Player {self.id}')

        # Make opponent's deck
        self.op = [Card.Card(self.backCardPath) for _ in self.conn.hand]

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
                y_offset=self.window_height - self.CARD_HEIGHT - 20, hand=self.conn.hand, enable_hover=True)
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
                    card_image.getPath()), (card_width, card_height)),
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

    def handle_click(self, pos, playable):
        """Handle mouse click events. Remove the clicked card and render it in the center."""
        for index, rect in enumerate(self.bottom_card_rects):
            clicked_card = self.conn.hand[index]
            if rect.collidepoint(pos) and playable:
                # Remove the clicked card from the hand
                # clicked_card = self.conn.hand[index]
                # middle_card = Card.Card(self.conn.middle)

                # log(self.conn.id, clicked_card.match(self.conn.middle_color))
                if clicked_card.match(self.conn.middle_color, self.conn.middle_value):

                    self.conn.hand.pop(index)

                    # Remove the clicked card's rect from the bottom card rectangles
                    self.bottom_card_rects.pop(index)

                    # Set the clicked card as the center card
                    self.conn.send_message("?"+clicked_card.getPath())

                    pygame.display.flip()

                    # Re-render the bottom cards after removal
                    self.display_user_cards()

                    # Send the card click to the server
                    self.conn.send_message(f"%-1, {self.id}")
                    time.sleep(0.1)
                    self.conn.send_message(f"!{clicked_card.color}|{
                                           clicked_card.value}")
                    # self.conn.send_message("UPDATE")

                    log(self.id, f"""{clicked_card.color == "extra"} {
                        self.conn.middle_color == "extra"}""")

                    if clicked_card.color == "extra":
                        return 1  # Exit after the first card click to avoid multiple removals

                    return 2  # Exit after the first card click to avoid multiple removals

        if self.side_card_rect.collidepoint(pos) and self.conn.can_draw and not playable:
            # # Send signal to server to increment opponents hand and update deck
            self.conn.send_message(f"%1, {self.id}")

            # Update screen
            pygame.display.update()

            # # Player can't draw anymore
            self.conn.can_draw = False

    def render_color_picker(self):
        """Render the color picker for wild cards."""

        colors = ["red", "green", "blue", "yellow"]
        picker_width = 50
        picker_height = 50
        picker_x = (self.window_width - picker_width * len(colors)) // 2
        picker_y = self.window_height // 2 + 100
        clicked = False

        while not clicked:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False

                for i, color in enumerate(colors):
                    picker_rect = pygame.Rect(
                        picker_x + i * picker_width, picker_y, picker_width, picker_height)
                    pygame.draw.rect(self.screen, self.COLORMAP[color],
                                     picker_rect, border_radius=5)

                    # Check if the mouse is hovering over the color picker
                    mouse_pos = pygame.mouse.get_pos()
                    if picker_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(self.screen, (255, 255, 255),
                                         picker_rect, border_radius=5, width=2)

                        # if the user clicks on a color, update the turn and middle.color
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.conn.middle_color = color
                            clicked = True
                            log(self.id, f"Color picked: {color}")
                            self.conn.send_message("UPDATE")
                            time.sleep(0.1)
                            self.conn.send_message(f"!{self.conn.middle_color}|{
                                                   self.conn.middle_value}")

            pygame.display.update()

        return clicked

    def run(self):
        """Main game loop to run the viewer."""
        self.id = self.conn.id
        pygame.display.set_caption(f'Player {self.id}')
        running = True
        item = 0
        clock = pygame.time.Clock()  # Add a clock to control framerate
        while running:
            playable = 0
            for index, _ in enumerate(self.conn.hand):
                # log(self.conn.id, self.conn.hand[index])
                if self.conn.hand[index].match(self.conn.middle_color, self.conn.middle_value):
                    playable += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # del self.hand
                    self.conn.close()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.conn.started and self.conn.myTurn:
                    log(self.id, f"CLICKED, PLAYABLE={playable}")
                    item = self.handle_click(event.pos, playable)

            if not self.conn.can_draw and playable == 0:
                self.conn.send_message("UPDATE")

            # Make background dark grey
            self.screen.fill((50, 50, 50))

            # print("TURN: ", self.conn.myTurn)

            # Display user's hand
            self.display_user_cards()

            try:
                # Display opponent's hand
                self.display_op_cards()
            except Exception as e:
                log(self.id, e)

            # Updated opponent's hand after play
            if self.conn.newCard == -1:
                if len(self.op):
                    self.op.pop()
                    self.conn.newCard = 0

            if self.conn.newCard == 1:
                if len(self.op):
                    self.op.append(Card.Card(self.backCardPath))
                    self.conn.newCard = 0

            # Display middle card
            if self.conn.middle:
                self.display_card_center(self.conn.middle)

            # Display side deck
            self.display_card_side()

            # Update the display
            pygame.display.flip()

            # Check if the middle card is wild card
            # If it is, render the color picker
            # Else render the middle card normally
            if item == 1:
                if self.render_color_picker():
                    # self.conn.send_message("UPDATE")
                    item = 0
            elif item == 2:
                self.conn.send_message("UPDATE")
                item = 0

            # Control the framerate
            clock.tick(60)  # 60 FPS


# Function to write in log file
def log(id, message):
    os.system(f"echo Player {id} {datetime.datetime.now()} {
              message} >> log.txt")


# Main Execution
if __name__ == "__main__":
    os.system("cls")
    client = Client()
    client.run()
