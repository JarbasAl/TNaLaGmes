from tnalagmes.engines.oregon75 import Oregon75Engine
from tnalagmes.data.template_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY


class TemplateGame(Oregon75Engine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY

    def __init__(self):
        Oregon75Engine.__init__(self)


if __name__ == "__main__":
    game = TemplateGame()
    game.run()
