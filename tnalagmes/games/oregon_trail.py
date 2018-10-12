from tnalagmes.oregonengine import OregonEngine
from tnalagmes.data.oregon_trail_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY
from random import choice


class OregonTrail(OregonEngine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY

    def __init__(self):
        OregonEngine.__init__(self, "Oregon Trail")
        # default events are clones of oregon trail!

    def output(self, text=""):
        if isinstance(text, list):
            text = [t.strip() for t in text if t.strip()]
            text = choice(text)
        else:
            if not text.strip():
                return ""
        # all upper case like the classic!
        self._output += text.upper() + "\n"
        return text.upper()


if __name__ == "__main__":
    game = OregonTrail()
    game.play()
