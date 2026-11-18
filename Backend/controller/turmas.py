from fastapi import APIRouter, HTTPException, Response, status
from typing import List, Optional
from database import supabase
from models.turmas import TurmaCreate, TurmaResponse

router = APIRouter(prefix="/turmas", tags=["Turmas"])

# String de colunas que faz o join com a tabela professor
COLUNAS = (
    "id_turma, codigo_turma, nome_turma, serie_ano, disciplina, turno, "
    "ano_letivo, status_turma, id_professor, professor:professor(nome)"
)


def validar_professor(id_professor: int):
    resposta = (
        supabase.table("professor")
        .select("id_professor, nome")
        .eq("id_professor", id_professor)
        .execute()
    )
    if not resposta.data:
        raise HTTPException(
            status_code=400,
            detail="Professor não encontrado. Consulte um professor cadastrado.",
        )


def preparar_saida(registro: dict) -> dict:
    professor = registro.get("professor")
    if not professor:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível consultar o professor da turma.",
        )
    return {
        "id_turma": registro["id_turma"],
        "codigo_turma": registro["codigo_turma"],
        "nome_turma": registro["nome_turma"],
        "serie_ano": registro["serie_ano"],
        "disciplina": registro["disciplina"],
        "turno": registro["turno"],
        "ano_letivo": registro["ano_letivo"],
        "status_turma": registro["status_turma"],
        "id_professor": registro["id_professor"],
        "nome_professor": professor["nome"],
    }


def buscar_turma(id_turma: int):
    resposta = (
        supabase.table("turma")
        .select(COLUNAS)
        .eq("id_turma", id_turma)
        .execute()
    )
    if not resposta.data:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    return preparar_saida(resposta.data[0])


@router.post("", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def criar_turma(turma: TurmaCreate):
    validar_professor(turma.id_professor)
    dados = turma.model_dump() if hasattr(turma, "model_dump") else turma.dict()
    res = supabase.table("turma").insert(dados).execute()
    if not res.data:
        raise HTTPException(status_code=502, detail="O Supabase não retornou a turma cadastrada.")
    id_novo = res.data[0]["id_turma"]
    return buscar_turma(id_novo)


@router.get("", response_model=List[TurmaResponse])
def listar_turmas(id_professor: Optional[int] = None):
    query = supabase.table("turma").select(COLUNAS).order("id_turma")
    if id_professor:
        query = query.eq("id_professor", id_professor)
    res = query.execute()
    return [preparar_saida(registro) for registro in res.data or []]


@router.get("/{id_turma}", response_model=TurmaResponse)
def consultar_turma(id_turma: int):
    return buscar_turma(id_turma)


@router.put("/{id_turma}", response_model=TurmaResponse)
def atualizar_turma(id_turma: int, turma: TurmaCreate):
    buscar_turma(id_turma)
    validar_professor(turma.id_professor)
    dados = turma.model_dump() if hasattr(turma, "model_dump") else turma.dict()
    res = (
        supabase.table("turma")
        .update(dados)
        .eq("id_turma", id_turma)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    return buscar_turma(id_turma)


@router.delete("/{id_turma}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_turma(id_turma: int):
    res = supabase.table("turma").delete().eq("id_turma", id_turma).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Turma não encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)