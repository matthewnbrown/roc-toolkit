import dataclasses


@dataclasses.dataclass(frozen=True)
class ItemCostPair:
    count: int = 0
    cost: int = -1

    @property
    def total_cost(self) -> int:
        return self.count * self.cost

    def __add__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count + other, self.cost)
        elif type(other) == ItemCostPair:
            return ItemCostPair(self.count + other.count, self.cost)
        return NotImplemented

    def __sub__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count - other, self.cost)
        elif type(other) == ItemCostPair:
            return ItemCostPair(self.count - other.count, self.cost)
        return NotImplemented

    def __mul__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count * other, self.cost)
        return NotImplemented

    def __iadd__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count + other, self.cost)
            return self
        elif type(other) == ItemCostPair:
            self = ItemCostPair(self.count + other.count, self.cost)
            return self
        return NotImplemented

    def __isub__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count - other, self.cost)
            return self
        elif type(other) == ItemCostPair:
            self = ItemCostPair(self.count - other.count, self.cost)
            return self
        return NotImplemented

    def __imul__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count * other, self.cost)
            return self
        return NotImplemented
