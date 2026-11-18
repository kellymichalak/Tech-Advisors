import glob, json, re, html, urllib.request
from urllib.parse import quote

# 1. Mostra as chaves exatas de um tópico para não errarmos o nome da aba de áudio
with open("../js/conteudos/1em_fisica.js", "r", encoding="utf-8") as f:
    txt_amostra = f.read()
ini = txt_amostra.find("{")
dados_amostra, _ = json.JSONDecoder().raw_decode(txt_amostra, ini)
primeiro_id = next(iter(dados_amostra))
print("Chaves do tópico:", list(dados_amostra[primeiro_id].keys()))
if "formatos" in dados_amostra[primeiro_id]:
    print("Chaves em formatos:", list(dados_amostra[primeiro_id]["formatos"].keys()))

# 2. Busca as 3 MELHORES aulas didáticas brasileiras (priorizando Brasil Escola, Descomplica, Toda Matéria, Boaro, Noslen, etc.)
CANAIS_CONFIÁVEIS = [
    "brasil escola", "descomplica", "toda matéria", "toda materia",
    "boaro", "noslen", "gis com giz", "parabólica", "parabolica",
    "jubilut", "ferretto", "proenem", "stoodi", "me salva", "mundo educação"
]

cache_top3 = {}

def buscar_melhores_aulas_br(titulo, materia_nome):
    chave = f"{materia_nome}::{titulo}"
    if chave in cache_top3:
        return cache_top3[chave]

    query = quote(f"{titulo} {materia_nome} aula resumo enem")
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "pt-BR,pt;q=0.9"
            }
        )
        pagina = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", errors="ignore")
        # Extrai blocos com videoId e título/canal próximos
        matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"([^"]+)"\}', pagina)
        vistos = set()
        pontuados = []
        for vid, tit_vid in matches:
            if vid in vistos:
                continue
            vistos.add(vid)
            low = tit_vid.lower()
            # Penaliza lives gigantes ou cortes aleatórios
            if any(p in low for p in ["live", "ao vivo", "podcast completo", "2 horas", "3 horas", "shorts"]):
                score = -5
            else:
                score = 1
            if any(c in low for c in CANAIS_CONFIÁVEIS):
                score += 10
            if any(w in low for w in ["resumo", "aula", "enem", "explicação", "explicacao", "exercícios"]):
                score += 4
            pontuados.append((score, vid, tit_vid))

        pontuados.sort(key=lambda x: x[0], reverse=True)
        top3 = [(vid, tit) for _, vid, tit in pontuados[:3]]
        if not top3:
            top3 = [("M7lc1UVf-VE", f"Aula de {titulo}")]
        cache_top3[chave] = top3
        return top3
    except Exception:
        cache_top3[chave] = [("M7lc1UVf-VE", f"Aula de {titulo}")]
        return cache_top3[chave]

def extrair_todo_texto_didatico(obj_topico):
    # Pega texto de TODAS as abas textuais (resumo, mapa mental, passo a passo, analogia, dicas)
    partes_texto = []
    def coletar(no):
        if isinstance(no, dict):
            mid = no.get("id", "")
            if mid in ("audioaula_podcast", "video_whiteboard", "simulador_virtual", "quiz_interativo"):
                return
            for k, v in no.items():
                if k in ("audioaula_podcast", "video_whiteboard", "simulador_virtual", "quiz_interativo"):
                    continue
                if isinstance(v, str) and len(v) > 60:
                    limpo = re.sub(r"<[^>]+>", " ", v)
                    limpo = re.sub(r"\s+", " ", limpo).strip()
                    if len(limpo) > 40:
                        partes_texto.append(limpo)
                else:
                    coletar(v)
        elif isinstance(no, list):
            for item in no:
                coletar(item)
    coletar(obj_topico)
    return " ".join(partes_texto)

def montar_audio_completo(titulo, texto_completo):
    sentencas = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto_completo) if len(s.strip()) > 18]
    # Remove duplicatas mantendo ordem
    unicas = []
    for s in sentencas:
        if s not in unicas:
            unicas.append(s)

    if not unicas:
        unicas = [f"Nesta aula vamos estudar os pontos fundamentais de {titulo}."]

    blocos = [ " ".join(unicas[i:i+2]) for i in range(0, min(len(unicas), 16), 2) ]
    cards = "".join([
        f"<div class='audio-bloco' data-idx='{idx}' style='display:flex;gap:12px;align-items:flex-start;background:#0f172a;border:1px solid #334155;padding:14px 16px;border-radius:14px;margin-bottom:10px;transition:all 0.25s;'>"
        f"<span style='background:#4f46e5;color:#fff;font-size:0.75em;font-weight:800;padding:4px 9px;border-radius:8px;flex-shrink:0;'>{idx+1:02d}</span>"
        f"<div class='audio-texto-fala' style='color:#f1f5f9;font-size:0.98em;line-height:1.72;'>{html.escape(b)}</div>"
        f"</div>"
        for idx, b in enumerate(blocos)
    ])

    return (
        "<div class='audio-player-box' style='background:linear-gradient(135deg,#1e1b4b,#0f172a);color:#f8fafc;padding:24px;border-radius:20px;border:1px solid #4338ca;'>"
        "<div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:16px;'>"
        f"<div><div style='font-size:0.76em;text-transform:uppercase;letter-spacing:1px;color:#34d399;font-weight:800;'>🎧 Áudio-Aula Guiada do Conteúdo</div>"
        f"<div style='font-weight:800;font-size:1.16em;margin-top:2px;'>{html.escape(titulo)}</div></div>"
        "<span class='audio-status' style='background:rgba(16,185,129,0.2);border:1px solid #10b981;color:#6ee7b7;padding:6px 14px;border-radius:999px;font-size:0.82em;font-weight:700;'>Pronto para ouvir</span>"
        "</div>"
        "<div style='background:#020617;border:1px solid #334155;border-radius:16px;padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;'>"
        "<button type='button' class='btn-play-audio' onclick='window.tocarAudioNaTela(this)' style='background:#10b981;color:#022c22;border:none;padding:10px 22px;border-radius:999px;font-weight:800;cursor:pointer;font-size:0.95em;'>▶ Ouvir Explicação</button>"
        "<button type='button' onclick='window.pausarOuPararAudio(this)' style='background:#334155;color:#f8fafc;border:none;padding:10px 14px;border-radius:999px;font-weight:700;cursor:pointer;font-size:0.86em;'>⏹ Parar</button>"
        "<select class='audio-voz-sel' style='background:#1e293b;color:#38bdf8;border:1px solid #38bdf8;border-radius:999px;padding:7px 12px;font-size:0.82em;font-weight:700;max-width:210px;'>"
        "<option value=''>🗣️ Voz PT-BR</option>"
        "</select>"
        "<select class='audio-vel' style='background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:999px;padding:7px 12px;font-size:0.82em;font-weight:700;'>"
        "<option value='1.0'>1.0x</option>"
        "<option value='1.2'>1.2x</option>"
        "<option value='0.85'>0.85x</option>"
        "</select>"
        "<div style='width:100%;margin-top:4px;'>"
        "<div style='height:7px;background:#1e293b;border-radius:999px;overflow:hidden;'>"
        "<div class='audio-prog-bar' style='width:0%;height:100%;background:linear-gradient(90deg,#38bdf8,#10b981);transition:width 0.3s;'></div>"
        "</div>"
        "<div class='audio-legenda' style='font-size:0.8em;color:#94a3b8;margin-top:6px;'>Clique em <strong>▶ Ouvir Explicação</strong> para escutar o roteiro completo abaixo.</div>"
        "</div></div>"
        f"<div class='audio-lista-partes'>{cards}</div>"
        "</div>"
    )

def montar_video_curado(titulo, top3):
    vid_principal = top3[0][0]
    q_yt = quote(f"{titulo} aula resumo ensino medio")
    url_yt_outros = f"https://www.youtube.com/results?search_query={q_yt}"

    botoes_aulas = "".join([
        f"<button type='button' onclick=\"this.closest('.video-aula-box').querySelector('iframe').src='https://www.youtube.com/embed/{vid}?rel=0&hl=pt-BR'\" "
        f"style='background:{'#38bdf8' if i==0 else '#1e293b'};color:{'#020617' if i==0 else '#e2e8f0'};border:1px solid #38bdf8;padding:7px 13px;border-radius:999px;font-size:0.8em;font-weight:700;cursor:pointer;'>"
        f"Aula {i+1}: {html.escape(t[:34])}{'...' if len(t)>34 else ''}</button>"
        for i, (vid, t) in enumerate(top3)
    ])

    return (
        "<div class='video-aula-box' style='padding:22px;border-radius:20px;background:#0f172a;border:1px solid #334155;'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:12px;'>"
        f"<div><div style='font-size:0.76em;font-weight:800;color:#f87171;letter-spacing:1px;'>▶️ VIDEOAULAS SELECIONADAS (ENSINO MÉDIO / ENEM)</div>"
        f"<div style='font-size:1.14em;font-weight:800;color:#f8fafc;'>{html.escape(titulo)}</div></div>"
        f"<a href='{url_yt_outros}' target='_blank' rel='noopener noreferrer' style='display:inline-flex;align-items:center;gap:6px;background:#1e293b;color:#cbd5e1;border:1px solid #475569;padding:8px 14px;border-radius:999px;font-weight:700;text-decoration:none;font-size:0.84em;'>Ver mais no YouTube ↗</a>"
        "</div>"
        f"<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;'>{botoes_aulas}</div>"
        "<div style='position:relative;width:100%;max-width:860px;margin:0 auto;padding-bottom:52%;border-radius:16px;overflow:hidden;border:2px solid #334155;background:#020617;box-shadow:0 12px 28px rgba(0,0,0,0.45);'>"
        f"<iframe src='https://www.youtube.com/embed/{vid_principal}?rel=0&hl=pt-BR' title='Videoaula: {html.escape(titulo)}' loading='lazy' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' allowfullscreen style='position:absolute;top:0;left:0;width:100%;height:100%;border:0;'></iframe>"
        "</div></div>"
    )

decoder = json.JSONDecoder()
arquivos = sorted(glob.glob("../js/conteudos/*.js"))
total = 0

for idx_arq, arq in enumerate(arquivos, 1):
    mat = arq.split("_")[-1].replace(".js", "")
    with open(arq, "r", encoding="utf-8") as f:
        txt = f.read()

    out = []
    pos = 0
    while pos < len(txt):
        ini = txt.find("{", pos)
        if ini == -1:
            out.append(txt[pos:])
            break
        try:
            dados, fim = decoder.raw_decode(txt, ini)
            out.append(txt[pos:ini])
            if isinstance(dados, dict):
                for tid, obj in dados.items():
                    if not isinstance(obj, dict):
                        continue
                    tit = obj.get("titulo") or obj.get("nome") or tid
                    texto_rico = extrair_todo_texto_didatico(obj)
                    top3_videos = buscar_melhores_aulas_br(tit, mat)

                    def sub(no):
                        global total
                        if isinstance(no, dict):
                            if no.get("id") == "audioaula_podcast" and isinstance(no.get("html"), str):
                                no["html"] = montar_audio_completo(tit, texto_rico)
                                total += 1
                            elif no.get("id") == "video_whiteboard" and isinstance(no.get("html"), str):
                                no["html"] = montar_video_curado(tit, top3_videos)
                                total += 1
                            for k, v in list(no.items()):
                                if k == "audioaula_podcast" and isinstance(v, str):
                                    no[k] = montar_audio_completo(tit, texto_rico)
                                    total += 1
                                elif k == "video_whiteboard" and isinstance(v, str):
                                    no[k] = montar_video_curado(tit, top3_videos)
                                    total += 1
                                else:
                                    sub(v)
                        elif isinstance(no, list):
                            for it in no:
                                sub(it)
                    sub(obj)

            out.append(json.dumps(dados, ensure_ascii=False, indent=2))
            pos = fim
        except Exception:
            out.append(txt[pos:ini+1])
            pos = ini + 1

    with open(arq, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"[{idx_arq}/{len(arquivos)}] {arq} atualizado")

with open("../pages/resumos.html", "r", encoding="utf-8") as f:
    h = f.read()
h = re.sub(r"v=\d+", "v=20261130", h)
with open("../pages/resumos.html", "w", encoding="utf-8") as f:
    f.write(h)

print(f"✅ PRONTO! {total} blocos atualizados com curadoria didática + áudio completo (v=20261130)!")
