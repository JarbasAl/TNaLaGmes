#!/usr/bin/python
import random
from threading import Thread
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.models import Player, Calendar, Inventory, ProgressTracker
from pprint import pprint
from os.path import expanduser, join, exists
from os import makedirs
import json


class TNaLaGmesEngine(TNaLaGmesConstruct):
    name = "TNaLaGmesEngine"

    def __init__(self, start_health=1000, from_json=True):
        TNaLaGmesConstruct.__init__(self, "game_engine")
        self.player = Player(start_health)
        self.from_json = from_json
        self.random_events = []
        self.inventory = Inventory()
        self.calendar = Calendar()
        self.tracker = ProgressTracker()
        self.playing = False
        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)

    def register_default_intents(self):
        # engine interface
        self.register_intent("save", ["save {file}", "save"], self.handle_save)
        self.register_intent("load", ["load {file}", "load"], self.handle_load)
        self.register_intent("export", ["export {file}"], self.handle_export)
        self.register_intent("import", ["import {file}"], self.handle_import)
        self.register_intent("quit", ["quit", "exit", "shutdown", "abort"], self.handle_quit)

    @property
    def chance_encounter_seed(self):
        # The convoluted original logic for a rider attack: RND(0)*10>((M/100-4)^2+72)/((M/100-4)^2+12)-1
        return (random.random() * 10) > ((
                                          self.tracker.mileage / 100.0 - 4) ** 2 + 72) / (
                       (
                               self.tracker.mileage / 100.0 - 4) ** 2 + 12) - 1

    def register_event(self, handler):
        self.random_events.append(handler)

    def register_from_json(self, dictionary,
                           event_handler=None,
                           damage_handler=None,
                           death_handler=None):
        event = {
            "intro": dictionary.get("intro", ""),
            "name": "",
            "conclusion": dictionary.get("conclusion", ""),
            "error": dictionary.get("error", ""),
            "damage": dictionary.get("damage", ""),
            "die": dictionary.get("die", ""),
            "type": dictionary.get("type", "custom")
        }

        def handler():
            intro = self.RANDOM_EVENTS.get(event["type"],
                                           {}).get("intro",
                                                   "")
            self.output = intro
            if event_handler is not None:
                event_handler()
            if damage_handler is not None:
                damage_handler()
            if death_handler is not None:
                death_handler()
            conclusion = self.RANDOM_EVENTS.get(
                event["type"], {}).get("conclusion", "")
            self.output = conclusion

        self.register_event(handler)

    def register_events(self):
        """
        load default events or from jsom
        :param from_json:
        :return:
        """
        if self.from_json:
            for event_type in self.RANDOM_EVENTS:
                event = self.RANDOM_EVENTS.get(event_type,
                                               {})
                name = list(event.keys())[0]
                data = event[name]
                data["name"] = name
                data["type"] = event_type
                self.register_from_json(dictionary=data)

    def intro(self):
        self.output = self.DATA["intro"]["intro"]
        self.output = self.DATA["intro"]["conclusion"]

    def on_turn(self):
        pass

    def on_win(self):
        self.output = self.DATA["win"]["intro"]
        # self.output = "AFTER " + str(self.objective.total_distance) + " LONG MILES---HOORAY!!!!!")
        self.calendar.rollback_date(int(self.tracker.last_turn_fraction * self.calendar.days_per_turn))
        self.calendar.print_date()
        self.inventory.print_inventory()
        self.output = self.DATA["win"]["conclusion"]
        self.playing = False

    def on_lose(self):
        self.output = self.DATA["lose"]["intro"]
        # TODO
        self.output = self.DATA["lose"]["conclusion"]
        self.playing = False

    def on_damage(self):
        pass

    def on_chance_encounter(self):
        pass

    def on_easy_difficulty(self):
        pass

    def on_medium_difficulty(self):
        pass

    def on_hard_difficulty(self):
        pass

    def on_shop(self):
        pass

    def on_game_over(self):
        # Turns have been exhausted or Oregon has been reached
        if self.tracker.completed():
            self.on_win()
        else:
            self.output = self.DATA["game_over"]["error"]
            self.output = self.DATA["game_over"]["conclusion"] + str(
                self.tracker.total_distance - self.tracker.mileage)
            self.on_lose()

    def on_difficulty_modifier(self):
        if not self.tracker.difficulty_triggered():
            return
        self.on_easy_difficulty()
        if self.tracker.medium_difficulty:
            self.on_medium_difficulty()
        if self.tracker.hard_difficulty:
            self.on_hard_difficulty()

    def manual_fix_parse(self, text):
        # replace vars
        text = text.replace("{inv.money}",
                            str(self.inventory.money))
        text = text.replace("{inv.cash}",
                            str(self.inventory.money))
        text = text.replace("{inv.currency}",
                            str(self.inventory.money))
        return text + "\n"

    def play(self):
        self._thread.start()
        while self.playing:
            if self.waiting_for_user:
                command = input(self.output)
                self.parse_command(command)

    def submit_command(self, text=""):
        self.input = text
        self.waiting_for_user = False

    def _run(self):
        self.playing = True
        if self.ask_yes_no("Do you need instructions?"):
            self.intro()
        self.register_events()

        while not self.calendar.is_final_turn and not self.tracker.completed:
            self.on_turn()
        self.on_game_over()
        self.playing = False

    def pprint_data(self):
        data = {"random_events": self.RANDOM_EVENTS,
                "terminology": self.TERMINOLOGY,
                "turn_data": self.DATA}
        pprint(data)

    def save(self, path=None):
        pass

    def load(self, path=None):
        pass

    def quit(self):
        if self.ask_yes_no(self.DATA.get("quit_message",
                                         "really want to quit?")):
            self.playing = False
            self.on_game_over()

    def handle_quit(self, intent):
        self.quit()
        return "game exited"

    def handle_save(self, intent):
        self.save(intent.get("file"))
        return "game saved"

    def handle_load(self, intent):
        self.load(intent.get("file"))
        return "game loaded"

    def handle_import(self, intent):
        self.import_game_data(intent["file"])
        return "game data imported"

    def handle_export(self, intent):
        self.export_game_data(intent["file"])
        return "game data exported"

    def parse_command(self, utterance):
        # parse intent
        intent = self.calc_intent(utterance)
        intent_name = intent.get("name", "unknown")
        if intent_name in self.intents:
            return self.intents[intent_name]()
        else:
            # fallback
            self.submit_command(utterance)
        return self.output

    @classmethod
    def export_game_data(cls, path=None):
        path = path or join(expanduser("~"),
                            "TextSurvivalGames")
        if not exists(path):
            makedirs(path)
        file = join(path, cls.name + ".json")
        data = {"random_events": cls.RANDOM_EVENTS,
                "terminology": cls.TERMINOLOGY,
                "turn_data": cls.DATA}
        with open(file, "w") as f:
            f.write(json.dumps(data))
        pprint(data)

    @classmethod
    def import_game_data(cls, path=None):
        path = path or join(expanduser("~"),
                            "TextSurvivalGames")
        file = join(path, cls.name + ".json")
        if exists(file):
            with open(file, "r") as f:
                data = json.loads(f.read())
            pprint(data)
            cls.DATA = data.get("data", cls.DATA)
            cls.TERMINOLOGY = data.get("data",
                                       cls.TERMINOLOGY)
            cls.RANDOM_EVENTS = data.get("data",
                                         cls.RANDOM_EVENTS)
