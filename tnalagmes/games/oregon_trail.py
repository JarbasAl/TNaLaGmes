from tnalagmes.engines.oregon75 import Oregon75Engine, Calendar
from tnalagmes.data.oregon_trail_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY
from datetime import date


class OregonTrail(Oregon75Engine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY
    name = "Oregon Trail"

    def __init__(self):
        Oregon75Engine.__init__(self)
        # default events are clones of oregon trail!
        self.calendar = Calendar(turn_delta=14, start_date=date(1847, 3, 29), total_turns=18)


if __name__ == "__main__":
    game = OregonTrail()
    game.run()
