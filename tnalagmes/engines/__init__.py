#!/usr/bin/python
import random
from threading import Thread
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.data.template_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from tnalagmes.models.objects import Calendar, Inventory, ProgressTracker
from pprint import pprint
from os.path import expanduser, join, exists
from os import makedirs
import json


class Event(TNaLaGmesConstruct):

    def __init__(self, name="", intro="", conclusion="", handler=None):
        TNaLaGmesConstruct.__init__(self, "event")
        self._name = name
        self._intro = intro
        self._conclusion = conclusion
        self.fields = {}
        self._num_triggers = 0
        self.event_handler = handler

    @property
    def num_triggers(self):
        return self._num_triggers

    @property
    def name(self):
        return self._name

    @property
    def intro(self):
        return self._intro

    @property
    def conclusion(self):
        return self._conclusion

    def add_field(self, name, data=None):
        # TODO set property
        self.fields[name] = data

    def from_json(self, data):
        for k in data:
            if k == "_name":
                self._name = data[k]
            elif k == "_intro":
                self._intro = data[k]
            elif k == "_conclusion":
                self._conclusion = data[k]
            else:
                self.add_field(k, data[k])

    @property
    def data(self):
        event_template = {

            "_name": self._name,
            "_intro": self._intro,
            "_conclusion": self._conclusion
        }
        for field in self.fields:
            event_template[field] = self.fields[field]
        return event_template

    def trigger(self, data=None):
        if self.event_handler is not None:
            try:
                return self.event_handler(data)
            except TypeError:
                return self.event_handler()

        self.output = self.intro
        self.output = self.conclusion
        return self.output

    def bind_handler(self, event_handler=None):
        self.event_handler = event_handler


class TNaLaGmesEngine(TNaLaGmesConstruct):
    TERMINOLOGY = TERMINOLOGY
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    name = "TNaLaGmesEngine"

    def __init__(self, from_json=True):
        TNaLaGmesConstruct.__init__(self, "game_engine", scene=self)
        self.from_json = from_json
        self.random_events = []
        self.calendar = Calendar()
        self.tracker = ProgressTracker()
        self.running = False
        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)

    def on_random_event(self):
        event = random.choice(self.random_events)
        self.output = event.trigger()

    @classmethod
    def get_entity(cls, text):
        return random.choice(cls.TERMINOLOGY.get(text, [""]))

    def pprint_data(self):
        data = {"random_events": self.RANDOM_EVENTS,
                "terminology": self.TERMINOLOGY,
                "turn_data": self.DATA}
        pprint(data)

    def register_core_intents(self):
        # TODO translate options strings to 1, 2, 3, 4

        # engine interface
        self.register_intent("save", ["save {file}", "save"], self.handle_save)
        self.register_intent("load", ["load {file}", "load"], self.handle_load)
        self.register_intent("export", ["export {file}"], self.handle_export)
        self.register_intent("import", ["import {file}"], self.handle_import)
        self.register_intent("quit", ["quit", "exit", "shutdown", "abort"], self.handle_quit)

    def register_event(self, event_object):
        if isinstance(event_object, Event):
            self.random_events.append(event_object)
        elif isinstance(event_object, dict):
            self.register_from_json(event_object)
        elif isinstance(event_object, str):
            e = Event(intro=event_object)
            self.random_events.append(e)
        elif isinstance(event_object, list):
            for e in event_object:
                self.register_event(e)
        elif isinstance(event_object, bool) or \
                isinstance(event_object, int) or \
                isinstance(event_object, float):
            raise AttributeError("attempted to register invalid event")
        else:
            e = Event()
            e.bind_handler(event_object)
            self.random_events.append(e)

    def register_from_json(self, dictionary, event_handler=None):
        event = Event()
        event.from_json(dictionary)
        if event_handler:
            event.bind_handler(event_handler)
        self.register_event(event)

    def register_events(self):
        """
        load default events or from jsom
        :param from_json:
        :return:
        """
        if self.from_json:
            for event_type in self.RANDOM_EVENTS:
                event = Event()
                event.from_json(self.RANDOM_EVENTS.get(event_type, {}))
                self.register_event(event)

    def intro(self):
        self.output = self.DATA.get("intro",{}).get("intro", "")
        self.output = self.DATA.get("intro", {}).get("conclusion", "")

    def on_turn(self):
        self.output = self.calendar.pretty_date

        self.output = "total progress: " + str(self.tracker.mileage)

        # progress for each turn
        self.tracker.random_advance()

        # Random thing happened
        self.on_chance_encounter()

        # Move to next turn
        self.calendar.advance_date()

    def on_win(self):
        self.calendar.rollback_date(int(self.tracker.last_turn_fraction * self.calendar.days_per_turn))
        self.output = self.calendar.pretty_date
        self.running = False

    def on_lose(self):
        self.running = False

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
        # Turns have been exhausted or objective has been reached
        if self.tracker.completed:
            self.on_win()
        else:
            self.on_lose()
        self.running = False

    def on_difficulty_modifier(self):
        if not self.tracker.difficulty_triggered():
            return
        self.on_easy_difficulty()
        if self.tracker.medium_difficulty:
            self.on_medium_difficulty()
        if self.tracker.hard_difficulty:
            self.on_hard_difficulty()

    def manual_fix_parse(self, text):
        # any parsing ou might want to reading from game data, ie replace {inv.money}
        return text

    def run(self):
        self._thread.start()
        while self.running:
            if self.waiting_for_user:
                command = input(self.output)
                self.parse_command(command)

    def submit_command(self, text=""):
        self.input = text
        self.waiting_for_user = False

    def _run(self):
        self.running = True
        self.on_start()
        self.register_events()

        while not self.calendar.is_final_turn and not self.tracker.completed:
            self.on_turn()
        self.on_game_over()
        self.running = False

    def save(self, path=None):
        pass

    def load(self, path=None):
        pass

    def quit(self):
        if self.ask_yes_no(self.DATA.get("quit_message",
                                         "really want to quit?")):
            self.running = False
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

    def ask_world(self, utterance):
        # query self intents first
        intents = self.calc_intents(utterance)
        answer = ""
        for intent in intents:
            answer += self.intent_parser.execute_intent(intent)
        if answer and answer != "?":
            return answer

        # query all game objects
        for obj in self.talking_objects:
            # parse intent
            answer = obj.parse_command(utterance)
            if answer.strip().replace(".", "") != "?":
                return answer

        # submit to internal game engine for handling
        return "?"

    @property
    def talking_objects(self):
        return []

    def parse_command(self, utterance):
        # parse intent
        answer = self.ask_world(utterance)
        if answer.strip().replace(".", "") != "?":
            self.output = answer
        else:
            # fallback
            self.output = self.submit_command(utterance)
        #return self.output

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

    def on_start(self):
        if self.ask_yes_no("Do you need instructions?"):
            self.intro()
