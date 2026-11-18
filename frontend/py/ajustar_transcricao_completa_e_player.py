import os, re, subprocess

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Adiciona extrator estruturado que preserva 100% dos blocos e itens desde o início do texto_teorico
marcador_func = "  function montarBlocosReaisDoEpisodio("
idx_func = js.find(marcador_func)
assert idx_func != -1, "montarBlocosReaisDoEpisodio não encontrado"

idx_fim_prep = js.find("  // === WRAPPER PRINCIPAL ===")
assert idx_fim_prep != -1, "WRAPPER PRINCIPAL não encontrado"

novo_bloco_trans_e_player = """  function extrairSecoesCompletasHtml(html) {
    if (!html) return [];
    // Insere delimitadores antes de títulos, parágrafos e itens de lista para não perder o início nem juntar frases
    const marcado = String(html)
      .replace(/<h[1-6][^>]*>/gi, ' |||SEC||| ')
      .replace(/<\/h[1-6]>/gi, ': ')
      .replace(/<li[^>]*>/gi, ' |||ITEM||| ')
      .replace(/<\/li>/gi, ' ')
      .replace(/<p[^>]*>/gi, ' |||ITEM||| ')
      .replace(/<\/p>/gi, ' ')
      .replace(/<br\s*\/?>/gi, ' ');

    const limpo = limparTexto(marcado);
    const partes = limpo
      .split(/\|\|\|(?:SEC|ITEM)\|\|\|/)
      .map(s => s.replace(/^[:\s-]+/, '').trim())
      .filter(s => s.length >= 12);

    return partes;
  }

  function montarBlocosReaisDoEpisodio(tituloEpisodio, materia, ementa, htmlCompletoTopico) {
    const ep = String(tituloEpisodio || '').trim();
    const epLow = ep.toLowerCase();
    const mat = materia || 'Ciências e Humanidades';
    const tituloLimpo = ep.replace(/\\|.*$/, '').trim() || ep;

    // 1. Se houver conteúdo completo estruturado do tópico (texto_teorico / resumo_narrativo), usa 100% desde o início!
    const itensCompletos = extrairSecoesCompletasHtml(htmlCompletoTopico);
    if (itensCompletos.length >= 3) {
      const cores = ['#38bdf8', '#34d399', '#a78bfa', '#fbbf24', '#f472b6'];
      const totalBlocos = Math.min(4, Math.max(2, Math.ceil(itensCompletos.length / 2)));
      const porBloco = Math.ceil(itensCompletos.length / totalBlocos);
      const blocos = [];

      for (let b = 0; b < totalBlocos; b++) {
        const fatia = itensCompletos.slice(b * porBloco, (b + 1) * porBloco);
        if (!fatia.length) continue;
        let cabecalho = `BLOCO 0${b + 1} • PARTE ${b + 1} DE ${totalBlocos}`;
        if (b === 0) {
          cabecalho = `BLOCO 01 • INTRODUÇÃO E FUNDAMENTOS (${tituloLimpo.toUpperCase()})`;
        } else if (b === totalBlocos - 1) {
          cabecalho = `BLOCO 0${b + 1} • APLICAÇÕES E SÍNTESE FINAL`;
        }
        blocos.push({
          tag: cabecalho,
          cor: cores[b % cores.length],
          texto: fatia.join(' ')
        });
      }
      return blocos;
    }

    // 2. Fallback específico quando não há htmlCompletoTopico (ex: troca dinâmica de episódio)
    if (epLow.includes('vetor') || epLow.includes('escalares')) {
      const focoVetores = epLow.includes('boaro') || epLow.includes('vetores - aula');
      if (focoVetores) {
        return [
          {
            tag: 'BLOCO 01 • INTRODUÇÃO AOS VETORES',
            cor: '#38bdf8',
            texto: 'Nesta aula sobre vetores e grandezas vetoriais, vamos compreender por que algumas grandezas da Física exigem muito mais do que apenas um número e uma unidade de medida para ficarem completamente definidas.'
          },
          {
            tag: 'BLOCO 02 • OS TRÊS ELEMENTOS FUNDAMENTAIS DO VETOR',
            cor: '#34d399',
            texto: 'Todo vetor é caracterizado por três elementos essenciais: módulo, que representa a intensidade ou valor numérico; direção, que indica a reta de atuação como horizontal, vertical ou inclinada; e sentido, que aponta a orientação sobre essa reta.'
          },
          {
            tag: 'BLOCO 03 • COMPARAÇÃO ENTRE ESCALARES E VETORIAIS',
            cor: '#a78bfa',
            texto: 'Enquanto tempo, massa, temperatura, volume e energia são grandezas escalares e ficam perfeitamente definidas com número e unidade, deslocamento, velocidade, aceleração, força e campo elétrico são grandezas vetoriais.'
          },
          {
            tag: 'BLOCO 04 • OPERAÇÕES COM VETORES EM PROVAS E ENEM',
            cor: '#fbbf24',
            texto: 'Na soma vetorial, vetores de mesma direção e mesmo sentido têm seus módulos somados; em sentidos opostos, subtraímos seus módulos; e quando são perpendiculares, o vetor resultante é calculado pelo Teorema de Pitágoras.'
          }
        ];
      }
      return [
        {
          tag: 'BLOCO 01 • CONCEITO DE GRANDEZA FÍSICA',
          cor: '#38bdf8',
          texto: 'Grandeza física é toda propriedade ou atributo de um corpo ou fenômeno que pode ser medido e comparado com um padrão estabelecido, como comprimento, massa, tempo, temperatura, velocidade e força.'
        },
        {
          tag: 'BLOCO 02 • GRANDEZAS FÍSICAS ESCALARES',
          cor: '#34d399',
          texto: 'As grandezas escalares ficam completamente definidas apenas por um valor numérico acompanhado de sua unidade de medida. Por exemplo: cinquenta quilogramas de massa, duas horas de tempo ou vinte e cinco graus Celsius de temperatura.'
        },
        {
          tag: 'BLOCO 03 • GRANDEZAS FÍSICAS VETORIAIS',
          cor: '#a78bfa',
          texto: 'As grandezas vetoriais precisam de três informações simultâneas: módulo ou intensidade, direção e sentido. Informar apenas que um veículo se move a oitenta quilômetros por hora não determina para onde ele está indo sem a orientação vetorial.'
        },
        {
          tag: 'BLOCO 04 • SISTEMA INTERNACIONAL E SÍNTESE FINAL',
          cor: '#fbbf24',
          texto: 'No Sistema Internacional de Unidades, utilizamos metro para comprimento, quilograma para massa e segundo para tempo. Lembre-se sempre: escalar precisa apenas de valor e unidade; vetorial exige módulo, direção e sentido.'
        }
      ];
    }

    const partes = String(ementa || tituloLimpo)
      .replace(/\\.$/, '')
      .split(/,|;|\\be\\b/i)
      .map(s => s.trim())
      .filter(s => s.length >= 4);

    const p1 = partes[0] || tituloLimpo;
    const p2 = partes[1] || `propriedades centrais de ${tituloLimpo}`;
    const p3 = partes[2] || `aplicações práticas de ${tituloLimpo}`;

    return [
      {
        tag: `BLOCO 01 • APRESENTAÇÃO (${mat.toUpperCase()})`,
        cor: '#38bdf8',
        texto: `Bem-vindo à aula: ${ep}. Neste estudo de ${mat}, vamos aprofundar ${tituloLimpo} abordando todos os conceitos essenciais: ${ementa || tituloLimpo}.`
      },
      {
        tag: `BLOCO 02 • ${p1.toUpperCase()}`,
        cor: '#34d399',
        texto: `Iniciamos pelo estudo de ${p1}, analisando sua definição fundamental, como identificá-lo nos problemas e sua importância dentro de ${tituloLimpo}.`
      },
      {
        tag: `BLOCO 03 • ${p2.toUpperCase()}`,
        cor: '#a78bfa',
        texto: `Na sequência, exploramos ${p2}, destacando as relações entre variáveis, interpretações gráficas e pontos de atenção em avaliações.`
      },
      {
        tag: `BLOCO 04 • ${p3.toUpperCase()} E SÍNTESE`,
        cor: '#fbbf24',
        texto: `Para finalizar, conectamos ${p3} com situações reais do cotidiano e questões do ENEM, consolidando todo o aprendizado sobre ${tituloLimpo}.`
      }
    ];
  }

  function gerarTranscricaoKaraokeBlocos(meta, ramos, tituloEpisodio, htmlCompletoTopico) {
    const ep = tituloEpisodio || meta.titulo;
    const contador = { n: 0 };
    const blocosDados = montarBlocosReaisDoEpisodio(ep, meta.materia, meta.ementa, htmlCompletoTopico);

    return blocosDados.map(b => `
      <div class="trans-bloco" style="margin-bottom:12px;padding:12px 14px;background:rgba(15,23,42,0.85);border-left:4px solid ${b.cor};border-radius:10px;">
        <div style="font-size:0.74rem;font-weight:800;color:${b.cor};letter-spacing:0.6px;margin-bottom:5px;">${b.tag}</div>
        <div style="font-size:0.93rem;line-height:1.72;">${tokenizarKaraoke(b.texto, contador)}</div>
      </div>
    `).join('');
  }
  window.__gerarTranscricaoKaraokeBlocos = gerarTranscricaoKaraokeBlocos;

  function prepararPlayerAudio(meta, ramos, htmlAudioOriginal, htmlCompletoTopico) {
    let tituloInicial = meta.titulo;
    let htmlBase = htmlAudioOriginal || '';

    // Barra de controles limpa, alinhada em linha própria logo abaixo do botão de Play
    const subBarraControles = `
      <div class="pod-barra-controles" style="margin-top:12px;padding-top:12px;border-top:1px solid #1e293b;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <button type="button" onclick="window.avancarRetrocederAudio(this, -10)" style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;padding:6px 14px;border-radius:8px;font-size:0.8rem;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:4px;">↺ -10s</button>
          <button type="button" onclick="window.avancarRetrocederAudio(this, 10)" style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;padding:6px 14px;border-radius:8px;font-size:0.8rem;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:4px;">+10s ↻</button>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:0.78rem;color:#94a3b8;font-weight:600;">Velocidade:</span>
          <select class="pod-velocidade-sel" onchange="window.alterarVelocidadeAudio(this, this.value)" style="background:#0f172a;color:#38bdf8;border:1px solid #334155;border-radius:8px;padding:6px 10px;font-size:0.8rem;font-weight:700;cursor:pointer;">
            <option value="0.75">0.75x</option>
            <option value="1" selected>1.0x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2.0x</option>
          </select>
        </div>
      </div>
    `;

    if (htmlBase && htmlBase.includes('audio-player-box')) {
      htmlBase = htmlBase.replace(
        /onclick="window\.trocarEpisodioPodcast\(this,'([^']+)',"([^"]*)"\)"/g,
        (m, vid, tit) => {
          const titLimpo = tit.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
                              .replace(/['"]/g, '');
          return `onclick="window.trocarEpisodioPodcast(this,'${vid}','${titLimpo}')"`;
        }
      );

      const mTit = htmlBase.match(/class='pod-titulo-ativo'[^>]*>([^<]+)</);
      if (mTit && mTit[1]) tituloInicial = mTit[1].trim();

      // Insere a subBarraControles dentro do card interno escuro (#020617), logo após as ondas
      if (/(<div[^>]*class=['"]pod-ondas['"][^>]*>[\s\S]*?<\/div>)/.test(htmlBase)) {
        htmlBase = htmlBase.replace(/(<div[^>]*class=['"]pod-ondas['"][^>]*>[\s\S]*?<\/div>)/, '$1' + subBarraControles);
      }
    } else {
      htmlBase = `
        <div class="audio-player-box" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;padding:22px;border-radius:18px;border:1px solid #312e81;">
          <div style="font-size:0.74em;font-weight:800;color:#34d399;letter-spacing:1px;">🎧 MODO ÁUDIO • AULA NARRADA SINCRONIZADA</div>
          <div style="font-size:1.12em;font-weight:800;margin:4px 0 14px;">${meta.titulo}</div>
          <div style="background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;">
            <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
              <button type="button" class="btn-play-pod" onclick="window.narrarTranscricaoAudio(this)" style="background:#10b981;color:#022c22;border:none;padding:11px 22px;border-radius:999px;font-weight:800;font-size:0.94em;cursor:pointer;">▶ Ouvir Aula em Áudio</button>
              <div style="flex:1;min-width:200px;">
                <div class="pod-titulo-ativo" style="font-size:0.92em;font-weight:700;color:#f1f5f9;">${meta.titulo}</div>
                <div class="pod-status" style="font-size:0.78em;color:#94a3b8;margin-top:3px;">Pronto para tocar • Apenas áudio</div>
              </div>
              <div class="pod-ondas" style="opacity:0.25;font-size:1.2em;letter-spacing:2px;color:#34d399;font-weight:900;">ılılılılı</div>
            </div>
            ${subBarraControles}
          </div>
        </div>
      `;
    }

    const transcricaoHtml = gerarTranscricaoKaraokeBlocos(meta, ramos, tituloInicial, htmlCompletoTopico);
    const painelTranscricao = `
      <div class="pod-transcricao-box" data-materia="${(meta.materia || '').replace(/"/g, '&quot;')}" data-ementa="${(meta.ementa || '').replace(/"/g, '&quot;')}" style="margin-top:14px;background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <span style="font-size:0.78rem;font-weight:800;color:#38bdf8;letter-spacing:0.8px;">📝 TRANSCRIÇÃO COMPLETA POR BLOCOS (CLIQUE NA PALAVRA PARA SALTAR)</span>
          <button type="button" onclick="window.narrarTranscricaoAudio(this)" style="background:#064e3b;color:#6ee7b7;border:1px solid #10b981;padding:5px 12px;border-radius:999px;font-size:0.76rem;font-weight:800;cursor:pointer;">🔊 Ler com Voz IA</button>
        </div>
        <div class="pod-transcricao-texto" style="max-height:320px;overflow-y:auto;padding-right:6px;">
          ${transcricaoHtml}
        </div>
      </div>
    `;

    const idxFim = htmlBase.lastIndexOf('</div>');
    if (idxFim !== -1) {
      return htmlBase.slice(0, idxFim) + painelTranscricao + '</div>';
    }
    return htmlBase + painelTranscricao;
  }
"""

js = js[:idx_func] + novo_bloco_trans_e_player + "\n" + js[idx_fim_prep:]

# Passa o HTML bruto (sem limpar antes) de texto_teorico / resumo_narrativo para preservar todos os itens desde o início
js = js.replace(
    "const textoCompletoTopico = limparTexto(dados.formatos.resumo_narrativo || dados.formatos.texto_teorico || '');",
    "const textoCompletoTopico = (dados.formatos.texto_teorico || dados.formatos.resumo_narrativo || '');"
)

with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js)

jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
if not os.path.exists(jsc):
    jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"

teste_js = """
const setTimeout = () => 1;
const clearTimeout = () => {};
const setInterval = () => 1;
const clearInterval = () => {};
const window = {
  location: { search: "", origin: "http://localhost:8080" },
  addEventListener: () => {},
  listaConteudosGlobal: [
    { id: "fis_2em_01", materiaId: "fis", serie: "2em", nome: "Termometria e escalas termométricas", ementa: "Temperatura, equilíbrio térmico, escalas Celsius, Fahrenheit e Kelvin." }
  ],
  infoMateriasGlobal: { fis: { nome: "Física" } }
};
const document = {
  body: null,
  head: { appendChild: () => {} },
  readyState: "complete",
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: () => null,
  getElementsByTagName: () => [],
  createElement: () => ({})
};
class MutationObserver { observe() {} }
""" + js + """
const res = window.obterResumoMultiformato("fis_2em_01");
if (!res.formatos.audioaula_podcast.includes("pod-barra-controles")) throw new Error("Sub-barra de controles ausente");
if (!res.formatos.audioaula_podcast.includes("Temperatura e Energia Térmica")) throw new Error("Início de Escalas Termométricas ausente na transcrição");
print("TESTE_OK: inicio_escalas_presente=OK | barra_controles_alinhada=OK");
"""

res = subprocess.run([jsc, "-e", teste_js], capture_output=True, text=True)
if res.returncode != 0:
    print("❌ Erro:", res.stderr, res.stdout)
    raise SystemExit(1)
print("✅", res.stdout.strip())

for page in ["../pages/resumos.html", "../pages/audios.html"]:
    if os.path.exists(page):
        with open(page, "r", encoding="utf-8") as f:
            html = f.read()
        html = re.sub(r"v=\d+", "v=20261201", html)
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)

print("✅ Sistema atualizado para v=20261201!")
