cat << 'EOF' > /Users/kelly/TechAdvisors/frontend/converter.py
import os
import re
import json
import shutil

PASTA_BUSCA = os.path.join(os.path.expanduser("~"), "Downloads")
PASTA_SAIDA = os.path.join(os.getcwd(), "js", "conteudos")
CAMINHO_RESUMOS_JS = os.path.join(os.getcwd(), "js", "resumos.js")

# Limpa a pasta de saída anterior para recriar tudo limpo
if os.path.exists(PASTA_SAIDA):
    shutil.rmtree(PASTA_SAIDA)
os.makedirs(PASTA_SAIDA, exist_ok=True)

if not os.path.exists(CAMINHO_RESUMOS_JS):
    print("❌ Erro: Não encontrei o arquivo js/resumos.js.")
    exit(1)

with open(CAMINHO_RESUMOS_JS, "r", encoding="utf-8") as f:
    resumos_code = f.read()

# Mapeia todos os tópicos oficiais do seu resumos.js
padrao_topico = re.compile(
    r'"id"\s*:\s*"([^"]+)"[\s\S]*?'
    r'"serie"\s*:\s*"([^"]+)"[\s\S]*?'
    r'"materiaId"\s*:\s*"([^"]+)"[\s\S]*?'
    r'"nome"\s*:\s*"([^"]+)"'
)

mapa_topicos = {}
for m in padrao_topico.finditer(resumos_code):
    tid = m.group(1)
    mapa_topicos[tid] = {
        "id": tid,
        "serie": m.group(2),
        "materiaId": m.group(3),
        "nome": m.group(4)
    }

def normalizar_id(raw_id):
    raw_id = raw_id.strip()
    if raw_id in mapa_topicos:
        return raw_id
    # Corrige prefixos caso no .md esteja 'port_' e no resumos.js esteja 'por_'
    trocas = [
        ("port_", "por_"),
        ("ingl_", "ing_"),
        ("espa_", "esp_"),
        ("hist_", "his_"),
        ("geog_", "geo_"),
        ("soci_", "soc_"),
        ("filo_", "fil_"),
        ("biol_", "bio_"),
        ("fisi_", "fis_"),
        ("quim_", "qui_"),
        ("mate_", "mat_"),
        ("arte_", "art_"),
        ("edfi_", "edf_")
    ]
    for antigo, novo in trocas:
        if raw_id.startswith(antigo):
            candidato = novo + raw_id[len(antigo):]
            if candidato in mapa_topicos:
                return candidato
    return None

def md_para_html(md):
    # Remove linhas divisórias soltas ---
    md = re.sub(r"^\s*---+\s*$", "", md, flags=re.MULTILINE)
    # Títulos internos (##### -> h4)
    html = re.sub(r"^#####\s+(.*)$", r"<h4>\1</h4>", md, flags=re.MULTILINE)
    html = re.sub(r"^####\s+(.*)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    # Negrito e Itálico
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)
    # Listas com - ou *
    html = re.sub(r"^\s*[-*]\s+(.*)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>[\s\S]*?</li>)", r"<ul>\1</ul>", html)
    html = re.sub(r"</ul>\s*<ul>", "", html)
    # Listas numeradas (1. 2. 3.)
    html = re.sub(r"^\s*\d+\.\s+(.*)$", r"<li>\1</li>", html, flags=re.MULTILINE)

    # Tabelas Markdown simples
    linhas = html.split("\n")
    resultado_linhas = []
    em_tabela = False
    for linha in linhas:
        l_strip = linha.strip()
        if l_strip.startswith("|") and l_strip.endswith("|"):
            if re.match(r"^\|[\s\-:|]+\|$", l_strip):
                continue
            celulas = [c.strip() for c in l_strip.strip("|").split("|")]
            if not em_tabela:
                resultado_linhas.append('<table class="tabela-didatica"><thead><tr>' + "".join(f"<th>{c}</th>" for c in celulas) + "</tr></thead><tbody>")
                em_tabela = True
            else:
                resultado_linhas.append("<tr>" + "".join(f"<td>{c}</td>" for c in celulas) + "</tr>")
        else:
            if em_tabela:
                resultado_linhas.append("</tbody></table>")
                em_tabela = False
            resultado_linhas.append(linha)
    if em_tabela:
        resultado_linhas.append("</tbody></table>")

    html = "\n".join(resultado_linhas)

    paragrafos = []
    for p in html.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p.startswith(("<h", "<ul", "<ol", "<table", "<div", "<blockquote")):
            paragrafos.append(p)
        else:
            paragrafos.append(f"<p>{p.replace(chr(10), '<br>')}</p>")
    return "\n".join(paragrafos)

print(f"🔍 Lendo todos os módulos em: {PASTA_BUSCA}...")

agrupado_por_arquivo = {}
topicos_importados = set()

for raiz, _, arquivos in os.walk(PASTA_BUSCA):
    for nome_arq in sorted(arquivos):
        if not nome_arq.lower().endswith(".md"):
            continue
        caminho = os.path.join(raiz, nome_arq)
        try:
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                conteudo = f.read()
        except Exception:
            continue

        # Divide o arquivo pelos cabeçalhos ## MÓDULO ... (`id_do_topico`)
        partes_modulos = re.split(r"\n##\s+[^\n]*?\(`([a-z0-9_]+)`\)", conteudo, flags=re.IGNORECASE)

        for i in range(1, len(partes_modulos), 2):
            id_bruto = partes_modulos[i]
            corpo_modulo = partes_modulos[i + 1]

            tid = normalizar_id(id_bruto)
            if not tid:
                continue

            # Divide os formatos dentro do módulo pelo padrão #### ... (`id_formato`)
            partes_formatos = re.split(r"\n####\s+[^\n]*?\(`([a-z0-9_]+)`\)", corpo_modulo, flags=re.IGNORECASE)
            formatos_obj = {}

            for j in range(1, len(partes_formatos), 2):
                fmt_id = partes_formatos[j].strip()
                fmt_conteudo = partes_formatos[j + 1].strip()
                # Remove eventuais títulos de grupo (### 🔤 GRUPO ...) que ficaram no final do bloco
                fmt_conteudo = re.split(r"\n###\s+", fmt_conteudo)[0].strip()
                if fmt_id and fmt_conteudo:
                    formatos_obj[fmt_id] = md_para_html(fmt_conteudo)

            if not formatos_obj:
                continue

            info = mapa_topicos[tid]
            chave_arquivo = f"{info['serie']}_{info['materiaId']}"
            if chave_arquivo not in agrupado_por_arquivo:
                agrupado_por_arquivo[chave_arquivo] = {}

            # Se houver arquivo duplicado (ex: (1).md e (2).md), mantém o mais completo sem duplicar tópico
            existente = agrupado_por_arquivo[chave_arquivo].get(tid, {}).get("formatos", {})
            if len(formatos_obj) > len(existente):
                agrupado_por_arquivo[chave_arquivo][tid] = {
                    "titulo": info["nome"],
                    "materia": info["materiaId"].upper(),
                    "serie": info["serie"].upper(),
                    "formatos": formatos_obj
                }
                topicos_importados.add(tid)

for chave in sorted(agrupado_por_arquivo.keys()):
    caminho_saida = os.path.join(PASTA_SAIDA, f"{chave}.js")
    conteudo_js = (
        "window.bancoConteudosModulares = Object.assign("
        "window.bancoConteudosModulares || {}, "
        f"{json.dumps(agrupado_por_arquivo[chave], ensure_ascii=False, indent=2)}"
        ");\n"
    )
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_js)
    print(f"✔ Gerado: js/conteudos/{chave}.js ({len(agrupado_por_arquivo[chave])} tópicos)")

print(f"\n✅ Total importado sem repetição: {len(topicos_importados)} de {len(mapa_topicos)} tópicos!")
EOF
python3 converter.py