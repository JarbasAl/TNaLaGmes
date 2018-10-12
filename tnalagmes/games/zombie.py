from tnalagmes.oregonengine import OregonEngine
from tnalagmes.data.zombie_survival_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY


class ZVirus(OregonEngine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY

    def __init__(self):
        OregonEngine.__init__(self, "ZVirus", from_json=True)


if __name__ == "__main__":
    game = ZVirus()
    game.play()
