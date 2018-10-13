#!/usr/bin/python
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.models.objects import Inventory


class Scene(TNaLaGmesConstruct):
    """
    go up / down / left / right / front /back
    go north / south / west / east ....
    who is in the roon
    items in the room
    connected rooms
    describe room
    room _name
    """
    def __init__(self, name, description="empty room", items=None, npcs=None, directions=None):
        TNaLaGmesConstruct.__init__(self, "room")
        self.name = name
        self.description = description
        self.items = items or Inventory()
        self.npcs = npcs or {}
        self.connections = directions or {}

    def add_connection(self, room, direction="front", message=None):
        if isinstance(room, str):
            room = Scene(room)
        self.connections[direction] = room
        message = message or direction + " there is a " + room.name
        self.description += "\n" + message

    def handle_up(self, intent):
        return ""

    def handle_down(self, intent):
        return ""

    def handle_front(self, intent):
        return ""

    def handle_back(self, intent):
        return ""

    def handle_left(self, intent):
        return ""

    def handle_right(self, intent):
        return ""

    def handle_north(self, intent):
        return ""

    def handle_south(self, intent):
        return ""

    def handle_east(self, intent):
        return ""

    def handle_west(self, intent):
        return ""

    def handle_northeast(self, intent):
        return ""

    def handle_northwest(self, intent):
        return ""

    def handle_southeast(self, intent):
        return ""

    def handle_southweast(self, intent):
        return ""

    def handle_describe(self, intent):
        return self.description

    def handle_look(self, intent):
        item = intent.get("item", "room")
        if item == "room":
            return self.handle_describe(intent)
        return "it is a " + item

    def handle_get(self, intent):
        item = intent.get("item", "nothing")
        if item in self.items:
            item = self.items[item].name
        return "got " + item

    def handle_talk(self, intent):
        npc = intent.get("npc", "yourself")
        if npc in self.npcs:
            npc = self.npcs[npc].name
        return self.talk_to_npc(npc)

    def register_default_intents(self):
        self.register_intent("up", ["up"], self.handle_up)
        self.register_intent("down", ["down"], self.handle_down)
        self.register_intent("front", ["forward"], self.handle_front)
        self.register_intent("back", ["back", "backward"], self.handle_back)
        self.register_intent("left", ["left"], self.handle_left)
        self.register_intent("right", ["right"], self.handle_right)
        self.register_intent("north", ["north"], self.handle_north)
        self.register_intent("south", ["south"], self.handle_south)
        self.register_intent("east", ["east"], self.handle_east)
        self.register_intent("west", ["west"], self.handle_west)
        self.register_intent("northeast", ["northeast"], self.handle_northeast)
        self.register_intent("northwest", ["northwest"], self.handle_northwest)
        self.register_intent("southeast", ["southeast"], self.handle_southeast)
        self.register_intent("southwest", ["southwest"], self.handle_southweast)
        self.register_intent("describe", ["describe room", "describe surroundings", "look"], self.handle_describe)
        self.register_intent("look", ["look {item}", "look at {item}", "describe {item}"], self.handle_look)
        self.register_intent("get", ["get {item}", "acquire {item}", "fetch {item}", "pick {item}", "stash {item}"], self.handle_look)
        self.register_intent("talk", ["talk with {npc}", "engage {npc}", "interact with {npc}"],
                             self.handle_look)

    def get_item(self, item):
        if item in self.items:
            item = self.items[item]
            self.items.pop(item)
            return item
        return None

    def talk_to_npc(self, npc, utterance="hello"):
        if npc in self.npcs:
            return self.npcs[npc].parse_command(utterance)
        return "talk to who?"


