from fastapi import FastAPI, HTTPException
from models import MatchRequest
from services.matchmaker import Matchmaker
import os

app = FastAPI()
matchmaker = Matchmaker()

@app.post("/matches/{tipo}")
async def get_matches(tipo: str, request: MatchRequest):
    if tipo not in ['colaboracao', 'permuta', 'apoio']:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use: colaboracao, permuta ou apoio")
    try:
        return matchmaker.calcular_matches_por_tipo(request.kawaiid, tipo, request.top_n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/matches/all")
async def get_all_matches(request: MatchRequest):
    try:
        return {
            'colaboracao': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'colaboracao', request.top_n),
            'permuta': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'permuta', request.top_n),
            'apoio': matchmaker.calcular_matches_por_tipo(request.kawaiid, 'apoio', request.top_n)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
