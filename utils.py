from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords

stemmer = None
stop_words = None

def init_nltk():
    global stemmer, stop_words
    if stemmer is None:
        stemmer = RSLPStemmer()
    if stop_words is None:
        stop_words = set(stopwords.words('portuguese'))

def preprocessar_texto(texto: str) -> str:
    init_nltk()
    palavras = word_tokenize(texto.lower())
    radicais = [stemmer.stem(p) for p in palavras if p.isalpha() and p not in stop_words]
    return " ".join(radicais)
