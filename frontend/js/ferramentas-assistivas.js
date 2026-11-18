document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  const STORAGE_THEME_KEY = 'techadvisors_assistiva_theme';
  const STORAGE_PREFS_KEY = 'techadvisors_assistiva_prefs';

  const btnLight = document.getElementById('btn-mode-light');
  const btnDark = document.getElementById('btn-mode-dark');
  const btnFabTheme = document.getElementById('btn-fab-theme');
  const toastEl = document.getElementById('assistiva-toast');
  const irlenOverlay = document.getElementById('irlen-overlay');

  let toastTimer = null;
  function showToast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2800);
  }

  const prefs = JSON.parse(localStorage.getItem(STORAGE_PREFS_KEY) || '{}');
  function savePrefs() {
    localStorage.setItem(STORAGE_PREFS_KEY, JSON.stringify(prefs));
    if (window.applyGlobalAssistivaPrefs) {
      window.applyGlobalAssistivaPrefs();
    }
  }

  // Tema Claro / Dark Mode
  function applyTheme(theme, notify = false) {
    const validTheme = theme === 'dark' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', validTheme);
    localStorage.setItem(STORAGE_THEME_KEY, validTheme);
    if (btnLight) btnLight.classList.toggle('active', validTheme === 'light');
    if (btnDark) btnDark.classList.toggle('active', validTheme === 'dark');
    if (notify) showToast(validTheme === 'dark' ? 'Dark Mode ativado' : 'Modo Claro ativado');
  }

  applyTheme(localStorage.getItem(STORAGE_THEME_KEY) || 'light', false);
  if (btnLight) btnLight.addEventListener('click', () => applyTheme('light', true));
  if (btnDark) btnDark.addEventListener('click', () => applyTheme('dark', true));
  if (btnFabTheme) {
    btnFabTheme.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark', true);
    });
  }

  // 1. FONTE PARA DISLEXIA (OpenDyslexic + espaçamento real em toda a plataforma)
  const chkDyslexic = document.getElementById('chk-dyslexic');
  if (chkDyslexic) {
    chkDyslexic.checked = !!prefs.dyslexic;
    document.body.classList.toggle('dyslexic-mode', !!prefs.dyslexic);
    chkDyslexic.addEventListener('change', () => {
      prefs.dyslexic = chkDyslexic.checked;
      document.body.classList.toggle('dyslexic-mode', prefs.dyslexic);
      savePrefs();
      showToast(prefs.dyslexic
        ? 'Fonte OpenDyslexic e espaçamento ampliado ativados em todo o sistema!'
        : 'Tipografia padrão restaurada');
    });
  }

  // 2. FILTRO DE COR (SÍNDROME DE IRLEN)
  const selIrlen = document.getElementById('sel-irlen');
  const irlenColors = {
    none: 'transparent',
    blue: 'rgba(147, 197, 253, 0.22)',
    yellow: 'rgba(253, 224, 71, 0.22)',
    green: 'rgba(134, 239, 172, 0.22)',
    pink: 'rgba(249, 168, 212, 0.22)'
  };
  if (selIrlen && irlenOverlay) {
    if (prefs.irlen && irlenColors[prefs.irlen]) {
      selIrlen.value = prefs.irlen;
      irlenOverlay.style.backgroundColor = irlenColors[prefs.irlen];
    }
    selIrlen.addEventListener('change', () => {
      prefs.irlen = selIrlen.value;
      irlenOverlay.style.backgroundColor = irlenColors[prefs.irlen] || 'transparent';
      savePrefs();
      showToast(prefs.irlen === 'none' ? 'Filtro de Irlen removido' : 'Filtro de cor aplicado na tela');
    });
  }

  // 3. LUPA DE DETALHES (Lente flutuante que amplia o texto sob o cursor)
  const chkLupa = document.getElementById('chk-lupa');
  const magnifier = document.createElement('div');
  magnifier.id = 'assistiva-magnifier';
  document.body.appendChild(magnifier);

  if (chkLupa) {
    chkLupa.checked = !!prefs.lupa;
    chkLupa.addEventListener('change', () => {
      prefs.lupa = chkLupa.checked;
      if (!prefs.lupa) magnifier.style.display = 'none';
      savePrefs();
      showToast(prefs.lupa ? 'Lupa ativada! Passe o mouse sobre qualquer texto.' : 'Lupa desativada');
    });

    document.addEventListener('mousemove', (e) => {
      if (!chkLupa.checked) {
        magnifier.style.display = 'none';
        return;
      }
      const target = document.elementFromPoint(e.clientX, e.clientY);
      const textEl = target && target.closest('p, h1, h2, h3, span, label, button, option');
      const txt = textEl ? textEl.innerText.trim() : '';
      if (txt && txt.length > 1) {
        magnifier.textContent = txt.slice(0, 110);
        magnifier.style.display = 'block';
        const left = Math.min(window.innerWidth - 260, e.clientX + 18);
        const top = Math.min(window.innerHeight - 130, e.clientY + 18);
        magnifier.style.left = left + 'px';
        magnifier.style.top = top + 'px';
      } else {
        magnifier.style.display = 'none';
      }
    });
  }

  // ATALHOS RÁPIDOS: MODO LEITURA FÁCIL, ZOOM 125% E LEITOR GLOBAL
  const btnLeituraFacil = document.getElementById('btn-leitura-facil');
  if (btnLeituraFacil) {
    btnLeituraFacil.classList.toggle('active', !!prefs.easyReading);
    btnLeituraFacil.addEventListener('click', () => {
      prefs.easyReading = !prefs.easyReading;
      if (prefs.easyReading && chkDyslexic && !chkDyslexic.checked) {
        chkDyslexic.checked = true;
        prefs.dyslexic = true;
      }
      btnLeituraFacil.classList.toggle('active', prefs.easyReading);
      savePrefs();
      showToast(prefs.easyReading ? 'Modo Leitura Fácil ativado (fonte + espaçamento amplo)' : 'Modo Leitura Fácil desativado');
    });
  }

  const btnZoom125 = document.getElementById('btn-zoom-125');
  if (btnZoom125) {
    btnZoom125.classList.toggle('active', !!prefs.zoom125);
    btnZoom125.addEventListener('click', () => {
      prefs.zoom125 = !prefs.zoom125;
      btnZoom125.classList.toggle('active', prefs.zoom125);
      savePrefs();
      showToast(prefs.zoom125 ? 'Zoom de 125% ativado' : 'Zoom restaurado para 100%');
    });
  }

  const btnLeitorGlobal = document.getElementById('btn-leitor-global');
  let leitorAtivo = false;
  function falarTexto(texto) {
    if (!('speechSynthesis' in window)) {
      showToast('Leitor de voz não suportado neste navegador');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = 'pt-BR';
    utterance.rate = 0.96;
    window.speechSynthesis.speak(utterance);
  }

  if (btnLeitorGlobal) {
    btnLeitorGlobal.addEventListener('click', () => {
      leitorAtivo = !leitorAtivo;
      btnLeitorGlobal.classList.toggle('active', leitorAtivo);
      if (!leitorAtivo) {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        showToast('Leitor em voz alta desativado');
        return;
      }
      const selecao = window.getSelection().toString().trim();
      falarTexto(selecao || 'Leitor global ativado. Clique em qualquer texto da tela para ouvi-lo em voz alta.');
      showToast('Leitor ativado! Clique em qualquer texto para ouvir.');
    });

    document.addEventListener('click', (e) => {
      if (!leitorAtivo || e.target.closest('#btn-leitor-global')) return;
      const bloco = e.target.closest('.tool-card, .page-header, p, h1, h2, h3');
      if (bloco && bloco.innerText.trim()) {
        falarTexto(bloco.innerText.trim());
      }
    });
  }

  // 4. SIMPLIFICADOR DE LINGUAGEM (Converte descrições longas em bullets curtos)
  const btnSimplificar = document.getElementById('btn-simplificar-ia');
  let textoSimplificado = false;
  const textosOriginais = new Map();
  const resumosSimples = [
    '• Letras com base mais pesada para não embaralhar.',
    '• Tela com cor suave para descansar os olhos.',
    '• Lente que aumenta as palavras ao passar o mouse.',
    '• Transforma textos difíceis em tópicos curtos.',
    '• Relógio que avisa a hora de estudar e descansar.',
    '• Som calmante para ajudar a manter a atenção.',
    '• Ícones e desenhos que explicam palavras difíceis.',
    '• Esquema visual em caixas para estudar mais rápido.'
  ];
  if (btnSimplificar) {
    btnSimplificar.addEventListener('click', () => {
      textoSimplificado = !textoSimplificado;
      const descs = document.querySelectorAll('.tool-desc');
      descs.forEach((p, idx) => {
        if (!textosOriginais.has(p)) textosOriginais.set(p, p.textContent);
        p.textContent = textoSimplificado
          ? (resumosSimples[idx] || '• Conteúdo resumido de forma direta.')
          : textosOriginais.get(p);
      });
      btnSimplificar.textContent = textoSimplificado ? 'Texto Original' : 'Ativar IA';
      showToast(textoSimplificado ? 'Textos convertidos para linguagem simples!' : 'Textos originais restaurados');
    });
  }

  // 5. CRONÔMETRO POMODORO REAL (Widget flutuante com contagem regressiva)
  const btnPomodoro = document.getElementById('btn-pomodoro-start');
  const selPomodoro = document.getElementById('sel-pomodoro');
  let pomodoroInterval = null;
  let segundosRestantes = 0;
  let pomodoroPausado = false;

  const pomoBox = document.createElement('div');
  pomoBox.style.cssText = 'position:fixed;bottom:76px;right:20px;background:#1e1b4b;color:#fff;border:1px solid #8b5cf6;border-radius:14px;padding:14px 18px;box-shadow:0 12px 30px rgba(0,0,0,0.35);z-index:9999;display:none;min-width:220px;';
  pomoBox.innerHTML = `
    <div style="font-size:0.75rem;color:#c4b5fd;font-weight:700;text-transform:uppercase;margin-bottom:4px;">⏱️ Cronômetro de Foco</div>
    <div id="pomo-clock" style="font-size:1.8rem;font-weight:800;letter-spacing:1px;margin-bottom:8px;">25:00</div>
    <div style="display:flex;gap:8px;">
      <button id="pomo-pause" type="button" style="flex:1;padding:6px 10px;border-radius:8px;border:none;background:#7c3aed;color:#fff;font-weight:600;cursor:pointer;">Pausar</button>
      <button id="pomo-close" type="button" style="padding:6px 10px;border-radius:8px;border:1px solid #4c1d95;background:transparent;color:#e2e8f0;cursor:pointer;">Fechar</button>
    </div>
  `;
  document.body.appendChild(pomoBox);

  function atualizarRelogio() {
    const min = String(Math.floor(segundosRestantes / 60)).padStart(2, '0');
    const seg = String(segundosRestantes % 60).padStart(2, '0');
    document.getElementById('pomo-clock').textContent = `${min}:${seg}`;
  }

  if (btnPomodoro && selPomodoro) {
    btnPomodoro.addEventListener('click', () => {
      clearInterval(pomodoroInterval);
      segundosRestantes = parseInt(selPomodoro.value, 10) * 60;
      pomodoroPausado = false;
      document.getElementById('pomo-pause').textContent = 'Pausar';
      pomoBox.style.display = 'block';
      atualizarRelogio();
      showToast(`Cronômetro de ${selPomodoro.value} minutos iniciado!`);

      pomodoroInterval = setInterval(() => {
        if (pomodoroPausado) return;
        segundosRestantes--;
        atualizarRelogio();
        if (segundosRestantes <= 0) {
          clearInterval(pomodoroInterval);
          showToast('🎉 Tempo de foco concluído! Hora de uma pausa.');
          falarTexto('Tempo de foco concluído! Faça uma pequena pausa.');
        }
      }, 1000);
    });

    document.getElementById('pomo-pause').addEventListener('click', (e) => {
      pomodoroPausado = !pomodoroPausado;
      e.target.textContent = pomodoroPausado ? 'Retomar' : 'Pausar';
    });

    document.getElementById('pomo-close').addEventListener('click', () => {
      clearInterval(pomodoroInterval);
      pomoBox.style.display = 'none';
    });
  }

  // 6. SONS DE FOCO (Ruído Rosa, Chuva Suave e Ondas do Mar via Web Audio API)
  let audioCtx = null;
  let noiseNode = null;
  let filterNode = null;
  const selSomFoco = document.getElementById('sel-som-foco');

  function stopNoise() {
    if (noiseNode) {
      try { noiseNode.disconnect(); } catch (_) {}
      noiseNode = null;
    }
    if (filterNode) {
      try { filterNode.disconnect(); } catch (_) {}
      filterNode = null;
    }
  }

  function startAmbientSound(tipo) {
    stopNoise();
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const bufferSize = 3 * audioCtx.sampleRate;
    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const output = buffer.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      let sample = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.035;
      if (tipo === 'sea') {
        const wave = 0.55 + 0.45 * Math.sin((2 * Math.PI * i) / bufferSize);
        sample *= wave * 1.4;
      }
      output[i] = sample;
      b6 = white * 0.115926;
    }

    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    source.loop = true;

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = tipo === 'rain' ? 1400 : (tipo === 'sea' ? 420 : 800);

    source.connect(filter);
    filter.connect(audioCtx.destination);
    source.start(0);
    noiseNode = source;
    filterNode = filter;
  }

  if (selSomFoco) {
    selSomFoco.addEventListener('change', () => {
      if (selSomFoco.value === 'off') {
        stopNoise();
        showToast('Áudio de fundo desativado');
      } else {
        startAmbientSound(selSomFoco.value);
        const nomes = { rain: 'Chuva Suave', pink: 'Ruído Rosa (TDAH)', sea: 'Ondas do Mar' };
        showToast(`Tocando: ${nomes[selSomFoco.value] || 'Som de Foco'}`);
      }
    });
  }

  // 7. DICIONÁRIO COM IMAGENS / PICTOGRAMAS (Destaca termos e exibe card visual)
  const chkPictogramas = document.getElementById('chk-pictogramas');
  const picTooltip = document.createElement('div');
  picTooltip.id = 'pictogram-tooltip';
  document.body.appendChild(picTooltip);

  const dicionarioVisual = {
    'OpenDyslexic': '🔤 Fonte com base reforçada que evita que letras como b/d ou p/q pareçam invertidas.',
    'Síndrome de Irlen': '🎨 Sensibilidade à luz e ao contraste; filtros coloridos reduzem o cansaço visual.',
    'Lupa': '🔍 Amplia trechos da tela para facilitar a leitura sem forçar a vista.',
    'Ruído Rosa': '🎧 Som contínuo grave que bloqueia barulhos externos e melhora o foco.',
    'pictogramas': '🖼️ Símbolos e ilustrações simples que representam ideias de forma direta.'
  };

  function aplicarPictogramas(ativo) {
    document.querySelectorAll('.tool-desc').forEach((p) => {
      if (!ativo) {
        p.innerHTML = p.textContent;
        return;
      }
      let html = p.textContent;
      Object.keys(dicionarioVisual).forEach((termo) => {
        const regex = new RegExp(`(${termo})`, 'gi');
        html = html.replace(regex, `<span class="pictogram-term" data-term="${termo}">$1</span>`);
      });
      p.innerHTML = html;
    });
  }

  if (chkPictogramas) {
    aplicarPictogramas(chkPictogramas.checked);
    chkPictogramas.addEventListener('change', () => {
      aplicarPictogramas(chkPictogramas.checked);
      picTooltip.style.display = 'none';
      showToast(chkPictogramas.checked ? 'Dicionário visual ativado nos termos destacados!' : 'Pictogramas ocultados');
    });

    document.addEventListener('mouseover', (e) => {
      const span = e.target.closest('.pictogram-term');
      if (!span || !chkPictogramas.checked) return;
      const chave = Object.keys(dicionarioVisual).find((k) => k.toLowerCase() === span.dataset.term.toLowerCase());
      if (chave) {
        picTooltip.textContent = dicionarioVisual[chave];
        picTooltip.style.display = 'block';
        picTooltip.style.left = Math.min(window.innerWidth - 290, e.clientX + 12) + 'px';
        picTooltip.style.top = Math.min(window.innerHeight - 100, e.clientY + 16) + 'px';
      }
    });
    document.addEventListener('mouseout', (e) => {
      if (e.target.closest('.pictogram-term')) picTooltip.style.display = 'none';
    });
  }

  // 8. RESUMOS EM ESQUEMAS VISUAIS (Modal com Mapa Mental / Fluxograma)
  const btnGerarMapa = document.getElementById('btn-gerar-mapa');
  const mapaModal = document.createElement('div');
  mapaModal.style.cssText = 'position:fixed;inset:0;background:rgba(11,9,25,0.78);display:none;align-items:center;justify-content:center;z-index:10002;padding:20px;';
  mapaModal.innerHTML = `
    <div style="background:#17142d;color:#fff;border:1px solid #7c3aed;border-radius:16px;max-width:680px;width:100%;padding:24px;box-shadow:0 20px 50px rgba(0,0,0,0.5);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <h3 style="font-size:1.2rem;font-weight:800;color:#c4b5fd;">🧠 Mapa Visual de Apoio ao Estudo</h3>
        <button id="fechar-mapa-modal" type="button" style="background:#2e1065;color:#fff;border:none;border-radius:8px;padding:6px 12px;cursor:pointer;font-weight:700;">✕ Fechar</button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">
        <div style="background:#231d47;border-left:4px solid #38bdf8;padding:12px;border-radius:10px;">
          <strong style="color:#7dd3fc;display:block;margin-bottom:4px;">1. Leitura & Visão</strong>
          <span style="font-size:0.84rem;color:#e2e8f0;">OpenDyslexic + Filtro Irlen + Lupa reduzem esforço visual.</span>
        </div>
        <div style="background:#231d47;border-left:4px solid #a855f7;padding:12px;border-radius:10px;">
          <strong style="color:#d8b4fe;display:block;margin-bottom:4px;">2. Foco (TDAH)</strong>
          <span style="font-size:0.84rem;color:#e2e8f0;">Blocos Pomodoro de 15–25 min + Ruído Rosa contínuo.</span>
        </div>
        <div style="background:#231d47;border-left:4px solid #34d399;padding:12px;border-radius:10px;">
          <strong style="color:#6ee7b7;display:block;margin-bottom:4px;">3. Apoio Cognitivo</strong>
          <span style="font-size:0.84rem;color:#e2e8f0;">Pictogramas + Texto Simplificado + Esquemas Visuais.</span>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(mapaModal);

  if (btnGerarMapa) {
    btnGerarMapa.addEventListener('click', () => {
      mapaModal.style.display = 'flex';
    });
    document.getElementById('fechar-mapa-modal').addEventListener('click', () => {
      mapaModal.style.display = 'none';
    });
    mapaModal.addEventListener('click', (e) => {
      if (e.target === mapaModal) mapaModal.style.display = 'none';
    });
  }
});
