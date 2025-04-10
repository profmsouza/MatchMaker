from pydantic import BaseModel
from typing import List, Dict

class MatchRequest(BaseModel):
    kawaiid: str
    top_n: int = 5
