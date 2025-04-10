from database import supabase
from utils import preprocessar_texto
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk

nltk.download('rslp')
nltk.download('punkt')
nltk.download('stopwords')

class Matchmaker:
    def __init__(self):
        self.stemmer = RSLPStemmer()
        self.stop_words = set(stopwords.words('portuguese'))
        self.vectorizers = {
            'colaboracao': TfidfVectorizer(),
            'permuta': TfidfVectorizer(),
            'apoio': TfidfVectorizer()
        }
        self.perfis = self.carregar_perfis()
        self.treinar_modelos()

    def carregar_perfis(self):
        response = supabase.table('perfis_matches').select("*").execute()
        return response.data

    def treinar_modelos(self):
        textos_treinamento = {tipo: [] for tipo in self.vectorizers.keys()}
        for perfil in self.perfis:
            for tipo in self.vectorizers.keys():
                textos_treinamento[tipo].extend(perfil.get(f'{tipo}_oferece', []))
                textos_treinamento[tipo].extend(perfil.get(f'{tipo}_necessita', []))
        for tipo, textos in textos_treinamento.items():
            textos_processados = [preprocessar_texto(t) for t in textos if t]
            if textos_processados:
                self.vectorizers[tipo].fit(textos_processados)

    def calcular_matches_por_tipo(self, kawaiid_alvo, tipo, top_n):
        perfil_alvo = next((p for p in self.perfis if p['kawaiid'] == kawaiid_alvo), None)
        if not perfil_alvo:
            return {}

        necessidades = perfil_alvo.get(f'{tipo}_necessita', [])
        resultados = {}

        for necessidade in necessidades:
            if not necessidade:
                continue
            necessidade_pp = preprocessar_texto(necessidade)
            vec_necessidade = self.vectorizers[tipo].transform([necessidade_pp])
            matches = []

            for perfil in self.perfis:
                if perfil['kawaiid'] == kawaiid_alvo:
                    continue
                ofertas = perfil.get(f'{tipo}_oferece', [])
                if not ofertas:
                    continue
                ofertas_pp = " ".join([preprocessar_texto(o) for o in ofertas])
                vec_ofertas = self.vectorizers[tipo].transform([ofertas_pp])
                similaridade = cosine_similarity(vec_necessidade, vec_ofertas)[0][0]
                if similaridade > 0:
                    matches.append({'kawaiid': perfil['kawaiid'], 'score': float(similaridade)})

            resultados[necessidade] = sorted(matches, key=lambda x: x['score'], reverse=True)[:top_n]

        return resultados
