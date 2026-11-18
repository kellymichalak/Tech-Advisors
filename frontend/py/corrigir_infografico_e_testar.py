import re, os, subprocess

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Remove eventual injeção indevida de dados.grupos no meio do arquivo (antes do wrapper final)
js = re.sub(
    r"\s*if \(Array\.isArray\(dados\.grupos\)\) \{\s*let achouInfo = false;[\s\S]*?grupoVisual\.modelos\.push\(\{\s*id:\s*'infografico_ilustrado',\s*html:\s*novoInfograficoHtml\s*\}\);\s*\}\s*\}\s*\}\s*agendarSetasMapasMentais\(\);\s*return dados;",
    "\n  return dados;",
    js
)

# 2. Atualiza o wrapper final (linhas 10236-10264) com proteção try/catch e preenchimento completo de grupos/categorias/formatos
padrao_wrapper = re.compile(
    r"window\.obterResumoMultiformato = function\(id\) \{[\s\S]*?\}\s*\)\(\);\s*$"
)

novo_wrapper = """window.obterResumoMultiformato = function(id) {
    const dados = prevObterResumo.apply(this, arguments);
    if (!dados || typeof dados !== 'object') return dados;

    let novoMapaHtml = null;
    let novoInfograficoHtml = null;

    try {
      novoMapaHtml = renderizarMapaMentalRadial(dados);
    } catch (e) {
      console.error('Erro no Mapa Mental:', e);
    }

    try {
      novoInfograficoHtml = renderizarInfograficoIlustrado(dados);
    } catch (e) {
      console.error('Erro no Infográfico Ilustrado:', e);
    }

    if (dados.formatos && typeof dados.formatos === 'object') {
      if (novoMapaHtml) dados.formatos.mapa_mental = novoMapaHtml;
      if (novoInfograficoHtml) dados.formatos.infografico_ilustrado = novoInfograficoHtml;
    }

    const atualizarListaGrupos = (lista) => {
      if (!Array.isArray(lista)) return;
      let achouInfo = false;
      lista.forEach(grupo => {
        if (!Array.isArray(grupo.modelos)) return;
        grupo.modelos.forEach(m => {
          if (!m) return;
          if (m.id === 'mapa_mental' && novoMapaHtml) m.html = novoMapaHtml;
          if (m.id === 'infografico_ilustrado' && novoInfograficoHtml) {
            m.html = novoInfograficoHtml;
            achouInfo = true;
          }
        });
      });
      if (!achouInfo && novoInfograficoHtml) {
        const gVisual = lista.find(g => /visual/i.test(g.nome || '')) || lista[0];
        if (gVisual && Array.isArray(gVisual.modelos)) {
          gVisual.modelos.push({
            id: 'infografico_ilustrado',
            html: novoInfograficoHtml
          });
        }
      }
    };

    atualizarListaGrupos(dados.grupos);
    atualizarListaGrupos(dados.categorias);

    agendarSetasMapasMentais();
    return dados;
  };
})();
"""

assert padrao_wrapper.search(js), "Wrapper final não encontrado"
js = padrao_wrapper.sub(novo_wrapper, js, count=1)

with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js)

# 3. Valida sintaxe no JavaScriptCore do macOS
jsc_paths = [
    "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc",
    "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"
]
jsc = next((p for p in jsc_paths if os.path.exists(p)), None)
if jsc:
    res = subprocess.run([jsc, "-e", f"new Function({repr(js)})"], capture_output=True, text=True)
    if res.returncode != 0:
        print("❌ Erro de sintaxe:", res.stderr)
        raise SystemExit(1)
    print("✅ JavaScriptCore validou sintaxe 100% limpa!")

# 4. Atualiza versão em pages/resumos.html
with open("../pages/resumos.html", "r", encoding="utf-8") as f:
    html = f.read()

html = re.sub(r"v=\d+", "v=20261180", html)
with open("../pages/resumos.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Correção aplicada com sucesso (v=20261180)!")
