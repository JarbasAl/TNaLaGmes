from padatious import IntentContainer
from tnalagmes.data.template_data import TERMINOLOGY, RANDOM_EVENTS, GAME_EVENTS
from time import sleep
import time
import random
from difflib import SequenceMatcher
from tnalagmes.util.time import now_local
from tnalagmes.util.log import LOG
from pprint import pprint
from tnalagmes.lang.parse_en import *
from tnalagmes.lang.parse_es import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_fr import *
from tnalagmes.lang.parse_it import *
from tnalagmes.lang.parse_pt import *
from tnalagmes.lang.parse_sv import *
from os.path import expanduser, join, exists
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from adapt.context import ContextManagerFrame
from os import makedirs


class TNaLaGmesConstruct(object):
    cache_dir = join(expanduser("~"), "tnalagmes", "intent_cache")
    if not exists(cache_dir):
        makedirs(cache_dir)
    TERMINOLOGY = {}
    DATA = GAME_EVENTS
    RANDOM_EVENTS = {}

    def __init__(self, object_type="tnalagmes_object", adapt=None):
        self.adapt = adapt or IntentDeterminationEngine()
        self.context_manager = ContextManager(self.adapt)
        self.object_type = object_type
        self.container = IntentContainer(self.cache_dir)
        self.intents = {}
        self.register_default_intents()
        self.register_core_intents()
        self.container.train()
        self.waiting_for_user = False
        self._output = ""
        self.input = ""

    def pprint_data(self):
        data = {"random_events": self.RANDOM_EVENTS,
                "terminology": self.TERMINOLOGY,
                "turn_data": self.DATA}
        pprint(data)

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

        best = (_choices[0], TNaLaGmesConstruct.fuzzy_match(query, _choices[0]))
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
        out = self._output
        self._output = ""
        return out

    @classmethod
    def get_entity(cls, text):
        return random.choice(cls.TERMINOLOGY.get(text, [""]))

    def manual_fix_parse(self, text):
        # TODO replace vars
        return text

    @output.setter
    def output(self, text=""):
        if isinstance(text, list):
            text = [t.strip() for t in text if t.strip()]
            text = random.choice(text)
        else:
            if not text.strip():
                return
        self._output += self.manual_fix_parse(text) + "\n"

    def ask_yes_no(self, prompt):
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        response = self.normalize(self.input)
        if response[0] == 'y':
            return True
        if response[0] == 'n':
            return False
        else:
            return self.ask_yes_no(prompt)

    def ask_numeric(self, prompt, lower_bound=None, upper_bound=None):
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        response = self.extract_number(self.input)
        try:
            value = int(response)
        except ValueError:
            self.output = self.DATA["numeric"]["error"]
            return self.ask_numeric(prompt, lower_bound, upper_bound)
        if lower_bound is not None:
            if value < lower_bound:
                self.output=self.DATA["numeric"]["low"]
                return self.ask_numeric(prompt, lower_bound, upper_bound)
        if upper_bound is not None:
            if value > upper_bound:
                self.output=self.DATA["numeric"]["high"]
                return self.ask_numeric(prompt, lower_bound, upper_bound)
        return value

    def ask_with_timeout(self, prompt="say BANG", timeout=7):
        self.output = prompt
        self.waiting_for_user = True
        while self.waiting_for_user:
            sleep(0.1)
        response = self.input.lower().strip()
        # TODO measure mic level or type speed
        return response, random.randint(1, 7)

    def register_default_intents(self):
        pass

    def handle_yes(self, intent):
        return "you sound positive"

    def handle_no(self, intent):
        return "you sound negative"

    def register_core_intents(self):
        self.register_keyword_intent("yes", ["yes", "affirmative", "correct", "agree", "agreed", "confirm", "y", "right"],
                                     handler=self.handle_yes)
        self.register_keyword_intent("no", ["no", "negative", "incorrect", "disagree", "disagreed", "abort", "n", "wrong"],
                                     handler=self.handle_no)

    def calc_intent(self, utterance, lang="en-us"):
        # check adapt
        best_intent = None
        utterances = utterance
        if isinstance(utterance, str):
            utterances = [utterance]
        for utterance in utterances:
            try:
                # normalize() changes "it's a boy" to "it is boy", etc.
                ut = self.normalize(utterance, lang)

                if not ut:
                    continue
                best_intent = next(self.adapt.determine_intent(
                    ut, 100,
                    include_tags=True,
                    context_manager=self.context_manager))
                # TODO - Should Adapt handle this?
                best_intent['utterance'] = utterance
                best_intent['normalized_utterance'] = ut
            except StopIteration:
                # don't show error in log
                continue
            except Exception as e:
                LOG.exception(e)
                continue
        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            return best_intent
        LOG.debug("unknown adapt command: " + str(utterances))
        # check padatious
        return self.container.calc_intent(utterance)

    def register_intent(self, name, samples, handler=None):
        self.container.add_intent(name, samples)
        self.intents[name] = handler

    def register_keyword_intent(self, name, samples=None, optionals=None, handler=None):
        optionals = optionals or {}
        samples = samples or {name: [name]}
        intent_name = self.object_type + ':' + name
        intent = IntentBuilder(intent_name)
        if samples and isinstance(samples, list):
            samples = {samples[0]: samples}
        if optionals and isinstance(optionals, list):
            optionals = {optionals[0]: optionals}
        for required in samples:
            for kw in samples[required]:
                self.adapt.register_entity(required, kw)
            intent.require(required)
        for optional in optionals:
            for kw in optionals[optional]:
                self.adapt.register_entity(optional, kw)
            intent.optionally(optional)
        self.adapt.register_intent_parser(intent.build())
        self.intents[intent_name] = handler

    def parse_command(self, utterance):
        # parse intent
        intent = self.calc_intent(utterance)
        intent_name = intent.get("intent_type", "")
        if intent_name in self.intents:
            return self.intents[intent_name](intent)
        return "?"


class ContextManager(object):
    """
    ContextManager
    Use to track context throughout the course of a conversational session.
    How to manage a session's lifecycle is not captured here.
    """

    def __init__(self, adapt, timeout=2):
        self.frame_stack = []
        self.timeout = timeout * 60  # minutes to seconds

    def clear_context(self):
        self.frame_stack = []

    def remove_context(self, context_id):
        self.frame_stack = [(f, t) for (f, t) in self.frame_stack
                            if context_id in f.entities[0].get('data', [])]

    def inject_context(self, entity, metadata=None):
        """
        Args:
            entity(object): Format example...
                               {'data': 'Entity tag as <str>',
                                'key': 'entity proper name as <str>',
                                'confidence': <float>'
                               }
            metadata(object): dict, arbitrary metadata about entity injected
        """
        metadata = metadata or {}
        try:
            if len(self.frame_stack) > 0:
                top_frame = self.frame_stack[0]
            else:
                top_frame = None
            if top_frame and top_frame[0].metadata_matches(metadata):
                top_frame[0].merge_context(entity, metadata)
            else:
                frame = ContextManagerFrame(entities=[entity],
                                            metadata=metadata.copy())
                self.frame_stack.insert(0, (frame, time.time()))
        except (IndexError, KeyError):
            pass

    def get_context(self, max_frames=None, missing_entities=None):
        """ Constructs a list of entities from the context.

        Args:
            max_frames(int): maximum number of frames to look back
            missing_entities(list of str): a list or set of tag names,
            as strings

        Returns:
            list: a list of entities
        """
        missing_entities = missing_entities or []

        relevant_frames = [frame[0] for frame in self.frame_stack if
                           time.time() - frame[1] < self.timeout]
        if not max_frames or max_frames > len(relevant_frames):
            max_frames = len(relevant_frames)

        missing_entities = list(missing_entities)
        context = []
        for i in range(max_frames):
            frame_entities = [entity.copy() for entity in
                              relevant_frames[i].entities]
            for entity in frame_entities:
                entity['confidence'] = entity.get('confidence', 1.0) \
                    / (2.0 + i)
            context += frame_entities

        result = []
        if len(missing_entities) > 0:
            for entity in context:
                if entity.get('data') in missing_entities:
                    result.append(entity)
                    # NOTE: this implies that we will only ever get one
                    # of an entity kind from context, unless specified
                    # multiple times in missing_entities. Cannot get
                    # an arbitrary number of an entity kind.
                    missing_entities.remove(entity.get('data'))
        else:
            result = context

        # Only use the latest instance of each keyword
        stripped = []
        processed = []
        for f in result:
            keyword = f['data'][0][1]
            if keyword not in processed:
                stripped.append(f)
                processed.append(keyword)
        result = stripped
        return result


if __name__ == "__main__":
    construct = TNaLaGmesConstruct()

    print(construct.parse_command("no"))
    print(construct.parse_command("yes"))
    print(construct.parse_command("what are you"))

    #print(construct.calc_intent("yes"))
    #print(construct.calc_intent("no"))
    #print(construct.calc_intent("what can you do"))

    # read buffer
    #print(construct.output) # empty
    # put something into the buffer
    #construct.output = "hello world"
    # read current buffer
    #print(construct.output)  # hello world
    #print(construct.output) # empty
    # put something into the buffer
    #construct.output = "hello world!"
    #construct.output = "how are you?"
    # read current buffer
    #print(construct.output)  # hello world\nhow are you?   #\n was added
    #print(construct.output)  # empty
