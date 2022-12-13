import re
import fuzzy
from word2number import w2n

soundex = fuzzy.Soundex(6)

soundexToNumberMap = {
    soundex(word): word for word in w2n.american_number_system.keys()}


def replaceSimilarWithNumbers(utterance):
    words = utterance.split(" ")
    replaced = [soundexToNumberMap[soundex(w)] if (
        soundex(w) in soundexToNumberMap) else w for w in words]
    return " ".join(replaced)


regex = "(" + "\\s*|".join(w2n.american_number_system.keys()) + "\\s*|\\d+\\s*)+"


def replaceNumberAsWordsWithDigits(utterance):
    copy = utterance
    for match in re.finditer(regex, utterance):
        number = match.group()
        try:
            number = str(w2n.word_to_num(match.group()))
        except ValueError:
            print("no matching number word found")
            print(match.group())

        copy = copy.replace(match.group(), number + " ")
    return copy

def vocalized(sentence: str):
    metaphone = fuzzy.DMetaphone()
    words = sentence.split(" ")
    vocalizations = [(w, metaphone(w)[0].decode("utf-8") if metaphone(w)[0] else w) for w in words]
    return " ".join([vocal for (w, vocal) in vocalizations])

def intentsNumbersReplaced(utterance, intents):
    intentsReplaced = []
    for intent in intents:
        numbersInUtterance = re.findall(r"-?\d+\.?\d*", utterance)
        replacedIntent: str = intent
        for i in range(len(numbersInUtterance)):
            replacedIntent = replacedIntent.replace(
                r"\num", numbersInUtterance[i], 1)
        intentsReplaced.append(
            (intent, replacedIntent, numbersInUtterance))
    return intentsReplaced
