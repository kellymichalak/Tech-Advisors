import os, re, glob, shutil, subprocess, tempfile

os.makedirs(".backups", exist_ok=True)
shutil.copy2("../js/resumos.js", ".backups/resumos.js.bak_v20261221")

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

idx_nosso_css = js.find(".audio-player-box .pod-transcricao-box { display: none !important; }")
assert idx_nosso_css != -1, "Marcador do bloco definitivo não encontrado"

idx_inicio_nosso_iife = js.rfind("(function", 0, idx_nosso_css)
assert idx_inicio_nosso_iife != -1, "Início do IIFE definitivo não encontrado"

# Localiza o primeiro IIFE legado de transcrição/player (onde está o primeiro carregarTranscricaoDoVideoAtual)
idx_primeiro_legado = js.find("function carregarTranscricaoDoVideoAtual")
assert idx_primeiro_legado != -1 and idx_primeiro_legado < idx_inicio_nosso_iife, "Bloco legado não encontrado"

idx_corte_inicio = js.rfind("(function", 0, idx_primeiro_legado)
assert idx_corte_inicio != -1, "Início do primeiro IIFE legado não encontrado"

print(f"Removendo IIFEs antigos duplicados: chars {idx_corte_inicio}..{idx_inicio_nosso_iife} ({idx_inicio_nosso_iife - idx_corte_inicio} bytes)")

js_limpo = js[:idx_corte_inicio] + "\n\n" + js[idx_inicio_nosso_iife:]

assert "trans-linha" not in js_limpo, "Ainda restou trans-linha em js/resumos.js"

with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js_limpo)

for page in glob.glob("**/*.html", recursive=True):
    with open(page, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    novo_html = re.sub(r'resumos\.js(\?v=\d+)?', 'resumos.js?v=20261222', html)
    if novo_html != html:
        with open(page, "w", encoding="utf-8") as f:
            f.write(novo_html)

jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
if not os.path.exists(jsc):
    jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"

teste_js = "const setTimeout = () => 1, clearTimeout = () => {}, setInterval = () => 1, clearInterval = () => {}, requestAnimationFrame = () => 1, cancelAnimationFrame = () => {}; const window = { location: { search: \"\", origin: \"http://localhost\", hostname: \"127.0.0.1\" }, addEventListener: () => {} }; const document = { body: null, head: { appendChild: () => {} }, readyState: \"complete\", addEventListener: () => {}, querySelectorAll: () => [], getElementById: () => null, getElementsByTagName: () => [], createElement: () => ({}) }; class MutationObserver { observe() {} }\n" + js_limpo + "\nprint(\"TESTE_OK_V20261222\");"
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
    tf.write(teste_js)
    tf_path = tf.name

try:
    res = subprocess.run([jsc, tf_path], capture_output=True, text=True)
finally:
    os.remove(tf_path)

if res.returncode != 0:
    print("❌ Erro:", res.stderr)
    raise SystemExit(1)

print("✅", res.stdout.strip(), "| Zero código legado 'trans-linha' restante!")
