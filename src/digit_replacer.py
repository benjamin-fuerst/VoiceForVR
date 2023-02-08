import re
from fuzzywuzzy import fuzz
import fuzzy
from word2number import w2n


def to_metaphone(expression: str) -> int:
    metaphone = fuzzy.DMetaphone()
    words = expression.split(" ")
    vocalizations = [(w, metaphone(w)[0].decode("utf-8")
                      if metaphone(w)[0] else w) for w in words]
    return " ".join([vocal for (w, vocal) in vocalizations])


def ratio_metaphone(expression1, expression2: str) -> int:
    return fuzz.ratio(to_metaphone(expression1), to_metaphone(expression2))


def ratio_worddistance(expression1, expression2: str) -> int:
    return fuzz.ratio(expression1, expression2)


def similarity(expression1, expression2: str) -> int:
    return (ratio_metaphone(expression1, expression2) + ratio_worddistance(expression1, expression2)) / 2


def replaceSimilarWithNumbers(utterance: str) -> str:
    r"""
    replace words with similar sounding numbers.
    This ensures numeric parameters are recognized correctly.  

    >>> replaceSimilarWithNumbers("for")
    'four'
    >>> replaceSimilarWithNumbers("too")
    'two'
    """
    metaphoneToNumberMap = {
        to_metaphone(word): word for word in w2n.american_number_system.keys()
    }
    words = utterance.split(" ")
    replaced = [metaphoneToNumberMap[to_metaphone(w)] if (
        to_metaphone(w) in metaphoneToNumberMap) else w for w in words]
    return " ".join(replaced)


def replaceNumberAsWordsWithDigits(utterance: str) -> str:
    r"""
    NOTE: this doesnt work for strings like "one point 3" which includes a mix
    of digit-numbers and numbers written out.

    >>> replaceNumberAsWordsWithDigits("one point three")
    '1.3'
    """
    copy = utterance
    regex = "(" + "\\s*|".join(w2n.american_number_system.keys()) + \
        "\\s*|\\d+\\s*)+"
    for match in re.finditer(regex, utterance):
        number = match.group()
        try:
            number = str(w2n.word_to_num(match.group()))
        except ValueError:
            print("no matching number word found")
            print(match.group())

        copy = copy.replace(match.group(), number + " ")
    return copy.strip()


def clearWhitespace(utteracene: str) -> str:
    r"""
    >>> clearWhitespace(" test  test")
    'test test'
    """
    return " ".join([match.group() for match in re.finditer(r"\S+", utteracene)])


def intentsNumbersReplaced(utterance: str, intents: list[str]) -> list[tuple[str, str, list]]:
    r"""
    >>> intentsNumbersReplaced("test 3", [r"test \num"])
    [('test \\num', 'test 3', ['3'])]
    """
    intentsReplaced = []
    for intent in intents:
        numCount = intent.count(r"\num")
        if numCount == 0:
            intentsReplaced.append((intent, intent, []))
            continue
        numbersInUtterance = re.findall(r"-?\d+\.?\d*", utterance)
        replacedIntent: str = intent
        for i in range(min(numCount, len(numbersInUtterance))):
            replacedIntent = replacedIntent.replace(
                r"\num", numbersInUtterance[i], 1)
        intentsReplaced.append((intent, replacedIntent, numbersInUtterance))
    return intentsReplaced


def intentsRestReplaced(utterance: str, intentsReplaced: list[tuple[str, str, list]]) -> list[tuple[str, str, list]]:
    r"""
    >>> intentsRestReplaced("test 3 bla", intentsNumbersReplaced("test 3", [r"test \num \rest"]))
    [('test \\num \\rest', 'test 3 bla', ['3', 'bla'])]
    """
    l = []
    for entry in intentsReplaced:
        if r"\rest" in entry[0]:
            before, _ = entry[1].split(r"\rest")
            l.append((entry[0], before + utterance[len(before):],
                     entry[2] + [utterance[len(before):]]))
        else:
            l.append(entry)
    return l
