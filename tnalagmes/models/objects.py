#!/usr/bin/python
from datetime import timedelta
from datetime import datetime
import random
from tnalagmes import TNaLaGmesConstruct
from math import ceil


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

    # standard python functionality, implementing date and turn tracking for our calendar
    def __init__(self, total_turns=20, start_date=None, turn_delta=0):
        TNaLaGmesConstruct.__init__(self, "calendar")  # pass a string with object_type if desired
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

    @property
    def week_of_month(self):
        # https://en.wikipedia.org/wiki/ISO_week_date#Weeks_per_month
        first_day = self.date.replace(day=1)

        day_of_month = self.date.day

        # adjust for sundays
        if (first_day.weekday() == 6):
            adjusted_dom = (1 + first_day.weekday()) / 7
        else:
            adjusted_dom = day_of_month + first_day.weekday()

        # days may belong to a month but their week may belong to another one
        # weeks belong to a month if its thursday falls on it
        if (first_day.weekday() > 3):
            return int(ceil(adjusted_dom / 7.0)) - 1
        else:
            return int(ceil(adjusted_dom / 7.0))

    # in here register the word triggers
    # im only using keyword rules instead of sample phrases
    # literal strings are used as keywords
    # if available on locale folder vocabulary is expanded
    def register_core_intents(self):
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
                                     required=["turns", "total"],
                                     optionals=["question"],
                                     handler=self.handle_turns_max)
        self.register_keyword_intent("turns_past",
                                     required=["turns", "past"],
                                     optionals=["question"],
                                     handler=self.handle_turns_past)
        self.register_keyword_intent("turns_current",
                                     required=["turns", "current"],
                                     optionals=["question"],
                                     handler=self.handle_turns_current)
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
        self.register_keyword_intent("ask_date",
                                     required=["date"],
                                     optionals=["question"],
                                     handler=self.handle_date)

    # handlers for each natural language questions
    def handle_date(self, intent):
        return self.pretty_date

    def handle_week(self, intent):
        # TODO util to pronounce cardinals
        return "it is the " + str(self.week_of_month) + " week of the month"

    def handle_weekday(self, intent):
        return self.weekday

    def handle_month(self, intent):
        return str(self.date.month)

    def handle_day(self, intent):
        return str(self.date.day)

    def handle_year(self, intent):
        return "it is the year " + str(self.date.year)

    def handle_days_per_turn(self, intent):
        return str(self._turn_delta) + " days per turn"

    def handle_turns_left(self, intent):
        return "you have " + str(self.max_turns - self.turns) + " left"

    def handle_turns_max(self, intent):
        return "maximum number of turns is " + str(self.max_turns)

    def handle_turns_current(self, intent):
        return "currently in turn" + str(self.turns)

    def handle_turns_past(self, intent):
        return str(self.turns - 1) + " passed"

    def handle_next_turn(self, intent):
        self.advance_date()
        return "now in turn" + str(self.turns)

    def handle_advance(self, intent):
        self.advance_date()
        return "advanced date by " + str(self._turn_delta) + " days"

    def handle_rollback(self, intent):
        number = self.extract_number(intent["utterance"])
        self.rollback_date(number)
        return "rolled back date by " + str(number) + " days"

    def handle_speed_decrease(self, intent):
        number = self.extract_number(intent["utterance"])
        number = number or 1
        self.change_speed(self._turn_delta - number)
        return "decreased speed by " + str(number) + " days"

    def handle_speed_increase(self, intent):
        number = self.extract_number(intent["utterance"])
        number = number or 1
        self.change_speed(self._turn_delta - number)
        return "increased speed by " + str(number) + " days"


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


if __name__ == "__main__":
    construct = Calendar()
    print(construct.parse_command("current date"))
    print(construct.parse_command("what day"))
    print(construct.parse_command("what month"))
    print(construct.parse_command("what weekday"))
    print(construct.parse_command("total turns"))
