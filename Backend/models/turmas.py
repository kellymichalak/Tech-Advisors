
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class TurmaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo_turma: str
    nome_turma: str
    serie_ano: str
    disciplina: str
    turno: str
    ano_letivo: int
    id_professor: int = Field(gt=0)
    status_turma: Optional[str] = "ativa"

class TurmaResponse(TurmaCreate):
    id_turma: int
    nome_professor: str
  