from fastapi import FastAPI, HTTPException
from models import MatchRequest
from services.matchmaker import Matchmaker

app = FastAPI()
matchmaker = None  # ainda não instanciado

@app.on_event("startup")
async def startup_event():
    global matchmaker
    matchmaker = Matchmaker()

@app.post("/matches/{tipo}")
async def get_matches(tipo: str, request: MatchRequest):
    if matchmaker is None:
        raise HTTPException(status_code=503, detail="Matchmaker ainda não carregado.")
    if tipo not in ['colaboracao', 'permuta', 'apoio']:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use: colaboracao, permuta ou apoio")
    return matchmaker.calcular_matches_por_tipo(request.kawaiid, tipo, request.top_n)

@app.post("/matches/all")
async def get_all_matches(request: MatchRequest):
    if matchmaker is None:
        raise HTTPException(status_code=503, detail="Matchmaker ainda não carregado.")
    return {
        'colaboracao': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'colaboracao', request.top_n),
        'permuta': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'permuta', request.top_n),
        'apoio': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'apoio', request.top_n)
    }
