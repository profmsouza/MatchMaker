from database import supabase
from utils import preprocessar_texto
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List

class Matchmaker:
    def __init__(self):
        self.vectorizers = {
            'colaboracao': TfidfVectorizer(),
            'permuta': TfidfVectorizer(),
            'apoio': TfidfVectorizer()
        }
        self.perfis = self.carregar_perfis()
        self.treinar_modelos()

    def carregar_perfis(self) -> List[Dict]:
        """Carrega perfis do Supabase com tratamento de erros"""
        try:
            response = supabase.table('perfis_matches').select("*").execute()
            return response.data or []
        except Exception as e:
            print(f"Erro ao carregar perfis: {str(e)}")
            return []

    def treinar_modelos(self):
        """Treina modelos com fallback para dados vazios"""
        textos_treinamento = {tipo: [] for tipo in self.vectorizers.keys()}
        
        for perfil in self.perfis:
            for tipo in self.vectorizers.keys():
                textos_treinamento[tipo].extend(perfil.get(f'{tipo}_oferece', []))
                textos_treinamento[tipo].extend(perfil.get(f'{tipo}_necessita', []))
        
        for tipo, textos in textos_treinamento.items():
            textos_processados = [preprocessar_texto(t) for t in textos if t]
            if textos_processados:
                try:
                    self.vectorizers[tipo].fit(textos_processados)
                except ValueError:
                    print(f"Falha ao treinar modelo para {tipo} - dados insuficientes")

    def calcular_matches_por_tipo(self, kawaiid_alvo: str, tipo: str, top_n: int = 5) -> Dict[str, List[Dict]]:
        """Calcula matches com otimização de performance"""
        if tipo not in self.vectorizers:
            return {}

        perfil_alvo = next((p for p in self.perfis if p['kawaiid'] == kawaiid_alvo), None)
        if not perfil_alvo:
            return {}

        necessidades = [n for n in perfil_alvo.get(f'{tipo}_necessita', []) if n]
        if not necessidades:
            return {}

        # Pré-processa todas as ofertas uma vez
        ofertas_disponiveis = []
        for perfil in self.perfis:
            if perfil['kawaiid'] != kawaiid_alvo:
                ofertas = [o for o in perfil.get(f'{tipo}_oferece', []) if o]
                if ofertas:
                    ofertas_disponiveis.append({
                        'kawaiid': perfil['kawaiid'],
                        'texto': " ".join([preprocessar_texto(o) for o in ofertas])
                    })

        resultados = {}
        for necessidade in necessidades:
            necessidade_pp = preprocessar_texto(necessidade)
            vec_necessidade = self.vectorizers[tipo].transform([necessidade_pp])
            
            matches = []
            for oferta in ofertas_disponiveis:
                vec_oferta = self.vectorizers[tipo].transform([oferta['texto']])
                similaridade = cosine_similarity(vec_necessidade, vec_oferta)[0][0]
                if similaridade > 0:
                    matches.append({
                        'kawaiid': oferta['kawaiid'],
                        'score': round(float(similaridade), 4)
                    })

            if matches:
                resultados[necessidade] = sorted(matches, key=lambda x: x['score'], reverse=True)[:top_n]

        return resultados
