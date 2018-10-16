#!/usr/bin/python
import random
from tnalagmes import TNaLaGmesConstruct
from tnalagmes.models.objects import Inventory
from tnalagmes.engines import TNaLaGmesEngine
import all_the_chatbots
import logging
logging.getLogger("urllib3").setLevel(logging.WARNING)

class NPC(TNaLaGmesConstruct):
    # TODO subclass agent from this ?
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
        """

        Args:
            name:
            health:
            mana:
            attack:
            magic:
            inventory:
        """
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
        """

        Returns:

        """
        return random.randrange(self.attack_low, self.attack_high)

    def take_damage(self, dmg):
        """

        Args:
            dmg:

        Returns:

        """
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return self.hp

    def heal(self, dmg):
        """

        Args:
            dmg:
        """
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def spend_mana(self, cost):
        """

        Args:
            cost:
        """
        self.mp -= cost

    def cast_spell(self):
        """

        Returns:

        """
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
        """

        """

        def hello(intent):
            """

            Args:
                intent:

            Returns:

            """
            return "hello"

        self.register_intent("hello", ["hi", "hey", "hello", "how are you", "yo"], hello)


class Agent(TNaLaGmesEngine):
    """
    """
    def __init__(self, name="you", autostart=False):
        """

        Args:
            name:
            autostart:
        """
        TNaLaGmesEngine.__init__(self)
        self.name = name
        if autostart:
            self._thread.start()  # start agent

    def interact_with(self, construct):
        """

        Args:
            construct:
        """
        self.interacting_with = construct

    def look_to(self, direction):
        """

        Args:
            direction:
        """
        direction = self.direction_to_int(direction)
        if direction is not None:
            self.direction = direction


    def take_damage(self, dmg):
        """

        Args:
            dmg:

        Returns:

        """
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return self.hp



    def handle_hello(self, intent):
        """

        Args:
            intent:

        Returns:

        """
        return "hello world"

    def register_default_intents(self):
        """

        """

        self.register_intent("hello", ["hi", "hey", "hello", "how are you", "yo"], self.handle_hello)

    def on_turn(self):
        """

        """
        print("agentt should perform action here")

    def on_start(self):
        """

        """
        print("agent ready")


class ChatAgent(Agent):
    """
    """
    def __init__(self, name):
        """

        Args:
            name:
        """
        Agent.__init__(self, name)
        self.chat_handler = None

    def on_turn(self):
        """

        """
        if not self.waiting_for_user:
            self.output = self.chat_handler(self.input)
        self.waiting_for_user = True

    def on_start(self):
        """

        """
        if self.chat_handler is None:
            handler = all_the_chatbots.bot_map().get(self.name)
            if not handler:
                def handler(text):
                    """

                    Args:
                        text:

                    Returns:

                    """
                    return "?"
            self.chat_handler = handler
        self.submit_command("what is your name?")

    @staticmethod
    def create_chatbot(name=None):
        """

        Args:
            name:

        Returns:

        """
        name = name or random.choice(all_the_chatbots.bot_list())
        return ChatAgent(name=name)


# Agents for Notable ChatBots
NeuralConvo = ChatAgent.create_chatbot("neuralconvo")
TheCatterpillar = ChatAgent.create_chatbot("the_catterpillar")
Mitsuku = ChatAgent.create_chatbot("mitsuku")
Aristo = ChatAgent.create_chatbot("aristo")
Euclid = ChatAgent.create_chatbot("euclid")

if __name__ == "__main__":
    chat = Mitsuku
    chat.run()
