import requests
from tnalagmes.util.log import LOG
ALLENNLP_URL = "http://demo.allennlp.org/predict/"

# TODO check for is_connected ?

# list of words that if present, trigger coref step
PRONOUNS_EN = ["i", "we", "me", "us", "you", "they", "them", "she", "he", "it", "her", "him",
               "that", "which", "who", "whom", "whose", "whichever", "whoever", "whomever",
               "this", "these", "those", "myself", "ourselves", "yourself", "yourselves",
               "himself", "herself", "itself", "themselves"]


def NER(text):
    """

    Args:
        text:

    Returns:

    """
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
    """

    Args:
        text:

    Returns:

    """
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


def textual_entailment(premise, hypothesis):
    # use the source: https://github.com/allenai/
    """
    Textual Entailment (TE) takes a pair of sentences and predicts whether the facts in the first necessarily imply the facts in the second one.
    The AllenNLP toolkit provides the following TE visualization, which can be run for any TE model you develop.
    This page demonstrates a reimplementation of the decomposable attention model (Parikh et al, 2017) ,
    which was state of the art for the SNLI benchmark (short sentences about visual scenes) in 2016.
    Rather than pre-trained Glove vectors, this model uses ELMo embeddings,
    which are completely character based and improve performance by 2%

    Args:
        premise: 
        hypotheses: 

    :return:
    """
    url = ALLENNLP_URL + "textual-entailment"
    data = {"premise": premise,
            "hypothesis": hypothesis}
    r = requests.post(url, json=data).json()
    probs = r["label_probs"]
    return {"entailment": probs[0], "contradiction": probs[1], "neutral": probs[2]}

    #p = "If you help the needy, God will reward you."
    #h = "Giving money to the poor has good consequences."
    #print(textual_entailment_demo(p, h)) # {'contradiction': 0.04034089669585228, 'neutral': 0.1409262865781784, 'entailment': 0.8187329173088074}
