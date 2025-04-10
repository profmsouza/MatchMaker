from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords

stemmer = RSLPStemmer()
stop_words = set(stopwords.words('portuguese'))

def preprocessar_texto(texto: str) -> str:
    palavras = word_tokenize(texto.lower())
    radicais = [stemmer.stem(p) for p in palavras if p.isalpha() and p not in stop_words]
    return " ".join(radicais)
