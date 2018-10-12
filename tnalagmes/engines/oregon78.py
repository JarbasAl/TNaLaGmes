from tnalagmes.data.oregon_trail_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from tnalagmes.engines.oregon75 import Oregon75Engine


class Oregon78Engine(Oregon75Engine):
    """ so called because logic is ported from 1978 basic version of oregon trail"""
    # https://www.filfre.net/misc/oregon1978.bas

    TERMINOLOGY = TERMINOLOGY
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    name = "Oregon78Engine"

    def __init__(self, name=None, from_json=False):
        Oregon75Engine.__init__(self, "game_engine", from_json)


if __name__ == "__main__":
    game = Oregon78Engine()
    game.play()
