from random import random, choice
from tnalagmes.data.oregon_trail_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from tnalagmes.engines import TNaLaGmesEngine
from tnalagmes.engines.oregon import Inventory, TurnState


class Oregon75Engine(TNaLaGmesEngine):
    """ so called because logic is ported from 1975 basic version of oregon trail"""
    # https://www.filfre.net/misc/oregon1975.bas

    TERMINOLOGY = TERMINOLOGY
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS
    name = "Oregon75Engine"

    def __init__(self, name=None, from_json=False):
        TNaLaGmesEngine.__init__(self, "game_engine", from_json)
        self.turn = TurnState()
        self.inventory = Inventory()
        if from_json:
            self.import_game_data()

    @property
    def chance_encounter_seed(self):
        # The convoluted original logic for a rider attack: RND(0)*10>((M/100-4)^2+72)/((M/100-4)^2+12)-1
        return (random.random() * 10) > ((
                                          self.tracker.mileage / 100.0 - 4) ** 2 + 72) / (
                       (
                               self.tracker.mileage / 100.0 - 4) ** 2 + 12) - 1

    def register_default_intents(self):
        # engine interface
        self.register_intent("save", ["save {file}", "save"], self.handle_save)
        self.register_intent("load", ["load {file}", "load"], self.handle_load)
        self.register_intent("export", ["export {file}"], self.handle_export)
        self.register_intent("import", ["import {file}"], self.handle_import)
        self.register_intent("quit", ["quit", "exit", "shutdown", "abort"], self.handle_quit)
        return
        self.register_intent("inventory", ["inventory", "backpack", "case", "briefcase",
                                           "pockets", "slots", "stash", "inv"], self.handle_inventory)
        self.register_intent("health", ["status", "turn data", "health"], self.handle_quit)
        self.register_intent("distance", ["distance"], self.handle_quit)
        self.register_intent("currency", ["currency", "coins", "coin", "cash", "money", "how much", "value"],
                             self.handle_quit)
        self.register_intent("supplies", ["count supplies", "how many supplies", "supply count", "supply number"],
                             self.handle_quit)
        self.register_intent("medicine", ["count medicine", "how many medicine", "medicine count", "medicine number"],
                             self.handle_quit)
        self.register_intent("fuel", ["count fuel", "how many fuel", "fuel count", "fuel number"],
                             self.handle_quit)
        self.register_intent("armour", ["count armour", "how many armour", "armour count", "armour number"],
                             self.handle_quit)
        self.register_intent("ammunition", ["count ammunition", "how many ammunition", "armour ammunition",
                                            "ammunition number"],
                             self.handle_quit)
        self.register_intent("date", ["day", "date", "weeks"],
                             self.handle_quit)
        self.register_intent("location", ["location", "place", "room", "look"],
                             self.handle_quit)

    # turn events
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
        # Responses to the first two questions are ignored intentionally
        response = True
        for question in self.DATA["lose"].get("yes_no_questions", []):
            response = self.ask_yes_no(question)
        if not response:
            self.output = self.DATA["lose"]["error"]
        self.output = self.DATA["lose"]["conclusion"]

        self.playing = False

    def on_maintenance(self):
        response = self.ask_numeric(self.DATA["maintenance"]["intro"], 1, 3)
        food_eaten = 8 + 5 * response
        if self.inventory.supplies.value < food_eaten:
            self.output = self.DATA["maintenance"]["error"]
            return self.on_maintenance()
        self.turn.eating_state = response
        self.inventory.supplies.subtract(food_eaten)

        self.output = self.DATA["maintenance"]["conclusion"]

    def on_damage(self):
        self.output = self.DATA["damage"]["intro"]
        if (100 * random()) < (10 + (35 * self.turn.eating_state - 1)):
            self.output = self.DATA["damage"]["mild"]
            self.tracker.subtract_mileage(5)
            self.inventory.medicine.subtract(2)
        elif (100 * random()) < (100 - (40 / (4 ** (self.turn.eating_state - 1)))):
            self.output = self.DATA["damage"]["high"]
            self.tracker.subtract_mileage(5)
            self.inventory.medicine.subtract(5)
        if self.inventory.medicine.value < 0:
            if self.turn.injured:
                self.output = self.DATA["damage"]["error"] + "INJURIES"
            else:
                self.output = self.DATA["damage"]["error"] + "PNEUMONIA"
            self.on_lose()
        return

    def on_chance_encounter(self):
        peaceful = True
        self.output = self.get_entity("enemy") + self.DATA["enemy_encounter"]["intro"]
        if random() < 0.8:
            self.output = self.DATA["enemy_encounter"]["peaceful_intro"]
        else:
            self.output = self.DATA["enemy_encounter"]["hostile_intro"]
            peaceful = False

        # riders may randomly switch sides
        if random() <= 0.2:
            peaceful = not peaceful

        response = self.ask_numeric(self.DATA["enemy_encounter"]["number_questions"][0], 1, 4)
        if not peaceful:
            if response == 1:  # run
                self.tracker.add_mileage(20)
                self.inventory.medicine.subtract(15)
                self.inventory.ammunition.subtract(150)
                self.inventory.fuel.subtract(40)
            elif response == 2:  # attack
                response, entry_time = self.ask_with_timeout()
                # Original bullet loss was "B=B-B1*40-80". This produces a gain in ammunitions
                # when response time is less than 2 seconds and small losses when the value is longer (max: 200)
                self.inventory.ammunition.subtract(entry_time * 28.57)
                if entry_time <= 1:
                    self.output = self.DATA["enemy_encounter"]["high_score"]
                elif entry_time <= 4:
                    self.output = self.DATA["enemy_encounter"]["low_score"]
                else:
                    self.output = self.DATA["enemy_encounter"]["damage"]
                    self.turn.injured = True
            elif response == 3:  # continue
                if random() <= 0.8:
                    self.inventory.medicine.subtract(15)
                    self.inventory.ammunition.subtract(150)
                else:
                    self.output = self.DATA["enemy_encounter"]["enemy_run"]
                    return
            else:  # circle wagons
                response, entry_time = self.ask_with_timeout()
                self.inventory.ammunition.subtract((entry_time * 30) - 80)
                self.tracker.subtract_mileage(25)
                if entry_time <= 1:
                    self.output = self.DATA["enemy_encounter"]["high_score"]
                elif entry_time <= 4:
                    self.output = self.DATA["enemy_encounter"]["low_score"]
                else:
                    self.output = self.DATA["enemy_encounter"]["damage"]
                    self.turn.injured = True
        else:  # peaceful riders
            if response == 1:  # run
                self.tracker.add_mileage(15)
                self.inventory.fuel.subtract(10)
            elif response == 2:  # attack
                self.tracker.subtract_mileage(5)
                self.inventory.ammunition.subtract(100)
            elif response == 4:  # circle wagons
                self.tracker.subtract_mileage(20)

        if peaceful:
            self.output = self.get_entity("enemy") + self.DATA["enemy_encounter"]["peaceful_conclusion"]
        else:
            self.output = self.get_entity("enemy") + self.DATA["enemy_encounter"]["hostile_conclusion"]
            if self.inventory.ammunition.value < 0:
                self.output = self.DATA["enemy_encounter"]["die"] + self.get_entity("enemy")
                self.on_lose()

    def on_easy_difficulty(self):
        # medium difficulty
        if (random() * 10) <= (
                9 - ((self.tracker.mileage / 100 - 15) ** 2 + 72) / ((self.tracker.mileage / 100 - 15) ** 2 + 12)):
            self.output = self.DATA["easy_difficulty"]["intro"]
            if random() <= 0.1:
                self.output = self.DATA["easy_difficulty"]["events"][0]
                self.tracker.subtract_mileage(60)
            elif random() <= 0.11:
                self.output = self.DATA["easy_difficulty"]["events"][1]
                self.tracker.subtract_mileage(20 + (30 * random()))
                self.inventory.medicine.subtract(5)
                self.inventory.ammunition.subtract(200)
            else:
                self.output = self.DATA["easy_difficulty"]["events"][2]
                self.tracker.subtract_mileage(45 + (random() // 0.02))

        # First pass evaluated at 950 miles (reached_mountains)
        if not self.tracker.medium_difficulty:
            self.tracker.medium_difficulty = True

    def on_medium_difficulty(self):
        # First pass evaluated at 950 miles (reached_mountains)
        if random() < 0.8:
            self.on_difficulty_damage()
        else:
            self.output = self.DATA["medium_difficulty"]["conclusion"]
            self.tracker.medium_difficulty = False
        if self.tracker.mileage >= 1700 and not self.tracker.hard_difficulty:
            self.tracker.hard_difficulty = True

    def on_hard_difficulty(self):
        # Second pass (blue mountains) at 1700 miles
        if random() < 0.7:
            self.on_difficulty_damage()

    def on_explore(self):
        if self.inventory.ammunition.value < 40:
            self.output = self.DATA["explore"]["error"]
            return
        self.tracker.subtract_mileage(45)

        response, entry_time = self.ask_with_timeout()
        # debug logging? print "User typed", response, "after", entry_time, "seconds"

        if entry_time < 1.0:
            self.output = self.DATA["explore"]["events"][0]
            self.inventory.supplies.add(52 + random() * 6)
            self.inventory.ammunition.subtract(10 - random() * 4)
        elif (100 * random()) < (13 * entry_time):
            self.output = self.DATA["explore"]["events"][1]
        else:
            self.output = self.DATA["explore"]["events"][2]
            self.inventory.supplies.add(48 - 2 * entry_time)
            self.inventory.ammunition.subtract(10 - 3 * entry_time)

    def on_shop(self):
        self.output = self.DATA["shop"]["intro"]
        food = self.ask_numeric(self.get_entity("supplies"), 0, self.inventory.money)
        ammo = self.ask_numeric(self.get_entity("ammunition"), 0, self.inventory.money)
        clothing = self.ask_numeric(self.get_entity("armour"), 0, self.inventory.money)
        misc = self.ask_numeric(self.get_entity("medicine"), 0, self.inventory.money)
        total_spend = food + ammo + clothing + misc
        if self.inventory.money < total_spend:
            self.output = self.DATA["shop"]["error"]
            return self.on_shop
        self.inventory.spend(total_spend)
        self.inventory.supplies.add(0.66 * food)
        self.inventory.ammunition.add(0.66 * ammo * 50)
        self.inventory.armour.add(0.66 * clothing)
        self.inventory.medicine.add(0.66 * misc)
        self.tracker.subtract_mileage(45)

    def on_heal(self):
        if self.turn.illness or self.turn.injured:
            self.inventory.spend(20)
            if self.inventory.money < 0:
                self.output = self.DATA["heal"]["error"]
                if self.turn.illness:
                    self.output = self.DATA["heal"]["die"] + self.get_entity("passive_damage")
                elif self.turn.injured:
                    self.output = self.DATA["heal"]["die"] + self.get_entity("attack_damage")
                self.on_lose()
            else:
                self.output = self.DATA["heal"]["conclusion"]
                self.turn.illness = False
                self.turn.injured = False

    def on_turn(self):
        self.output = self.calendar.pretty_date()
        self.inventory.normalize_negative_values()

        # Resolve health issues from the previous turn
        self.on_heal()

        # Show inventory status and mileage
        self.inventory.print_warnings()
        self.tracker.print_mileage()

        # Ask for turn options
        self.inventory.print_inventory()
        turn_response = self.ask_numeric(self.DATA["turn"]["intro"], 1, 3)
        if turn_response == 1:
            self.on_shop()
        elif turn_response == 2:
            self.on_explore()

        # Eating
        if self.inventory.supplies.value < 13:
            self.output = self.DATA["turn"]["die"]
            self.on_lose()
            return

        self.on_maintenance()

        # Advance mileage now, events may subtract from overall
        # progress for each turn
        self.tracker.random_advance(self.inventory.fuel)

        # Rider attack
        if self.chance_encounter_seed:
            self.on_chance_encounter()

        # Random per turn events
        self.on_random_event()

        # Mountain events
        self.on_difficulty_modifier()

        # Move to next turn
        self.calendar.advance_date()

        # turns

    def on_difficulty_damage(self):
        self.output = self.DATA["difficulty_damage"]["intro"]
        self.inventory.supplies.subtract(25)
        self.inventory.medicine.subtract(10)
        self.inventory.ammunition.subtract(300)
        self.tracker.subtract_mileage(30 + (40 * random()))
        if self.inventory.armour.value < (18 + (2 * random())):
            self.on_damage()

    def on_random_event(self):
        event = choice(self.random_events)
        event()

    # random events
    def rain(self):
        if self.tracker.difficulty_triggered():
            self.output = self.RANDOM_EVENTS["weather"]["rain"]["intro"]
            self.inventory.supplies.subtract(10)
            self.inventory.ammunition.subtract(500)
            self.inventory.medicine.subtract(15)
            self.tracker.subtract_mileage((10 * random()) + 5)
            self.output = self.RANDOM_EVENTS["weather"]["conclusion"]

    def storm(self):
        self.output = self.RANDOM_EVENTS["weather"]["storm"]["intro"]
        self.tracker.subtract_mileage(5 + (10 * random()))
        self.inventory.ammunition.subtract(200)
        self.inventory.medicine.subtract(4 + (3 * random()))

    def cold(self):
        self.output = self.RANDOM_EVENTS["weather"]["cold"]["intro"]
        insufficient_clothing = False
        if self.inventory.armour.value < (22 + (4 * random())):
            self.output = self.RANDOM_EVENTS["weather"]["cold"]["error"]
        insufficient_clothing = True
        self.output = self.RANDOM_EVENTS["weather"]["cold"]["conclusion"]
        if insufficient_clothing:
            self.on_damage()

    def enemy_attack(self):
        self.output = self.RANDOM_EVENTS["injury"]["attack"]["intro"]
        response, entry_time = self.ask_with_timeout()
        self.inventory.ammunition.subtract(20 * entry_time)
        if self.inventory.ammunition.value <= 0:
            self.output = self.RANDOM_EVENTS["injury"]["attack"]["error"]
            self.inventory.spend(self.inventory.money * 0.66)
        elif entry_time <= 1:
            self.output = self.RANDOM_EVENTS["injury"]["attack"]["conclusion"]
        else:
            self.output = self.RANDOM_EVENTS["injury"]["attack"]["damage"]
            self.turn.injured = True
            self.inventory.medicine.subtract(5)
            self.inventory.fuel.subtract(20)

    def get_poisoned(self):
        self.output = self.RANDOM_EVENTS["injury"]["poison"]["intro"]
        self.inventory.ammunition.subtract(10)
        self.inventory.medicine.subtract(5)
        if self.inventory.medicine.value <= 0:
            self.output = "YOU DIE OF SNAKEBITE SINCE YOU HAVE NO MEDICINE"
        self.on_lose()
        self.output = self.RANDOM_EVENTS["injury"]["poison"]["conclusion"]

    def animal_attack(self):
        self.output = self.RANDOM_EVENTS["injury"]["animal"]["intro"]
        response, entry_time = self.ask_with_timeout()
        if self.inventory.ammunition.value < 40:
            self.output = self.RANDOM_EVENTS["injury"]["animal"]["damage"]
        self.turn.injured = True
        if entry_time <= 2:
            self.output = self.RANDOM_EVENTS["injury"]["animal"]["conclusion"]
        else:
            self.output = self.RANDOM_EVENTS["injury"]["animal"]["error"]
        self.inventory.ammunition.subtract(20 * entry_time)
        self.inventory.armour.subtract(4 * entry_time)
        self.inventory.supplies.subtract(8 * entry_time)

    def shelter_damage(self):
        self.output = self.RANDOM_EVENTS["travel"]["shelter_damage"]["intro"]
        self.tracker.subtract_mileage(15 + 5 * random())
        self.inventory.medicine.subtract(8)
        self.output = self.RANDOM_EVENTS["travel"]["shelter_damage"]["conclusion"]

    def vehicle_damage(self):
        self.output = self.RANDOM_EVENTS["travel"]["vehicle_damage"]["intro"]
        self.tracker.subtract_mileage(25)
        self.inventory.fuel.subtract(20)
        self.output = self.RANDOM_EVENTS["travel"]["vehicle_damage"]["conclusion"]

    def fuel_damage(self):
        self.output = self.RANDOM_EVENTS["travel"]["fuel_damage"]["intro"]
        self.tracker.subtract_mileage(17)
        self.output = self.RANDOM_EVENTS["travel"]["fuel_damage"]["conclusion"]

    def lose_companion(self):
        self.output = self.RANDOM_EVENTS["travel"]["companion_lose"]["intro"]
        self.tracker.subtract_mileage(10)
        self.output = self.RANDOM_EVENTS["travel"]["companion_lose"]["conclusion"]

    def supply_damage(self):
        self.output = self.RANDOM_EVENTS["travel"]["supply_damage"]["intro"]
        self.tracker.subtract_mileage((10 * random()) + 2)
        self.output = self.RANDOM_EVENTS["travel"]["supply_damage"]["conclusion"]

    def shelter_fire(self):
        self.output = self.RANDOM_EVENTS["travel"]["shelter_fire"]["intro"]
        self.inventory.supplies.subtract(40)
        self.inventory.ammunition.subtract(400)
        self.inventory.medicine.subtract((random() * 8) + 3)
        self.tracker.subtract_mileage(15)
        self.output = self.RANDOM_EVENTS["travel"]["shelter_fire"]["conclusion"]

    def heavy_fog(self):
        self.output = self.RANDOM_EVENTS["weather"]["fog"]["intro"]
        self.tracker.subtract_mileage(10 + (5 * random()))
        self.output = self.RANDOM_EVENTS["weather"]["fog"]["conclusion"]

    def bad_terrain(self):
        self.output = self.RANDOM_EVENTS["travel"]["bad_terrain"]["intro"]
        self.inventory.supplies.subtract(30)
        self.inventory.armour.subtract(20)
        self.tracker.subtract_mileage(20 + (20 * random()))
        self.output = self.RANDOM_EVENTS["travel"]["bad_terrain"]["conclusion"]

    def find_supplies(self):
        self.output = self.RANDOM_EVENTS["travel"]["find_supplies"]["intro"]
        self.inventory.supplies.add(14)
        self.output = self.RANDOM_EVENTS["travel"]["find_supplies"]["conclusion"]

    def companion_injury(self):
        self.output = self.RANDOM_EVENTS["injury"]["companion"]["intro"]
        self.tracker.subtract_mileage(5 + 4 * random())
        self.inventory.medicine.subtract(2 + 3 * random())
        self.output = self.RANDOM_EVENTS["injury"]["companion"][
            "conclusion"]

    def illness(self):
        self.output = self.RANDOM_EVENTS["injury"]["illness"]["intro"]
        if self.turn.eating_poorly():
            self.on_damage()
        elif self.turn.eating_moderately() and random() > 0.25:
            self.on_damage()
        elif self.turn.eating_well() and random() < 0.5:
            self.on_damage()
        self.output = self.RANDOM_EVENTS["injury"]["illness"]["intro"]

    # engine
    def manual_fix_parse(self, text):
        # replace vars
        text = text.replace("{inv.money}",
                            str(self.inventory.money))
        text = text.replace("{inv.fuel}",
                            str(self.inventory.fuel.value))
        text = text.replace("{inv.supplies}",
                            str(self.inventory.supplies.value))
        text = text.replace("{inv.medicine}",
                            str(self.inventory.medicine.value))
        text = text.replace("{inv.ammunition}",
                            str(self.inventory.ammunition.value))
        text = text.replace("{inv.armour}",
                            str(self.inventory.armour.value))
        text = text.replace("{journey.distance}",
                            str(self.tracker.total_distance))
        return text + "\n"

    def populate_inventory(self):
        self.inventory = Inventory()
        vehicle_spend = self.ask_numeric(
            self.DATA["inventory"]["intro"] +
            self.TERMINOLOGY["fuel"][0], 200, 300)
        self.inventory.spend(vehicle_spend)
        food_spend = self.ask_numeric(
            self.DATA["inventory"]["intro"] +
            self.TERMINOLOGY["supplies"][0], 0)
        self.inventory.spend(food_spend)
        ammunition_spend = self.ask_numeric(
            self.DATA["inventory"]["intro"] +
            self.TERMINOLOGY["ammunition"][0], 0)
        self.inventory.spend(ammunition_spend)
        clothing_spend = self.ask_numeric(
            self.DATA["inventory"]["intro"] +
            self.TERMINOLOGY["armour"][0], 0)
        self.inventory.spend(clothing_spend)
        misc_spend = self.ask_numeric(
            self.DATA["inventory"]["intro"] +
            self.TERMINOLOGY["medicine"][0], 0)
        self.inventory.spend(misc_spend)

        if self.inventory.money < 0:
            self.output = self.DATA["inventory"]["error"]
            return self.populate_inventory()

        self.inventory.fuel.value = vehicle_spend
        self.inventory.supplies.value = food_spend
        self.inventory.ammunition.value = 50 * ammunition_spend
        self.inventory.armour.value = clothing_spend
        self.inventory.medicine.value = misc_spend

        self.output = self.DATA["inventory"]["conclusion"]

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
        else:
            self.register_event(self.shelter_damage)
            self.register_event(self.shelter_fire)
            self.register_event(self.lose_companion)
            self.register_event(self.supply_damage)
            self.register_event(self.fuel_damage)
            self.register_event(self.vehicle_damage)
            self.register_event(self.heavy_fog)
            self.register_event(self.bad_terrain)
            self.register_event(self.find_supplies)
            self.register_event(self.companion_injury)
            self.register_event(self.illness)
            self.register_event(self.rain)
            self.register_event(self.animal_attack)
            self.register_event(self.get_poisoned)
            self.register_event(self.enemy_attack)
            self.register_event(self.cold)
            self.register_event(self.storm)

    def _run(self):
        self.playing = True
        if self.ask_yes_no("Do you need instructions?"):
            self.intro()
        self.populate_inventory()
        self.register_events()

        while not self.calendar.is_final_turn() and not self.tracker.completed():
            self.on_turn()
        self.on_game_over()
        self.playing = False

    def parse_command(self, utterance):
        # parse intent
        intent = self.calc_intents(utterance)
        intent_name = intent.get("name", "unknown")
        if intent_name in self.intents:
            self.intents[intent_name]()
        else:
            # fallback
            self.submit_command(utterance)
        return self.output


if __name__ == "__main__":
    game = Oregon75Engine()
    game.play()
