import random


class TradeGood:

    def __init__(self, name, normal_price_range):
        self.name = name
        self.normalPriceRange = normal_price_range

    def get_random_price_in_range(self):
        return random.randint(self.normalPriceRange[0], self.normalPriceRange[1])
