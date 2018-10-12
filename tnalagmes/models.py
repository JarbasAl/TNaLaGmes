#!/usr/bin/python
from datetime import date
from datetime import timedelta
from datetime import datetime
import random
from tnalagmes import TNaLaGmesConstruct

# https://mentalfloss.com/article/28968/where-are-they-now-diseases-killed-you-oregon-trail
#https://www.format.com/magazine/features/design/you-have-died-of-dysentery-oregon-trail-design
# TODO default intents
# TODO use locale for reading strings


class ProgressTracker(TNaLaGmesConstruct):
    """
    "total distance"
    "current mileage"
    "add mileage"
    "subtract mileage"
    "are you completed?"
    """
    def __init__(self):
        TNaLaGmesConstruct.__init__(self, "progress_tracker")
        self._total_distance = 2040
        self._difficulty_trigger = 950
        self.last_advance = 0
        self.last_turn_fraction = 0
        self.mileage = 0
        self.medium_difficulty = False
        self.hard_difficulty = False

    def random_advance(self, fuel):
        # original logic from oregon trail
        self.last_advance = int(200 + (fuel.value - 220) / 5 + 10 * random.random())
        self.mileage += self.last_advance

    # this function should only be used for increases in mileage
    # during a turn
    def add_mileage(self, gained_ground):
        self.last_advance += gained_ground
        self.mileage += int(gained_ground)

    def subtract_mileage(self, lost_ground):
        self.mileage -= int(lost_ground)
        if self.mileage < 0:
            self.mileage = 0

    def print_mileage(self):
        print("TOTAL MILEAGE IS", self.mileage)

    def difficulty_triggered(self):
        if self.mileage >= self._difficulty_trigger:
            return True
        return False

    @property
    def completed(self):
        if self.mileage >= self._total_distance:
            try:
                self.last_turn_fraction = (self._total_distance - self.last_advance) / (
                        self.mileage - self.last_advance)
            except ZeroDivisionError:
                self.last_turn_fraction = 0
            return True
        return False

    @property
    def total_distance(self):
        return self._total_distance

    @property
    def difficulty_threshold(self):
        return self._difficulty_trigger


class Calendar(TNaLaGmesConstruct):
    """
    Calendar Object

    "What day/date/week/weekday/month/year is it?"
    "increase speed"
    "decrease speed"
    "rollback X days/months/weeks/years"
    "advance X days/months/weeks/years"

    "next turn"
    "how many turns left"
    "how many turns passed"
    "how many days per turn"
    "maximum number of turns"

    """
    def __init__(self, total_turns=20, start_date=None, turn_delta=0):
        TNaLaGmesConstruct.__init__(self, "calendar")
        self._date = start_date or datetime.now()
        self.days_per_turn = turn_delta
        self._turn_delta = timedelta(days=self.days_per_turn) if self.days_per_turn else None
        self._turn_count = 1
        self._max_turns = total_turns

    def change_speed(self, days_per_turn=0):
        if isinstance(days_per_turn, str):
            if days_per_turn.strip().lower().startswith("easy"):
                days_per_turn = 1
            elif days_per_turn.strip().lower().startswith("hard"):
                days_per_turn = 14
            days_per_turn = self.extract_number(days_per_turn)

        self._turn_delta = timedelta(days_per_turn)

    def advance_date(self):
        if self._turn_delta is None:
            self._date = datetime.now()
            return
        self._date += self._turn_delta
        self._turn_count += 1

    def rollback_date(self, rollback_days=None):
        rollback_days = rollback_days or self.days_per_turn
        self._date -= timedelta(days=rollback_days)

    @property
    def pretty_date(self):
        return self._date.strftime('%d, %b %Y')

    @property
    def is_final_turn(self):
        if not self._turn_delta:
            return False
        if self._turn_count >= self._max_turns:
            return True
        else:
            return False

    @property
    def turns(self):
        return self._turn_count

    @property
    def date(self):
        return self._date

    @property
    def max_turns(self):
        return self._max_turns


class InventoryItem(TNaLaGmesConstruct):
    """
    what are you
    what can you do
    what is your name
    """
    def __init__(self, name="thing", description="a thing", item_type="object"):
        TNaLaGmesConstruct.__init__(self, name)
        self._value = 0
        self.name = name
        self.description = description
        self.item_type = item_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = int(value)

    def add(self, value):
        self._value += int(value)

    def subtract(self, value):
        self._value -= int(value)


class Inventory(TNaLaGmesConstruct):
    """
    what do you have
    how much money do you have
    how much are you worth
    spend X money
    """
    def __init__(self, start_money=700):
        TNaLaGmesConstruct.__init__(self, "inventory")
        self.start_money = start_money
        self._money = start_money
        self.items = []

    @property
    def money(self):
        return self._money

    def spend(self, cost):
        self._money -= int(cost)

    def print_warnings(self):
        pass

    def print_inventory(self):
        pass


class Ability(TNaLaGmesConstruct):
    """
    what is your name
    what is your cost
    what is your damage
    what are you
    generate some damage
    """
    def __init__(self, name, cost, dmg, type):
        TNaLaGmesConstruct.__init__(self, "ability")
        self.name = name
        self.cost = cost
        self.dmg = dmg
        self.type = type

    def generate_damage(self):
        low = self.dmg - 15
        high = self.dmg + 15
        return random.randrange(low, high)


class NPC(TNaLaGmesConstruct):
    """
    hello world
    what is your name
    attack
    take damage
    heal
    spend mana
    cast spell
    """
    def __init__(self, name, health, mana=0, attack=1, magic=None, inventory=None):
        TNaLaGmesConstruct.__init__(self, "NPC")
        self.items = inventory or Inventory()
        self.max_hp = health
        self.hp = health
        self.max_mp = mana
        self.mp = mana
        self.attack_low = attack - 10
        self.attack_high = attack + 10
        self.magic = magic or []
        self.actions = ["Attack", "Magic", "Items"]
        self.name = name

    def attack(self):
        return random.randrange(self.attack_low, self.attack_high)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def heal(self, dmg):
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def spend_mana(self, cost):
        self.mp -= cost

    def cast_spell(self):
        if not len(self.magic):
            return "", 0
        spell = random.choice(self.magic)
        magic_dmg = spell.attack()

        pct = self.hp / self.max_hp * 100

        if self.mp < spell.cost or spell.type == "white" and pct > 50:
            self.cast_spell()
        else:
            return spell, magic_dmg

    def register_default_intents(self):

        def hello(intent):
            return "hello"

        self.register_intent("hello", ["hi", "hey", "hello", "how are you", "yo"], hello)


class Room(TNaLaGmesConstruct):
    """
    go up / down / left / right / front /back
    go north / south / west / east ....
    who is in the roon
    items in the room
    connected rooms
    describe room
    room name
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
            room = Room(room)
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


class Player(TNaLaGmesConstruct):
    def __init__(self, health, name="you", mana=0, attack=1, magic=None, inventory=None):
        TNaLaGmesConstruct.__init__(self, "player")
        self.max_hp = health
        self.hp = health
        self.max_mp = mana
        self.mp = mana
        self.attack_low = attack - 20
        self.attack_high = attack + 20
        self.magic = magic or []
        self.items = inventory or Inventory()
        self.actions = ["Attack", "Magic", "Items"]
        self.name = name

    def attack(self):
        return random.randrange(self.attack_low, self.attack_high)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def heal(self, dmg):
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def spend_mana(self, cost):
        self.mp -= cost

    def cast_spell(self):
        if not len(self.magic):
            return "", 0
        spell = random.choice(self.magic)
        magic_dmg = spell.attack()

        pct = self.hp / self.max_hp * 100

        if self.mp < spell.cost or spell.type == "white" and pct > 50:
            self.cast_spell()
        else:
            return spell, magic_dmg

    def register_default_intents(self):

        def hello(intent):
            return "hello world"

        self.register_intent("hello", ["hi", "hey", "hello", "how are you", "yo"], hello)

