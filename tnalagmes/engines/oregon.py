import random
from tnalagmes.data.template_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from tnalagmes.models.objects import Calendar, InventoryItem, ProgressTracker, Inventory
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.engines import TNaLaGmesEngine


class TurnState(TNaLaGmesConstruct):
    """
    am i injured
    am i eating/poorly/moderately/well
    suffering illness
    """

    def __init__(self):
        TNaLaGmesConstruct.__init__(self, "turn_state")
        self._injured = False
        self._ill = False
        self.bad_luck = False
        self._maintenance_state = 0

    @property
    def injured(self):
        return self._injured

    @injured.setter
    def injured(self, value):
        self._injured = value

    @property
    def illness(self):
        return self._ill

    @illness.setter
    def illness(self, value):
        self._ill = value

    @property
    def eating_state(self):
        return self._maintenance_state

    @eating_state.setter
    def eating_state(self, value):
        if value < 1 or value > 3:
            self._maintenance_state = 0
        else:
            self._maintenance_state = value

    def eating_poorly(self):
        return self._maintenance_state == 1

    def eating_moderately(self):
        return self._maintenance_state == 2

    def eating_well(self):
        return self._maintenance_state == 3


class SimpleInventory(Inventory):
    TERMINOLOGY = TERMINOLOGY

    def __init__(self, start_money=700):
        TNaLaGmesConstruct.__init__(self, "inventory")
        self.start_money = start_money
        self._money = start_money
        self.fuel = InventoryItem()
        self.supplies = InventoryItem()
        self.ammunition = InventoryItem()
        self.armour = InventoryItem()
        self.medicine = InventoryItem()

    @classmethod
    def get_entity(cls, text):
        return random.choice(cls.TERMINOLOGY.get(text, [""]))

    @property
    def currency(self):
        return self._money

    def spend(self, cost):
        self._money -= int(cost)

    @property
    def warnings(self):
        if self.supplies.value < 12:
            return GAME_EVENTS.get("low_supplies", {}).get("intro", "")

    @property
    def pretty_inventory(self):
        text = "{} - {}\n".format(self.get_entity("supplies"), self.supplies.value)
        text += "{} - {}\n".format(self.get_entity("ammunition"), self.ammunition.value)
        text += "{} - {}\n".format(self.get_entity("armour"), self.armour.value)
        text += "{} - {}\n".format(self.get_entity("medicine"), self.medicine.value)
        text += "{} - {}\n".format(self.get_entity("currency"), self.currency)
        return text

    def normalize_negative_values(self):
        if self.fuel.value < 0:
            self.fuel.value = 0
        if self.supplies.value < 0:
            self.supplies.value = 0
        if self.ammunition.value < 0:
            self.ammunition.value = 0
        if self.armour.value < 0:
            self.armour.value = 0
        if self.medicine.value < 0:
            self.medicine.value = 0


class OregonEngine(TNaLaGmesEngine):
    """ so called because logic is based on oregon trail"""
    TERMINOLOGY = TERMINOLOGY
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    name = "OregonEngine"
