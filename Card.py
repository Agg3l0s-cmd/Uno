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

    def match(self, color, value):
        return self.color == color or self.color == "extra" or self.value == value

