# show help
# show/hide processes
# start/stop processes
# keyboard
import re
import string

# define intents
intents = []
intents.append("Copy")
intents.append("Paste")
intents.append("Cut")
intents.append("Undo")
intents.append("ShowKeyboard")
intents.append("HideKeyboard")
intents.append("StartProcess")
intents.append("StopProcess")
intents.append("BUILTIN.HelpIntent")
intents.append("BUILTIN.CancelIntent")
intents.append("BUILTIN.StopIntent")
intents.append("BUILTIN.StartOverIntent")
intents.append("BUILTIN.FallbackIntent")
intents.append("BUILTIN.YesIntent")
intents.append("BUILTIN.NoIntent")


# map spoken terms to intents in the form of INTENT:KEYWORD
# consider shortest form of word for stemming
utterances = []
# ENGLISH SHORTCUTS
utterances.append(("Copy", re.compile(r"copi")))
utterances.append(("Paste", re.compile(r"paste")))
utterances.append(("Cut", re.compile(r"cut")))
utterances.append(("Undo", re.compile(r"undo")))
#...
# ENGLISH HELPERS
utterances.append(("ShowKeyboard", re.compile(r"show keyboard")))
utterances.append(("HideKeyboard", re.compile(r"hide keyboard")))
utterances.append(("StartApplication", re.compile(r"start \d+")))
utterances.append(("StopApplication", re.compile(r"stop \d+")))
#...
# ENGLISH BUILT-INS
utterances.append(("BUILTIN.HelpIntent", re.compile(r"help")))
utterances.append(("BUILTIN.HelpIntent", re.compile(r"show help")))
utterances.append(("BUILTIN.HelpIntent", re.compile(r"display help")))
utterances.append(("BUILTIN.CancelIntent", re.compile(r"cancel"))) # cancel current task, but remain in current session
utterances.append(("BUILTIN.StopIntent", re.compile(r"stop"))) # cancel current task and stop current session
utterances.append(("BUILTIN.StartOverIntent", re.compile(r"restart"))) # restart current session
utterances.append(("BUILTIN.FallbackIntent", re.compile(r"FALLBACK"))) # called if user input is not understood
utterances.append(("BUILTIN.YesIntent", re.compile(r"yes"))) # request help
utterances.append(("BUILTIN.NoIntent", re.compile(r"no"))) # request help

# GERMAN SHORTCUTS
#utterances.append("Copy", "kopieren")
#utterances.append("Paste", "einfügen")
#utterances.append("Cut", "ausschneiden")
#utterances.append("Undo", "rückgängig")
#utterances.append("SelectLine", "zeile auswählen")
#utterances.append("DeleteLine", "zeile löschen")
#utterances.append("HideKeyboard", "tastatur verstecken")


import nltk
#nltk.download()
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
nltk.download('punkt')
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
nltk.download('stopwords')


# removes contractions
def expand_abbreviations(words):
    #words = re.sub(r"ain\'t", "is not", words) # am not, are not, has not, have not
    words = re.sub(r"aren\'t", "are not", words)
    words = re.sub(r"can\'t", "cannot", words)
    words = re.sub(r"can\'t\'ve", "cannot have", words)
    #words = re.sub(r"cause", "because", words)
    words = re.sub(r"could\'ve", "could have", words)
    words = re.sub(r"couldn\'t", "could not", words)
    words = re.sub(r"couldn\'t\'ve", "could not have", words)
    words = re.sub(r"didn\'t", "did not", words)
    words = re.sub(r"doesn\'t", "does not", words)
    words = re.sub(r"don\'t", "do not", words)
    words = re.sub(r"hadn\'t", "had not", words)
    words = re.sub(r"hadn\'t\'ve", "had not have", words)
    words = re.sub(r"hasn\'t", "has not", words)
    words = re.sub(r"haven\'t", "have not", words)
    words = re.sub(r"he\'d", "he had", words) # he would
    words = re.sub(r"he\'d\'ve", "he would have", words)
    words = re.sub(r"he\'ll", "he will", words) # he shall
    words = re.sub(r"he\'ll\'ve", "he will have", words) # he shall have
    words = re.sub(r"he\'s", "he is", words) # he has
    words = re.sub(r"how\'d", "how did", words)
    words = re.sub(r"how\'d\'y", "how do you", words)
    words = re.sub(r"how\'ll", "how will", words)
    words = re.sub(r"how\'s", "how has", words) # how is, how does
    words = re.sub(r"I\'d", "I would", words) # I had
    words = re.sub(r"I\'d\'ve", "I would have", words)
    words = re.sub(r"I\'ll", "I will", words) # I shall
    words = re.sub(r"I\'ll\'ve", "I will have", words) # I shall have
    words = re.sub(r"I\'m", "I am", words)
    words = re.sub(r"I\'ve", "I have", words)
    words = re.sub(r"isn\'t", "is not", words)
    words = re.sub(r"it\'d", "it had", words) # it would
    words = re.sub(r"it\'d\'ve", "it would have", words)
    words = re.sub(r"it\'ll", "it will", words) # it shall
    words = re.sub(r"it\'ll\'ve", "it will have", words) # it shall have
    words = re.sub(r"it\'s", "it is", words) # it has
    words = re.sub(r"let\'s", "let us", words)
    words = re.sub(r"ma\'am", "madam", words)
    words = re.sub(r"mayn\'t", "may not", words)
    words = re.sub(r"might\'ve", "might have", words)
    words = re.sub(r"mightn\'t", "might not", words)
    words = re.sub(r"mightn\'t\'ve", "might not have", words)
    words = re.sub(r"must\'ve", "must have", words)
    words = re.sub(r"mustn\'t", "must not", words)
    words = re.sub(r"mustn\'t\'ve", "must not have", words)
    words = re.sub(r"needn\'t", "need not", words)
    words = re.sub(r"needn\'t\'ve", "need not have", words)
    words = re.sub(r"o\'clock", "of the clock", words)
    words = re.sub(r"oughtn\'t", "ought not", words)
    words = re.sub(r"oughtn\'t\'ve", "ought not have", words)
    words = re.sub(r"shan\'t", "shall not", words)
    words = re.sub(r"sha\'n\'t", "shall not", words)
    words = re.sub(r"shan\'t\'ve", "shall not have", words)
    words = re.sub(r"she\'d", "she had", words) # she would
    words = re.sub(r"she\'d\'ve", "she would have", words)
    words = re.sub(r"she\'ll", "she will", words) # she shall
    words = re.sub(r"she\'ll\'ve", "she will have", words) # she will have
    words = re.sub(r"she\'s", "she is", words) # she has
    words = re.sub(r"should\'ve", "should have", words)
    words = re.sub(r"shouldn\'t", "should not", words)
    words = re.sub(r"shouldn\'t\'ve", "should not have", words)
    words = re.sub(r"so\'ve", "so have", words)
    words = re.sub(r"so\'s", "so is", words) # so as
    words = re.sub(r"that\'d", "that would / that had", words)
    words = re.sub(r"that\'d\'ve", "that would have", words)
    words = re.sub(r"that\'s", "that is", words) # that has
    words = re.sub(r"there\'d", "there had", words) # there would
    words = re.sub(r"there\'d\'ve", "there would have", words)
    words = re.sub(r"there\'s", "there is", words) # there has
    words = re.sub(r"they\'d", "they had", words) # they would
    words = re.sub(r"they\'d\'ve", "they would have", words)
    words = re.sub(r"they\'ll", "they will", words) # they shall
    words = re.sub(r"they\'ll\'ve", "they will have", words) # they shall have
    words = re.sub(r"they\'re", "they are", words)
    words = re.sub(r"they\'ve", "they have", words)
    words = re.sub(r"to\'ve", "to have", words)
    words = re.sub(r"wasn\'t", "was not", words)
    words = re.sub(r"we\'d", "we had", words) # we would
    words = re.sub(r"we\'d\'ve", "we would have", words)
    words = re.sub(r"we\'ll", "we will", words)
    words = re.sub(r"we\'ll\'ve", "we will have", words)
    words = re.sub(r"we\'re", "we are", words)
    words = re.sub(r"we\'ve", "we have", words)
    words = re.sub(r"weren\'t", "were not", words)
    words = re.sub(r"what\'ll", "what will", words) # what shall
    words = re.sub(r"what\'ll\'ve", "what will have", words) # what shall have
    words = re.sub(r"what\'re", "what are", words)
    words = re.sub(r"what\'s", "what is", words) # what has
    words = re.sub(r"what\'ve", "what have", words)
    words = re.sub(r"when\'s", "when is", words) # when has
    words = re.sub(r"when\'ve", "when have", words)
    words = re.sub(r"where\'d", "where did", words)
    words = re.sub(r"where\'s", "where is", words) # where has
    words = re.sub(r"where\'ve", "where have", words)
    words = re.sub(r"who\'ll", "who will", words) # who shall
    words = re.sub(r"who\'ll've", "who will have", words) # who shall have
    words = re.sub(r"who\'s", "who is", words) # who has
    words = re.sub(r"who\'ve", "who have", words)
    words = re.sub(r"why\'s", "why is", words) # why has
    words = re.sub(r"why\'ve", "why have", words)
    words = re.sub(r"will\'ve", "will have", words)
    words = re.sub(r"won\'t", "will not", words)
    words = re.sub(r"won\'t\'ve", "will not have", words)
    words = re.sub(r"would\'ve", "would have", words)
    words = re.sub(r"wouldn\'t", "would not", words)
    words = re.sub(r"wouldn\'t\'ve", "would not have", words)
    words = re.sub(r"y\'all", "you all", words)
    words = re.sub(r"y\'all\'d", "you all would", words)
    words = re.sub(r"y\'all\'d\'ve", "you all would have", words)
    words = re.sub(r"y\'all\'re", "you all are", words)
    words = re.sub(r"y\'all\'ve", "you all have", words)
    words = re.sub(r"you\'d", "you had", words) # you would
    words = re.sub(r"you\'d\'ve", "you would have", words)
    words = re.sub(r"you\'ll", "you will", words) # you shall
    words = re.sub(r"you\'ll\'ve", "you will have", words) # you shall have
    words = re.sub(r"you\'re", "you are", words)
    words = re.sub(r"you\'ve", "you have", words)
    return words


def to_lowercase(sentence):
    return sentence.lower()

def remove_punctuation(sentence):
    tokenizer = RegexpTokenizer(r"\w+")
    cleaned_words = tokenizer.tokenize(" ".join(sentence))
    return cleaned_words

def remove_stopwords(words):
    english_stopwords = stopwords.words("english")
    english_stopwords.append("please")
    filtered_words = [word for word in words if word not in english_stopwords]
    return filtered_words

def stem_words(words):
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()
    stemmed_words = [wnl.lemmatize(word) if wnl.lemmatize(word).endswith("e") else ps.stem(word) for word in words]
    return stemmed_words


def preprocess_utterance(utterance):
    sentence = to_lowercase(utterance) # change to lowercase
    sentence = expand_abbreviations(sentence) # expand abbreviations like "I'm" or "can't"
    words = word_tokenize(sentence) # word tokenization
    words = remove_punctuation(words) # removes special characters, leaves numbers in
    words = remove_stopwords(words) # removes stopwords like "I", "here" or "to"
    words = stem_words(words)
    return words


def get_intent(utterance=""):
    if utterance == "":
        return "BUILTIN.FallbackIntent"
    
    words = preprocess_utterance(utterance)
    words_joined = " ".join(words)
    
    for keyword in range(len(utterances)):
        if utterances[keyword][1].match(words_joined):
            intent = utterances[keyword][0]
            if intent == "StartApplication" or intent == "StopApplication":
                argument = re.search(r"\d+$", words_joined).group()
                return utterances[keyword][0], argument
            else:
                return utterances[keyword][0], "None"
    # if nothing is recognized
    return "BUILTIN.FallbackIntent"

'''
intent, argument = get_intent("help")
print(intent)
print(argument)
'''
