from tnalagmes.lang.phonemes_en import *


def guess_phonemes(word, lang="en-us"):
    if "en" in lang.lower():
        return guess_phonemes_en(word)
    return []


def get_phonemes(name, lang="en-us"):
    name = name.replace("_", " ")
    if "en" in lang.lower():
        return get_phonemes_en(name)
    return None
