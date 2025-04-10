import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords
import os

def download_nltk_resources():
    resources = ['rslp', 'punkt', 'stopwords']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}') if resource == 'punkt' else nltk.data.find(f'stemmers/{resource}') if resource == 'rslp' else nltk.data.find(f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, download_dir='/opt/render/nltk_data')
            nltk.data.path.append('/opt/render/nltk_data')

# Garante que os recursos sejam baixados
download_nltk_resources()

# Configurações após garantir os recursos
stemmer = RSLPStemmer()
stop_words = set(stopwords.words('portuguese'))

def preprocessar_texto(texto: str) -> str:
    palavras = word_tokenize(texto.lower())
    radicais = [stemmer.stem(p) for p in palavras if p.isalpha() and p not in stop_words]
    return " ".join(radicais)
