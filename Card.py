class Card:
    def __init__(self, path):
        """
        Initialize an Uno card.

        Args:
            color (str): The color of the card ('red', 'blue', 'green', 'yellow').
            value (str or int): The value of the card (e.g., 0-9, 's for Skip', 'r for Reverse', 'd for Draw Two', 'e0 for Change Color', 'e1 for Draw Four').
            card_type (str): The type of card ('number' or 'action' or 'wild').
        """

        self.path = path
        self.color = path[6:-7]
        self.value = path[-5:-4]

    def __str__(self):
        """
        Return a string representation of the card.
        """
        return " ".join([self.path, self.color, self.value])

    def getPath(self):
        return self.path

    def matches(self, middle):
        """
        Determine if this card can be played on top of another card.

        Args:
            other_card (UnoCard): The card to match against.

        Returns:
            bool: True if the card matches, False otherwise.
        """
        return (self.color == middle.color or self.value == middle.value or self.color == "extra")


# Example usage
if __name__ == "__main__":
    card = Card("cards\\extra\\e1.png")
    m = Card('cards\\extra\\e1.png')
    print(card, " | ", m)
    print(card.matches(m))
