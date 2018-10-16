#!/usr/bin/python
from tnalagmes.engines import TNaLaGmesEngine
from tnalagmes.models.objects import Inventory
from tnalagmes.models.agents import Agent
import random


class Scene(TNaLaGmesEngine):
    """
    """
    # TODO basic physics engine, collision detection is the urgent part
    name = "location"
    """
    go up / down / left / right / front /back
    go north / south / west / east ....
    who is in the room
    items in the room
    connected rooms
    describe room
    room _name
    """

    def __init__(self, description="empty room", items=None, npcs=None, directions=None, dimensions=3):
        """

        Args:
            description:
            items:
            npcs:
            directions:
            dimensions:
        """
        TNaLaGmesEngine.__init__(self, "scene")
        self.description = description
        self.items = items or Inventory()
        self.npcs = npcs or {}
        self.connections = directions or {}
        self.dimensions = dimensions

    # TODO add object / npc to scene
    def add_connection(self, room, direction="front", message=None):
        """

        Args:
            room:
            direction:
            message:
        """
        if isinstance(room, str):
            room = Scene(room)
        self.connections[direction] = room
        message = message or direction + " there is a " + room.name
        self.description += "\n" + message

    def handle_look(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        item = intent.get("item", "room")
        if item == "room":
            return self.description
        return "it is a " + item

    def handle_get(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        item = intent.get("item", "nothing")
        if item in self.items:
            item = self.items[item].name
        return "got " + item

    def handle_talk(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        npc = intent.get("npc", "yourself")
        if npc in self.npcs:
            npc = self.npcs[npc].name
        return self.talk_to_npc(npc)

    def register_default_intents(self):
        """

        """

        self.register_intent("look", ["look {item}", "look at {item}", "describe {item}"], self.handle_look)
        self.register_intent("get", ["get {item}", "acquire {item}", "fetch {item}", "pick {item}", "stash {item}"],
                             self.handle_look)
        self.register_intent("talk", ["talk with {npc}", "engage {npc}", "interact with {npc}"],
                             self.handle_look)

    def get_item(self, item):
        """

        Args:
            item:

        Returns:

        """
        if item in self.items:
            item = self.items[item]
            self.items.pop(item)
            return item
        return None

    def talk_to_npc(self, npc, utterance="hello"):
        """

        Args:
            npc:
            utterance:

        Returns:

        """
        if npc in self.npcs:
            return self.npcs[npc].parse_command(utterance)
        return "talk to who?"


class World(Scene):
    """
    """
    name = "Text Universe"
    """
    volume / height / width / area / dimensions
    number of rooms
    teleport to room
    how many players
    how many npcs
    how many items
    create scene
    create npc
    """

    def __init__(self, description="the text universe", agent=None, scenes=None, dimensions=3):
        """

        Args:
            description:
            agent:
            scenes:
            dimensions:
        """
        Scene.__init__(self, dimensions=dimensions)
        self.object_type = "world"
        self.agent = agent or Agent()
        self.description = description
        self.scenes = scenes or {"emptiness": Scene()}

    def register_default_intents(self):
        """

        """
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

    def place_player(self, scene_name=None):
        """

        Args:
            scene_name:
        """
        scene_name = scene_name or random.choice(self.scenes)
        self.agent.scene = self.scenes.get(scene_name)

    @property
    def current_scene(self):
        """

        Returns:

        """
        return self.agent.scene

    def handle_describe(self, intent):
        """

        Args:
            intent: 

        :return:
        """
        return self.agent.scene.description

    def handle_up(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_down(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_front(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_back(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_left(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_right(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_north(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_south(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_east(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_west(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_northeast(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_northwest(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_southeast(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""

    def handle_southweast(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return ""


class PhysicsEngine(World):
    """
    """
    # TODO real physics simulation helpers pyOde
    laws = {}
