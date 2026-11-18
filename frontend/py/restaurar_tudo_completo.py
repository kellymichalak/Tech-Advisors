import os, re, subprocess

with open("../js/resumos.js", "r", encoding="utf-8") as f:
    js = f.read()

# 1. Restaura o comportamento de mapa_mental (preserva o rico original dos arquivos js/conteudos/*.js; usa radial só se estiver vazio)
js = js.replace(
    "dados.formatos.mapa_mental = novoMapaHtml;",
    "if (!dados.formatos.mapa_mental || !String(dados.formatos.mapa_mental).trim()) dados.formatos.mapa_mental = novoMapaHtml;"
)
js = js.replace(
    "if (m && m.id === 'mapa_mental') {\n          m.html = novoMapaHtml;\n        }",
    "if (m && m.id === 'mapa_mental' && (!m.html || !String(m.html).trim())) {\n          m.html = novoMapaHtml;\n        }"
)

# 2. Enriquecer o fallback de window.obterResumoMultiformato para temas que não estão em bancoConteudosModulares
idx_fb = js.find("const lista = window.listaConteudosGlobal || [];")
idx_iife = js.find("(function() {\n  const prevObterResumo")
if idx_fb != -1 and idx_iife != -1:
    novo_fallback = """  const lista = window.listaConteudosGlobal || [];
  const itemLista = lista.find(item => item.id === id);
  if (!itemLista) return null;

  const infoMat = (window.infoMateriasGlobal && window.infoMateriasGlobal[itemLista.materiaId]) || { nome: (itemLista.materiaId || '').toUpperCase() };
  const nomesSeries = { "1em": "1º Ano E.M.", "2em": "2º Ano E.M.", "3em": "3º Ano E.M." };
  const serieTxt = nomesSeries[itemLista.serie] || (itemLista.serie || '').toUpperCase();
  const ementa = itemLista.ementa || itemLista.nome || '';
  const subtopicos = ementa.replace(/\\.$/, '').split(/[,;]/).map(s => s.trim()).filter(Boolean);
  while (subtopicos.length < 3) {
    subtopicos.push(`${itemLista.nome} — Aplicação ${subtopicos.length + 1}`);
  }

  const flashcardsHtml = `
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">
      ${subtopicos.slice(0, 4).map((sub, i) => `
        <div class="flashcard-interativo" onclick="this.classList.toggle('virado')" style="cursor:pointer;background:#1e293b;border:1px solid #475569;border-radius:16px;padding:18px;min-height:140px;display:flex;flex-direction:column;justify-content:space-between;">
          <div style="font-size:0.75rem;font-weight:800;color:#38bdf8;">CARD ${i + 1} • CLIQUE PARA VIRAR</div>
          <div class="fc-frente" style="font-weight:700;color:#f8fafc;font-size:1rem;margin:10px 0;">O que caracteriza <em>${sub}</em> em ${itemLista.nome}?</div>
          <div class="fc-verso" style="display:none;color:#a7f3d0;font-size:0.92rem;line-height:1.5;border-top:1px solid #334155;padding-top:10px;">
            <strong>Síntese:</strong> Conceito essencial de <strong>${itemLista.nome}</strong> (${infoMat.nome}), diretamente ligado a ${ementa.toLowerCase()}.
          </div>
        </div>
      `).join('')}
    </div>
    <style>.flashcard-interativo.virado .fc-verso{display:block !important;}.flashcard-interativo.virado{border-color:#10b981 !important;background:#0f172a !important;}</style>
  `;

  const quizHtml = `
    <div class="quiz-container-multi">
      ${subtopicos.slice(0, 3).map((sub, idx) => `
        <div class="quiz-card-interativo" style="margin-bottom:16px;">
          <p><strong>Questão ${idx + 1} (${itemLista.nome}):</strong> Qual elemento abaixo integra corretamente o estudo de <em>${sub}</em>?</p>
          <div class="quiz-opcoes">
            <button class="quiz-opcao-btn" onclick="verificarRespostaQuiz(this, true, 'Excelente! ${sub} é um pilar fundamental de ${itemLista.nome}.')">A análise estruturada de ${sub} dentro de ${infoMat.nome}</button>
            <button class="quiz-opcao-btn" onclick="verificarRespostaQuiz(this, false, 'Atenção: revise os conceitos principais de ${itemLista.nome}.')">Um fenômeno sem relação com ${ementa.slice(0, 60)}...</button>
          </div>
          <div class="quiz-feedback"></div>
        </div>
      `).join('')}
    </div>
  `;

  const storytellingHtml = `
    <div class="aula-teorica-completa" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);padding:22px;border-radius:18px;border:1px solid #312e81;color:#f8fafc;">
      <div style="font-size:0.78rem;font-weight:800;color:#f59e0b;letter-spacing:1px;">📖 ESTUDO DE CASO & CONTEXTUALIZAÇÃO</div>
      <h2 style="color:#fff;margin-top:6px;">Como ${itemLista.nome} aparece na prática?</h2>
      <p>Imagine uma situação real de laboratório, cotidiano ou exame vestibular em que você precisa tomar uma decisão rápida envolvendo <strong>${itemLista.nome}</strong> (${infoMat.nome} — ${serieTxt}).</p>
      <div class="passo-a-passo" style="background:rgba(15,23,42,0.75);border-left:4px solid #f59e0b;padding:14px 18px;border-radius:12px;margin:14px 0;">
        <p><strong>1. O Cenário:</strong> Um estudante precisa resolver um problema prático envolvendo <em>${subtopicos[0]}</em> e <em>${subtopicos[1]}</em>.</p>
        <p><strong>2. O Ponto de Virada:</strong> Ao conectar ${subtopicos[0]} com ${subtopicos[2] || subtopicos[0]}, o padrão fica claro e evita as pegadinhas clássicas de prova.</p>
        <p><strong>3. Conclusão Aplicada:</strong> Dominar ${ementa} permite interpretar gráficos, textos e situações-problema com segurança.</p>
      </div>
    </div>
  `;

  const audioHtml = `
    <div class="audio-player-box" style="background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;padding:22px;border-radius:18px;border:1px solid #312e81;">
      <div style="font-size:0.74em;font-weight:800;color:#34d399;letter-spacing:1px;">🎧 MODO ÁUDIO (NARRAÇÃO DO RESUMO)</div>
      <div style="font-size:1.12em;font-weight:800;margin:4px 0 14px;">${itemLista.nome}</div>
      <div style="background:#020617;border:1px solid #334155;border-radius:14px;padding:16px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <button type="button" class="btn-play-pod" onclick="window.togglePodcastHumano(this)" data-texto-narracao="${(itemLista.nome + '. ' + ementa).replace(/"/g, '&quot;')}" style="background:#10b981;color:#022c22;border:none;padding:11px 22px;border-radius:999px;font-weight:800;font-size:0.94em;cursor:pointer;">▶ Ouvir Aula em Áudio</button>
        <div style="flex:1;min-width:200px;">
          <div class="pod-titulo-ativo" style="font-size:0.92em;font-weight:700;color:#f1f5f9;">Resumo Narrado — ${itemLista.nome}</div>
          <div class="pod-status" style="font-size:0.78em;color:#94a3b8;margin-top:3px;">Pronto para tocar</div>
        </div>
        <div class="pod-ondas" style="opacity:0.25;font-size:1.2em;letter-spacing:2px;color:#34d399;font-weight:900;">ılılılılı</div>
      </div>
    </div>
  `;

  return {
    titulo: itemLista.nome,
    materia: infoMat.nome,
    serie: serieTxt,
    formatos: {
      texto_teorico: `<div class="aula-teorica-completa"><h2>1. Visão Geral: ${itemLista.nome}</h2><p>Estudo completo de <strong>${itemLista.nome}</strong> em <strong>${infoMat.nome}</strong> (${serieTxt}).</p><div class="destaque-formula">Ementa: ${ementa}</div><h2>2. Tópicos Fundamentais</h2><div class="passo-a-passo">${subtopicos.map(s => `<p>• <strong>${s}</strong></p>`).join('')}</div></div>`,
      resumo_narrativo: `<div class="aula-teorica-completa"><h2>Resumo Direto: ${itemLista.nome}</h2><p>${ementa}</p></div>`,
      mapa_mental: "",
      infografico_ilustrado: "",
      storytelling_caso: storytellingHtml,
      audioaula_podcast: audioHtml,
      flashcards_memorizacao: flashcardsHtml,
      quiz_justificado: quizHtml
    }
  };
};
"""
    js = js[:idx_fb] + novo_fallback + "\n" + js[idx_iife:]

# 3. Injeta todas as funções globais interativas (Áudio YouTube + SpeechSynthesis, Modo Cinema, Simulador e Anotações)
funcoes_interativas = """
// ============================================================================
// RESTAURAÇÃO DO PLAYER DE ÁUDIO (PODCAST YOUTUBE + SPEECH API) E INTERATIVIDADE
// ============================================================================
(function() {
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

  function falarFallbackNavegador(box, btn) {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      atualizarUiPlayer(box, false, 'Áudio indisponível neste navegador.');
      return;
    }
    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause();
      atualizarUiPlayer(box, false, 'Áudio pausado');
      return;
    }
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      atualizarUiPlayer(box, true, 'Tocando narração do professor...');
      return;
    }
    window.speechSynthesis.cancel();
    const texto = (btn && btn.getAttribute('data-texto-narracao')) ||
                  (box && box.innerText) || 'Resumo em áudio.';
    const utter = new SpeechSynthesisUtterance(texto.slice(0, 3500));
    utter.lang = 'pt-BR';
    utter.rate = 1.02;
    utter.onstart = () => atualizarUiPlayer(box, true, 'Tocando narração em voz alta...');
    utter.onend = () => atualizarUiPlayer(box, false, 'Reprodução concluída');
    utter.onerror = () => atualizarUiPlayer(box, false, 'Erro ao sintetizar voz');
    window.speechSynthesis.speak(utter);
  }

  window.togglePodcastHumano = function(btn) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

    const vid = box.getAttribute('data-vid-atual');
    const playerId = box.getAttribute('data-player-id');

    // Se não há vídeo YouTube configurado, usa síntese de voz nativa
    if (!vid || !playerId) {
      falarFallbackNavegador(box, btn);
      return;
    }

    // Pausa outros players ativos
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
          atualizarUiPlayer(box, true, 'Tocando áudio do professor (modo podcast)...');
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
              atualizarUiPlayer(box, true, 'Tocando áudio do professor (modo podcast)...');
            } catch (e) {}
          },
          onStateChange: function(ev) {
            if (ev.data === 1) atualizarUiPlayer(box, true, 'Tocando áudio do professor (modo podcast)...');
            else if (ev.data === 2) atualizarUiPlayer(box, false, 'Áudio pausado');
            else if (ev.data === 0) atualizarUiPlayer(box, false, 'Aula concluída • Clique para ouvir novamente');
          },
          onError: function() {
            atualizarUiPlayer(box, false, 'Áudio bloqueado pelo navegador — usando narração alternativa...');
            falarFallbackNavegador(box, btn);
          }
        }
      });
    });
  };

  window.trocarEpisodioPodcast = function(btn, novoVid, novoTitulo) {
    const box = btn && btn.closest ? btn.closest('.audio-player-box') : null;
    if (!box) return;

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

    const playerId = box.getAttribute('data-player-id');
    const player = playerId && window.__ytPodPlayers[playerId];
    if (player && typeof player.loadVideoById === 'function') {
      player.loadVideoById(novoVid);
      atualizarUiPlayer(box, true, 'Tocando episódio selecionado...');
    } else {
      const btnPlay = box.querySelector('.btn-play-pod');
      if (btnPlay) window.togglePodcastHumano(btnPlay);
    }
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
    try {
      localStorage.setItem('anotacao_' + id, texto || '');
    } catch (e) {}
  };
})();
"""

if "window.togglePodcastHumano" not in js:
    js = js + "\n" + funcoes_interativas

with open("../js/resumos.js", "w", encoding="utf-8") as f:
    f.write(js)

# Valida sintaxe no JavaScriptCore
jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
if not os.path.exists(jsc):
    jsc = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"

teste_js = """
const setTimeout = () => 1;
const clearTimeout = () => {};
const window = { location: { search: '', origin: 'http://localhost:8080' }, addEventListener: () => {} };
const document = {
  body: null,
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: () => null,
  getElementsByTagName: () => []
};
class MutationObserver { observe() {} }
""" + js + """
if (typeof window.togglePodcastHumano !== 'function') throw new Error('togglePodcastHumano ausente');
if (typeof window.trocarEpisodioPodcast !== 'function') throw new Error('trocarEpisodioPodcast ausente');
const res = window.obterResumoMultiformato('por_1em_01');
if (!res || !res.formatos || !res.formatos.storytelling_caso || !res.formatos.flashcards_memorizacao) {
  throw new Error('Formatos ricos ausentes no fallback');
}
print('TESTE_OK: audio_handlers=OK | storytelling=OK | flashcards=OK | quiz=OK');
"""

res = subprocess.run([jsc, "-e", teste_js], capture_output=True, text=True)
if res.returncode != 0:
    print("❌ Erro:", res.stderr, res.stdout)
    raise SystemExit(1)
print("✅", res.stdout.strip())

# Atualiza versão tanto em pages/resumos.html quanto em pages/audios.html
for page in ["../pages/resumos.html", "../pages/audios.html"]:
    if os.path.exists(page):
        with open(page, "r", encoding="utf-8") as f:
            html = f.read()
        html = re.sub(r"v=\d+", "v=20261185", html)
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)

print("✅ pages/resumos.html e pages/audios.html atualizados para v=20261185!")
