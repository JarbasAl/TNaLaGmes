import requests
from tnalagmes.util.log import LOG

# TODO check for is_connected ?

# list of words that if present, trigger coref step
PRONOUNS_EN = ["i", "we", "me", "us", "you", "they", "them", "she", "he", "it", "her", "him",
               "that", "which", "who", "whom", "whose", "whichever", "whoever", "whomever",
               "this", "these", "those", "myself", "ourselves", "yourself", "yourselves",
               "himself", "herself", "itself", "themselves"]


def NER(text):
    ents = []
    # TODO on device
    try:
       data = {"model": "en_core_web_lg", "text": text}
       r = requests.post("https://api.explosion.ai/displacy/ent", data)
       r = r.json()
       for e in r:
           txt = text[e["start"]:e["end"]]
           ents.append((e["label"].lower(), txt))
    except Exception as e:
       LOG.error(e)
    return ents


def replace_coreferences(text):
    # TODO on device
    # "My sister has a dog. She loves him." -> "My sister has a dog. My sister loves a dog."
    for w in text.split(" "):
        # do not trigger coref resolution step if it isn't needed
        if w.lower() in PRONOUNS_EN:
            params = {"text": text}
            try:
                text = requests.get("https://coref.huggingface.co/coref", params=params).json()["corefResText"]
            except Exception as e:
                LOG.error(e)
            break
    return text
