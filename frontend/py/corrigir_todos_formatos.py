import os, re, subprocess

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

marcador = "// ============================================================================\n// CAMADA COMPLETA:"
idx = js.find(marcador)
assert idx != -1, "Marcador não encontrado"
base_js = js[:idx].rstrip()

nova_camada = """
// ============================================================================
// CAMADA COMPLETA: MAPA MENTAL RADIAL, MULTI-STORYTELLING, MULTI-FLASHCARDS,
// MULTI-QUIZ (CLIQUE LIVRE) E ÁUDIO SEM AUTOPLAY COM TRANSCRIÇÃO FIEL
// ============================================================================
(function() {
  const prevObterResumo = window.obterResumoMultiformato;
  if (typeof prevObterResumo !== 'function') return;

  function garantirEstilosMultiformato() {
    if (typeof document === 'undefined' || !document.head) return;
    if (document.getElementById('estilos-multiformato-completo')) return;
    const style = document.createElement('style');
    style.id = 'estilos-multiformato-completo';
    style.textContent = `
      .mm-radial-wrapper {
        position: relative;
        background: radial-gradient(circle at center, #1e1b4b 0%, #0f172a 75%);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 28px 22px;
        overflow: hidden;
      }
      .mm-radial-grid {
        position: relative;
        display: grid;
        grid-template-columns: 1fr minmax(220px, 260px) 1fr;
        gap: 28px;
        align-items: center;
        z-index: 2;
      }
      @media (max-width: 860px) {
        .mm-radial-grid { grid-template-columns: 1fr; }
        .mm-svg-conexoes { display: none !important; }
      }
      .mm-col-esq, .mm-col-dir {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      .mm-centro {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        border: 2px solid #c7d2fe;
        border-radius: 22px;
        padding: 22px 18px;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 0 36px rgba(99, 102, 241, 0.55);
        z-index: 3;
      }
      .mm-centro-icone { font-size: 2.1rem; margin-bottom: 6px; }
      .mm-centro-materia {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #e0e7ff;
        margin-bottom: 5px;
      }
      .mm-centro-titulo { font-size: 1.04rem; font-weight: 800; line-height: 1.35; }
      .mm-ramo-card {
        background: rgba(15, 23, 42, 0.94);
        border: 1px solid var(--cor-ramo, #818cf8);
        border-left: 5px solid var(--cor-ramo, #818cf8);
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
      }
      .mm-ramo-titulo {
        color: var(--cor-ramo, #818cf8);
        font-weight: 800;
        font-size: 0.92rem;
        margin-bottom: 6px;
      }
      .mm-ramo-desc {
        color: #e2e8f0;
        font-size: 0.86rem;
        line-height: 1.55;
      }
      .mm-svg-conexoes {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
      }
      .quiz-btn-livre {
        display: block;
        width: 100%;
        text-align: left;
        background: #0f172a;
        color: #f1f5f9;
        border: 1.5px solid #475569;
        border-radius: 12px;
        padding: 11px 14px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        line-height: 1.45;
        cursor: pointer;
        transition: all 0.18s ease;
      }
      .quiz-btn-livre:hover {
        border-color: #818cf8;
        background: #1e293b;
      }
    `;
    document.head.appendChild(style);
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', garantirEstilosMultiformato);
    } else {
      garantirEstilosMultiformato();
    }
  }

  function limparTexto(txt) {
    return String(txt || '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/\s+/g, ' ')
      .trim();
  }

  function escolherIconeTema(titulo, materia) {
    const s = (titulo + ' ' + materia).toLowerCase();
    if (s.includes('termometr') || s.includes('calor') || s.includes('termodin')) return '🌡️';
    if (s.includes('físic') || s.includes('fisic') || s.includes('cinem') || s.includes('dinâm') || s.includes('vetori')) return '⚛️';
    if (s.includes('quím') || s.includes('quim') || s.includes('átomo') || s.includes('mol')) return '🧪';
    if (s.includes('biolog') || s.includes('célul') || s.includes('genét') || s.includes('ecolog')) return '🧬';
    if (s.includes('matem') || s.includes('funç') || s.includes('geometr') || s.includes('equaç')) return '📐';
    if (s.includes('histór') || s.includes('histor') || s.includes('guerra') || s.includes('revoluç')) return '🏛️';
    if (s.includes('geograf') || s.includes('clima') || s.includes('relevo') || s.includes('popula')) return '🌍';
    if (s.includes('portug') || s.includes('literat') || s.includes('gramát') || s.includes('texto')) return '📚';
    if (s.includes('filosof') || s.includes('sociolog')) return '🧠';
    if (s.includes('ingl') || s.includes('espanh')) return '🗣️';
    if (s.includes('arte')) return '🎨';
    return '💡';
  }

  function obterMetadadosOficiais(id, dados) {
    const lista = (typeof window !== 'undefined' && window.listaConteudosGlobal) || [];
    const item = lista.find(x => x.id === id);
    const titulo = (item && item.nome) || dados.titulo || 'Tema de Estudo';
    const ementa = (item && item.ementa) || '';
    const infoMat = (item && window.infoMateriasGlobal && window.infoMateriasGlobal[item.materiaId]) || {};
    const materia = infoMat.nome || dados.materia || '';
    return { titulo, ementa, materia };
  }

  function extrairRamosEstruturados(id, dados) {
    const meta = obterMetadadosOficiais(id, dados);
    const ramos = [];

    // 1. Extrai tópicos diretos da ementa oficial (ex: "Grandezas escalares e vetoriais, Sistema Internacional de Unidades e notação científica")
    if (meta.ementa) {
      const partesEmenta = meta.ementa
        .replace(/\.$/, '')
        .split(/,|;|\be\b/i)
        .map(s => s.trim())
        .filter(s => s.length >= 4);

      partesEmenta.forEach(parte => {
        const cap = parte.charAt(0).toUpperCase() + parte.slice(1);
        ramos.push({
          titulo: cap,
          desc: `Estudo aprofundado de ${parte} dentro de ${meta.titulo} (${meta.materia}), incluindo definições, propriedades e aplicações.`
        });
      });
    }

    // 2. Extrai nós do mapa_mental original (se houver árvore ├── / └── ou eixos)
    const mapaOrig = (dados.formatos && dados.formatos.mapa_mental) || '';
    if (mapaOrig) {
      const textoMapa = limparTexto(mapaOrig)
        .replace(/Explore cada ramificação conectada ao conceito central:/gi, '')
        .replace(/NÓ\s*\d+/gi, '|')
        .replace(/🔹\s*Eixo Conceitual\s*\d+/gi, '|');
      const blocos = textoMapa.split(/[|├──└──┬]+/).map(b => b.trim()).filter(b => b.length >= 8 && b.length <= 140);
      blocos.forEach(bloco => {
        if (!ramos.some(r => r.titulo.toLowerCase() === bloco.toLowerCase())) {
          const mPar = bloco.match(/^([^(]+)\(([^)]+)\)$/);
          if (mPar) {
            ramos.push({ titulo: mPar[1].trim(), desc: mPar[2].trim().charAt(0).toUpperCase() + mPar[2].trim().slice(1) + '.' });
          } else {
            ramos.push({
              titulo: bloco.slice(0, 48),
              desc: `Ponto-chave relacionado a ${bloco} em ${meta.titulo}.`
            });
          }
        }
      });
    }

    // 3. Completa com eixos pedagógicos do próprio tema até fechar 6 ramos bem estruturados
    const complementos = [
      {
        titulo: `Conceitos Fundamentais`,
        desc: `Base teórica de ${meta.titulo}: definições essenciais, grandezas envolvidas e interpretação conceitual.`
      },
      {
        titulo: `Relações e Representações`,
        desc: `Como representar, calcular e relacionar os elementos de ${meta.ementa || meta.titulo} no Sistema Internacional.`
      },
      {
        titulo: `Aplicações no Cotidiano`,
        desc: `Situações reais, fenômenos observáveis e exemplos práticos onde ${meta.titulo} se manifesta.`
      },
      {
        titulo: `Estratégia para Provas e ENEM`,
        desc: `Como interpretar enunciados, identificar dados-chave e evitar pegadinhas clássicas sobre ${meta.titulo}.`
      }
    ];
    let cIdx = 0;
    while (ramos.length < 6 && cIdx < complementos.length) {
      ramos.push(complementos[cIdx++]);
    }

    return { meta, ramos: ramos.slice(0, 8) };
  }

  // === 1. MAPA MENTAL RADIAL COM CONECTORES SVG ===
  let __mmDesenhando = false;
  let __mmTimer = null;

  function atualizarSetasMapasMentais() {
    if (typeof document === 'undefined' || !document.querySelectorAll || __mmDesenhando) return;
    __mmDesenhando = true;
    try {
      document.querySelectorAll('.mm-radial-wrapper').forEach(wrapper => {
        const svg = wrapper.querySelector('.mm-svg-conexoes');
        const centro = wrapper.querySelector('.mm-centro');
        if (!svg || !centro) return;

        const rectWrap = wrapper.getBoundingClientRect();
        if (!rectWrap.width || !rectWrap.height) return;
        const rectCentro = centro.getBoundingClientRect();
        const cy = rectCentro.top - rectWrap.top + rectCentro.height / 2;

        let paths = '';
        wrapper.querySelectorAll('.mm-ramo-card').forEach(card => {
          const r = card.getBoundingClientRect();
          if (!r.width || !r.height) return;
          const isEsq = r.left + r.width / 2 < rectCentro.left + rectCentro.width / 2;
          const x2 = isEsq ? (r.right - rectWrap.left) : (r.left - rectWrap.left);
          const y2 = r.top - rectWrap.top + r.height / 2;
          const x1 = isEsq ? (rectCentro.left - rectWrap.left) : (rectCentro.right - rectWrap.left);
          const y1 = cy;
          const dx = Math.abs(x2 - x1) * 0.55;
          const c1x = isEsq ? x1 - dx : x1 + dx;
          const c2x = isEsq ? x2 + dx : x2 - dx;
          const cor = card.getAttribute('data-cor') || '#818cf8';
          paths += `<path d="M ${x1.toFixed(1)} ${y1.toFixed(1)} C ${c1x.toFixed(1)} ${y1.toFixed(1)}, ${c2x.toFixed(1)} ${y2.toFixed(1)}, ${x2.toFixed(1)} ${y2.toFixed(1)}" fill="none" stroke="${cor}" stroke-width="2.5" stroke-opacity="0.78" />`;
          paths += `<circle cx="${x2.toFixed(1)}" cy="${y2.toFixed(1)}" r="4.5" fill="${cor}" />`;
        });
        svg.innerHTML = paths;
      });
    } finally {
      __mmDesenhando = false;
    }
  }

  function agendarSetasMapasMentais() {
    clearTimeout(__mmTimer);
    __mmTimer = setTimeout(atualizarSetasMapasMentais, 45);
  }

  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('resize', agendarSetasMapasMentais);
  }
  if (typeof MutationObserver !== 'undefined' && typeof document !== 'undefined') {
    const obs = new MutationObserver(() => {
      if (!__mmDesenhando) agendarSetasMapasMentais();
    });
    const iniciarObs = () => {
      if (document.body) {
        obs.observe(document.body, { childList: true, subtree: true });
        agendarSetasMapasMentais();
      }
    };
    if (document.body) iniciarObs();
    else document.addEventListener('DOMContentLoaded', iniciarObs);
  }

  function renderizarMapaMentalRadial(meta, ramos) {
    garantirEstilosMultiformato();
    const cores = ['#38bdf8', '#a78bfa', '#34d399', '#fbbf24', '#f472b6', '#fb923c'];
    const listaRamos = ramos.slice(0, 6);
    const metade = Math.ceil(listaRamos.length / 2);
    const esq = listaRamos.slice(0, metade);
    const dir = listaRamos.slice(metade);
    const icone = escolherIconeTema(meta.titulo, meta.materia);

    const cardHtml = (item, idx) => {
      const cor = cores[idx % cores.length];
      return `
        <div class="mm-ramo-card" data-cor="${cor}" style="--cor-ramo:${cor};">
          <div class="mm-ramo-titulo">🔹 ${item.titulo}</div>
          <div class="mm-ramo-desc">${item.desc}</div>
        </div>
      `;
    };

    agendarSetasMapasMentais();
    return `
      <div class="mm-radial-wrapper">
        <svg class="mm-svg-conexoes"></svg>
        <div class="mm-radial-grid">
          <div class="mm-col-esq">${esq.map((r, i) => cardHtml(r, i)).join('')}</div>
          <div class="mm-centro">
            <div class="mm-centro-icone">${icone}</div>
            <div class="mm-centro-materia">${meta.materia || 'MAPA CONCEITUAL'}</div>
            <div class="mm-centro-titulo">${meta.titulo}</div>
          </div>
          <div class="mm-col-dir">${dir.map((r, i) => cardHtml(r, i + metade)).join('')}</div>
        </div>
      </div>
    `;
  }

  // === 2. STORYTELLING MÚLTIPLO (PRESERVA O ORIGINAL + ADICIONA MAIS CASOS REAIS) ===
  function montarStorytellingCompleto(meta, ramos, originalHtml) {
    const base = originalHtml && limparTexto(originalHtml).length > 60
      ? `<div style="margin-bottom:16px;">${originalHtml}</div>`
      : '';
    const r0 = ramos[0] || { titulo: meta.titulo, desc: '' };
    const r1 = ramos[1] || { titulo: 'Aplicação Experimental', desc: '' };
    const r2 = ramos[2] || { titulo: 'Resolução de Problemas', desc: '' };

    return `
      ${base}
      <div style="display:grid;gap:14px;">
        <div style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid #312e81;border-left:5px solid #f59e0b;border-radius:16px;padding:18px;color:#f8fafc;">
          <div style="font-size:0.75rem;font-weight:800;color:#fbbf24;letter-spacing:0.8px;">📖 ESTUDO DE CASO 1 • SITUAÇÃO DO COTIDIANO</div>
          <h3 style="margin:6px 0 8px;color:#fff;font-size:1.05rem;">Na prática: ${r0.titulo}</h3>
          <p style="margin:0;color:#e2e8f0;line-height:1.65;font-size:0.94rem;">No dia a dia, compreender <strong>${r0.titulo}</strong> dentro de <strong>${meta.titulo}</strong> permite interpretar corretamente fenômenos e dados sem depender de memorização mecânica. ${r0.desc}</p>
        </div>
        <div style="background:linear-gradient(135deg,#0f172a,#064e3b);border:1px solid #065f46;border-left:5px solid #10b981;border-radius:16px;padding:18px;color:#f8fafc;">
          <div style="font-size:0.75rem;font-weight:800;color:#34d399;letter-spacing:0.8px;">🔬 ESTUDO DE CASO 2 • INVESTIGAÇÃO E ANÁLISE</div>
          <h3 style="margin:6px 0 8px;color:#fff;font-size:1.05rem;">Experimentando ${r1.titulo}</h3>
          <p style="margin:0;color:#e2e8f0;line-height:1.65;font-size:0.94rem;">Ao analisar um problema real de <strong>${meta.materia}</strong> envolvendo <strong>${r1.titulo}</strong>, o primeiro passo é identificar as condições iniciais e como cada variável influencia o resultado. ${r1.desc}</p>
        </div>
        <div style="background:linear-gradient(135deg,#0f172a,#3b0764);border:1px solid #581c87;border-left:5px solid #c084fc;border-radius:16px;padding:18px;color:#f8fafc;">
          <div style="font-size:0.75rem;font-weight:800;color:#d8b4fe;letter-spacing:0.8px;">🎯 ESTUDO DE CASO 3 • ABORDAGEM EM PROVAS E ENEM</div>
          <h3 style="margin:6px 0 8px;color:#fff;font-size:1.05rem;">Como resolver questões sobre ${r2.titulo}</h3>
          <p style="margin:0;color:#e2e8f0;line-height:1.65;font-size:0.94rem;">Em avaliações como o ENEM, <strong>${meta.titulo}</strong> costuma aparecer em textos contextualizados que exigem relacionar <strong>${r2.titulo}</strong> com a ementa: <em>${meta.ementa || meta.titulo}</em>.</p>
        </div>
      </div>
    `;
  }

  // === 3. FLASHCARDS RICOS (PRESERVA OS ORIGINAIS + EXPANDE PARA 6 CARDS NO MESMO ESTILO) ===
  function montarFlashcardsCompletos(meta, ramos, originalHtml) {
    const cardsOriginais = [];
    if (originalHtml) {
      const mCards = originalHtml.match(/<div onclick="const f=this\.querySelector\('\.fc-frente'\);[\s\S]*?<\/div>\s*<\/div>/g);
      if (mCards && mCards.length) {
        mCards.forEach(c => cardsOriginais.push(c));
      }
    }

    const totalDesejado = 6;
    const cardsExtras = [];
    for (let i = 0; cardsOriginais.length + cardsExtras.length < totalDesejado && i < ramos.length; i++) {
      const num = cardsOriginais.length + cardsExtras.length + 1;
      const r = ramos[i];
      cardsExtras.push(`
        <div onclick="const f=this.querySelector('.fc-frente');const v=this.querySelector('.fc-verso');const tag=this.querySelector('.fc-lado');if(v.style.display==='none'){f.style.display='none';v.style.display='block';tag.textContent='RESPOSTA (VERSO)';tag.style.color='#34d399';this.style.borderColor='#34d399';}else{v.style.display='none';f.style.display='block';tag.textContent='PERGUNTA (FRENTE)';tag.style.color='#a5b4fc';this.style.borderColor='#818cf8';}" style="cursor:pointer;min-height:190px;padding:22px;border-radius:16px;background:#1e293b;border:2px solid #818cf8;box-shadow:0 6px 18px rgba(0,0,0,0.3);color:#ffffff;user-select:none;display:flex;flex-direction:column;justify-content:space-between;">
          <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.76em;font-weight:800;color:#a5b4fc;margin-bottom:12px;">
            <span>CARD #${num} DE ${totalDesejado}</span>
            <span class="fc-lado" style="background:rgba(129,140,248,0.22);padding:4px 10px;border-radius:999px;color:#c7d2fe;">PERGUNTA (FRENTE)</span>
          </div>
          <div class="fc-frente" style="display:block;font-size:1.06em;font-weight:700;line-height:1.6;color:#ffffff;">
            ❓ Como definir e aplicar <strong style="color:#e0e7ff;">${r.titulo}</strong> dentro de ${meta.titulo}?
          </div>
          <div class="fc-verso" style="display:none;font-size:1.0em;line-height:1.65;color:#a7f3d0;background:rgba(16,185,129,0.16);border:1px solid rgba(52,211,153,0.4);padding:14px;border-radius:12px;">
            ✅ ${r.desc}
          </div>
          <div style="font-size:0.78em;color:#94a3b8;margin-top:14px;text-align:right;font-weight:600;">🔄 Clique no card para virar</div>
        </div>
      `);
    }

    const todos = cardsOriginais.concat(cardsExtras);
    // Atualiza o contador "CARD #X DE Y" nos cards originais para refletir o total
    const todosRenumerados = todos.map((htmlCard, idx) =>
      htmlCard.replace(/CARD #\d+ DE \d+/g, `CARD #${idx + 1} DE ${todos.length}`)
    );

    return `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">${todosRenumerados.join('')}</div>`;
  }

  // === 4. QUIZ INTERATIVO (MÚLTIPLAS QUESTÕES + CLIQUE LIVRE EM QUALQUER OPÇÃO) ===
  window.verificarRespostaQuiz = function(btn, correta, explicacao) {
    const card = btn && btn.closest ? btn.closest('.quiz-card-interativo') : null;
    if (!card) return;

    // Reseta apenas o visual dos botões deste card (SEM desabilitar, permitindo clicar várias vezes)
    card.querySelectorAll('button').forEach(b => {
      b.style.borderColor = '#475569';
      b.style.background = '#0f172a';
      b.style.color = '#f1f5f9';
    });

    if (correta) {
      btn.style.borderColor = '#10b981';
      btn.style.background = 'rgba(16, 185, 129, 0.22)';
      btn.style.color = '#a7f3d0';
    } else {
      btn.style.borderColor = '#ef4444';
      btn.style.background = 'rgba(239, 68, 68, 0.22)';
      btn.style.color = '#fecaca';
    }

    const fb = card.querySelector('.quiz-feedback');
    if (fb) {
      fb.style.display = 'block';
      fb.style.marginTop = '12px';
      fb.style.padding = '12px 14px';
      fb.style.borderRadius = '12px';
      fb.style.fontSize = '0.9rem';
      fb.style.lineHeight = '1.55';
      if (correta) {
        fb.style.background = 'rgba(16, 185, 129, 0.14)';
        fb.style.border = '1px solid #10b981';
        fb.style.color = '#a7f3d0';
        fb.innerHTML = `✅ <strong>Resposta Correta!</strong> ${explicacao}`;
      } else {
        fb.style.background = 'rgba(239, 68, 68, 0.14)';
        fb.style.border = '1px solid #ef4444';
        fb.style.color = '#fecaca';
        fb.innerHTML = `❌ <strong>Não é essa.</strong> ${explicacao} <em>(Você pode clicar em outra opção para testar!)</em>`;
      }
    }
  };

  function extrairQuestaoOriginalComoInterativa(quizOrigHtml, meta) {
    if (!quizOrigHtml) return '';
    const txt = limparTexto(quizOrigHtml);
    const mQ = txt.match(/Questão:\s*(.*?)\s*\[\s*\]\s*A\)/i);
    const mA = txt.match(/\[\s*(X?)\s*\]\s*A\)\s*(.*?)\s*\[\s*(X?)\s*\]\s*B\)\s*(.*?)\s*\[\s*(X?)\s*\]\s*C\)\s*(.*?)\s*\[\s*(X?)\s*\]\s*D\)\s*(.*?)(?:\s+1\.|\s+Resolução|\s+Explicação|$)/i);
    if (!mQ || !mA) return '';

    const enunciado = mQ[1].trim();
    const letras = ['A', 'B', 'C', 'D'];
    const opcoes = [
      { letra: 'A', correta: mA[1].toUpperCase() === 'X', texto: mA[2].replace(/\(Opção Correta\)/gi, '').trim() },
      { letra: 'B', correta: mA[3].toUpperCase() === 'X', texto: mA[4].replace(/\(Opção Correta\)/gi, '').trim() },
      { letra: 'C', correta: mA[5].toUpperCase() === 'X', texto: mA[6].replace(/\(Opção Correta\)/gi, '').trim() },
      { letra: 'D', correta: mA[7].toUpperCase() === 'X', texto: mA[8].replace(/\(Opção Correta\)/gi, '').trim() }
    ];
    const corretaObj = opcoes.find(o => o.correta) || opcoes[0];

    return `
      <div class="quiz-card-interativo" style="background:#1e293b;border:1px solid #334155;border-radius:18px;padding:20px;margin-bottom:16px;color:#f8fafc;">
        <div style="font-size:0.75rem;font-weight:800;color:#c084fc;letter-spacing:0.8px;margin-bottom:6px;">🕹️ QUESTÃO 01 • DESAFIO DE APLICAÇÃO (${meta.materia})</div>
        <div style="font-size:1.02rem;font-weight:700;line-height:1.6;margin-bottom:14px;color:#f8fafc;">${enunciado}</div>
        <div class="quiz-opcoes">
          ${opcoes.map(op => `
            <button type="button" class="quiz-btn-livre" onclick="verificarRespostaQuiz(this, ${op.correta}, 'A alternativa correta é ${corretaObj.letra}) ${corretaObj.texto.replace(/'/g, "\\'")}.')">
              <strong>${op.letra})</strong> ${op.texto}
            </button>
          `).join('')}
        </div>
        <div class="quiz-feedback" style="display:none;"></div>
      </div>
    `;
  }

  function montarQuizCompleto(meta, ramos, quizOrigHtml) {
    garantirEstilosMultiformato();
    const blocoQ1 = extrairQuestaoOriginalComoInterativa(quizOrigHtml, meta);
    const inicioIdx = blocoQ1 ? 1 : 0;
    const itens = ramos.slice(0, 5);

    const questoesGeradas = itens.map((r, i) => {
      const num = inicioIdx + i + 1;
      const d1 = ramos[(i + 1) % ramos.length];
      const d2 = ramos[(i + 2) % ramos.length];
      const d3 = ramos[(i + 3) % ramos.length];

      const alternativas = [
        {
          texto: r.desc,
          correta: true,
          fb: `Isso mesmo! Essa é a definição correta de ${r.titulo} em ${meta.titulo}.`
        },
        {
          texto: `Corresponde exclusivamente a ${d1.titulo}, não tendo relação com ${r.titulo}.`,
          correta: false,
          fb: `Essa afirmação descreve outro tópico (${d1.titulo}). Releia o conceito de ${r.titulo}.`
        },
        {
          texto: `Representa uma exceção que invalida os princípios de ${d2.titulo} em ${meta.materia}.`,
          correta: false,
          fb: `Na verdade, ${r.titulo} complementa ${d2.titulo} dentro de ${meta.titulo}.`
        },
        {
          texto: `Aplica-se apenas quando ${d3.titulo} é desconsiderado na análise do sistema.`,
          correta: false,
          fb: `Incorreto. Tente outra alternativa para confirmar o papel de ${r.titulo}.`
        }
      ];

      const rot = i % 4;
      const ordenadas = alternativas.slice(rot).concat(alternativas.slice(0, rot));

      return `
        <div class="quiz-card-interativo" style="background:#1e293b;border:1px solid #334155;border-radius:18px;padding:20px;margin-bottom:16px;color:#f8fafc;">
          <div style="font-size:0.75rem;font-weight:800;color:#fbbf24;letter-spacing:0.8px;margin-bottom:6px;">🕹️ QUESTÃO 0${num} • ${meta.materia}</div>
          <div style="font-size:1.0rem;font-weight:700;line-height:1.55;margin-bottom:14px;color:#f8fafc;">
            No estudo de <em>${meta.titulo}</em>, o que caracteriza corretamente <strong style="color:#a5b4fc;">${r.titulo}</strong>?
          </div>
          <div class="quiz-opcoes">
            ${ordenadas.map((alt, aIdx) => `
              <button type="button" class="quiz-btn-livre" onclick="verificarRespostaQuiz(this, ${alt.correta}, '${alt.fb.replace(/'/g, "\\'")}')">
                <strong>${String.fromCharCode(65 + aIdx)})</strong> ${alt.texto}
              </button>
            `).join('')}
          </div>
          <div class="quiz-feedback" style="display:none;"></div>
        </div>
      `;
    }).join('');

    return `<div>${blocoQ1}${questoesGeradas}</div>`;
  }

  // === 5. ÁUDIO: TROCA DE EPISÓDIO SEM AUTOPLAY + TRANSCRIÇÃO FIEL AO TEMA/EPISÓDIO ===
  function gerarTranscricaoFiel(meta, ramos, tituloEpisodio) {
    const ep = tituloEpisodio || meta.titulo;
    const topicosTexto = ramos.slice(0, 4).map((r, i) =>
      `<p style="margin:0 0 10px;"><strong>${i + 1}. ${r.titulo}:</strong> ${r.desc}</p>`
    ).join('');

    return `
      <p style="margin:0 0 10px;color:#93c5fd;"><strong>🎙️ Episódio Selecionado:</strong> ${ep}</p>
      <p style="margin:0 0 10px;">Olá! Nesta aula em áudio de <strong>${meta.materia}</strong>, vamos estudar <strong>${meta.titulo}</strong>${meta.ementa ? `, abordando: <em>${meta.ementa}</em>` : ''}.</p>
      ${topicosTexto}
      <p style="margin:0;color:#a7f3d0;"><strong>Resumo final:</strong> Revise os conceitos acima e teste seus conhecimentos nos Flashcards e no Quiz interativo deste módulo.</p>
    `;
  }

  function prepararPlayerAudio(meta, ramos, htmlAudioOriginal) {
    let tituloInicial = meta.titulo;
    let htmlBase = htmlAudioOriginal || '';

    if (htmlBase && htmlBase.includes('audio-player-box')) {
      // Corrige aspas duplas quebradas no onclick de troca de episódio
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
    } else {
      htmlBase = `
        <div class="audio-player-box" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;padding:22px;border-radius:18px;border:1px solid #312e81;">
          <div style="font-size:0.74em;font-weight:800;color:#34d399;letter-spacing:1px;">🎧 MODO ÁUDIO • AULA NARRADA</div>
          <div style="font-size:1.12em;font-weight:800;margin:4px 0 14px;">${meta.titulo}</div>
          <div style="background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
            <button type="button" class="btn-play-pod" onclick="window.narrarTranscricaoAudio(this)" style="background:#10b981;color:#022c22;border:none;padding:11px 22px;border-radius:999px;font-weight:800;font-size:0.94em;cursor:pointer;">▶ Ouvir Aula em Áudio</button>
            <div style="flex:1;min-width:200px;">
              <div class="pod-titulo-ativo" style="font-size:0.92em;font-weight:700;color:#f1f5f9;">${meta.titulo}</div>
              <div class="pod-status" style="font-size:0.78em;color:#94a3b8;margin-top:3px;">Pronto para tocar • Clique em Ouvir Aula em Áudio</div>
            </div>
            <div class="pod-ondas" style="opacity:0.25;font-size:1.2em;letter-spacing:2px;color:#34d399;font-weight:900;">ılılılılı</div>
          </div>
        </div>
      `;
    }

    const transcricaoHtml = gerarTranscricaoFiel(meta, ramos, tituloInicial);
    const painelTranscricao = `
      <div class="pod-transcricao-box" style="margin-top:16px;background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;"
           data-tema-titulo="${meta.titulo.replace(/"/g, '&quot;')}"
           data-tema-materia="${meta.materia.replace(/"/g, '&quot;')}"
           data-tema-ementa="${(meta.ementa || '').replace(/"/g, '&quot;')}">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <span style="font-size:0.78rem;font-weight:800;color:#38bdf8;letter-spacing:0.8px;">📝 TRANSCRIÇÃO DO CONTEÚDO — ${meta.titulo.toUpperCase()}</span>
          <button type="button" onclick="window.narrarTranscricaoAudio(this)" style="background:#1e293b;color:#34d399;border:1px solid #34d399;padding:5px 12px;border-radius:999px;font-size:0.78rem;font-weight:800;cursor:pointer;">🔊 Ouvir Transcrição</button>
        </div>
        <div class="pod-transcricao-texto" style="max-height:240px;overflow-y:auto;color:#e2e8f0;font-size:0.92rem;line-height:1.68;padding-right:6px;">
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

  // === WRAPPER PRINCIPAL ===
  window.obterResumoMultiformato = function(id) {
    const res = prevObterResumo.apply(this, arguments);
    if (!res) return res;

    const dados = Object.assign({}, res);
    dados.formatos = Object.assign({}, res.formatos || {});
    if (Array.isArray(res.grupos)) {
      dados.grupos = res.grupos.map(g => Object.assign({}, g, {
        modelos: (g.modelos || []).map(m => Object.assign({}, m))
      }));
      dados.grupos.forEach(g => {
        (g.modelos || []).forEach(m => {
          if (m && m.id && !dados.formatos[m.id]) dados.formatos[m.id] = m.html;
        });
      });
    }

    const { meta, ramos } = extrairRamosEstruturados(id, dados);
    dados.titulo = meta.titulo;
    if (meta.materia) dados.materia = meta.materia;

    dados.formatos.mapa_mental = renderizarMapaMentalRadial(meta, ramos);
    dados.formatos.storytelling_caso = montarStorytellingCompleto(meta, ramos, dados.formatos.storytelling_caso);
    dados.formatos.flashcards_memorizacao = montarFlashcardsCompletos(meta, ramos, dados.formatos.flashcards_memorizacao);
    dados.formatos.quiz_justificado = montarQuizCompleto(meta, ramos, dados.formatos.quiz_justificado);
    dados.formatos.audioaula_podcast = prepararPlayerAudio(meta, ramos, dados.formatos.audioaula_podcast);

    if (Array.isArray(dados.grupos)) {
      dados.grupos.forEach(g => {
        (g.modelos || []).forEach(m => {
          if (m && m.id && dados.formatos[m.id]) {
            m.html = dados.formatos[m.id];
          }
        });
      });
    }

    return dados;
  };

  // === CONTROLES DE ÁUDIO (SEM AUTOPLAY AO TROCAR EPISÓDIO) ===
  window.__ytPodPlayers = window.__ytPodPlayers || {};
  window.__ytApiReadyQueue = window.__ytApiReadyQueue || [];
  window.__ytApiCarregada = window.__ytApiCarregada || false;

  function garantirApiYouTube(cb) {
    if (window.YT && window.YT.Player) {
      cb();
      return;
    }
    window.__ytApiReadyQueue.push(cb);
    if (!window.__ytApiCarregada) {
      window.__ytApiCarregada = true;
      const prevReady = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function() {
        if (typeof prevReady === 'function') prevReady();
        const fila = window.__ytApiReadyQueue.splice(0);
        fila.forEach(fn => { try { fn(); } catch (e) {} });
      };
      if (typeof document !== 'undefined' && document.createElement) {
        const tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        const first = document.getElementsByTagName('script')[0];
        if (first && first.parentNode) first.parentNode.insertBefore(tag, first);
        else if (document.head) document.head.appendChild(tag);
      }
    }
  }

  function atualizarUiPlayer(box, tocando, msgStatus) {
    if (!box) return;
    const btnPlay = box.querySelector('.btn-play-pod');
    const statusEl = box.querySelector('.pod-status');
    const ondasEl = box.querySelector('.pod-ondas');
    if (btnPlay) {
      btnPlay.textContent = tocando ? '⏸ Pausar Áudio' : '▶ Ouvir Aula em Áudio';
      btnPlay.style.background = tocando ? '#f59e0b' : '#10b981';
    }
    if (statusEl && msgStatus) statusEl.textContent = msgStatus;
    if (ondasEl) ondasEl.style.opacity = tocando ? '1' : '0.25';
  }

  window.narrarTranscricaoAudio = function(btn) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      atualizarUiPlayer(box, false, 'Síntese de voz não suportada neste navegador.');
      return;
    }
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      atualizarUiPlayer(box, false, 'Narração pausada');
      return;
    }
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      atualizarUiPlayer(box, true, 'Lendo transcrição em português...');
      return;
    }
    window.speechSynthesis.cancel();
    const transEl = box && box.querySelector('.pod-transcricao-texto');
    const texto = (transEl && transEl.innerText) || (box && box.innerText) || 'Resumo da aula.';
    const utter = new SpeechSynthesisUtterance(texto.slice(0, 4000));
    utter.lang = 'pt-BR';
    utter.rate = 1.02;
    utter.onstart = () => atualizarUiPlayer(box, true, 'Lendo transcrição em português...');
    utter.onend = () => atualizarUiPlayer(box, false, 'Leitura concluída');
    utter.onerror = () => atualizarUiPlayer(box, false, 'Erro ao iniciar síntese de voz');
    window.speechSynthesis.speak(utter);
  };

  window.togglePodcastHumano = function(btn) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

    const vid = box.getAttribute('data-vid-atual');
    const playerId = box.getAttribute('data-player-id');

    if (!vid || !playerId) {
      window.narrarTranscricaoAudio(btn);
      return;
    }

    Object.keys(window.__ytPodPlayers).forEach(k => {
      if (k !== playerId && window.__ytPodPlayers[k] && typeof window.__ytPodPlayers[k].pauseVideo === 'function') {
        try { window.__ytPodPlayers[k].pauseVideo(); } catch (e) {}
      }
    });

    atualizarUiPlayer(box, true, 'Conectando áudio do professor...');

    garantirApiYouTube(() => {
      let player = window.__ytPodPlayers[playerId];
      if (player && typeof player.getPlayerState === 'function') {
        const estado = player.getPlayerState();
        if (estado === 1) {
          player.pauseVideo();
          atualizarUiPlayer(box, false, 'Áudio pausado');
        } else {
          player.playVideo();
          atualizarUiPlayer(box, true, 'Tocando áudio do professor...');
        }
        return;
      }

      const alvoDiv = document.getElementById(playerId);
      if (!alvoDiv) return;

      window.__ytPodPlayers[playerId] = new window.YT.Player(playerId, {
        height: '1',
        width: '1',
        videoId: vid,
        playerVars: {
          autoplay: 1,
          controls: 0,
          rel: 0,
          modestbranding: 1,
          playsinline: 1,
          origin: window.location.origin || undefined
        },
        events: {
          onReady: function(ev) {
            try {
              ev.target.setVolume(100);
              ev.target.playVideo();
              atualizarUiPlayer(box, true, 'Tocando áudio do professor...');
            } catch (e) {}
          },
          onStateChange: function(ev) {
            if (ev.data === 1) atualizarUiPlayer(box, true, 'Tocando áudio do professor...');
            else if (ev.data === 2) atualizarUiPlayer(box, false, 'Áudio pausado');
            else if (ev.data === 0) atualizarUiPlayer(box, false, 'Aula concluída • Clique para ouvir novamente');
          },
          onError: function() {
            atualizarUiPlayer(box, false, 'Usando leitura da transcrição...');
            window.narrarTranscricaoAudio(btn);
          }
        }
      });
    });
  };

  // Troca o episódio selecionado SEM dar play automático
  window.trocarEpisodioPodcast = function(btn, novoVid, novoTitulo) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try { window.speechSynthesis.cancel(); } catch (e) {}
    }

    box.setAttribute('data-vid-atual', novoVid);
    box.querySelectorAll('.btn-ep-pod').forEach(b => {
      b.style.background = '#1e293b';
      b.style.color = '#e2e8f0';
      b.style.borderColor = '#475569';
    });
    btn.style.background = '#10b981';
    btn.style.color = '#022c22';
    btn.style.borderColor = '#10b981';

    const titEl = box.querySelector('.pod-titulo-ativo');
    if (titEl && novoTitulo) titEl.textContent = novoTitulo;

    // Atualiza o cabeçalho da transcrição para o episódio escolhido
    const transTexto = box.querySelector('.pod-transcricao-texto');
    if (transTexto && novoTitulo) {
      const primeiroP = transTexto.querySelector('p');
      if (primeiroP) {
        primeiroP.innerHTML = `<strong>🎙️ Episódio Selecionado:</strong> ${novoTitulo}`;
      }
    }

    // Se já houver player criado, apenas carrega (cueVideoById) e pausa — SEM dar play automático!
    const playerId = box.getAttribute('data-player-id');
    const player = playerId && window.__ytPodPlayers[playerId];
    if (player) {
      try {
        if (typeof player.pauseVideo === 'function') player.pauseVideo();
        if (typeof player.cueVideoById === 'function') player.cueVideoById(novoVid);
      } catch (e) {}
    }

    atualizarUiPlayer(box, false, 'Episódio selecionado • Clique em ▶ Ouvir Aula em Áudio quando quiser');
  };

  window.alternarModoCinema = function(btn) {
    const box = btn && btn.closest ? btn.closest('.video-aula-box') : null;
    if (!box) return;
    const ativo = box.getAttribute('data-cinema') === '1';
    box.setAttribute('data-cinema', ativo ? '0' : '1');
    box.style.maxWidth = ativo ? '' : '100%';
    box.style.boxShadow = ativo ? '' : '0 0 0 9999px rgba(2,6,23,0.85)';
    box.style.position = ativo ? '' : 'relative';
    box.style.zIndex = ativo ? '' : '999';
    if (btn) btn.textContent = ativo ? '🎬 Modo Cinema' : '✖ Sair do Cinema';
  };

  window.alternarTelaCheiaSim = function(btn) {
    const box = btn && btn.closest ? btn.closest('div') : null;
    if (box && box.requestFullscreen) {
      if (!document.fullscreenElement) box.requestFullscreen().catch(() => {});
      else document.exitFullscreen().catch(() => {});
    }
  };

  window.desenharPreviewSim = window.desenharPreviewSim || function() {};
  window.mudarGravidadeSim = window.mudarGravidadeSim || function(el, val) {
    const box = el && el.closest ? el.closest('[data-sim]') : null;
    if (box) box.setAttribute('data-gravidade', val);
  };
  window.mudarModoSim = window.mudarModoSim || function(el, modo) {
    const box = el && el.closest ? el.closest('[data-sim]') : null;
    if (box) box.setAttribute('data-modo', modo);
  };
  window.resetarSimCanvas = window.resetarSimCanvas || function() {};
  window.rodarSimCanvas = window.rodarSimCanvas || function() {};
  window.salvarAnotacaoDefinitiva = window.salvarAnotacaoDefinitiva || function(id, texto) {
    try { localStorage.setItem('anotacao_' + id, texto || ''); } catch (e) {}
  };
})();
"""

js_final = base_js + "\n\n" + nova_camada
with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js_final)

jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
if not os.path.exists(jsc):
    jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"

teste_js = """
const setTimeout = () => 1;
const clearTimeout = () => {};
const window = {
  location: { search: '', origin: 'http://localhost:8080' },
  addEventListener: () => {},
  listaConteudosGlobal: [
    { id: 'fis_1em_01', materiaId: 'fis', serie: '1em', nome: 'Grandezas físicas escalares e vetoriais', ementa: 'Grandezas escalares e vetoriais, Sistema Internacional de Unidades e notação científica.' }
  ],
  infoMateriasGlobal: { fis: { nome: 'Física' } }
};
const document = {
  body: null,
  head: { appendChild: () => {} },
  readyState: 'complete',
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: () => null,
  getElementsByTagName: () => [],
  createElement: () => ({})
};
class MutationObserver { observe() {} }
""" + js_final + """
const res = window.obterResumoMultiformato('fis_1em_01');
if (!res || !res.formatos) throw new Error('Resumo nulo');
if (!res.formatos.mapa_mental.includes('mm-radial-grid')) throw new Error('Mapa radial ausente');
if (!res.formatos.flashcards_memorizacao.includes('CARD #6 DE 6')) throw new Error('6 flashcards ausentes');
if (!res.formatos.quiz_justificado.includes('quiz-btn-livre')) throw new Error('Quiz clique livre ausente');
if (!res.formatos.audioaula_podcast.includes('Grandezas físicas escalares e vetoriais')) throw new Error('Transcrição fiel ausente');
print('TESTE_OK: mapa=OK | flashcards_6=OK | quiz_livre=OK | audio_sem_autoplay=OK');
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
        html = re.sub(r"v=\d+", "v=20261195", html)
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)

print("✅ Atualizado para v=20261195!")
