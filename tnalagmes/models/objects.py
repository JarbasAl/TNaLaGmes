#!/usr/bin/python
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
    "current difficulty
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

    def register_core_intents(self):
        """
            "total distance"
            "current mileage"
            "add mileage"
            "subtract mileage"
            "are you completed?"
            "yes"
            "no"
        """
        self.register_keyword_intent("total_distance",
                                     required=["total", "distance"],
                                     optionals=["question"],
                                     handler=self.handle_total_distance)
        self.register_keyword_intent("current_mileage",
                                     required=["mileage"],
                                     optionals=["question", "current"],
                                     handler=self.handle_mileage)
        self.register_keyword_intent("sub_mileage",
                                     required=["mileage", "subtract"],
                                     optionals=["question"],
                                     handler=self.handle_sub_mileage)
        self.register_keyword_intent("add_mileage",
                                     required=["mileage", "add"],
                                     optionals=["question"],
                                     handler=self.handle_add_mileage)
        self.register_keyword_intent("completed",
                                     required=["finished", "question"],
                                     optionals=["you"],
                                     handler=self.handle_completed)

    def handle_completed(self, intent=None):
        return "yes" if self.completed else "no"

    def handle_add_mileage(self, intent=None):
        amount = self.extract_number(intent["utterance"])
        self.add_mileage(amount)
        return "mileage increased by " + str(amount)

    def handle_sub_mileage(self, intent=None):
        amount = self.extract_number(intent["utterance"])
        self.subtract_mileage(amount)
        return "mileage diminished by " + str(amount)

    def handle_mileage(self, intent=None):
        return str(self.mileage)

    def handle_total_distance(self, intent=None):
        return str(self.total_distance)

    def random_advance(self, seed=150):
        # original logic from oregon trail
        self.last_advance = int(200 + (seed - 220) / 5 + 10 * random.random())
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

    def __init__(self, total_turns=20, start_date=None, turn_delta=0):
        TNaLaGmesConstruct.__init__(self, "calendar")
        self._date = start_date or datetime.now()
        self.days_per_turn = turn_delta
        self._turn_delta = timedelta(days=self.days_per_turn) if self.days_per_turn else None
        self._turn_count = 1
        self._max_turns = total_turns

    def register_core_intents(self):
        """
        Calendar Object

        "What day/date/week/weekday/month/year is it?"

        "next turn"
        "how many turns left"
        "how many turns passed"
        "how many days per turn"
        "maximum number of turns"

        "increase speed"
        "decrease speed"
        "rollback X days/months/weeks/years"
        "advance X days/months/weeks/years"


        """
        return


        self.register_keyword_intent("advance",
                                     required=["date", "advance"],
                                     optionals=[],
                                     handler=self.handle_advance)
        self.register_keyword_intent("rollback",
                                     required=["rollback", "date"],
                                     optionals=[],
                                     handler=self.handle_rollback)
        self.register_keyword_intent("speed_decrease",
                                     required=["decrease", "speed"],
                                     optionals=[],
                                     handler=self.handle_speed_decrease)
        self.register_keyword_intent("speed_increase",
                                     required=["increase", "speed"],
                                     optionals=[],
                                     handler=self.handle_speed_increase)
        self.register_keyword_intent("days_per_turn",
                                     required=["turns", "day"],
                                     optionals=["question"],
                                     handler=self.handle_days_per_turn)
        self.register_keyword_intent("turns_max",
                                     required=["turns", "maximum"],
                                     optionals=["question"],
                                     handler=self.handle_turns_left)
        self.register_keyword_intent("turns_past",
                                     required=["turns", "past"],
                                     optionals=["question"],
                                     handler=self.handle_turns_past)
        self.register_keyword_intent("turns_left",
                                     required=["turns", "remaining"],
                                     optionals=["question"],
                                     handler=self.handle_turns_left)
        self.register_keyword_intent("next_turn",
                                     required=["next", "turn"],
                                     optionals=[],
                                     handler=self.handle_next_turn)
        self.register_keyword_intent("ask_day",
                                     required=["day"],
                                     optionals=["question"],
                                     handler=self.handle_day)
        self.register_keyword_intent("ask_week",
                                     required=["week"],
                                     optionals=["question"],
                                     handler=self.handle_week)
        self.register_keyword_intent("ask_weekday",
                                     required=["weekday"],
                                     optionals=["question"],
                                     handler=self.handle_weekday)
        self.register_keyword_intent("ask_month",
                                     required=["month"],
                                     optionals=["question"],
                                     handler=self.handle_month)
        self.register_keyword_intent("ask_year",
                                     required=["year"],
                                     optionals=["question"],
                                     handler=self.handle_year)

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
    def weekday(self):
        day = self._date.weekday()
        if day == 0:
            return "Monday"
        elif day == 1:
            return "Tuesday"
        elif day == 2:
            return "Wednesday"
        elif day == 3:
            return "Thursday"
        elif day == 4:
            return "Friday"
        elif day == 5:
            return "Saturday"
        elif day == 6:
            return "Sunday"
        return "What kind of calendar is this? "

    @property
    def pretty_date(self):
        return self.weekday + " " + self._date.strftime('%d, %b %Y')

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
    how much are you worth
    """
    def __init__(self, name="thing", description="a thing", item_type="object"):
        self._value = 0
        self.name = name
        self.description = description
        self.item_type = item_type
        TNaLaGmesConstruct.__init__(self, name)


    def register_core_intents(self):
        "" """
            what are you
            what can you do
            how much are you worth
        """
        return


        self.register_keyword_intent("_name",
                                     required="_name",
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)
        self.register_keyword_intent("describe",
                                     required=self.name,
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("value",
                                     required=["worth"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)
        self.register_keyword_intent("abilities",
                                     required=["abilities"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)

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
    """
    def __init__(self, start_money=700):
        self.start_money = start_money
        self._money = start_money
        self.items = []
        TNaLaGmesConstruct.__init__(self, "inventory")

    def register_core_intents(self):
        "" """
             what do you have
            how much money do you have
            how much are you worth
        """
        return

        self.register_keyword_intent("content",
                                     required="content",
                                     optionals=["question", "you"],
                                     handler=self.handle_total_distance)

        self.register_keyword_intent("money",
                                     required=["value"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)
        self.register_keyword_intent("value",
                                     required=["worth"],
                                     optionals=["question", "you"],
                                     handler=self.handle_mileage)

    @property
    def money(self):
        return self._money

    def spend(self, cost):
        self._money -= int(cost)

    def print_warnings(self):
        pass

    def print_inventory(self):
        pass

