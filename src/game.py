class Game:
    def __init__(self, title, type=None, discount=None, price=None, lowest=None, stock=None, status=None, last_time_updated=None):
        """
        Constructor for the Game class.

        :param title: The title of the game.
        :param type: The type of the game (default is 'game' if not provided).
        :param discount: The discount percentage for the game.
        :param price: The current price of the game.
        :param lowest: The lowest price the game has been offered for.
        :param stock: The stock quantity of the game.
        :param status: The status of the game.
        :param last_time_updated: The timestamp of the last time the game information was updated.
        """
        self.title = title
        self.type = type if type else "game"
        self.discount = discount
        self.price = price
        self.lowest = lowest
        self.stock = stock
        self.status = status
        self.last_time_updated = last_time_updated

    @classmethod
    def create_from_dict(cls, game_dict):
        """
        Creates a Game instance from a dictionary.

        :param game_dict: A dictionary containing game information.
        :return: A new Game instance.
        """
        return cls(
            title=game_dict.get("title", ""),
            type=game_dict.get("type", ""),
            discount=game_dict.get("discount", ""),
            price=game_dict.get("price", ""),
            lowest=game_dict.get("lowest", ""),
            stock=game_dict.get("stock", ""),
            status=game_dict.get("status", ""),
            last_time_updated=game_dict.get("last_time_updated", "")
        )

    def to_dict(self):
        """
        Converts the Game instance to a dictionary.

        :return: A dictionary representation of the Game instance.
        """
        return {
            'title': self.title,
            'type': self.type,
            'discount': self.discount,
            'price': self.price,
            'lowest': self.lowest,
            'stock': self.stock,
            'status': self.status,
            'last_time_updated': self.last_time_updated
        }

    def __str__(self):
        """
        Returns a string representation of the Game instance.

        :return: A string containing the title, price, and discount of the game.
        """
        return f"{self.title} - {self.price} ({self.discount}): {self.lowest}"

    def __eq__(self, other):
        """
        Checks if two Game instances are equal based on their titles.

        :param other: Another Game instance to compare.
        :return: True if the titles are equal, False otherwise.
        """
        if isinstance(other, Game):
            return self.title == other.title
        return False
