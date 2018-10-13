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


class TNaLaGmesIntent(TNaLaGmesConstruct):
    """
    what can you do
    how do i trigger you
    conflicting intents
    what is your engine
    how many entities matched
    """

    def __init__(self, data):
        TNaLaGmesConstruct.__init__(self)
        self.matches = []
        self.confidence = data.get("confidence") or data.get("conf")
        self.engine = data.get("intent_engine")
        self.intent_name = data.get("intent_name",
                                    "TNaLaGmesIntent:TestIntent")
        self.disambiguation = data.get("disambiguation", {})
        self.description = data.get("description")


# wrappers for intent engines
# TODO
# Parsetron
# Rasa

from tnalagmes.util.nlp import textual_entailment
from os.path import join, dirname


class TNaLaGmesBaseIntentParser(object):
    def __init__(self):
        self.engine = None
        self.intents = {}
        self.samples = {}

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
                  "intent_engine": "fuzzymatch",
                  "intent_name": best_match}
        return intent

    def register_intent(self, name, samples=None, handler=None,
                        ignore_defaults=False):
        samples = self._normalize_samples_input(name, samples, ignore_defaults)
        name = "Fuzzy:" + name
        self.samples[name] = samples
        self.samples[name] = [TNaLaGmesConstruct.normalize(s) for s in
                              self.samples[name]]
        self.intents[name] = handler

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

    @staticmethod
    def _normalize_keyword_input(name, required=None, optionals=None,
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
            optionals= bucket

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
    def _normalize_samples_input(name, samples=None,
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

    def register_keyword_intent(self, name, required=None, optionals=None,
                                handler=None, ignore_defaults=False):
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
        required, optionals = self._normalize_keyword_input(name, required,
                                                            optionals,
                                                            ignore_defaults)

        min_sentence = " ".join(required.keys())

        samples = [min_sentence]
        for optional in optionals:
            extended_sentence = min_sentence + " " + optional
            samples.append(extended_sentence)
        self.register_intent(name, samples)


class TNaLaGmesEntailmentIntentParser(TNaLaGmesBaseIntentParser):
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
                  "intent_engine": "entailer",
                  "intent_name": best_match}
        return intent


class TNaLaGmesAdaptIntentParser(TNaLaGmesBaseIntentParser):
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
            best_intent["conf"] = best_intent["confidence"]
            best_intent["intent_engine"] = "adapt"
            best_intent["intent_name"] = best_intent["intent_type"]
            best_intent.pop("confidence")

            return best_intent
        return None

    def register_keyword_intent(self, name, required=None, optionals=None,
                                handler=None, ignore_defaults=False):
        required, optionals = self._normalize_keyword_input(name, required,
                                                            optionals,
                                                            ignore_defaults)
        intent_name = 'Adapt:' + name
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
        self.intents[intent_name] = handler


class TNaLaGmesPadatiousIntentParser(TNaLaGmesBaseIntentParser):
    def __init__(self):
        TNaLaGmesBaseIntentParser.__init__(self)
        self.engine = IntentContainer(TNaLaGmesConstruct.cache_dir)

    def calc_intent(self, utterance, lang="en-us"):
        best_intent = self.engine.calc_intent(utterance)
        if best_intent and best_intent.get('conf', 0.0) > 0.0:
            best_intent["intent_engine"] = "padatious"
            return best_intent
        return None

    def learn(self):
        # train registered intents
        self.engine.train()

    def register_intent(self, name, samples=None, handler=None,
                        ignore_defaults=False):
        samples = self._normalize_samples_input(name, samples, ignore_defaults)
        name = 'Padatious:' + name
        self.engine.add_intent(name, samples)
        self.intents[name] = handler


class TNaLaGmesIntentContainer(object):
    def __init__(self):
        self.engine_list = [
            TNaLaGmesAdaptIntentParser(),
            TNaLaGmesPadatiousIntentParser(),
            TNaLaGmesBaseIntentParser()
        ]

    def register_intent(self, name,
                        samples=None,
                        handler=None,
                        ignore_defaults=False):
        samples = \
            TNaLaGmesBaseIntentParser._normalize_samples_input(
                name, samples, ignore_defaults)
        for engine in self.engine_list:
            engine.register_intent(name, samples, handler, True)

    def register_keyword_intent(self, name,
                                required=None,
                                optionals=None,
                                handler=None,
                                ignore_defaults=False):
        required, optionals = \
            TNaLaGmesBaseIntentParser._normalize_keyword_input(
                name, required, optionals, ignore_defaults)
        for engine in self.engine_list:
            engine.register_keyword_intent(name, required, optionals,
                                           handler, True)

    def learn(self):
        # train registered intents
        for engine in self.engine_list:
            engine.learn()

    def execute_intent(self, intent):
        name = intent.get("intent_name", "engine:name")
        for engine in self.engine_list:
            if engine.intents.get(name):

                return engine.intents[name](intent)
        return "?"

    def calc_intent(self, utterance, lang="en-us"):

        commands = self.extract_multiple_commands(utterance)
        number = TNaLaGmesConstruct.extract_number(utterance)
        intents = []
        for best_intent in self.disambiguate(commands, lang):
            if not best_intent:
                continue
            best_intent['utterance'] = utterance
            if number:
                best_intent["extracted_number"] = number
            # TODO build TNaLaGmesIntent object
            intents.append(best_intent)
        # list of all intents to execute, there may be more than one
        return intents

    def extract_multiple_commands(self, utterance, markers=None):
        markers = markers or ["."]
        # TODO check for multiple commands in sentence
        return utterance.split(markers[0])

    def chose_best_intent(self, utterance, intent_list):
        intent_list = [i for i in intent_list if i]
        best_intent = None
        if not len(intent_list):
            return None, 0
        elif len(intent_list) == 1:
            best_intent = intent_list[0]
        else:
            # TODO simulate triggering and evaluate best instead
            # unless padatious is fairly sure chose adapt
            for inte in intent_list:
                if inte.get("intent_engine", "") == "adapt":
                    best_intent = inte
                    break
            for inte in intent_list:
                if inte.get("intent_engine", "") == "padatious":
                    score = inte.get("conf") or inte[1].get("confidence")
                    if score > 0.9:
                        best_intent = inte
            # choose randomly
            if best_intent is None:
                best_intent = random.choice(intent_list)

        # best_intent = random.choice(intent_list)  # insert randomness?
        score = best_intent.get("conf") or best_intent.get("confidence")
        return best_intent, score

    def disambiguate(self, commands, lang="en-us"):

        # check for multiple intents in utterance
        for command in commands:
            intents = []
            for engine in self.engine_list:

                intents.append(engine.calc_intent(command, lang))

            best_intent, score = self.chose_best_intent(command, intents)

            yield best_intent


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
