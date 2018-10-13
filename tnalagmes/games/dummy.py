from tnalagmes.engines import TNaLaGmesEngine
from tnalagmes.data.template_data import GAME_EVENTS, RANDOM_EVENTS, TERMINOLOGY


class TemplateGame(TNaLaGmesEngine):
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    TERMINOLOGY = TERMINOLOGY

    def __init__(self):
        TNaLaGmesEngine.__init__(self, "TemplateGame")
        self.calendar.change_speed(1)

    def on_turn(self):
        print(self.calendar.pretty_date)

        self.calendar.advance_date()


if __name__ == "__main__":
    game = TemplateGame()
    game.play()
