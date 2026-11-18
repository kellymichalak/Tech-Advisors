import threading
import os
import re
import threading
import os
import re
import threading
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Exemplo comum de middleware
from controller.professores import router as professores_router
from controller.turmas import router as turmas_router


# 1. Primeiro você cria a instância
app = FastAPI()

# 2. Depois você adiciona os middlewares ou rotas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Importação de todos os controllers
from controller import (
    auth,
    professores,
    responsaveis,
    tipos_deficiencia,
    niveis_suporte,
    turmas,
    alunos,
    alunos_deficiencia,
    config_acessibilidade,
    tipos_atividade,
    atividades,
    recursos_acessibilidade,
    atividade_recurso,
    respostas,
    resposta_recurso,
    analise_ia
)

app = FastAPI(
    title="Tech Advisors API",
    version="4.0.0",
    description="API Completa com suporte total a 15 tabelas."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registo de todos os roteadores
app.include_router(auth.router)
app.include_router(professores.router)
app.include_router(responsaveis.router)
app.include_router(tipos_deficiencia.router)
app.include_router(niveis_suporte.router)
app.include_router(turmas.router)
app.include_router(alunos.router)
app.include_router(alunos_deficiencia.router)
app.include_router(config_acessibilidade.router)
app.include_router(tipos_atividade.router)
app.include_router(atividades.router)
app.include_router(recursos_acessibilidade.router)
app.include_router(atividade_recurso.router)
app.include_router(respostas.router)
app.include_router(resposta_recurso.router)
app.include_router(analise_ia.router)

@app.get("/")
def root():
    return {"message": "API Tech Advisors rodando com sucesso!"}
# === ROTA DE TRANSCRIÇÃO SINCRONIZADA DO YOUTUBE ===
_CACHE_TRANSCRICOES_YT = {}

import json
from pathlib import Path

_DIR_CACHE_WHISPER = Path(__file__).resolve().parent / "cache_transcricoes"
_DIR_CACHE_WHISPER.mkdir(parents=True, exist_ok=True)
_WHISPER_MODEL_INST = None

def _obter_modelo_whisper():
    global _WHISPER_MODEL_INST
    if _WHISPER_MODEL_INST is None:
        from faster_whisper import WhisperModel
        _WHISPER_MODEL_INST = WhisperModel("small", device="cpu", compute_type="int8")
    return _WHISPER_MODEL_INST

_CORRECOES_FONETICAS_YT = [
    # Saudações e vícios de transcrição falada
    (r"^\s*a\s+galerinh[as]\b", "Fala galerinha"),
    (r"\bgalerinh[as]\b", "galerinha"),
    (r"\bnossa\s+viola\b", "nossa videoaula"),
    (r"\bdaa\b", "da"),
    (r"\bdoo\b", "do"),
    (r"\bv[ií]deoaula\b", "videoaula"),
    (r"\bmatem[aá]tica no papel\b", "Matemática no Papel"),
    # Escalas termométricas e Física
    (r"\bcau[eê]\s+meteria\b", "e calorimetria"),
    (r"\bcaue\s+metria\b", "e calorimetria"),
    (r"\bcalor\s+metria\b", "calorimetria"),
    (r"\bcalo\s+metria\b", "calorimetria"),
    (r"\bcalorimetria\b", "calorimetria"),
    (r"\bgraus\s+c[eé]us\b", "graus Celsius"),
    (r"\bescala\s+c[eé]us\b", "escala Celsius"),
    (r"\bem\s+c[eé]us\b", "em Celsius"),
    (r"\bpara\s+c[eé]us\b", "para Celsius"),
    (r"\bde\s+c[eé]us\b", "de Celsius"),
    (r"\bc[eé]us\b", "Celsius"),
    (r"\bc[eé]ls\b", "Celsius"),
    (r"\bc[eé]l[cs]ius\b", "Celsius"),
    (r"\bfah?renheit\b", "Fahrenheit"),
    (r"\bfahenheit\b", "Fahrenheit"),
    (r"\bfarenheit\b", "Fahrenheit"),
    (r"\bfarenhait\b", "Fahrenheit"),
    (r"\bkelvin\b", "Kelvin"),
    (r"\btermometricas\b", "termométricas"),
    (r"\btermometrica\b", "termométrica"),
    (r"\btermodinamica\b", "termodinâmica"),
    (r"\bcinematica\b", "cinemática"),
    (r"\bdinamica\b", "dinâmica"),
    (r"\beletromagnetismo\b", "eletromagnetismo"),
    # Química
    (r"\bestequiometria\b", "estequiometria"),
    (r"\beletrons\b", "elétrons"),
    (r"\beletron\b", "elétron"),
    (r"\bprotons\b", "prótons"),
    (r"\bproton\b", "próton"),
    (r"\bneutrons\b", "nêutrons"),
    (r"\bneutron\b", "nêutron"),
    (r"\bmolecula\b", "molécula"),
    (r"\bmoleculas\b", "moléculas"),
    (r"\batomo\b", "átomo"),
    (r"\batomos\b", "átomos"),
    (r"\boxidacao\b", "oxidação"),
    (r"\breducao\b", "redução"),
    # Biologia
    (r"\bmitocondria\b", "mitocôndria"),
    (r"\bmitocondrias\b", "mitocôndrias"),
    (r"\bfotossintese\b", "fotossíntese"),
    (r"\bcloroplasto\b", "cloroplasto"),
    (r"\bribossomo\b", "ribossomo"),
    (r"\bribossomos\b", "ribossomos"),
    (r"\blisossomo\b", "lisossomo"),
    (r"\blisossomos\b", "lisossomos"),
    (r"\beucarionte\b", "eucarionte"),
    (r"\beucariontes\b", "eucariontes"),
    (r"\bprocarionte\b", "procarionte"),
    (r"\bprocariontes\b", "procariontes"),
    (r"\bcelula\b", "célula"),
    (r"\bcelulas\b", "células"),
    (r"\bnucleo\b", "núcleo"),
    (r"\bmembrana plasmatica\b", "membrana plasmática"),
    (r"\bgenetica\b", "genética"),
    (r"\bcromossomo\b", "cromossomo"),
    (r"\bcromossomos\b", "cromossomos"),
    (r"\bproteina\b", "proteína"),
    (r"\bproteinas\b", "proteínas"),
    (r"\baminoacido\b", "aminoácido"),
    (r"\baminoacidos\b", "aminoácidos"),
    (r"\bevolucao\b", "evolução"),
    # Matemática e Humanas
    (r"\bequacao\b", "equação"),
    (r"\bequacoes\b", "equações"),
    (r"\bfuncao\b", "função"),
    (r"\bfuncoes\b", "funções"),
    (r"\bestatistica\b", "estatística"),
    (r"\bhistoria\b", "história"),
    (r"\bconstituicao\b", "Constituição"),
    (r"\brevolucao\b", "revolução"),
]

def _limpar_texto_legenda_yt(texto: str) -> str:
    t = re.sub(r"\[(?:m[uú]sica|aplausos|risos|music|applause)\]", " ", str(texto or ""), flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for padrao, subst in _CORRECOES_FONETICAS_YT:
        t = re.sub(padrao, subst, t, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", t).strip()

_LOCKS_WHISPER = {}
_LOCKS_WHISPER_GUARD = threading.Lock()

def _obter_lock_whisper(vid: str):
    with _LOCKS_WHISPER_GUARD:
        if vid not in _LOCKS_WHISPER:
            _LOCKS_WHISPER[vid] = threading.Lock()
        return _LOCKS_WHISPER[vid]

def _transcrever_audio_whisper_word_level(vid: str):
    import tempfile
    import yt_dlp

    url = f"https://www.youtube.com/watch?v={vid}"
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tmpl = os.path.join(tmpdir, "audio.%(ext)s")
        audio_path = None
        ultimo_erro_dl = None
        for cliente_yt in (None, ["android"]):
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": out_tmpl,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "nocheckcertificate": True,
            }
            if cliente_yt:
                ydl_opts["extractor_args"] = {"youtube": {"player_client": cliente_yt}}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    cand = ydl.prepare_filename(info)
                    if os.path.exists(cand) and os.path.getsize(cand) > 50000:
                        audio_path = cand
                        break
            except Exception as e_dl:
                ultimo_erro_dl = e_dl
        if not audio_path:
            raise ultimo_erro_dl or RuntimeError("Falha ao baixar áudio do YouTube")

        model = _obter_modelo_whisper()
        prompt_ini = "Aula de ensino médio em português: Matemática no Papel, Física, Química, Biologia, História, Geografia, Celsius, Fahrenheit, Kelvin, termologia, videoaula."
        segs_iter, _ = model.transcribe(
            audio_path,
            language="pt",
            vad_filter=True,
            word_timestamps=True,
            initial_prompt=prompt_ini
        )
        segs_lista = list(segs_iter)
        if not segs_lista:
            segs_iter2, _ = model.transcribe(
                audio_path,
                language="pt",
                vad_filter=False,
                word_timestamps=True,
                initial_prompt=prompt_ini
            )
            segs_lista = list(segs_iter2)
        segs_iter = segs_lista

        segmentos = []
        for s in segs_iter:
            txt_seg = _limpar_texto_legenda_yt(s.text)
            if not txt_seg:
                continue
            palavras = []
            for w in (getattr(s, "words", None) or []):
                w_txt = _limpar_texto_legenda_yt(getattr(w, "word", ""))
                if w_txt:
                    palavras.append({
                        "word": w_txt,
                        "start": round(float(w.start), 3),
                        "end": round(float(w.end), 3)
                    })
            segmentos.append({
                "start": round(float(s.start), 3),
                "duration": round(max(0.2, float(s.end) - float(s.start)), 3),
                "text": txt_seg,
                "words": palavras
            })
        return segmentos

@app.get("/api/transcricao/{video_id}")
def obter_transcricao_youtube(video_id: str):
    vid = re.sub(r"[^A-Za-z0-9_-]", "", video_id or "")
    if not vid:
        return {"ok": False, "segmentos": []}

    arq_cache = _DIR_CACHE_WHISPER / f"{vid}.json"
    if arq_cache.exists():
        try:
            data = json.loads(arq_cache.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                for seg in data:
                    if isinstance(seg, dict):
                        if "text" in seg:
                            seg["text"] = _limpar_texto_legenda_yt(seg["text"])
                        if isinstance(seg.get("words"), list):
                            for w in seg["words"]:
                                if isinstance(w, dict) and "word" in w:
                                    w["word"] = _limpar_texto_legenda_yt(w["word"])
                _CACHE_TRANSCRICOES_YT[vid] = data
                return {"ok": True, "video_id": vid, "fonte": "whisper_cache", "segmentos": data}
        except Exception:
            pass

    if vid in _CACHE_TRANSCRICOES_YT and any(s.get("words") for s in _CACHE_TRANSCRICOES_YT[vid]):
        return {"ok": True, "video_id": vid, "fonte": "whisper_mem", "segmentos": _CACHE_TRANSCRICOES_YT[vid]}

    # 1. Transcrição de alta precisão com timestamps reais por palavra (Faster-Whisper) com lock por video_id
    try:
        with _obter_lock_whisper(vid):
            if arq_cache.exists():
                data = json.loads(arq_cache.read_text(encoding="utf-8"))
                if isinstance(data, list) and data:
                    _CACHE_TRANSCRICOES_YT[vid] = data
                    return {"ok": True, "video_id": vid, "fonte": "whisper_cache", "segmentos": data}
            segs_whisper = _transcrever_audio_whisper_word_level(vid)
        if segs_whisper:
            _CACHE_TRANSCRICOES_YT[vid] = segs_whisper
            try:
                arq_cache.write_text(json.dumps(segs_whisper, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            return {"ok": True, "video_id": vid, "fonte": "whisper", "segmentos": segs_whisper}
    except Exception as e_whisper:
        print(f"[Whisper fallback para {vid}]: {e_whisper}")

    # 2. Fallback caso o download do áudio falhe
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            raw_items = YouTubeTranscriptApi.get_transcript(vid, languages=["pt", "pt-BR", "en"])
        else:
            raw_items = YouTubeTranscriptApi().fetch(vid, languages=["pt", "pt-BR", "en"])
        segmentos = []
        for item in raw_items:
            raw_txt = item.get("text", "") if isinstance(item, dict) else getattr(item, "text", "")
            raw_st = item.get("start", 0) if isinstance(item, dict) else getattr(item, "start", 0)
            raw_dur = item.get("duration", 2.0) if isinstance(item, dict) else getattr(item, "duration", 2.0)
            txt = _limpar_texto_legenda_yt(raw_txt)
            if txt:
                segmentos.append({"start": float(raw_st), "duration": float(raw_dur), "text": txt})
        if segmentos:
            _CACHE_TRANSCRICOES_YT[vid] = segmentos
            return {"ok": True, "video_id": vid, "fonte": "yt_fallback", "segmentos": segmentos}
    except Exception as e:
        return {"ok": False, "erro": str(e), "segmentos": []}

    return {"ok": False, "segmentos": []}
    if vid in _CACHE_TRANSCRICOES_YT:
        return {"ok": True, "video_id": vid, "segmentos": _CACHE_TRANSCRICOES_YT[vid]}

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        raw_items = None

        # Prioriza legenda revisada/manual em português antes da automática
        try:
            api_inst = YouTubeTranscriptApi() if not hasattr(YouTubeTranscriptApi, "list_transcripts") else YouTubeTranscriptApi
            tlist = api_inst.list(vid) if hasattr(api_inst, "list") else api_inst.list_transcripts(vid)
            escolhida = None
            try:
                escolhida = tlist.find_manually_created_transcript(["pt", "pt-BR"])
            except Exception:
                try:
                    escolhida = tlist.find_generated_transcript(["pt", "pt-BR"])
                except Exception:
                    for tr in tlist:
                        if str(getattr(tr, "language_code", "")).startswith("pt"):
                            escolhida = tr
                            break
            if escolhida is not None:
                raw_items = escolhida.fetch()
        except Exception:
            raw_items = None

        if raw_items is None:
            if hasattr(YouTubeTranscriptApi, "get_transcript"):
                raw_items = YouTubeTranscriptApi.get_transcript(vid, languages=["pt", "pt-BR", "en"])
            else:
                raw_items = YouTubeTranscriptApi().fetch(vid, languages=["pt", "pt-BR", "en"])

        segmentos = []
        for item in raw_items:
            raw_txt = item.get("text", "") if isinstance(item, dict) else getattr(item, "text", "")
            raw_st = item.get("start", 0) if isinstance(item, dict) else getattr(item, "start", 0)
            raw_dur = item.get("duration", 2.0) if isinstance(item, dict) else getattr(item, "duration", 2.0)
            txt = _limpar_texto_legenda_yt(raw_txt)
            if txt:
                segmentos.append({
                    "start": float(raw_st),
                    "duration": float(raw_dur),
                    "text": txt
                })

        if segmentos:
            _CACHE_TRANSCRICOES_YT[vid] = segmentos
            return {"ok": True, "video_id": vid, "segmentos": segmentos}
    except Exception as e:
        return {"ok": False, "erro": str(e), "segmentos": []}

    return {"ok": False, "segmentos": []}
    if vid in _CACHE_TRANSCRICOES_YT:
        return {"ok": True, "video_id": vid, "segmentos": _CACHE_TRANSCRICOES_YT[vid]}

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        segmentos = []
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            raw = YouTubeTranscriptApi.get_transcript(vid, languages=["pt", "pt-BR", "en"])
            for item in raw:
                txt = _limpar_texto_legenda_yt(item.get("text", ""))
                if txt:
                    segmentos.append({
                        "start": float(item.get("start", 0)),
                        "duration": float(item.get("duration", 2.0)),
                        "text": txt
                    })
        else:
            api = YouTubeTranscriptApi()
            fetched = api.fetch(vid, languages=["pt", "pt-BR", "en"])
            for snip in fetched:
                txt = _limpar_texto_legenda_yt(getattr(snip, "text", ""))
                if txt:
                    segmentos.append({
                        "start": float(getattr(snip, "start", 0)),
                        "duration": float(getattr(snip, "duration", 2.0)),
                        "text": txt
                    })

        if segmentos:
            _CACHE_TRANSCRICOES_YT[vid] = segmentos
            return {"ok": True, "video_id": vid, "segmentos": segmentos}
    except Exception as e:
        return {"ok": False, "erro": str(e), "segmentos": []}

    return {"ok": False, "segmentos": []}
