#!/usr/bin/python
import random
from tnalagmes import TNaLaGmesConstruct


class Ability(TNaLaGmesConstruct):
    """
    what is your _name
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

    def register_core_intents(self):
        "" """
            what is your _name
            what is your cost
            what is your damage
            generate some damage
        """
        self.register_keyword_intent("yes",  handler=self.handle_yes)
        self.register_keyword_intent("no", handler=self.handle_no)
        self.register_keyword_intent("_name",
                                     required="_name",
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("type",
                                     required=self.name,
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("damage",
                                     required=["damage"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)
        self.register_keyword_intent("create_damage",
                                     required=["damage", "create"],
                                     optionals=["you"],
                                     handler=self.handle_mileage)
        self.register_keyword_intent("cost",
                                     required=["value"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)

    def generate_damage(self):
        low = self.dmg - 15
        high = self.dmg + 15
        return random.randrange(low, high)


