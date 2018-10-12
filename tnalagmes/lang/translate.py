from mtranslate import translate as tx
from tnalagmes.util import play_mp3, play_wav
from os.path import expanduser
from os import system


GOOGLE_LANGUAGES = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'bn': 'Bengali',
    'ca': 'Catalan',
    'zh': 'Chinese',
    'zh-cn': 'Chinese (Mandarin/China)',
    'zh-tw': 'Chinese (Mandarin/Taiwan)',
    'zh-yue': 'Chinese (Cantonese)',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'en-au': 'English (Australia)',
    'en-uk': 'English (United Kingdom)',
    'en-us': 'English (United States)',
    'en-ca': 'English (Canada)',
    'en-gh': 'English (Ghana)',
    'en-in': 'English (India)',
    'en-ie': 'English (Ireland)',
    'en-nz': 'English (New Zealand)',
    'en-ng': 'English (Nigeria)',
    'en-ph': 'English (Philippines)',
    'en-za': 'English (South Africa)',
    'en-tz': 'English (Tanzania)',
    'eo': 'Esperanto',
    'fi': 'Finnish',
    'fr': 'French',
    'de': 'German',
    'el': 'Greek',
    'hi': 'Hindi',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'km': 'Khmer (Cambodian)',
    'ko': 'Korean',
    'la': 'Latin',
    'lv': 'Latvian',
    'mk': 'Macedonian',
    'no': 'Norwegian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pt-br': 'Brazilian Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sr': 'Serbian',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'es': 'Spanish',
    'es-es': 'Spanish (Spain)',
    'es-us': 'Spanish (United States)',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'ta': 'Tamil',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'vi': 'Vietnamese',
    'cy': 'Welsh'
}


def translate_text(text, lang="en-us"):
    sentence = tx(text, lang)
    return sentence


def say_in_language(sentence, lang="en-us", wav_file="~/tnalagmes/translated"):
    sentence = translate_text(sentence, lang)
    type = "mp3"
    wav_file += "." + type
    wav_file = expanduser(wav_file)
    get_sentence = 'wget -q -U Mozilla -O' + wav_file + \
                   ' "https://translate.google.com/translate_tts?tl=' + \
                   lang + '&q=' + sentence + '&client=tw-ob' + '"'
    system(get_sentence)
    if type == "mp3":
        play_mp3(wav_file)
    elif type == "wav":
        play_wav(wav_file)
    return sentence
