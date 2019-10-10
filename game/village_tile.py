from game.tile import Tile


class VillageTile(Tile):

    def __init__(self, position, tile_angle, tile_data, layer, name, export, all_goods):
        super().__init__(position, tile_angle, tile_data, layer)

        self.port_radius = 64

        self.name = name
        self.export = export

        self.buy_goods_and_prices = []
        self.sell_goods_and_prices = []
        
        for good in all_goods:
            price = good.get_random_price_in_range()
            if export == good.name:
                price = max(1, int(price * 0.5))
            self.buy_goods_and_prices.append([good, price])
            self.sell_goods_and_prices.append([good, max(1, int(price * 0.75))])
