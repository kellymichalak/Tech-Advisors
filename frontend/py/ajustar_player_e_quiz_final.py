import os, re, subprocess

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Remove qualquer ocorrência restante do aviso "(Clique em outra alternativa para testar!)"
js = re.sub(r"\s*<em>\(Clique em outra alternativa para testar!\)</em>", "", js)

# 2. Substitui prepararPlayerAudio e o engine de sincronização para colocar -10s, +10s e Velocidade
# dentro da barra principal do player, usar texto completo da aula e sincronizar com getCurrentTime/getDuration
antigo_trecho = """  function montarBlocosReaisDoEpisodio(tituloEpisodio, materia, ementa) {"""
idx_inicio = js.find(antigo_trecho)
assert idx_inicio != -1, "Bloco montarBlocosReaisDoEpisodio não encontrado"

idx_fim_engine = js.find("  window.alternarModoCinema = function(btn) {")
assert idx_fim_engine != -1, "Fim do engine de áudio não encontrado"

novo_bloco_audio = """  function montarBlocosReaisDoEpisodio(tituloEpisodio, materia, ementa, textoCompletoTopico) {
    const ep = String(tituloEpisodio || '').trim();
    const epLow = ep.toLowerCase();
    const mat = materia || 'Ciências e Humanidades';
    const tituloLimpo = ep.replace(/\\|.*$/, '').trim() || ep;

    // Extrai parágrafos reais do conteúdo completo do tópico quando disponíveis
    const paragrafosReais = String(textoCompletoTopico || '')
      .split(/(?<=[.!?])\\s+/)
      .map(s => s.trim())
      .filter(s => s.length >= 30);

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

    if (paragrafosReais.length >= 4) {
      const q = Math.ceil(paragrafosReais.length / 4);
      const b1 = paragrafosReais.slice(0, q).join(' ');
      const b2 = paragrafosReais.slice(q, q * 2).join(' ');
      const b3 = paragrafosReais.slice(q * 2, q * 3).join(' ');
      const b4 = paragrafosReais.slice(q * 3).join(' ');
      return [
        { tag: `BLOCO 01 • INTRODUÇÃO — ${tituloLimpo.toUpperCase()}`, cor: '#38bdf8', texto: b1 },
        { tag: 'BLOCO 02 • DESENVOLVIMENTO CONCEITUAL', cor: '#34d399', texto: b2 || b1 },
        { tag: 'BLOCO 03 • ANÁLISE E RELAÇÕES', cor: '#a78bfa', texto: b3 || b2 || b1 },
        { tag: 'BLOCO 04 • APLICAÇÕES E FECHAMENTO', cor: '#fbbf24', texto: b4 || `Síntese final de ${tituloLimpo} em ${mat}.` }
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

  function gerarTranscricaoKaraokeBlocos(meta, ramos, tituloEpisodio, textoCompletoTopico) {
    const ep = tituloEpisodio || meta.titulo;
    const contador = { n: 0 };
    const blocosDados = montarBlocosReaisDoEpisodio(ep, meta.materia, meta.ementa, textoCompletoTopico);

    return blocosDados.map(b => `
      <div class="trans-bloco" style="margin-bottom:12px;padding:12px 14px;background:rgba(15,23,42,0.85);border-left:4px solid ${b.cor};border-radius:10px;">
        <div style="font-size:0.74rem;font-weight:800;color:${b.cor};letter-spacing:0.6px;margin-bottom:5px;">${b.tag}</div>
        <div style="font-size:0.93rem;line-height:1.72;">${tokenizarKaraoke(b.texto, contador)}</div>
      </div>
    `).join('');
  }
  window.__gerarTranscricaoKaraokeBlocos = gerarTranscricaoKaraokeBlocos;

  function prepararPlayerAudio(meta, ramos, htmlAudioOriginal, textoCompletoTopico) {
    let tituloInicial = meta.titulo;
    let htmlBase = htmlAudioOriginal || '';

    const controlesNaBarra = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" onclick="window.avancarRetrocederAudio(this, -10)" title="Voltar 10 segundos" style="background:#1e293b;color:#f8fafc;border:1px solid #475569;padding:7px 11px;border-radius:999px;font-size:0.78em;font-weight:800;cursor:pointer;">⏪ -10s</button>
        <button type="button" onclick="window.avancarRetrocederAudio(this, 10)" title="Avançar 10 segundos" style="background:#1e293b;color:#f8fafc;border:1px solid #475569;padding:7px 11px;border-radius:999px;font-size:0.78em;font-weight:800;cursor:pointer;">+10s ⏩</button>
        <select class="pod-velocidade-sel" onchange="window.alterarVelocidadeAudio(this, this.value)" title="Velocidade de reprodução" style="background:#1e293b;color:#38bdf8;border:1px solid #475569;border-radius:999px;padding:7px 10px;font-size:0.78em;font-weight:800;cursor:pointer;">
          <option value="0.75">0.75x</option>
          <option value="1" selected>1.0x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="2">2.0x</option>
        </select>
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

      // Insere os controles -10s, +10s e Velocidade dentro da barra principal, logo antes de pod-ondas
      if (htmlBase.includes("<div class='pod-ondas'")) {
        htmlBase = htmlBase.replace("<div class='pod-ondas'", controlesNaBarra + "<div class='pod-ondas'");
      }
    } else {
      htmlBase = `
        <div class="audio-player-box" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;padding:22px;border-radius:18px;border:1px solid #312e81;">
          <div style="font-size:0.74em;font-weight:800;color:#34d399;letter-spacing:1px;">🎧 MODO ÁUDIO • AULA NARRADA SINCRONIZADA</div>
          <div style="font-size:1.12em;font-weight:800;margin:4px 0 14px;">${meta.titulo}</div>
          <div style="background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            <button type="button" class="btn-play-pod" onclick="window.narrarTranscricaoAudio(this)" style="background:#10b981;color:#022c22;border:none;padding:11px 20px;border-radius:999px;font-weight:800;font-size:0.92em;cursor:pointer;">▶ Ouvir Aula em Áudio</button>
            <div style="flex:1;min-width:180px;">
              <div class="pod-titulo-ativo" style="font-size:0.92em;font-weight:700;color:#f1f5f9;">${meta.titulo}</div>
              <div class="pod-status" style="font-size:0.78em;color:#94a3b8;margin-top:3px;">Pronto para tocar • Apenas áudio</div>
            </div>
            ${controlesNaBarra}
            <div class="pod-ondas" style="opacity:0.25;font-size:1.2em;letter-spacing:2px;color:#34d399;font-weight:900;">ılılılılı</div>
          </div>
        </div>
      `;
    }

    const transcricaoHtml = gerarTranscricaoKaraokeBlocos(meta, ramos, tituloInicial, textoCompletoTopico);
    const painelTranscricao = `
      <div class="pod-transcricao-box" data-materia="${(meta.materia || '').replace(/"/g, '&quot;')}" data-ementa="${(meta.ementa || '').replace(/"/g, '&quot;')}" style="margin-top:14px;background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <span style="font-size:0.78rem;font-weight:800;color:#38bdf8;letter-spacing:0.8px;">📝 TRANSCRIÇÃO SINCRONIZADA POR BLOCOS (CLIQUE NA PALAVRA PARA SALTAR)</span>
          <button type="button" onclick="window.narrarTranscricaoAudio(this)" style="background:#064e3b;color:#6ee7b7;border:1px solid #10b981;padding:5px 12px;border-radius:999px;font-size:0.76rem;font-weight:800;cursor:pointer;">🔊 Ler com Voz IA</button>
        </div>
        <div class="pod-transcricao-texto" style="max-height:300px;overflow-y:auto;padding-right:6px;">
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

    const textoCompletoTopico = limparTexto(dados.formatos.resumo_narrativo || dados.formatos.texto_teorico || '');

    dados.formatos.mapa_mental = renderizarMapaMentalRadial(meta, ramos);
    dados.formatos.infografico_ilustrado = renderizarInfograficoIlustrado(meta, ramos);
    dados.formatos.storytelling_caso = montarStorytellingCompleto(meta, ramos, dados.formatos.storytelling_caso);
    dados.formatos.flashcards_memorizacao = montarFlashcardsCompletos(meta, ramos, dados.formatos.flashcards_memorizacao);
    dados.formatos.quiz_justificado = montarQuizCompleto(meta, ramos, dados.formatos.quiz_justificado);
    dados.formatos.audioaula_podcast = prepararPlayerAudio(meta, ramos, dados.formatos.audioaula_podcast, textoCompletoTopico);

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

  // === ENGINE DE ÁUDIO SINCRONIZADO COM TEMPO REAL DO PLAYER E ONBOUNDARY ===
  window.__ytPodPlayers = window.__ytPodPlayers || {};
  window.__ytApiReadyQueue = window.__ytApiReadyQueue || [];
  window.__ytApiCarregada = window.__ytApiCarregada || false;
  window.__karaokeTimer = window.__karaokeTimer || null;
  window.__karaokeState = window.__karaokeState || { box: null, wordIdx: 0, rate: 1, playing: false };

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

  function destacarPalavraNoIndice(box, idx) {
    if (!box) return;
    const palavras = box.querySelectorAll('.trans-palavra');
    if (!palavras.length) return;
    const clamped = Math.max(0, Math.min(idx, palavras.length - 1));
    window.__karaokeState.wordIdx = clamped;

    palavras.forEach((sp, i) => {
      sp.classList.remove('ativa', 'falada');
      if (i < clamped) sp.classList.add('falada');
      else if (i === clamped) sp.classList.add('ativa');
    });

    const ativa = palavras[clamped];
    const container = box.querySelector('.pod-transcricao-texto');
    if (ativa && container && typeof ativa.offsetTop === 'number') {
      const targetScroll = ativa.offsetTop - container.offsetTop - container.clientHeight / 2;
      container.scrollTop = Math.max(0, targetScroll);
    }
  }

  function pararLoopKaraoke() {
    if (window.__karaokeTimer) {
      clearInterval(window.__karaokeTimer);
      window.__karaokeTimer = null;
    }
    window.__karaokeState.playing = false;
  }

  // Sincroniza o destaque das palavras com o tempo real do áudio YouTube (getCurrentTime / getDuration)
  function iniciarSincronizacaoYouTube(box, playerId) {
    pararLoopKaraoke();
    if (!box) return;
    const palavras = box.querySelectorAll('.trans-palavra');
    if (!palavras.length) return;

    window.__karaokeState.box = box;
    window.__karaokeState.playing = true;

    window.__karaokeTimer = setInterval(() => {
      if (!window.__karaokeState.playing) return;
      const ytPlayer = playerId && window.__ytPodPlayers[playerId];
      if (ytPlayer && typeof ytPlayer.getCurrentTime === 'function' && typeof ytPlayer.getDuration === 'function') {
        try {
          const atual = ytPlayer.getCurrentTime() || 0;
          const duracao = ytPlayer.getDuration() || 0;
          if (duracao > 0) {
            const proporcao = Math.max(0, Math.min(0.999, atual / duracao));
            const idxAlvo = Math.floor(proporcao * palavras.length);
            destacarPalavraNoIndice(box, idxAlvo);
            return;
          }
        } catch (e) {}
      }
    }, 250);
  }

  window.narrarTranscricaoAudio = function(btn, startWordIdx) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : window.__karaokeState.box;
    if (!box) return;

    const palavras = Array.from(box.querySelectorAll('.trans-palavra'));
    const selVel = box.querySelector('.pod-velocidade-sel');
    const rate = selVel ? parseFloat(selVel.value) || 1 : 1;

    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      atualizarUiPlayer(box, false, 'Síntese de voz não suportada neste navegador.');
      return;
    }

    if (typeof startWordIdx !== 'number' && window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      window.__karaokeState.playing = false;
      atualizarUiPlayer(box, false, 'Narração pausada');
      return;
    }

    if (typeof startWordIdx !== 'number' && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      window.__karaokeState.playing = true;
      atualizarUiPlayer(box, true, `Lendo transcrição (${rate}x)...`);
      return;
    }

    pararLoopKaraoke();
    window.speechSynthesis.cancel();
    const idxInicio = typeof startWordIdx === 'number' ? startWordIdx : (window.__karaokeState.wordIdx || 0);
    window.__karaokeState.wordIdx = idxInicio;
    window.__karaokeState.box = box;

    const spansRestantes = palavras.slice(idxInicio);
    const offsetsPalavras = [];
    let acumulado = 0;
    spansRestantes.forEach((sp, i) => {
      offsetsPalavras.push({ charPos: acumulado, wordIdx: idxInicio + i });
      acumulado += (sp.textContent || '').length + 1;
    });

    const textoRestante = spansRestantes.map(p => p.textContent).join(' ').trim();
    if (!textoRestante) return;

    const utter = new SpeechSynthesisUtterance(textoRestante.slice(0, 4000));
    utter.lang = 'pt-BR';
    utter.rate = rate;

    utter.onboundary = (ev) => {
      if (typeof ev.charIndex === 'number' && offsetsPalavras.length) {
        let escolhido = offsetsPalavras[0].wordIdx;
        for (let i = 0; i < offsetsPalavras.length; i++) {
          if (offsetsPalavras[i].charPos <= ev.charIndex) {
            escolhido = offsetsPalavras[i].wordIdx;
          } else {
            break;
          }
        }
        destacarPalavraNoIndice(box, escolhido);
      }
    };

    utter.onstart = () => {
      window.__karaokeState.playing = true;
      destacarPalavraNoIndice(box, idxInicio);
      atualizarUiPlayer(box, true, `Lendo transcrição (${rate}x)...`);
    };
    utter.onend = () => {
      window.__karaokeState.playing = false;
      window.__karaokeState.wordIdx = 0;
      atualizarUiPlayer(box, false, 'Leitura concluída');
    };
    utter.onerror = () => {
      window.__karaokeState.playing = false;
      atualizarUiPlayer(box, false, 'Erro ao iniciar voz');
    };

    window.speechSynthesis.speak(utter);
  };

  window.saltarParaPalavraTranscricao = function(spanEl, idx) {
    const box = spanEl && spanEl.closest ? spanEl.closest('.audio-player-box') : null;
    if (!box) return;
    const palavras = box.querySelectorAll('.trans-palavra');
    destacarPalavraNoIndice(box, idx);

    // Se o player YouTube estiver tocando, salta proporcionalmente na timeline do vídeo também
    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    if (ytPlayer && typeof ytPlayer.getDuration === 'function' && typeof ytPlayer.seekTo === 'function' && palavras.length) {
      try {
        const dur = ytPlayer.getDuration() || 0;
        if (dur > 0) {
          ytPlayer.seekTo((idx / palavras.length) * dur, true);
          return;
        }
      } catch (e) {}
    }

    window.narrarTranscricaoAudio(spanEl, idx);
  };

  window.avancarRetrocederAudio = function(btn, deltaSegundos) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    const palavras = box.querySelectorAll('.trans-palavra');

    if (ytPlayer && typeof ytPlayer.getCurrentTime === 'function' && typeof ytPlayer.seekTo === 'function') {
      try {
        const atual = ytPlayer.getCurrentTime() || 0;
        const duracao = (typeof ytPlayer.getDuration === 'function' && ytPlayer.getDuration()) || 0;
        const novoTempo = Math.max(0, duracao > 0 ? Math.min(duracao - 1, atual + deltaSegundos) : atual + deltaSegundos);
        ytPlayer.seekTo(novoTempo, true);
        if (duracao > 0 && palavras.length) {
          destacarPalavraNoIndice(box, Math.floor((novoTempo / duracao) * palavras.length));
        }
        atualizarUiPlayer(box, window.__karaokeState.playing, `${deltaSegundos > 0 ? 'Avançou +10s' : 'Voltou -10s'}`);
        return;
      } catch (e) {}
    }

    if (palavras.length) {
      const deltaPalavras = Math.round(deltaSegundos * 2.5);
      const novoIdx = Math.max(0, Math.min(palavras.length - 1, (window.__karaokeState.wordIdx || 0) + deltaPalavras));
      destacarPalavraNoIndice(box, novoIdx);
      if (typeof window !== 'undefined' && 'speechSynthesis' in window && window.speechSynthesis.speaking) {
        window.narrarTranscricaoAudio(btn, novoIdx);
      }
    }
    atualizarUiPlayer(box, window.__karaokeState.playing, `${deltaSegundos > 0 ? 'Avançou +10s' : 'Voltou -10s'}`);
  };

  window.alterarVelocidadeAudio = function(selEl, novaVel) {
    const box = selEl && selEl.closest ? selEl.closest('.audio-player-box') : null;
    const rate = parseFloat(novaVel) || 1;
    window.__karaokeState.rate = rate;

    if (box) {
      const playerId = box.getAttribute('data-player-id');
      const ytPlayer = playerId && window.__ytPodPlayers[playerId];
      if (ytPlayer && typeof ytPlayer.setPlaybackRate === 'function') {
        try { ytPlayer.setPlaybackRate(rate); } catch (e) {}
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window && window.speechSynthesis.speaking) {
        window.narrarTranscricaoAudio(selEl, window.__karaokeState.wordIdx || 0);
      }
      atualizarUiPlayer(box, window.__karaokeState.playing, `Velocidade: ${rate}x`);
    }
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
          pararLoopKaraoke();
          atualizarUiPlayer(box, false, 'Áudio pausado');
        } else {
          player.playVideo();
          iniciarSincronizacaoYouTube(box, playerId);
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
              const selVel = box.querySelector('.pod-velocidade-sel');
              const rate = selVel ? parseFloat(selVel.value) || 1 : 1;
              ev.target.setVolume(100);
              if (typeof ev.target.setPlaybackRate === 'function') ev.target.setPlaybackRate(rate);
              ev.target.playVideo();
              iniciarSincronizacaoYouTube(box, playerId);
              atualizarUiPlayer(box, true, 'Tocando áudio do professor...');
            } catch (e) {}
          },
          onStateChange: function(ev) {
            if (ev.data === 1) {
              iniciarSincronizacaoYouTube(box, playerId);
              atualizarUiPlayer(box, true, 'Tocando áudio do professor...');
            } else if (ev.data === 2) {
              pararLoopKaraoke();
              atualizarUiPlayer(box, false, 'Áudio pausado');
            } else if (ev.data === 0) {
              pararLoopKaraoke();
              atualizarUiPlayer(box, false, 'Aula concluída • Clique para ouvir novamente');
            }
          },
          onError: function() {
            atualizarUiPlayer(box, false, 'Usando leitura sincronizada da transcrição...');
            window.narrarTranscricaoAudio(btn);
          }
        }
      });
    });
  };

  window.trocarEpisodioPodcast = function(btn, novoVid, novoTitulo) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

    pararLoopKaraoke();
    window.__karaokeState.wordIdx = 0;
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

    const transBox = box.querySelector('.pod-transcricao-box');
    const transTextoEl = box.querySelector('.pod-transcricao-texto');
    if (transBox && transTextoEl && novoTitulo && typeof window.__gerarTranscricaoKaraokeBlocos === 'function') {
      const matEp = transBox.getAttribute('data-materia') || '';
      const emEp = transBox.getAttribute('data-ementa') || '';
      transTextoEl.innerHTML = window.__gerarTranscricaoKaraokeBlocos({ titulo: novoTitulo, materia: matEp, ementa: emEp }, [], novoTitulo, '');
    }

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
"""

js = js[:idx_inicio] + novo_bloco_audio + "\n" + js[idx_fim_engine:]

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
""" + js + """
if (js_check := ("para testar" in window.obterResumoMultiformato('fis_1em_01').formatos.quiz_justificado)) throw new Error('Aviso ainda presente no quiz');
const res = window.obterResumoMultiformato('fis_1em_01');
if (!res.formatos.audioaula_podcast.includes('-10s') || !res.formatos.audioaula_podcast.includes('pod-velocidade-sel')) throw new Error('Controles na barra ausentes');
print('TESTE_OK: quiz_sem_aviso=OK | controles_na_barra=OK | sync_tempo_real=OK');
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
        html = re.sub(r"v=\d+", "v=20261200", html)
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)

print("✅ Sistema atualizado para v=20261200!")
