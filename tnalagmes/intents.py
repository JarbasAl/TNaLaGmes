from tnalagmes import TNaLaGmesConstruct
from os.path import exists
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from adapt.context import ContextManagerFrame
import json
from padatious import IntentContainer
import time
import random
from tnalagmes.util.log import LOG
from tnalagmes.util import resolve_resource_file
# from parsetron import *  # waiting py3 support


class TNaLaGmesIntent(TNaLaGmesConstruct):
    """
    what can you do # self.description
    how do i trigger you  # self.samples
    alternative meanings of question  # other intents that could/will trigger / self.disambiguation
    what is your engine
    why did you trigger  # matches
    what did you answer  # last answer
    what is the question # last utterance
    can you answer X  # judge if good question
    does answer X look correct # judge if good answer to question
    """

    def __init__(self, data=None):
        data = data or {}
        TNaLaGmesConstruct.__init__(self)
        self.handler = None
        self.question_validator = None
        self.answer_validator = None
        self.from_json(data)

    def __getitem__(self, key):
        return self.as_json.get(key)

    def __setitem__(self, key, data):
        updated = self.as_json
        updated[key] = data
        self.from_json(updated)

    def __call__(self, *args, **kwargs):
        if self.handler is not None:
            # TODO if intent not in args inject self
            return self.handler(*args, **kwargs)
        raise AttributeError("intent handler not yet binded")

    def bind_handler(self, handler):
        self.handler = handler

    def bind_question_validator(self, handler):
        self.question_validator = handler

    def bind_answer_validator(self, handler):
        self.answer_validator = handler

    def from_json(self, data):
        self.confidence = data.get("confidence") or data.get("conf")
        self.intent_engine = data.get("intent_engine")
        self.intent_name = data.get("intent_name",
                                    "TNaLaGmesIntent:TestIntent")
        self.disambiguation = data.get("disambiguation", {})
        self.description = data.get("description", "")
        self.samples = data.get("samples", [])
        self.optionals = data.get("optionals", {})
        self.required = data.get("required", {})
        self.matches = data.get("matches", [])
        self.utterance = data.get("utterance", "")
        self.answer = data.get("answer", "")
        return self

    @property
    def as_json(self):
        bucket = {}
        bucket["confidence"] = self.confidence
        bucket["intent_engine"] = self.intent_engine
        bucket["intent_name"] = self.intent_name
        bucket["disambiguation"] = self.disambiguation
        bucket["description"] = self.description
        bucket["samples"] = self.samples
        bucket["optionals"] = self.optionals
        bucket["required"] = self.required
        bucket["matches"] = self.matches
        bucket["utterance"] = self.utterance
        bucket["answer"] = self.answer
        return bucket

    def validate_question(self, intent):
        """
        when asked if you can solve this intent return True or False

        this step is called for disambiguation after an intent already matched

        return True -> can solve intent
        return False -> can not solve intent
        """
        if self.question_validator:
            if isinstance(intent, str):
                self.utterance = intent
            else:
                self.utterance = intent.utterance
            return self.question_validator(self)
        return True

    def validate_answer(self, intent):
        """
        when asked if the answer of this intent looks good return True or False

        this step is called for disambiguation after an intent already matched

        return True -> intent looks good
        return False -> intent looks bad
        """
        if self.answer_validator:
            if isinstance(intent, str):
                self.answer = intent
            else:
                self.answer = intent.answer
            return self.answer_validator(self)
        return True


# wrappers for intent engines
# TODO
# Rasa

from tnalagmes.util.nlp import textual_entailment


class TNaLaGmesBaseIntentParser(object):
    name = "fuzzy"

    def __init__(self):
        self.engine = None
        self.intents = {}
        self.samples = {}

    def build_intent(self, data, handler, validator):
        intent = TNaLaGmesIntent()
        intent.from_json(data)
        intent.bind_handler(handler)
        intent.bind_question_validator(validator)
        self.intents[intent.intent_name] = intent
        return intent

    def learn(self):
        """
        For parsers that need a training phase
        :return:
        """
        # train registered intents
        pass

    def match(self, utterance, ut):
        return TNaLaGmesConstruct.fuzzy_match(utterance, ut)

    def calc_intent(self, utterance, lang="en-us"):
        # simple demo, fuzzy_match
        utterance = TNaLaGmesConstruct.normalize(utterance)
        best_score = 0
        best_match = ""
        for s in self.samples:
            utterances = self.samples[s]
            for ut in utterances:
                score = self.match(utterance, ut)
                if score > best_score:
                    best_score = score
                    best_match = s
        if best_score < 0.5:
            return None
        intent = {"conf": best_score,
                  "intent_engine": self.name,
                  "intent_name": best_match}
        return self.intents.get(best_match, intent)

    def register_intent(self, name, samples=None, handler=None,
                        ignore_defaults=False, validator=None):
        samples = samples or []
        name = self.name + ":" + name
        self.samples[name] = samples
        self.samples[name] = [TNaLaGmesConstruct.normalize(s) for s in
                              self.samples[name]]
        data = {
            "intent_engine": self.name,
            "intent_name": name,
            "samples": samples
        }
        return self.build_intent(data, handler, validator)

    @staticmethod
    def load_resource(name, sep="\n", is_json=False):
        path = resolve_resource_file(name)
        if path and exists(path):
            with open(path, "r") as f:
                lines = f.read()
                if is_json:
                    return json.loads(lines)
                return lines.split(sep)
        return None

    def register_keyword_intent(self, name, required=None, optionals=None,
                                handler=None, ignore_defaults=False, validator=None):
        """
        rule based intent,

        required and optionals keywords
            may be dict , list or None, will be formatted into

            { word : [sample1, sample2] }

        :param name:
        :param required:
        :param optionals:
        :param handler:
        :param ignore_defaults:
        :return:
        """
        required, optionals = TNaLaGmesIntentContainer.normalize_keyword_input(name, required,
                                                                               optionals,
                                                                               ignore_defaults)

        min_sentence = " ".join(required.keys())

        samples = [min_sentence]
        for optional in optionals:
            extended_sentence = min_sentence + " " + optional
            samples.append(extended_sentence)
        return self.register_intent(name, samples)


class TNaLaGmesEntailmentIntentParser(TNaLaGmesBaseIntentParser):
    name = "entailer"

    def match(self, utterance, sample):
        return textual_entailment(utterance, sample).get("entailment", 0)

    def calc_intent(self, utterance, lang="en-us"):
        utterance = TNaLaGmesConstruct.normalize(utterance)
        best_score = 0
        best_match = ""
        for s in self.samples:
            utterances = self.samples[s]
            for ut in utterances:
                score = self.match(utterance, ut)
                if score > best_score:
                    best_score = score
                    best_match = s

        if best_score < 0.5:
            return None
        intent = {"conf": best_score,
                  "intent_engine": self.name,
                  "intent_name": best_match}
        return intent


class TNaLaGmesAdaptIntentParser(TNaLaGmesBaseIntentParser):
    name = "adapt"

    def __init__(self):
        TNaLaGmesBaseIntentParser.__init__(self)
        self.engine = IntentDeterminationEngine()
        self.context_manager = ContextManager()

    def calc_intent(self, utterance, lang="en-us"):
        best_intent = None
        utterances = utterance
        if isinstance(utterance, str):
            utterances = [utterance]
        for utterance in utterances:
            try:

                if not utterance:
                    continue
                best_intent = next(self.engine.determine_intent(
                    utterance, 100,
                    include_tags=True,
                    context_manager=self.context_manager))

            except StopIteration:
                # don't show error in log
                continue
            except Exception as e:
                LOG.exception(e)
                continue
        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            best_intent["intent_engine"] = "adapt"
            best_intent["intent_name"] = best_intent["intent_type"]
            # cast into intent object
            intent = self.intents.get(best_intent.get("intent_name", ""), best_intent)
            intent.from_json(best_intent)
            return intent
        return None

    def register_keyword_intent(self, name, required=None, optionals=None,
                                handler=None, ignore_defaults=False, validator=None):
        required, optionals = TNaLaGmesIntentContainer.normalize_keyword_input(name, required,
                                                                               optionals,
                                                                               ignore_defaults)
        intent_name = self.name + ':' + name
        intent = IntentBuilder(intent_name)

        for req in required:
            for kw in required[req]:
                self.engine.register_entity(req, kw)
            intent.require(req)
        for optional in optionals:
            for kw in optionals[optional]:
                self.engine.register_entity(optional, kw)
            intent.optionally(optional)
        self.engine.register_intent_parser(intent.build())

        data = {
            "intent_engine": self.name,
            "intent_name": intent_name,
            "required": required,
            "optionals": optionals
        }
        return self.build_intent(data, handler, validator)


class TNaLaGmesPadatiousIntentParser(TNaLaGmesBaseIntentParser):
    name = "padatious"

    def __init__(self):
        TNaLaGmesBaseIntentParser.__init__(self)
        self.engine = IntentContainer(TNaLaGmesConstruct.cache_dir)

    def calc_intent(self, utterance, lang="en-us"):
        best_intent = self.engine.calc_intent(utterance)
        if best_intent and best_intent.get('conf', 0.0) > 0.0:
            best_intent["intent_engine"] = self.name
            # cast into intent object (update confidence in stored object)
            intent = self.intents.get(best_intent.get("intent_name", ""), best_intent)
            intent.from_json(best_intent)
            return intent
        return None

    def learn(self):
        # train registered intents
        self.engine.train()

    def register_intent(self, name, samples=None, handler=None,
                        ignore_defaults=False, validator=None):
        samples = TNaLaGmesIntentContainer.normalize_samples_input(name, samples, ignore_defaults)
        intent_name = self.name + ':' + name
        self.engine.add_intent(intent_name, samples)
        data = {
            "intent_engine": self.name,
            "intent_name": intent_name,
            "samples": samples
        }
        return self.build_intent(data, handler, validator)


class TNaLaGmesIntentContainer(object):
    name = "TNaLaGmesIntentContainer"

    def __init__(self):
        self.engine_list = [
            TNaLaGmesAdaptIntentParser(),
            TNaLaGmesPadatiousIntentParser(),
            TNaLaGmesBaseIntentParser()
        ]
        self.parsers = {}

    def register_intent(self, name,
                        samples=None,
                        handler=None,
                        ignore_defaults=False):
        if isinstance(name, TNaLaGmesIntent):
            intent = name
            name = intent.intent_name
            handler = intent.handler
            return
        samples = self.normalize_samples_input(name, samples, ignore_defaults)
        for engine in self.engine_list:
            engine.register_intent(name, samples, handler, True)

    def register_keyword_intent(self, name,
                                required=None,
                                optionals=None,
                                handler=None,
                                ignore_defaults=False):
        required, optionals = self.normalize_keyword_input(
                name, required, optionals, ignore_defaults)
        for engine in self.engine_list:
            engine.register_keyword_intent(name, required, optionals,
                                           handler, True)
        # self.register_parsetron(name, required, optionals)

    @staticmethod
    def normalize_keyword_input(name=None, required=None, optionals=None,
                                ignore_defaults=False):
        """
        keywords may be a list, each will be loaded into a dict as {kw: [kw]}
        keywords may be None, name will be used as single keyword {name: [name]}
        keywords may be a dict, each key is a keyword + list of synonyms

        keyword samples will be expanded from .voc files if ignore_defaults=False

        :param name: str
        :param required: dict/list/None
        :param optionals: dict/list/None
        :param ignore_defaults: bool
        :return: required(dict), optionals(dict)
        """
        assert name or required
        optionals = optionals or []
        required = required or [name]

        if required and isinstance(required, list):
            bucket = {}
            for r in required:
                bucket[r] = [r]
            required = bucket
        if optionals and isinstance(optionals, list):
            bucket = {}
            for r in optionals:
                bucket[r] = [r]
            optionals = bucket

        if not ignore_defaults:
            for req in required:
                data = TNaLaGmesBaseIntentParser.load_resource(req)
                if data:
                    # merge file data
                    for new in data:
                        if new not in required[req]:
                            required[req].append(new)

            for optional in optionals:
                data = TNaLaGmesBaseIntentParser.load_resource(optional)
                if data:
                    # merge file data
                    for new in data:
                        optionals[optional] = optionals[optional] or []
                        if new not in optionals[optional]:
                            optionals[optional].append(new)

        return required, optionals

    @staticmethod
    def normalize_samples_input(name=None, samples=None,
                                ignore_defaults=False):
        """
        samples may be None and name will be used as single sample
        samples may be a list of sample phrases to trigger this intent
        if ignore_defaults is False, samples will be expanded from disk vocabulary

        :param name:
        :param samples:
        :param ignore_defaults:
        :return:
        """
        assert samples or name
        samples = samples or [name]

        if not ignore_defaults:
            for req in samples:
                data = TNaLaGmesBaseIntentParser.load_resource(req)
                if data:
                    # merge file data
                    for new in data:
                        if new not in samples:
                            samples.append(new)

        return samples

    """
    def register_parsetron(self, name, required=None, optionals=None):
        # extracts multiple intents/matches in a single utterance
        # sentences are then reconstructed from parsetron matches
        # reconstructed sentences sent to intent parsers
        # used in disambiguation when validating intents
        
        required, optionals = self.normalize_keyword_input(name, required=required, optionals=optionals)
        one_parse = None

        for req in required:
            word = Set(required[req])
            one_parse = one_parse + word if one_parse else word

        for optional in optionals:
            # these ones will only be detected at end of sentence
            word = Set(optionals[optional])
            one_parse = one_parse + Optional(word) if one_parse else word

        class ParsetronGrammar(Grammar):
            GOAL = OneOrMore(one_parse)

        def parse(utterance):
            parser = RobustParser((ParsetronGrammar()))
            tree, result = parser.parse(utterance)
            disambiguation = result.one_parse
            return disambiguation

        self.parsers[name] = parse
    """

    def learn(self):
        # train registered intents
        for engine in self.engine_list:
            engine.learn()

    def execute_intent(self, intent):
        if isinstance(intent, TNaLaGmesIntent):
            if intent.handler is not None:
                return intent.handler(intent)
            name = intent.intent_name
        else:
            name = intent.get("intent_name", "intent_engine:name")
        for engine in self.engine_list:
            if engine.intents.get(name) and engine.intents[name].handler:
                return engine.intents[name].handler(intent)
        return "?"

    def calc_intent(self, utterance, lang="en-us"):

        commands = self.extract_multiple_commands(utterance)
        intents = []
        for best_intent in self.disambiguate(commands, lang):
            if not best_intent:
                continue
            best_intent['utterance'] = utterance
            intents.append(best_intent)
        # list of all intents to execute, there may be more than one
        return intents

    def extract_multiple_commands(self, utterance, markers=None):
        markers = markers or ["."]

        # TODO check for multiple commands in sentence
        # waiting for py3 parsetron
        #for p in self.parsers:
        #    print(self.parsers[p]())
        #   from here extract disambiguation data to inject in intent
        #   rebuild new commands # TODO test how rebuilt commands look

        return utterance.split(markers[0])

    def chose_best_intent(self, utterance, intent_list):
        intent_list = [i for i in intent_list if i]

        if not len(intent_list):
            return None
        elif len(intent_list) == 1:
            best_intent = intent_list[0]
        else:
            best_intent = None

            # ask intents to validate utterance
            # "hey you are going to trigger, are you sure you can answer this?"
            for idx, inte in enumerate(intent_list):
                if isinstance(inte, dict):
                    intent = TNaLaGmesIntent()
                    intent.from_json(inte)
                    inte = intent
                inte.bind_question_validator(self.fetch_question_validator(inte))
                if not inte.validate_question(utterance):
                    intent_list[idx] = None

            # prune list from None s
            intent_list = [i for i in intent_list if i]

            # TODO check answer validators
            # create copy object of the intent
            # simulate trigger
            # pass answer to validator

            # chose best adapt intent
            best_score = 0
            for inte in intent_list:
                if isinstance(inte, dict):
                    intent = TNaLaGmesIntent()
                    intent.from_json(inte)
                    inte = intent
                if inte.intent_engine == "adapt":
                    score = inte.confidence or 0
                    if score > best_score:
                        best_intent = inte
                        best_score = score

            # unless padatious is fairly sure
            best_score = 0
            for inte in intent_list:
                if isinstance(inte, dict):
                    intent = TNaLaGmesIntent()
                    intent.from_json(inte)
                    inte = intent
                if inte.intent_engine == "padatious":
                    score = inte.confidence or 0
                    if score > 0.9 and score > best_score:
                        best_intent = inte
                        best_score = score
            # choose randomly (fuzzy intent_engine only by default)
            if best_intent is None:
                best_intent = random.choice(intent_list)

        # fetch handler
        best_intent.bind_handler(self.fetch_handler(best_intent))
        return best_intent

    def fetch_handler(self, intent):
        if isinstance(intent, dict):
            intent = TNaLaGmesIntent().from_json(intent)
        for engine in self.engine_list:
            if engine.name == intent.intent_engine:
                i = engine.intents.get(intent.intent_name)
                if i:
                    return i.handler
        return None

    def fetch_question_validator(self, intent):
        if isinstance(intent, dict):
            intent = TNaLaGmesIntent().from_json(intent)
        for engine in self.engine_list:
            if engine.name == intent.intent_engine:
                i = engine.intents.get(intent.intent_name)
                if i:
                    return i.question_validator
        return None

    def fetch_answer_validator(self, intent):
        if isinstance(intent, dict):
            intent = TNaLaGmesIntent().from_json(intent)
        for engine in self.engine_list:
            if engine.name == intent.intent_engine:
                i = engine.intents.get(intent.intent_name)
                if i:
                    return i.answer_validator
        return None

    def disambiguate(self, commands, lang="en-us"):

        # check for multiple intents in utterance
        for command in commands:
            intents = []
            for engine in self.engine_list:
                intents.append(engine.calc_intent(command, lang))

            yield self.chose_best_intent(command, intents)


class ContextManager(object):
    """
    ContextManager
    Use to track context throughout the course of a conversational session.
    How to manage a session's lifecycle is not captured here.
    """

    def __init__(self, timeout=2):
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
                                'key': 'entity proper _name as <str>',
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
