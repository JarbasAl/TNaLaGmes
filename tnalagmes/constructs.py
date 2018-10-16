from time import sleep
import time
import random
from difflib import SequenceMatcher
from tnalagmes.util.time import now_local
from tnalagmes.util.log import LOG
from tnalagmes.util import resolve_resource_file
from pprint import pprint
from tnalagmes.lang.parse_en import *
from tnalagmes.lang.parse_es import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_it import *
from tnalagmes.lang.parse_pt import *
from tnalagmes.lang.parse_sv import *
from os.path import exists
import json


class TNaLaGmesConstruct(object):
    """
    """
    # if input matches these vocabs index will be selected in ask_numeric
    OPTION_VOCS = []

    def __init__(self, object_type="tnalagmes_object", direction=None,
                 interacting_with=None, scene=None, coordinates=None):
        """

        Args:
            object_type: human string for object type identifier
            direction: direction object is facing 0 to 360 , where 0 is north
            interacting_with: where the object will send queries
            scene: where the object is located
        """

        from tnalagmes.intents import TNaLaGmesIntentContainer
        self.intent_parser = TNaLaGmesIntentContainer()
        self.object_type = object_type
        self.register_default_intents()
        self.register_core_intents()
        self.intent_parser.learn()

        self.waiting_for_user = False
        self._output = ""
        self.input = ""

        self.direction = direction
        self.interacting_with = interacting_with
        self.scene = scene
        self._coordinates = coordinates or [0]

    def move_to(self, coordinates):
        """

        Args:
            coordinates:
        """
        self._coordinates = coordinates

    @staticmethod
    def direction_to_int(direction, reference=0):
        """
        match a string into a degree between 0 and 360 where 0 is north and direction if clockwise

        Args:
            direction: string
            reference: reference angle if direction is relative, "increase angle by 2"

        Returns:
            int
        """
        # check resource matches
        if TNaLaGmesConstruct.match_resource(direction,
                                             "up") or TNaLaGmesConstruct.match_resource(
            direction, "north") \
                or TNaLaGmesConstruct.match_resource(direction, "front"):
            return 0
        if TNaLaGmesConstruct.match_resource(direction,
                                             "down") or TNaLaGmesConstruct.match_resource(
            direction, "south") \
                or TNaLaGmesConstruct.match_resource(direction, "back"):
            return 180
        if TNaLaGmesConstruct.match_resource(direction,
                                             "left") or TNaLaGmesConstruct.match_resource(
            direction, "west"):
            return 270
        if TNaLaGmesConstruct.match_resource(direction,
                                             "right") or TNaLaGmesConstruct.match_resource(
            direction, "east"):
            return 90
        if TNaLaGmesConstruct.match_resource(direction, "northeast"):
            return 45
        if TNaLaGmesConstruct.match_resource(direction, "northwest"):
            return 315
        if TNaLaGmesConstruct.match_resource(direction, "southeast"):
            return 135
        if TNaLaGmesConstruct.match_resource(direction, "southwest"):
            return 225

        # parse text
        if direction == "up" or (
                "n" in direction and "w" not in direction and "e" not in direction):
            return 0  # north
        if direction == "down" or (
                "s" in direction and "w" not in direction and "e" not in direction):
            return 180  # south
        if direction == "right" or (
                "e" in direction and "s" not in direction and "n" not in direction):
            return 90  # east
        if direction == "left" or (
                "w" in direction and "s" not in direction and "n" not in direction):
            return 270  # west
        if "n" in direction and "w" in direction:
            return 315  # northwest
        if "s" in direction and "w" in direction:
            return 225  # southwest
        if "n" in direction and "e" in direction:
            return 45  # ne
        if "s" in direction and "e" in direction:
            return 135  # se

        # handle num degrees
        number = TNaLaGmesConstruct.extract_number(direction)
        if number:
            if TNaLaGmesConstruct.match_resource(direction, "radians"):
                # TODO convert number to degrees
                pass
            if TNaLaGmesConstruct.match_resource(direction,
                                                 "angle") or "degrees" in direction or \
                    TNaLaGmesConstruct.match_resource(direction, "radians"):
                # handle "by 2" vs "to 2"
                if "by" in direction:
                    return reference + number
                return number
        return None  # raise exception?

    @staticmethod
    def fuzzy_match(x, against):
        """Perform a 'fuzzy' comparison between two strings.
        Returns:
            float: match percentage -- 1.0 for perfect match,
                   down to 0.0 for no match at all.
        """
        return SequenceMatcher(None, x, against).ratio()

    @staticmethod
    def match_one(query, choices):
        """
            Find best match from a list or dictionary given an input

            Arguments:
                query:   string to test
                choices: list or dictionary of choices

            Returns: tuple with best match, score
        """
        if isinstance(choices, dict):
            _choices = list(choices.keys())
        elif isinstance(choices, list):
            _choices = choices
        else:
            raise ValueError('a list or dict of choices must be provided')

        best = (
            _choices[0], TNaLaGmesConstruct.fuzzy_match(query, _choices[0]))
        for c in _choices[1:]:
            score = TNaLaGmesConstruct.fuzzy_match(query, c)
            if score > best[1]:
                best = (c, score)

        if isinstance(choices, dict):
            return choices[best[0]], best[1]
        else:
            return best

    @staticmethod
    def extract_number(text, short_scale=True, ordinals=False, lang="en-us"):
        """Takes in a string and extracts a number.

        Args:
            text (str): the string to extract a number from
            short_scale (bool): Use "short scale" or "long scale" for large
                numbers -- over a million.  The default is short scale, which
                is now common in most English speaking countries.
                See https://en.wikipedia.org/wiki/Names_of_large_numbers
            ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
            lang (str): the BCP-47 code for the language to use
        Returns:
            (int, float or False): The number extracted or False if the input
                                   text contains no numbers
        """
        lang_lower = str(lang).lower()
        if lang_lower.startswith("en"):
            return extract_number_en(text, short_scale=short_scale,
                                     ordinals=ordinals)
        elif lang_lower.startswith("pt"):
            return extractnumber_pt(text)
        elif lang_lower.startswith("it"):
            return extractnumber_it(text)
        elif lang_lower.startswith("fr"):
            return extractnumber_fr(text)
        elif lang_lower.startswith("sv"):
            return extractnumber_sv(text)
        # elif lang_lower.startswith("de"):
        #    return extractnumber_de(text)
        # TODO: extractnumber_xx for other languages
        return text

    @staticmethod
    def extract_datetime(text, anchor=None, lang="en-us"):
        """
        Extracts date and time information from a sentence.  Parses many of the
        common ways that humans express dates and times, including relative dates
        like "5 days from today", "tomorrow', and "Tuesday".

        Vague terminology are given arbitrary values, like:
            - morning = 8 AM
            - afternoon = 3 PM
            - evening = 7 PM

        If a time isn't supplied or implied, the function defaults to 12 AM

        Args:
            text (str): the text to be interpreted
            anchor (:obj:`datetime`, optional): the date to be used for
                relative dating (for example, what does "tomorrow" mean?).
                Defaults to the current local date/time.
            lang (string): the BCP-47 code for the language to use

        Returns:
            [:obj:`datetime`, :obj:`str`]: 'datetime' is the extracted date
                as a datetime object in the user's local timezone.
                'leftover_string' is the original phrase with all date and time
                related keywords stripped out. See examples for further
                clarification

                Returns 'None' if the input string is empty.

        Examples:

            extract_datetime(
            ... "What is the weather like the day after tomorrow?",
            ... datetime(2017, 06, 30, 00, 00)
            ... )
            [datetime.datetime(2017, 7, 2, 0, 0), 'what is weather like']

            extract_datetime(
            ... "Set up an appointment 2 weeks from Sunday at 5 pm",
            ... datetime(2016, 02, 19, 00, 00)
            ... )
            [datetime.datetime(2016, 3, 6, 17, 0), 'set up appointment']
        """

        lang_lower = str(lang).lower()

        if not anchor:
            anchor = now_local()

        if lang_lower.startswith("en"):
            return extract_datetime_en(text, anchor)
        elif lang_lower.startswith("pt"):
            return extract_datetime_pt(text, anchor)
        elif lang_lower.startswith("it"):
            return extract_datetime_it(text, anchor)
        elif lang_lower.startswith("fr"):
            return extract_datetime_fr(text, anchor)
        elif lang_lower.startswith("sv"):
            return extract_datetime_sv(text, anchor)
        # TODO: extract_datetime for other languages
        return text

    @staticmethod
    def normalize(text, lang="en-us", remove_articles=True):
        """Prepare a string for parsing

        This function prepares the given text for parsing by making
        numbers consistent, getting rid of contractions, etc.
        Args:
            text (str): the string to normalize
            lang (str): the code for the language text is in
            remove_articles (bool): whether to remove articles (like 'a', or
                                    'the'). True by default.
        Returns:
            (str): The normalized string.
        """

        lang_lower = str(lang).lower()
        if lang_lower.startswith("en"):
            return normalize_en(text, remove_articles)
        elif lang_lower.startswith("es"):
            return normalize_es(text, remove_articles)
        elif lang_lower.startswith("pt"):
            return normalize_pt(text, remove_articles)
        elif lang_lower.startswith("it"):
            return normalize_it(text, remove_articles)
        elif lang_lower.startswith("fr"):
            return normalize_fr(text, remove_articles)
        elif lang_lower.startswith("sv"):
            return normalize_sv(text, remove_articles)
        # TODO: Normalization for other languages
        return text

    @staticmethod
    def word_gender(word, input_string="", lang="en-us"):
        '''
        guess gender of word, optionally use raw input text for context
        returns "m" if the word is male, "f" if female, False if unknown
        '''
        if "pt" in lang or "es" in lang:
            # spanish follows same rules
            return get_gender_pt(word, input_string)
        elif "it" in lang:
            return get_gender_it(word, input_string)

        return False

    @property
    def output(self):
        """

        Returns:

        """
        out = self._output
        self._output = ""
        return out

    def manual_fix_parse(self, text):
        """

        Args:
            text:

        Returns:

        """
        # TODO replace vars
        return text

    @output.setter
    def output(self, text=""):
        """

        Args:
            text:

        Returns:

        """
        if isinstance(text, list):
            text = [t.strip() for t in text if t.strip()]
            text = random.choice(text)
        else:
            if text is None or not text.strip():
                return
        # custom substitutions
        text = self.manual_fix_parse(text)

        # check for dialog files
        lines = self.load_resource(text)
        if lines:
            text = random.choice(lines)
        self._output += text + "\n"

    def ask_yes_no(self, prompt):
        """
        ask question and expect yes or no response
        ask in a loop until answer matches "yes" or "no" resource

        Args:
            prompt: question to ask

        Returns:
            True if yes, False if no
        """
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        response = self.normalize(self.input)
        if self.match_resource(response[0], "yes"):
            return True
        if self.match_resource(response[0], "no"):
            return False
        else:
            return self.ask_yes_no(prompt)

    def ask_numeric(self, prompt, lower_bound=None, upper_bound=None):
        """
        asks a question in a loop until a numeric answer is received

        text is matched against self.OPTION_VOCS for synonym translation

        ask again if number does not fit into lower_bound < number < upper_bound

        Args:
            prompt: question to ask
            lower_bound: minimum number
            upper_bound: maximum number

        Returns:
            number
        """
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        text = self.input
        response = None
        for idx, voc in enumerate(self.OPTION_VOCS):
            for v in voc:
                if self.match_resource(text, v):
                    response = idx
                    break
        response = response or self.extract_number(text)
        try:
            value = int(response)
        except ValueError:
            self.output = "impossible!"
            return self.ask_numeric(prompt, lower_bound, upper_bound)
        if lower_bound is not None:
            if value < lower_bound:
                self.output = str(response) + " is too low"
                return self.ask_numeric(prompt, lower_bound, upper_bound)
        if upper_bound is not None:
            if value > upper_bound:
                self.output = str(response) + " is too high"
                return self.ask_numeric(prompt, lower_bound, upper_bound)
        return value

    def ask_with_timeout(self, prompt="say BANG", answer="bang", timeout=7):
        """

        Args:
            prompt:
            answer:
            timeout:

        Returns:

        """
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        response = self.input.lower().strip()
        if response != answer:
            return self.ask_with_timeout(prompt, answer, timeout) + 1
        # TODO measure mic level or type speed
        return response, random.randint(1, 7)

    def register_default_intents(self):
        """

        """
        pass

    def register_core_intents(self):
        """

        """
        pass

    def calc_intents(self, utterance, lang="en-us"):
        """
        raw intent match data

        Args:
            utterance: 
            lang: 

        :return:
        """
        return self.intent_parser.calc_intent(utterance)

    def register_intent(self, name, samples, handler=None):
        """
        register samples based intent (padatious)

        Args:
            name: intent name
            samples: list of sample phrases or resource files, if None becomes [name]
            handler: handle intent and return string response

        :return:
        """
        self.intent_parser.register_intent(name, samples)

    @staticmethod
    def load_resource(name, sep="\n", is_json=False):
        """
       search all paths for a resource file (.voc/.intent/.dialog/.rx)

        :param name: resource filename or path
        :param sep: separate entries at this, default \n
        :param is_json: load as json
        :return:
        """
        path = resolve_resource_file(name)
        if path and exists(path):
            with open(path, "r") as f:
                lines = f.read()
                if is_json:
                    return json.loads(lines)
                return lines.split(sep)
        return None

    @staticmethod
    def match_resource(utterance, resource):
        """
        if utterance matches a resource file (.voc/.intent/.dialog/.rx) return True

        Args:
            utterance: 
            resource: 

        :return:
        """
        lines = TNaLaGmesConstruct.load_resource(resource)
        if lines:
            for l in lines:
                if l.lower().strip() in utterance.lower().strip():
                    return True
        if resource.lower().strip() in utterance.lower().strip():
            return True
        return False

    def register_keyword_intent(self, name, required=None, optionals=None,
                                handler=None, ignore_default_kw=False):
        """

        regster keyword based intent (adapt)

        Args:
            name: 
            required: list of [required keywords] or dict of kw: [synonyms] or if None becomes [name]
            optionals: list of [optional keywords] or dict of kw: [synonyms] or if None becomes [name]
            handler: intent handler, returns string response
            ignore_default_kw: if false do not expand vocabulary

        :return:
        """
        self.intent_parser.register_keyword_intent(name, required, optionals,
                                                   handler, ignore_default_kw)

    def parse_command(self, utterance):
        """ chooses and executes best intent returning result """
        # parse intent
        intents = self.calc_intents(utterance)
        for intent in intents:
            self.output += self.intent_parser.execute_intent(intent)
        return self.output or "?"


if __name__ == "__main__":
    construct = TNaLaGmesConstruct()

    print(construct.parse_command("no"))
    print(construct.parse_command("yes"))
    print(construct.parse_command("what are you"))

    # print(construct.calc_intent("yes"))
    # print(construct.calc_intent("no"))
    # print(construct.calc_intent("what can you do"))

    # read buffer
    # print(construct.output) # empty
    # put something into the buffer
    # construct.output = "hello world"
    # read current buffer
    # print(construct.output)  # hello world
    # print(construct.output) # empty
    # put something into the buffer
    # construct.output = "hello world!"
    # construct.output = "how are you?"
    # read current buffer
    # print(construct.output)  # hello world\nhow are you?   #\n was added
    # print(construct.output)  # empty
