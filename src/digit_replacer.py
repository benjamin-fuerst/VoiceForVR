import re
from fuzzywuzzy import fuzz
import fuzzy
from word2number import w2n

#soundex = fuzzy.Soundex(6)

#soundexToNumberMap = {
#    soundex(word): word for word in w2n.american_number_system.keys()}


def to_metaphone(expression: str) -> int:
    metaphone = fuzzy.DMetaphone()
    words = expression.split(" ")
    vocalizations = [(w, metaphone(w)[0].decode("utf-8") if metaphone(w)[0] else w) for w in words]
    return " ".join([vocal for (w, vocal) in vocalizations])


def ratio_metaphone(expression1, expression2: str) -> int:
    return fuzz.ratio(to_metaphone(expression1), to_metaphone(expression2))


def replaceSimilarWithNumbers(utterance):
    # to, too -> two, for -> four
    # makes some words unusable as they are always transformed
    metaphone = fuzzy.DMetaphone()
    metaphoneToNumberMap = {
        to_metaphone(word): word for word in w2n.american_number_system.keys()
    }
    words = utterance.split(" ")
    replaced = [metaphoneToNumberMap[to_metaphone(w)] if (to_metaphone(w) in metaphoneToNumberMap) else w for w in words]
    return " ".join(replaced)


regex = "(" + "\\s*|".join(w2n.american_number_system.keys()) + "\\s*|\\d+\\s*)+"


def replaceNumberAsWordsWithDigits(utterance):
    # "one point 3" -> "1.3"
    copy = utterance
    regex = "(" + "\\s*|".join(w2n.american_number_system.keys()) + "\\s*|\\d+\\s*)+"
    for match in re.finditer(regex, utterance):
        number = match.group()
        try:
            number = str(w2n.word_to_num(match.group()))
        except ValueError:
            print("no matching number word found")
            print(match.group())

        copy = copy.replace(match.group(), number + " ")
    return copy

def intentsNumbersReplaced(utterance, intents):
    intentsReplaced = []
    for intent in intents:
        numbersInIntents = intent.count(r"\num")
        if numbersInIntents == 0:
            intentsReplaced.append(
            (intent, intent, []))
            continue
        numbersInUtterance = re.findall(r"-?\d+\.?\d*", utterance)
        replacedIntent: str = intent
        for i in range(numbersInIntents):
            replacedIntent = replacedIntent.replace(
                r"\num", numbersInUtterance[i], 1)
                #( "note add \rest", "note add remind meto ...", )
                # "note addd remind me to buy bla"
        intentsReplaced.append(
            (intent, replacedIntent, numbersInUtterance))
    return intentsReplaced


def intentsRestReplaced(utterance, intentsReplaced):
    l = []
    for entry in intentsReplaced:
        if r"\rest" in entry[0]:
            before, rest = entry[1].split(r"\rest")
            l.append((entry[0], before + utterance[len(before):], entry[2] + [utterance[len(before):]]))
        else:
            l.append(entry)
    return l
