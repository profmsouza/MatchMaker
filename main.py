from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from models import MatchRequest
from services.matchmaker import Matchmaker
from datetime import timedelta

app = FastAPI(title="Matchmaker API", version="1.0.0")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa cache e serviços
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

matchmaker = Matchmaker()

@app.get("/health", tags=["Monitoramento"])
async def health_check():
    return {"status": "healthy", "perfis_carregados": len(matchmaker.perfis)}

@app.post("/matches/{tipo}")
@cache(expire=timedelta(minutes=30))
async def get_matches(tipo: str, request: MatchRequest):
    """Endpoint principal para obter matches por tipo"""
    if tipo not in ['colaboracao', 'permuta', 'apoio']:
        raise HTTPException(400, detail="Tipo inválido. Use: colaboracao, permuta ou apoio")
    
    try:
        return matchmaker.calcular_matches_por_tipo(request.kawaiid, tipo, request.top_n)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/matches/all")
@cache(expire=timedelta(minutes=30))
async def get_all_matches(request: MatchRequest):
    """Endpoint para obter todos os tipos de matches"""
    try:
        return {
            'colaboracao': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'colaboracao', request.top_n),
            'permuta': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'permuta', request.top_n),
            'apoio': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'apoio', request.top_n)
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
