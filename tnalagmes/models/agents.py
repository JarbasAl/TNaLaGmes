#!/usr/bin/python
from datetime import date
from datetime import timedelta
from datetime import datetime
import random
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.models.objects import Inventory


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

    def register_core_intents(self):
        "" """
            hello world
            take damage
            spend mana
        """
        self.register_intent("name", samples=[],
                             handler=self.handle_total_distance)
        self.register_keyword_intent("name",
                                     required=["name"],
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("health",
                                     required=["health"],
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("heal",
                                     required=["heal"],
                                     optionals=["you", "execute"],
                                     handler=self.handle_mileage)

        self.register_keyword_intent("execute_spell",
                                     required=["spell"],
                                     optionals=["you", "execute"],
                                     handler=self.handle_mileage)

        self.register_keyword_intent("execute_attack",
                                     required=["attack"],
                                     optionals=["you", "execute"],
                                     handler=self.handle_mileage)

        self.register_keyword_intent("attack_value",
                                     required=["damage"],
                                     optionals=["question", "you", "value"],
                                     handler=self.handle_mileage)

        self.register_keyword_intent("mana_value",
                                     required=["mana", "value"],
                                     optionals=["question", "you", "value"],
                                     handler=self.handle_mileage)

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

