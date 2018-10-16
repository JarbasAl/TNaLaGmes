from tnalagmes.lang.phonemes_en import *


# guessing phonemes rule-based
def guess_phonemes(word, lang="en-us"):
    """

    Args:
        word:
        lang:

    Returns:

    """
    if "en" in lang.lower():
        return guess_phonemes_en(word)
    return []


def get_phonemes(name, lang="en-us"):
    """

    Args:
        name:
        lang:

    Returns:

    """
    name = name.replace("_", " ")
    if "en" in lang.lower():
        return get_phonemes_en(name)
    return None
