import random
from tnalagmes.data.oregon_trail_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from tnalagmes.engines import TNaLaGmesEngine, Event
from tnalagmes.engines.oregon import SimpleInventory, TurnState


class Oregon75Engine(TNaLaGmesEngine):
    """ so called because logic is ported from 1975 basic version of oregon trail"""
    # https://www.filfre.net/misc/oregon1975.bas

    TERMINOLOGY = TERMINOLOGY
    DATA = GAME_EVENTS
    RANDOM_EVENTS = RANDOM_EVENTS

    name = "Oregon75Engine"

    def __init__(self, from_json=False):
        TNaLaGmesEngine.__init__(self, from_json)
        self.turn = TurnState()
        self.inventory = SimpleInventory()

        if from_json:
            self.import_game_data()

    @property
    def talking_objects(self):
        return [self.inventory, self.turn, self.calendar, self.tracker]

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
        self.output = self.DATA.get("win", {}).get("intro", "")
        # self.output = "AFTER " + str(self.objective.total_distance) + " LONG MILES---HOORAY!!!!!")
        self.calendar.rollback_date(int(self.tracker.last_turn_fraction * self.calendar.days_per_turn))
        self.output = self.calendar.pretty_date
        self.output = self.inventory.pretty_inventory
        self.output = self.DATA.get("win", {}).get("conclusion", "")

    def on_lose(self):
        self.output = self.DATA.get("lose", {}).get("intro", "")
        # Responses to the first two questions are ignored intentionally
        response = True
        for question in self.DATA.get("lose", "").get("yes_no_questions", []):
            response = self.ask_yes_no(question)
        if not response:
            self.output = self.DATA.get("lose", {}).get("error", "")
        self.output = self.DATA.get("lose", {}).get("conclusion", "")

    def on_maintenance(self):
        response = self.ask_numeric(self.DATA.get("maintenance", {}).get("intro", ""), 1, 3)
        food_eaten = 8 + 5 * response
        if self.inventory.supplies.value < food_eaten:
            self.output = self.DATA.get("maintenance", {}).get("error", "")
            return self.on_maintenance()
        self.turn.eating_state = response
        self.inventory.supplies.subtract(food_eaten)

        self.output = self.DATA.get("maintenance", {}).get("conclusion", "")

    def on_damage(self):
        self.output = self.DATA.get("damage", {}).get("intro", "")
        if (100 * random.random()) < (10 + (35 * self.turn.eating_state - 1)):
            self.output = self.DATA.get("damage", {}).get("mild", "")
            self.tracker.subtract_mileage(5)
            self.inventory.medicine.subtract(2)
        elif (100 * random.random()) < (100 - (40 / (4 ** (self.turn.eating_state - 1)))):
            self.output = self.DATA.get("damage", {}).get("high", "")
            self.tracker.subtract_mileage(5)
            self.inventory.medicine.subtract(5)
        if self.inventory.medicine.value < 0:
            if self.turn.injured:
                self.output = self.DATA.get("damage", {}).get("error", "") + "INJURIES"
            else:
                self.output = self.DATA.get("damage", {}).get("error", "") + "PNEUMONIA"
            self.on_game_over()
        return

    def on_chance_encounter(self):
        peaceful = True
        self.output = self.get_entity("enemy") + self.DATA.get("enemy_encounter", {}).get("intro", "")
        if random.random() < 0.8:
            self.output = self.DATA.get("enemy_encounter", {}).get("peaceful_intro", "")
        else:
            self.output = self.DATA.get("enemy_encounter", {}).get("hostile_intro", "")
            peaceful = False

        # riders may randomly switch sides
        if random.random() <= 0.2:
            peaceful = not peaceful

        response = self.ask_numeric(self.DATA.get("enemy_encounter", {}).get("number_questions", "")[0], 1, 4)
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
                    self.output = self.DATA.get("enemy_encounter", {}).get("high_score", "")
                elif entry_time <= 4:
                    self.output = self.DATA.get("enemy_encounter", {}).get("low_score", "")
                else:
                    self.output = self.DATA.get("enemy_encounter", {}).get("damage", "")
                    self.turn.injured = True
            elif response == 3:  # continue
                if random.random() <= 0.8:
                    self.inventory.medicine.subtract(15)
                    self.inventory.ammunition.subtract(150)
                else:
                    self.output = self.DATA.get("enemy_encounter", {}).get("enemy_run", "")
                    return
            else:  # circle wagons
                response, entry_time = self.ask_with_timeout()
                self.inventory.ammunition.subtract((entry_time * 30) - 80)
                self.tracker.subtract_mileage(25)
                if entry_time <= 1:
                    self.output = self.DATA.get("enemy_encounter", {}).get("high_score", "")
                elif entry_time <= 4:
                    self.output = self.DATA.get("enemy_encounter", {}).get("low_score", "")
                else:
                    self.output = self.DATA.get("enemy_encounter", {}).get("damage", "")
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
            self.output = self.get_entity("enemy") + self.DATA.get("enemy_encounter", {}).get("peaceful_conclusion", "")
        else:
            self.output = self.get_entity("enemy") + self.DATA.get("enemy_encounter", {}).get("hostile_conclusion", "")
            if self.inventory.ammunition.value < 0:
                self.output = self.DATA.get("enemy_encounter", {}).get("die", "") + self.get_entity("enemy")
                self.on_game_over()

    def on_easy_difficulty(self):
        # medium difficulty
        if (random.random() * 10) <= (
                9 - ((self.tracker.mileage / 100 - 15) ** 2 + 72) / ((self.tracker.mileage / 100 - 15) ** 2 + 12)):
            self.output = self.DATA.get("easy_difficulty", {}).get("intro", "")
            if random.random() <= 0.1:
                self.output = self.DATA.get("easy_difficulty", {}).get("events", "")[0]
                self.tracker.subtract_mileage(60)
            elif random.random() <= 0.11:
                self.output = self.DATA.get("easy_difficulty", {}).get("events", "")[1]
                self.tracker.subtract_mileage(20 + (30 * random.random()))
                self.inventory.medicine.subtract(5)
                self.inventory.ammunition.subtract(200)
            else:
                self.output = self.DATA.get("easy_difficulty", {}).get("events", "")[2]
                self.tracker.subtract_mileage(45 + (random.random() // 0.02))

        # First pass evaluated at 950 miles (reached_mountains)
        if not self.tracker.medium_difficulty:
            self.tracker.medium_difficulty = True

    def on_medium_difficulty(self):
        # First pass evaluated at 950 miles (reached_mountains)
        if random.random() < 0.8:
            self.on_difficulty_damage()
        else:
            self.output = self.DATA.get("medium_difficulty", {}).get("conclusion", "")
            self.tracker.medium_difficulty = False
        if self.tracker.mileage >= 1700 and not self.tracker.hard_difficulty:
            self.tracker.hard_difficulty = True

    def on_hard_difficulty(self):
        # Second pass (blue mountains) at 1700 miles
        if random.random() < 0.7:
            self.on_difficulty_damage()

    def on_explore(self):
        if self.inventory.ammunition.value < 40:
            self.output = self.DATA.get("explore", {}).get("error", "")
            return
        self.tracker.subtract_mileage(45)

        response, entry_time = self.ask_with_timeout()
        # debug logging? print "User typed", response, "after", entry_time, "seconds"

        if entry_time < 1.0:
            self.output = self.DATA.get("explore", {}).get("events", "")[0]
            self.inventory.supplies.add(52 + random.random() * 6)
            self.inventory.ammunition.subtract(10 - random.random() * 4)
        elif (100 * random.random()) < (13 * entry_time):
            self.output = self.DATA.get("explore", {}).get("events", "")[1]
        else:
            self.output = self.DATA.get("explore", {}).get("events", "")[2]
            self.inventory.supplies.add(48 - 2 * entry_time)
            self.inventory.ammunition.subtract(10 - 3 * entry_time)

    def on_shop(self):
        self.output = self.DATA.get("shop", {}).get("intro", "")
        food = self.ask_numeric(self.get_entity("supplies"), 0, self.inventory.currency)
        ammo = self.ask_numeric(self.get_entity("ammunition"), 0, self.inventory.currency)
        clothing = self.ask_numeric(self.get_entity("armour"), 0, self.inventory.currency)
        misc = self.ask_numeric(self.get_entity("medicine"), 0, self.inventory.currency)
        total_spend = food + ammo + clothing + misc
        if self.inventory.currency < total_spend:
            self.output = self.DATA.get("shop", {}).get("error", "")
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
            if self.inventory.currency < 0:
                self.output = self.DATA.get("heal", {}).get("error", "")
                if self.turn.illness:
                    self.output = self.DATA.get("heal", {}).get("die", "") + self.get_entity("passive_damage")
                elif self.turn.injured:
                    self.output = self.DATA.get("heal", {}).get("die", "") + self.get_entity("attack_damage")
                return False
            else:
                self.output = self.DATA.get("heal", {}).get("conclusion", "")
                self.turn.illness = False
                self.turn.injured = False

        return True

    def on_turn(self):
        if self.tracker.completed:
            return
        self.output = self.calendar.pretty_date
        self.inventory.normalize_negative_values()

        # Resolve health issues from the previous turn
        if not self.on_heal():
            self.on_game_over()
            return

        # Show inventory status and mileage
        self.output = self.inventory.warnings
        self.tracker.print_mileage()

        # Ask for turn options
        self.output = self.inventory.pretty_inventory
        turn_response = self.ask_numeric(self.DATA.get("turn", {}).get("intro", ""), 1, 3)
        if turn_response == 1:
            self.on_shop()
        elif turn_response == 2:
            self.on_explore()

        # Eating
        if self.inventory.supplies.value < 13:
            self.output = self.DATA.get("turn", {}).get("die", "")
            self.on_game_over()
            return

        self.on_maintenance()

        # Advance mileage now, events may subtract from overall
        # progress for each turn
        self.tracker.random_advance(self.inventory.fuel.value)

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
        self.output = self.DATA.get("difficulty_damage", {}).get("intro", "")
        self.inventory.supplies.subtract(25)
        self.inventory.medicine.subtract(10)
        self.inventory.ammunition.subtract(300)
        self.tracker.subtract_mileage(30 + (40 * random.random()))
        if self.inventory.armour.value < (18 + (2 * random.random())):
            self.on_damage()

    # random events
    def rain(self):
        if self.tracker.difficulty_triggered():
            self.output = self.RANDOM_EVENTS.get("rain", {}).get("intro", "")
            self.inventory.supplies.subtract(10)
            self.inventory.ammunition.subtract(500)
            self.inventory.medicine.subtract(15)
            self.tracker.subtract_mileage((10 * random.random()) + 5)
            self.output = self.RANDOM_EVENTS.get("conclusion", "")

    def storm(self):
        self.output = self.RANDOM_EVENTS.get("storm", {}).get("intro")
        self.tracker.subtract_mileage(5 + (10 * random.random()))
        self.inventory.ammunition.subtract(200)
        self.inventory.medicine.subtract(4 + (3 * random.random()))

    def cold(self):
        self.output = self.RANDOM_EVENTS.get("cold", {}).get("intro", "")
        insufficient_clothing = False
        if self.inventory.armour.value < (22 + (4 * random.random())):
            self.output = self.RANDOM_EVENTS.get("cold", {}).get("error", "")
            insufficient_clothing = True
        self.output = self.RANDOM_EVENTS.get("cold", {}).get("conclusion", "")
        if insufficient_clothing:
            self.on_damage()

    def enemy_attack(self):
        self.output = self.RANDOM_EVENTS.get("attack", {}).get("intro", "")
        response, entry_time = self.ask_with_timeout()
        self.inventory.ammunition.subtract(20 * entry_time)
        if self.inventory.ammunition.value <= 0:
            self.output = self.RANDOM_EVENTS.get("attack", {}).get("error", "")
            self.inventory.spend(self.inventory.currency * 0.66)
        elif entry_time <= 1:
            self.output = self.RANDOM_EVENTS.get("attack", {}).get("conclusion", "")
        else:
            self.output = self.RANDOM_EVENTS.get("attack", {}).get("damage", "")
            self.turn.injured = True
            self.inventory.medicine.subtract(5)
            self.inventory.fuel.subtract(20)

    def get_poisoned(self):
        self.output = self.RANDOM_EVENTS.get("poison", {}).get("intro", "")
        self.inventory.ammunition.subtract(10)
        self.inventory.medicine.subtract(5)
        if self.inventory.medicine.value <= 0:
            # TODO use data
            self.output = "YOU DIE OF SNAKEBITE SINCE YOU HAVE NO MEDICINE"
        self.on_game_over()
        self.output = self.RANDOM_EVENTS.get("poison", {}).get("conclusion", "")

    def animal_attack(self):
        self.output = self.RANDOM_EVENTS.get("animal", {}).get("intro", "")
        response, entry_time = self.ask_with_timeout()
        if self.inventory.ammunition.value < 40:
            self.output = self.RANDOM_EVENTS.get("animal", {}).get("damage", "")
        self.turn.injured = True
        if entry_time <= 2:
            self.output = self.RANDOM_EVENTS.get("animal", {}).get("conclusion", "")
        else:
            self.output = self.RANDOM_EVENTS.get("animal", {}).get("error", "")
        self.inventory.ammunition.subtract(20 * entry_time)
        self.inventory.armour.subtract(4 * entry_time)
        self.inventory.supplies.subtract(8 * entry_time)

    def shelter_damage(self):
        self.output = self.RANDOM_EVENTS.get("shelter_damage", {}).get("intro", "")
        self.tracker.subtract_mileage(15 + 5 * random.random())
        self.inventory.medicine.subtract(8)
        self.output = self.RANDOM_EVENTS.get("shelter_damage", {}).get("conclusion", "")

    def vehicle_damage(self):
        self.output = self.RANDOM_EVENTS.get("vehicle_damage", {}).get("intro", "")
        self.tracker.subtract_mileage(25)
        self.inventory.fuel.subtract(20)
        self.output = self.RANDOM_EVENTS.get("vehicle_damage", {}).get("conclusion", "")

    def fuel_damage(self):
        self.output = self.RANDOM_EVENTS.get("fuel_damage", {}).get("intro", "")
        self.tracker.subtract_mileage(17)
        self.output = self.RANDOM_EVENTS.get("fuel_damage", {}).get("conclusion", "")

    def lose_companion(self):
        self.output = self.RANDOM_EVENTS.get("companion_lose", {}).get("intro", "")
        self.tracker.subtract_mileage(10)
        self.output = self.RANDOM_EVENTS.get("companion_lose", {}).get("conclusion", "")

    def supply_damage(self):
        self.output = self.RANDOM_EVENTS.get("supply_damage", {}).get("intro", "")
        self.tracker.subtract_mileage((10 * random.random()) + 2)
        self.output = self.RANDOM_EVENTS.get("supply_damage", {}).get("conclusion", "")

    def shelter_fire(self):
        self.output = self.RANDOM_EVENTS.get("shelter_fire", {}).get("intro", "")
        self.inventory.supplies.subtract(40)
        self.inventory.ammunition.subtract(400)
        self.inventory.medicine.subtract((random.random() * 8) + 3)
        self.tracker.subtract_mileage(15)
        self.output = self.RANDOM_EVENTS.get("shelter_fire", {}).get("conclusion", "")

    def heavy_fog(self):
        self.output = self.RANDOM_EVENTS.get("fog", {}).get("intro", "")
        self.tracker.subtract_mileage(10 + (5 * random.random()))
        self.output = self.RANDOM_EVENTS.get("fog", {}).get("conclusion", "")

    def bad_terrain(self):
        self.output = self.RANDOM_EVENTS.get("bad_terrain", {}).get("intro", "")
        self.inventory.supplies.subtract(30)
        self.inventory.armour.subtract(20)
        self.tracker.subtract_mileage(20 + (20 * random.random()))
        self.output = self.RANDOM_EVENTS.get("bad_terrain", {}).get("conclusion", "")

    def find_supplies(self):
        self.output = self.RANDOM_EVENTS.get("find_supplies", {}).get("intro", "")
        self.inventory.supplies.add(14)
        self.output = self.RANDOM_EVENTS.get("find_supplies", {}).get("conclusion", "")

    def companion_injury(self):
        self.output = self.RANDOM_EVENTS.get("companion", {}).get("intro", "")
        self.tracker.subtract_mileage(5 + 4 * random.random())
        self.inventory.medicine.subtract(2 + 3 * random.random())
        self.output = self.RANDOM_EVENTS.get("companion", {}).get("conclusion", "")

    def illness(self):
        self.output = self.RANDOM_EVENTS.get("illness", {}).get("intro", "")
        if self.turn.eating_poorly():
            self.on_damage()
        elif self.turn.eating_moderately() and random.random() > 0.25:
            self.on_damage()
        elif self.turn.eating_well() and random.random() < 0.5:
            self.on_damage()
        self.output = self.RANDOM_EVENTS.get("illness", {}).get("conclusion", "")

    # engine
    def handle_yes(self, intent):
        self.submit_command("yes")
        return ""

    def handle_no(self, intent):
        self.submit_command("no")
        return ""

    def manual_fix_parse(self, text):
        # replace vars
        text = text.replace("{inv.money}",
                            str(self.inventory.currency))
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

    def on_start(self):
        self.running = True
        if self.ask_yes_no("Do you need instructions?"):
            self.intro()
        self.inventory = SimpleInventory()
        vehicle_spend = self.ask_numeric(
            self.DATA.get("inventory", {}).get("intro", "") +
            self.TERMINOLOGY["fuel"][0], 200, 300)
        self.inventory.spend(vehicle_spend)
        food_spend = self.ask_numeric(
            self.DATA.get("inventory", {}).get("intro", "") +
            self.TERMINOLOGY["supplies"][0], 0)
        self.inventory.spend(food_spend)
        ammunition_spend = self.ask_numeric(
            self.DATA.get("inventory", {}).get("intro", "") +
            self.TERMINOLOGY["ammunition"][0], 0)
        self.inventory.spend(ammunition_spend)
        clothing_spend = self.ask_numeric(
            self.DATA.get("inventory", {}).get("intro", "") +
            self.TERMINOLOGY["armour"][0], 0)
        self.inventory.spend(clothing_spend)
        misc_spend = self.ask_numeric(
            self.DATA.get("inventory", {}).get("intro", "") +
            self.TERMINOLOGY["medicine"][0], 0)
        self.inventory.spend(misc_spend)

        if self.inventory.currency < 0:
            self.output = self.DATA.get("inventory", {}).get("error", "")
            return self.on_start()

        self.inventory.fuel.value = vehicle_spend
        self.inventory.supplies.value = food_spend
        self.inventory.ammunition.value = 50 * ammunition_spend
        self.inventory.armour.value = clothing_spend
        self.inventory.medicine.value = misc_spend

        self.output = self.DATA.get("inventory", {}).get("conclusion", "")

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


if __name__ == "__main__":
    game = Oregon75Engine()
    game.run()
