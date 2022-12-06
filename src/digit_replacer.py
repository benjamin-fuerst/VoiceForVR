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
