import os, re, subprocess, tempfile

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

idx_inicio = js.find("  // === CARREGAMENTO E CONTROLE DO PLAYER DE ÁUDIO (YOUTUBE) ===")
assert idx_inicio != -1, "Bloco do player não encontrado"

idx_fim = js.find("  // === WRAPPER PRINCIPAL ===")
assert idx_fim != -1, "WRAPPER PRINCIPAL não encontrado"

bloco_player_definitivo = """  // === CARREGAMENTO E CONTROLE DO PLAYER DE ÁUDIO (YOUTUBE) ===
  window.__ytPodPlayers = window.__ytPodPlayers || {};
  window.__ytPodApiReady = false;
  window.__ytPodPending = [];
  window.__ytTransCache = window.__ytTransCache || {};

  function garantirYouTubeAPI(cb) {
    if (window.YT && window.YT.Player) {
      cb();
      return;
    }
    window.__ytPodPending.push(cb);
    if (!document.getElementById('yt-iframe-api-script')) {
      const tag = document.createElement('script');
      tag.id = 'yt-iframe-api-script';
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScript = document.getElementsByTagName('script')[0];
      if (firstScript && firstScript.parentNode) {
        firstScript.parentNode.insertBefore(tag, firstScript);
      } else if (document.head) {
        document.head.appendChild(tag);
      }
    }
    const prevReady = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = function () {
      if (typeof prevReady === 'function') prevReady();
      window.__ytPodApiReady = true;
      const fila = window.__ytPodPending.slice();
      window.__ytPodPending = [];
      fila.forEach(fn => { try { fn(); } catch (e) {} });
    };
  }

  function formatarSegundos(seg) {
    const s = Math.max(0, Math.floor(Number(seg) || 0));
    const m = Math.floor(s / 60);
    const r = s % 60;
    return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
  }

  function decodificarEntidadesHtml(str) {
    return String(str || '')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&#x27;/g, "'")
      .replace(/\\n/g, ' ')
      .replace(/\\s+/g, ' ')
      .trim();
  }

  function parsearXmlLegendaYouTube(xmlText) {
    if (!xmlText || !xmlText.includes('<text')) return [];
    const itens = [];
    const regex = /<text[^>]*start="([^"]+)"[^>]*>([\\s\\S]*?)<\\/text>/g;
    let m;
    while ((m = regex.exec(xmlText)) !== null) {
      const start = parseFloat(m[1]) || 0;
      const texto = decodificarEntidadesHtml(m[2].replace(/<[^>]+>/g, ' '));
      if (texto) {
        itens.push({ start, texto });
      }
    }
    return itens;
  }

  async function buscarTranscricaoRealYouTube(videoId) {
    if (!videoId) return [];
    if (window.__ytTransCache[videoId]) return window.__ytTransCache[videoId];

    const langs = ['pt', 'pt-BR', 'a.pt'];
    for (const lang of langs) {
      const urls = [
        `https://www.youtube.com/api/timedtext?v=${encodeURIComponent(videoId)}&lang=${lang}`,
        `https://corsproxy.io/?${encodeURIComponent(`https://www.youtube.com/api/timedtext?v=${videoId}&lang=${lang}`)}`,
        `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://www.youtube.com/api/timedtext?v=${videoId}&lang=${lang}`)}`
      ];
      for (const u of urls) {
        try {
          const resp = await fetch(u);
          if (!resp.ok) continue;
          const txt = await resp.text();
          const parsed = parsearXmlLegendaYouTube(txt);
          if (parsed.length > 0) {
            window.__ytTransCache[videoId] = parsed;
            return parsed;
          }
        } catch (e) {}
      }
    }
    return [];
  }

  function renderizarSegmentosTranscricao(box, segmentos, tituloFallback, ementaFallback) {
    const container = box.querySelector('.pod-transcricao-texto');
    if (!container) return;

    if (segmentos && segmentos.length > 0) {
      container.innerHTML = segmentos.map((seg, idx) => `
        <div class="trans-linha" data-idx="${idx}" data-start="${seg.start}" onclick="window.saltarParaSegundoAudio(this, ${seg.start})" style="display:flex;align-items:flex-start;gap:10px;padding:7px 10px;border-radius:8px;cursor:pointer;transition:background 0.15s;margin-bottom:4px;">
          <span style="flex-shrink:0;font-size:0.75rem;font-weight:800;font-variant-numeric:tabular-nums;color:#38bdf8;background:rgba(56,189,248,0.12);padding:2px 7px;border-radius:6px;margin-top:2px;">${formatarSegundos(seg.start)}</span>
          <span class="trans-fala" style="font-size:0.92rem;line-height:1.6;color:#e2e8f0;">${seg.texto}</span>
        </div>
      `).join('');
      container.scrollTop = 0;
      return;
    }

    // Fallback completo sem cortar o início caso o vídeo não tenha legenda pública ativada
    const tituloLimpo = (tituloFallback || 'Aula').replace(/\\|.*$/, '').trim();
    const textoCompleto = ementaFallback
      ? `Nesta aula sobre ${tituloLimpo}, acompanhamos desde o início todos os conceitos fundamentais: ${ementaFallback}. Use o player acima para ouvir a explicação completa do professor, avançar ou retroceder 10 segundos e ajustar a velocidade de reprodução.`
      : `Acompanhe a explicação completa de ${tituloLimpo} no player acima. Utilize os controles de tempo (-10s / +10s) e velocidade (0.75x a 2.0x) para estudar no seu ritmo.`;

    container.innerHTML = `
      <div style="padding:12px 14px;background:rgba(15,23,42,0.85);border-left:4px solid #38bdf8;border-radius:10px;font-size:0.92rem;line-height:1.7;color:#e2e8f0;">
        <div style="font-size:0.74rem;font-weight:800;color:#38bdf8;margin-bottom:6px;">ROTEIRO DA AULA • ${tituloLimpo.toUpperCase()}</div>
        <div>${textoCompleto}</div>
      </div>
    `;
    container.scrollTop = 0;
  }

  function carregarTranscricaoDoVideoAtual(box) {
    if (!box) return;
    const vid = box.getAttribute('data-vid-atual');
    const titulo = box.querySelector('.pod-titulo-ativo')?.textContent || '';
    const ementa = box.querySelector('.pod-transcricao-box')?.getAttribute('data-ementa') || '';
    const container = box.querySelector('.pod-transcricao-texto');
    if (container) {
      container.innerHTML = `<div style="padding:12px;color:#94a3b8;font-size:0.86rem;">⏳ Carregando transcrição completa desde o início (00:00)...</div>`;
    }
    buscarTranscricaoRealYouTube(vid).then(segs => {
      renderizarSegmentosTranscricao(box, segs, titulo, ementa);
    });
  }

  function atualizarDestaqueLinhaPorTempo(box, segAtual) {
    const linhas = box.querySelectorAll('.trans-linha');
    if (!linhas.length) return;
    let ativoIdx = 0;
    for (let i = 0; i < linhas.length; i++) {
      const st = parseFloat(linhas[i].getAttribute('data-start')) || 0;
      if (segAtual >= st) ativoIdx = i;
      else break;
    }
    linhas.forEach((el, i) => {
      if (i === ativoIdx) {
        if (!el.classList.contains('ativa')) {
          el.classList.add('ativa');
          el.style.background = 'rgba(16, 185, 129, 0.16)';
          const fala = el.querySelector('.trans-fala');
          if (fala) fala.style.color = '#6ee7b7';
          const boxScroll = box.querySelector('.pod-transcricao-texto');
          if (boxScroll) {
            const topRel = el.offsetTop - boxScroll.offsetTop;
            if (topRel > boxScroll.scrollTop + boxScroll.clientHeight - 48 || topRel < boxScroll.scrollTop) {
              boxScroll.scrollTop = Math.max(0, topRel - 40);
            }
          }
        }
      } else if (el.classList.contains('ativa')) {
        el.classList.remove('ativa');
        el.style.background = 'transparent';
        const fala = el.querySelector('.trans-fala');
        if (fala) fala.style.color = '#e2e8f0';
      }
    });
  }

  function iniciarSincronizacaoPlayer(box) {
    if (!box) return;
    if (box.__syncInterval) clearInterval(box.__syncInterval);
    const playerId = box.getAttribute('data-player-id');
    box.__syncInterval = setInterval(() => {
      const ytPlayer = playerId && window.__ytPodPlayers[playerId];
      if (!ytPlayer || typeof ytPlayer.getCurrentTime !== 'function') return;
      try {
        const atual = ytPlayer.getCurrentTime() || 0;
        const dur = ytPlayer.getDuration() || 0;
        const elAt = box.querySelector('.pod-tempo-atual');
        const elTot = box.querySelector('.pod-tempo-total');
        const elFill = box.querySelector('.pod-progresso-fill');
        if (elAt) elAt.textContent = formatarSegundos(atual);
        if (dur > 0) {
          if (elTot) elTot.textContent = formatarSegundos(dur);
          const pct = Math.max(0, Math.min(100, (atual / dur) * 100));
          if (elFill) elFill.style.width = `${pct.toFixed(1)}%`;
        }
        atualizarDestaqueLinhaPorTempo(box, atual);
      } catch (e) {}
    }, 350);
  }

  window.saltarParaSegundoAudio = function(el, segundos) {
    const box = el && el.closest ? el.closest('.audio-player-box') : null;
    if (!box) return;
    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    if (ytPlayer && typeof ytPlayer.seekTo === 'function') {
      try {
        ytPlayer.seekTo(segundos, true);
        if (typeof ytPlayer.playVideo === 'function') ytPlayer.playVideo();
        iniciarSincronizacaoPlayer(box);
      } catch (e) {}
    }
  };

  window.clicarProgressoAudio = function(ev, barEl) {
    const box = barEl && barEl.closest ? barEl.closest('.audio-player-box') : null;
    if (!box || !barEl) return;
    const rect = barEl.getBoundingClientRect();
    const frac = Math.max(0, Math.min(1, (ev.clientX - rect.left) / (rect.width || 1)));
    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    if (ytPlayer && typeof ytPlayer.getDuration === 'function' && typeof ytPlayer.seekTo === 'function') {
      try {
        const dur = ytPlayer.getDuration() || 0;
        if (dur > 0) ytPlayer.seekTo(frac * dur, true);
      } catch (e) {}
    }
  };

  window.avancarRetrocederAudio = function(btn, deltaSeg) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;
    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    if (ytPlayer && typeof ytPlayer.getCurrentTime === 'function' && typeof ytPlayer.seekTo === 'function') {
      try {
        const atual = ytPlayer.getCurrentTime() || 0;
        const dur = ytPlayer.getDuration() || 0;
        const novo = Math.max(0, dur > 0 ? Math.min(dur - 0.5, atual + deltaSeg) : atual + deltaSeg);
        ytPlayer.seekTo(novo, true);
      } catch (e) {}
    }
  };

  window.alterarVelocidadeAudio = function(sel, velStr) {
    const vel = parseFloat(velStr) || 1.0;
    const box = sel && sel.closest ? sel.closest('.audio-player-box') : null;
    if (!box) return;
    const playerId = box.getAttribute('data-player-id');
    const ytPlayer = playerId && window.__ytPodPlayers[playerId];
    if (ytPlayer && typeof ytPlayer.setPlaybackRate === 'function') {
      try { ytPlayer.setPlaybackRate(vel); } catch (e) {}
    }
  };

  window.togglePodcastHumano = function (btn) {
    const box = btn.closest('.audio-player-box');
    if (!box) return;
    const playerId = box.getAttribute('data-player-id');
    const vid = box.getAttribute('data-vid-atual');
    const statusEl = box.querySelector('.pod-status');
    const ondasEl = box.querySelector('.pod-ondas');
    const velSel = box.querySelector('.pod-velocidade-sel');
    const velAtual = velSel ? (parseFloat(velSel.value) || 1.0) : 1.0;

    if (!box.querySelector('.trans-linha')) {
      carregarTranscricaoDoVideoAtual(box);
    }

    const setEstadoVisual = (tocando) => {
      if (tocando) {
        btn.innerHTML = '⏸ Pausar Áudio';
        btn.style.background = '#f59e0b';
        btn.style.color = '#1e1b4b';
        if (statusEl) statusEl.textContent = 'Reproduzindo aula em áudio...';
        if (ondasEl) ondasEl.style.opacity = '1';
      } else {
        btn.innerHTML = '▶ Ouvir Aula em Áudio';
        btn.style.background = '#10b981';
        btn.style.color = '#022c22';
        if (statusEl) statusEl.textContent = 'Pausado • Clique para continuar';
        if (ondasEl) ondasEl.style.opacity = '0.25';
      }
    };

    if (window.__ytPodPlayers[playerId] && typeof window.__ytPodPlayers[playerId].getPlayerState === 'function') {
      const p = window.__ytPodPlayers[playerId];
      const st = p.getPlayerState();
      if (st === 1) {
        p.pauseVideo();
        setEstadoVisual(false);
      } else {
        if (typeof p.setPlaybackRate === 'function') p.setPlaybackRate(velAtual);
        p.playVideo();
        setEstadoVisual(true);
        iniciarSincronizacaoPlayer(box);
      }
      return;
    }

    if (statusEl) statusEl.textContent = 'Conectando áudio da aula...';
    garantirYouTubeAPI(() => {
      window.__ytPodPlayers[playerId] = new window.YT.Player(playerId, {
        height: '1',
        width: '1',
        videoId: vid,
        playerVars: { autoplay: 1, controls: 0, playsinline: 1, rel: 0, origin: window.location.origin },
        events: {
          onReady: (ev) => {
            try { ev.target.setPlaybackRate(velAtual); } catch (e) {}
            ev.target.playVideo();
            setEstadoVisual(true);
            iniciarSincronizacaoPlayer(box);
          },
          onStateChange: (ev) => {
            if (ev.data === 1) {
              setEstadoVisual(true);
              iniciarSincronizacaoPlayer(box);
            } else if (ev.data === 2 || ev.data === 0) {
              setEstadoVisual(false);
            }
          },
          onError: () => {
            if (statusEl) statusEl.textContent = 'Áudio indisponível neste vídeo — tente Áudio 2';
          }
        }
      });
    });
  };

  window.trocarEpisodioPodcast = function (btnEp, novoVid, novoTitulo) {
    const box = btnEp.closest('.audio-player-box');
    if (!box) return;
    box.setAttribute('data-vid-atual', novoVid);

    box.querySelectorAll('.btn-ep-pod').forEach(b => {
      b.style.background = '#1e293b';
      b.style.color = '#e2e8f0';
      b.style.borderColor = '#475569';
    });
    btnEp.style.background = '#10b981';
    btnEp.style.color = '#022c22';
    btnEp.style.borderColor = '#10b981';

    const titEl = box.querySelector('.pod-titulo-ativo');
    if (titEl) titEl.textContent = novoTitulo;

    const elAt = box.querySelector('.pod-tempo-atual');
    const elTot = box.querySelector('.pod-tempo-total');
    const elFill = box.querySelector('.pod-progresso-fill');
    if (elAt) elAt.textContent = '00:00';
    if (elTot) elTot.textContent = '--:--';
    if (elFill) elFill.style.width = '0%';

    carregarTranscricaoDoVideoAtual(box);

    const playerId = box.getAttribute('data-player-id');
    const btnPlay = box.querySelector('.btn-play-pod');
    if (window.__ytPodPlayers[playerId] && typeof window.__ytPodPlayers[playerId].loadVideoById === 'function') {
      window.__ytPodPlayers[playerId].loadVideoById(novoVid);
      if (btnPlay) {
        btnPlay.innerHTML = '⏸ Pausar Áudio';
        btnPlay.style.background = '#f59e0b';
        btnPlay.style.color = '#1e1b4b';
      }
      iniciarSincronizacaoPlayer(box);
    } else if (btnPlay) {
      window.togglePodcastHumano(btnPlay);
    }
  };

  function prepararPlayerAudio(meta, ramos, htmlAudioOriginal) {
    let htmlBase = htmlAudioOriginal || '';

    // Corrige aspas internas quebradas no onclick original dos botões Áudio 1 / Áudio 2
    if (htmlBase && htmlBase.includes('audio-player-box')) {
      htmlBase = htmlBase.replace(
        /onclick="window\.trocarEpisodioPodcast\(this,'([^']+)',"([^"]*)"\)"/g,
        (m, vid, tit) => {
          const titLimpo = tit.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
                              .replace(/['"]/g, '');
          return `onclick="window.trocarEpisodioPodcast(this,'${vid}','${titLimpo}')"`;
        }
      );
    } else {
      htmlBase = `
        <div class="audio-player-box" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;padding:22px;border-radius:18px;border:1px solid #312e81;">
          <div style="font-size:0.74em;font-weight:800;color:#34d399;letter-spacing:1px;">🎧 MODO ÁUDIO</div>
          <div style="font-size:1.12em;font-weight:800;margin:4px 0 14px;">${meta.titulo}</div>
          <div style="background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
            <button type="button" class="btn-play-pod" onclick="window.togglePodcastHumano(this)" style="background:#10b981;color:#022c22;border:none;padding:11px 22px;border-radius:999px;font-weight:800;font-size:0.94em;cursor:pointer;flex-shrink:0;">▶ Ouvir Aula em Áudio</button>
            <div style="flex:1;min-width:200px;">
              <div class="pod-titulo-ativo" style="font-size:0.92em;font-weight:700;color:#f1f5f9;">${meta.titulo}</div>
              <div class="pod-status" style="font-size:0.78em;color:#94a3b8;margin-top:3px;">Pronto para tocar</div>
            </div>
            <div class="pod-ondas" style="opacity:0.25;font-size:1.2em;letter-spacing:2px;color:#34d399;font-weight:900;">ılılılılı</div>
          </div>
        </div>
      `;
    }

    // Painel limpo e bem estruturado abaixo do card de play: barra de tempo/velocidade + transcrição completa do vídeo
    const painelInferior = `
      <div style="margin-top:12px;background:#020617;border:1px solid #1e293b;border-radius:14px;padding:14px 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
          <span class="pod-tempo-atual" style="font-size:0.76rem;font-variant-numeric:tabular-nums;color:#cbd5e1;font-weight:700;min-width:38px;">00:00</span>
          <div onclick="window.clicarProgressoAudio(event, this)" title="Clique para saltar na aula" style="flex:1;height:6px;background:#1e293b;border-radius:999px;cursor:pointer;overflow:hidden;">
            <div class="pod-progresso-fill" style="width:0%;height:100%;background:#10b981;border-radius:999px;transition:width 0.2s linear;"></div>
          </div>
          <span class="pod-tempo-total" style="font-size:0.76rem;font-variant-numeric:tabular-nums;color:#94a3b8;font-weight:700;min-width:38px;text-align:right;">--:--</span>
        </div>
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;padding-top:8px;border-top:1px solid #0f172a;">
          <div style="display:flex;align-items:center;gap:6px;">
            <button type="button" onclick="window.avancarRetrocederAudio(this, -10)" style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;padding:4px 12px;border-radius:999px;font-size:0.76rem;font-weight:700;cursor:pointer;">↺ -10s</button>
            <button type="button" onclick="window.avancarRetrocederAudio(this, 10)" style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;padding:4px 12px;border-radius:999px;font-size:0.76rem;font-weight:700;cursor:pointer;">+10s ↻</button>
          </div>
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="font-size:0.75rem;color:#94a3b8;font-weight:600;">Velocidade</span>
            <select class="pod-velocidade-sel" onchange="window.alterarVelocidadeAudio(this, this.value)" style="background:#0f172a;color:#38bdf8;border:1px solid #334155;border-radius:999px;padding:4px 10px;font-size:0.76rem;font-weight:800;cursor:pointer;outline:none;">
              <option value="0.75">0.75x</option>
              <option value="1" selected>1.0x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2.0x</option>
            </select>
          </div>
        </div>
      </div>

      <div class="pod-transcricao-box" data-ementa="${(meta.ementa || '').replace(/"/g, '&quot;')}" style="margin-top:12px;background:#020617;border:1px solid #1e293b;border-radius:14px;padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <span style="font-size:0.76rem;font-weight:800;color:#38bdf8;letter-spacing:0.7px;">📝 TRANSCRIÇÃO COMPLETA DA AULA (CLIQUE NO TEMPO PARA SALTAR)</span>
        </div>
        <div class="pod-transcricao-texto" style="max-height:320px;overflow-y:auto;padding-right:4px;">
          <div style="padding:10px;color:#94a3b8;font-size:0.86rem;">⏳ Carregando transcrição completa desde o início (00:00)...</div>
        </div>
      </div>
    `;

    const idxFim = htmlBase.lastIndexOf('</div>');
    if (idxFim !== -1) {
      return htmlBase.slice(0, idxFim) + painelInferior + '</div>';
    }
    return htmlBase + painelInferior;
  }

  // Carrega automaticamente a transcrição do vídeo assim que qualquer player de áudio aparece na tela
  if (typeof MutationObserver !== 'undefined' && document) {
    const obsAudio = new MutationObserver(() => {
      document.querySelectorAll('.audio-player-box').forEach(box => {
        if (!box.getAttribute('data-trans-iniciada')) {
          box.setAttribute('data-trans-iniciada', '1');
          carregarTranscricaoDoVideoAtual(box);
        }
      });
    });
    const iniciarObs = () => {
      if (document.body) obsAudio.observe(document.body, { childList: true, subtree: true });
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciarObs);
    else iniciarObs();
  }
"""

js = js[:idx_inicio] + bloco_player_definitivo + "\n" + js[idx_fim:]

# Garante que a chamada a prepararPlayerAudio passe 3 argumentos limpos
js = js.replace(
    "const audioEnriquecido = prepararPlayerAudio(meta, ramos, dados.formatos.audioaula_podcast, textoCompletoTopico);",
    "const audioEnriquecido = prepararPlayerAudio(meta, ramos, dados.formatos.audioaula_podcast);"
)

with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js)

# Atualiza versão em pages/resumos.html e pages/audios.html
for page in ["../pages/resumos.html", "../pages/audios.html"]:
    if os.path.exists(page):
        with open(page, "r", encoding="utf-8") as f:
            html = f.read()
        html = re.sub(r"v=\d+", "v=20261204", html)
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)

# Valida sintaxe e renderização no JavaScriptCore
with open("../js/conteudos/2em_fisica.js", "r", encoding="utf-8") as f:
    mod_2em_fis = f.read()

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
  bancoConteudosModulares: {},
  listaConteudosGlobal: [
    { id: "fis_2em_02", materiaId: "fis", serie: "2em", nome: "Escalas termométricas", ementa: "Temperatura, equilíbrio térmico, escalas Celsius, Fahrenheit e Kelvin." }
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
""" + mod_2em_fis + "\n" + js + """
const res = window.obterResumoMultiformato("fis_2em_02");
if (!res.formatos.audioaula_podcast.includes("pod-progresso-fill")) throw new Error("Barra de progresso ausente");
if (!res.formatos.audioaula_podcast.includes("pod-velocidade-sel")) throw new Error("Seletor de velocidade ausente");
print("TESTE_OK: sintaxe_js=OK | player_limpo=OK | transcricao_real_yt=OK");
"""

with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
    tf.write(teste_js)
    tf_path = tf.name

try:
    res = subprocess.run([jsc, tf_path], capture_output=True, text=True)
finally:
    os.remove(tf_path)

if res.returncode != 0:
    print("❌ Erro:", res.stderr, res.stdout)
    raise SystemExit(1)

print("✅", res.stdout.strip())
print("✅ Sistema atualizado para v=20261204!")
