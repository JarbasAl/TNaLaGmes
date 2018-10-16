from tnalagmes.engines.oregon75 import Oregon75Engine, SimpleInventory
from tnalagmes.models.objects import Calendar
from tnalagmes.data.zombie_survival_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY


class ZVirus(Oregon75Engine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY
    name = "ZVirus"

    def __init__(self):
        Oregon75Engine.__init__(self)
        self.calendar = Calendar(turn_delta=1, total_turns=25)
        self.inventory = SimpleInventory(1000)


if __name__ == "__main__":
    game = ZVirus()
    game.run()
