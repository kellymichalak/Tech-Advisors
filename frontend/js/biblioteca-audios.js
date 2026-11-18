document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) window.lucide.createIcons();
  
    // Tema sincronizado com o portal
    const themeKey = 'techadvisors_assistiva_theme';
    const btnLight = document.getElementById('btn-audio-light');
    const btnDark = document.getElementById('btn-audio-dark');
  
    function applyTheme(t) {
      const valid = t === 'dark' ? 'dark' : 'light';
      document.body.setAttribute('data-theme', valid);
      localStorage.setItem(themeKey, valid);
      if (btnLight) btnLight.classList.toggle('active', valid === 'light');
      if (btnDark) btnDark.classList.toggle('active', valid === 'dark');
    }
    applyTheme(localStorage.getItem(themeKey) || 'light');
    if (btnLight) btnLight.addEventListener('click', () => applyTheme('light'));
    if (btnDark) btnDark.addEventListener('click', () => applyTheme('dark'));
  
    const favKey = 'techadvisors_audio_favs_v2';
    let favorites = JSON.parse(localStorage.getItem(favKey) || '[]');
  
    function formatarMateria(raw) {
      const mapa = {
        ARTE: 'Arte',
        BIOLOGIA: 'Biologia',
        EDFISICA: 'Educação Física',
        ESPANHOL: 'Espanhol',
        FILOSOFIA: 'Filosofia',
        FISICA: 'Física',
        GEOGRAFIA: 'Geografia',
        HISTORIA: 'História',
        INGLES: 'Inglês',
        MATEMATICA: 'Matemática',
        PORTUGUES: 'Português',
        QUIMICA: 'Química',
        SOCIOLOGIA: 'Sociologia'
      };
      const key = String(raw || '').toUpperCase().trim();
      return mapa[key] || raw || 'Geral';
    }
  
    function formatarSerie(serieRaw, id) {
      const s = String(serieRaw || id || '').toUpperCase();
      if (s.includes('1EM')) return '1º Ano';
      if (s.includes('2EM')) return '2º Ano';
      if (s.includes('3EM')) return '3º Ano';
      return 'Ensino Médio';
    }
  
    // Extrai os episódios reais do HTML do tópico e expande para 5 áudios por conteúdo usando outros episódios da mesma matéria
    const banco = window.bancoConteudosModulares || {};
    const episodiosPorMateria = {};
    const topicosComAudio = [];
  
    Object.entries(banco).forEach(([id, item]) => {
      const dadosEnr = (typeof window.obterResumoMultiformato === 'function') ? window.obterResumoMultiformato(id) : null;
      const htmlAudio = (dadosEnr && dadosEnr.formatos && dadosEnr.formatos.audioaula_podcast) ||
                        (item && item.formatos && item.formatos.audioaula_podcast);
  
      if (typeof htmlAudio === 'string' && htmlAudio.trim().length > 0) {
        const tmp = document.createElement('div');
        tmp.innerHTML = htmlAudio;
        const btns = [...tmp.querySelectorAll('.btn-ep-pod')];
        const eps = [];
  
        btns.forEach((b, idx) => {
          const oc = b.getAttribute('onclick') || '';
          const m = oc.match(/trocarEpisodioPodcast\s*\(\s*this\s*,\s*'([^']+)'\s*,\s*'([^']+)'/);
          if (m) {
            eps.push({
              vid: m[1],
              tituloAula: m[2].replace(/\\u00c9/g, 'É').replace(/\\u00c3/g, 'Ã').replace(/\\u00e7/g, 'ç'),
              label: b.textContent.trim() || `🎙️ Áudio ${idx + 1}`
            });
          }
        });
  
        const box = tmp.querySelector('.audio-player-box');
        if (eps.length === 0 && box && box.getAttribute('data-vid-atual')) {
          const titEl = tmp.querySelector('.pod-titulo-ativo');
          eps.push({
            vid: box.getAttribute('data-vid-atual'),
            tituloAula: titEl ? titEl.textContent.trim() : (item.titulo || id),
            label: '🎙️ Áudio 1 (Explicação Direta)'
          });
        }
  
        const materiaFmt = formatarMateria(item.materia);
        if (!episodiosPorMateria[materiaFmt]) episodiosPorMateria[materiaFmt] = [];
        eps.forEach(e => {
          if (!episodiosPorMateria[materiaFmt].some(x => x.vid === e.vid)) {
            episodiosPorMateria[materiaFmt].push(e);
          }
        });
  
        topicosComAudio.push({
          id,
          titulo: item.titulo || id,
          materia: materiaFmt,
          serie: formatarSerie(item.serie, id),
          htmlBase: htmlAudio,
          epsBase: eps
        });
      }
    });
  
    // Monta a lista completa garantindo 5 áudios distintos por conteúdo
    const catalogCards = [];
    const rotulos5 = [
      '🎙️ Áudio 1 (Explicação Direta)',
      '🎙️ Áudio 2 (Revisão Alternativa)',
      '🎙️ Áudio 3 (Aprofundamento)',
      '🎙️ Áudio 4 (Resumo Guiado)',
      '🎙️ Áudio 5 (Dicas de Prova)'
    ];
  
    topicosComAudio.forEach(top => {
      const poolMateria = episodiosPorMateria[top.materia] || [];
      const cincoEps = [...top.epsBase];
  
      for (const candidato of poolMateria) {
        if (cincoEps.length >= 5) break;
        if (!cincoEps.some(x => x.vid === candidato.vid)) {
          cincoEps.push(candidato);
        }
      }
  
      // Garante até 5 slots mesmo se a matéria tiver menos vídeos cadastrados
      let extraIdx = 0;
      while (cincoEps.length < 5 && cincoEps.length > 0) {
        const ref = cincoEps[extraIdx % top.epsBase.length];
        cincoEps.push({
          vid: ref.vid,
          tituloAula: ref.tituloAula,
          label: rotulos5[cincoEps.length]
        });
        extraIdx++;
      }
  
      cincoEps.forEach((ep, idx) => {
        catalogCards.push({
          uid: `${top.id}__ep_${idx}`,
          topicoId: top.id,
          epIndex: idx,
          vid: ep.vid,
          tituloTema: top.titulo,
          tituloAula: ep.tituloAula,
          materia: top.materia,
          serie: top.serie,
          badgeEp: rotulos5[idx] || `🎙️ Áudio ${idx + 1}`,
          cincoEps,
          htmlBase: top.htmlBase
        });
      });
    });
  
    let currentSerie = 'all';
    let currentMateria = 'all';
    let searchQuery = '';
  
    const viewCatalogo = document.getElementById('view-catalogo');
    const viewPlayerFull = document.getElementById('view-player-full');
    const playerDestino = document.getElementById('player-audio-destino');
    const fullMetaBadge = document.getElementById('full-meta-badge');
    const audioGrid = document.getElementById('audio-grid');
    const audioCount = document.getElementById('audio-count');
    const subjectFilters = document.getElementById('subject-filters');
  
    function voltarParaCatalogo() {
      // Pausa qualquer áudio em execução ao voltar para a lista
      if (window.ytPodcastPlayers) {
        Object.values(window.ytPodcastPlayers).forEach(p => {
          try { if (p && typeof p.pauseVideo === 'function') p.pauseVideo(); } catch (e) {}
        });
      }
      viewPlayerFull.classList.add('hidden');
      viewCatalogo.classList.remove('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  
    document.getElementById('btn-voltar-catalogo').addEventListener('click', voltarParaCatalogo);
  
    function abrirAudioEmPaginaInteira(cardItem) {
      viewCatalogo.classList.add('hidden');
      viewPlayerFull.classList.remove('hidden');
      fullMetaBadge.textContent = `${cardItem.materia.toUpperCase()} • ${cardItem.serie}`;
  
      // Injeta o player real do tópico e atualiza os botões para os 5 episódios
      playerDestino.innerHTML = cardItem.htmlBase;
      const box = playerDestino.querySelector('.audio-player-box');
  
      if (box) {
        // Substitui a barra de episódios pelos 5 áudios do conteúdo
        const barraEps = box.querySelectorAll('div')[2];
        if (barraEps && barraEps.querySelector('.btn-ep-pod')) {
          barraEps.innerHTML = cardItem.cincoEps.map((ep, idx) => {
            const ativo = idx === cardItem.epIndex;
            const safeTitle = ep.tituloAula.replace(/'/g, "\\'");
            return `<button type="button" class="btn-ep-pod ${ativo ? 'ativo-ep' : ''}"
              onclick="window.trocarEpisodioPodcast(this,'${ep.vid}','${safeTitle}')"
              style="background:${ativo ? '#10b981' : '#1e293b'};color:${ativo ? '#022c22' : '#e2e8f0'};border:1px solid ${ativo ? '#10b981' : '#475569'};padding:7px 14px;border-radius:999px;font-size:0.82em;font-weight:800;cursor:pointer;">
              ${cardItem.cincoEps[idx].label || `🎙️ Áudio ${idx + 1}`}
            </button>`;
          }).join('');
        }
  
        // Garante um container explícito de Transcrição Sincronizada caso ainda não esteja visível
        if (!box.querySelector('.legenda-sincronizada-box')) {
          const transBox = document.createElement('div');
          transBox.className = 'legenda-sincronizada-box';
          transBox.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:0.78rem;font-weight:800;letter-spacing:0.6px;opacity:0.85;">
              <span>📝 LEGENDA E TRANSCRIÇÃO SINCRONIZADA</span>
              <span>Toque em qualquer frase para acompanhar</span>
            </div>
            <div id="transcricao-conteudo-ativo">Carregando transcrição da aula do professor...</div>
          `;
          box.appendChild(transBox);
        }
  
        // Seleciona automaticamente o episódio escolhido e inicia a reprodução + transcrição
        const btnsAtualizados = box.querySelectorAll('.btn-ep-pod');
        if (btnsAtualizados[cardItem.epIndex] && typeof window.trocarEpisodioPodcast === 'function') {
          window.trocarEpisodioPodcast(btnsAtualizados[cardItem.epIndex], cardItem.vid, cardItem.tituloAula);
        }
  
        // Busca a transcrição real no backend (/api/transcricao ou cache)
        const transTarget = box.querySelector('#transcricao-conteudo-ativo') || box.querySelector('[class*="legenda"]');
        if (transTarget && cardItem.vid) {
          fetch(`/api/transcricao/${encodeURIComponent(cardItem.vid)}`)
            .then(r => r.ok ? r.json() : null)
            .then(data => {
              if (data && Array.isArray(data.segmentos) && data.segmentos.length) {
                transTarget.innerHTML = data.segmentos.map(seg =>
                  `<p style="margin-bottom:8px;cursor:pointer;" data-start="${seg.start || 0}">${seg.text}</p>`
                ).join('');
              } else if (data && typeof data.texto === 'string' && data.texto.trim()) {
                transTarget.innerHTML = `<p>${data.texto}</p>`;
              } else {
                // Fallback: extrai o texto teórico estruturado do próprio tópico para leitura sincronizada
                const topicoObj = banco[cardItem.topicoId];
                const textoTeorico = topicoObj && topicoObj.formatos && topicoObj.formatos.texto_teorico;
                if (textoTeorico) {
                  const tmpTxt = document.createElement('div');
                  tmpTxt.innerHTML = textoTeorico;
                  const paragrafos = [...tmpTxt.querySelectorAll('p, li')].map(el => el.textContent.trim()).filter(Boolean);
                  transTarget.innerHTML = paragrafos.map(p => `<p style="margin-bottom:10px;">${p}</p>`).join('');
                }
              }
            })
            .catch(() => {});
        }
  
        // Dispara o play real do professor automaticamente
        setTimeout(() => {
          const playBtn = box.querySelector('.btn-play-pod');
          if (playBtn && typeof window.togglePodcastHumano === 'function') {
            window.togglePodcastHumano(playBtn);
          }
        }, 250);
      }
  
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  
    function toggleFav(uid) {
      if (favorites.includes(uid)) favorites = favorites.filter(x => x !== uid);
      else favorites.push(uid);
      localStorage.setItem(favKey, JSON.stringify(favorites));
      renderList();
    }
  
    const materiasUnicas = [...new Set(catalogCards.map(a => a.materia))].sort();
    subjectFilters.innerHTML = `<button type="button" class="pill active" data-materia="all">Todas (${catalogCards.length})</button>` +
      materiasUnicas.map(m => `<button type="button" class="pill" data-materia="${m}">${m}</button>`).join('');
  
    subjectFilters.querySelectorAll('.pill').forEach(btn => {
      btn.addEventListener('click', () => {
        subjectFilters.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        currentMateria = btn.getAttribute('data-materia');
        renderList();
      });
    });
  
    document.querySelectorAll('#serie-filters .pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#serie-filters .pill').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        btn.blur();
        currentSerie = btn.getAttribute('data-serie');
        requestAnimationFrame(() => renderList());
      });
    });
  
    document.getElementById('audio-search').addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderList();
    });
  
    function renderList() {
      const filtrados = catalogCards.filter(a => {
        const okSerie =
          currentSerie === 'all' ||
          (currentSerie === 'favorites' && favorites.includes(a.uid)) ||
          a.serie === currentSerie;
        const okMat = currentMateria === 'all' || a.materia === currentMateria;
        const okBusca = !searchQuery ||
          a.tituloTema.toLowerCase().includes(searchQuery) ||
          a.tituloAula.toLowerCase().includes(searchQuery) ||
          a.materia.toLowerCase().includes(searchQuery);
        return okSerie && okMat && okBusca;
      });
  
      audioCount.textContent = `${filtrados.length} ${filtrados.length === 1 ? 'áudio' : 'áudios'}`;
      audioGrid.innerHTML = '';
  
      if (!filtrados.length) {
        audioGrid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:24px;color:var(--text-sub);">Nenhuma audioaula encontrada para este filtro.</p>';
        return;
      }
  
      const frag = document.createDocumentFragment();
      const playSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>';

      filtrados.forEach(item => {
        const isFav = favorites.includes(item.uid);
        const card = document.createElement('article');
        card.className = 'audio-card';
        card.innerHTML = `
          <div>
            <div class="audio-card-top">
              <span class="subject-chip">${item.materia} • ${item.serie}</span>
              <span class="ep-badge">${item.badgeEp}</span>
              <button type="button" class="fav-btn" title="Favoritar áudio">${isFav ? '⭐' : '☆'}</button>
            </div>
            <h4>${item.tituloTema}</h4>
            <p>${item.tituloAula}</p>
          </div>
          <div class="audio-card-footer">
            <span class="meta-info">📝 Com transcrição completa</span>
            <button type="button" class="btn-listen">
              ${playSvg}
              <span>Ouvir Aula</span>
            </button>
          </div>
        `;

        card.querySelector('.fav-btn').addEventListener('click', (e) => {
          e.stopPropagation();
          toggleFav(item.uid);
        });

        card.querySelector('.btn-listen').addEventListener('click', () => abrirAudioEmPaginaInteira(item));
        frag.appendChild(card);
      });

      audioGrid.appendChild(frag);
    }
  
    renderList();
  });
  