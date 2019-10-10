
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


DamageType = enum('PHYSICAL', 'MAGIC')


class Damage:
    def __init__(self, amount, damage_type):
        self.amount = amount
        self.type = damage_type
