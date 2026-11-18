(function () {
  const STORAGE_PREFS_KEY = 'techadvisors_assistiva_prefs';
  const STORAGE_THEME_KEY = 'techadvisors_assistiva_theme';

  // Injeta @font-face OpenDyslexic e estilos assistivos globais
  if (!document.getElementById('techadvisors-assistiva-styles')) {
    const style = document.createElement('style');
    style.id = 'techadvisors-assistiva-styles';
    style.textContent = `
      @font-face {
        font-family: 'OpenDyslexic';
        src: url('https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/OpenDyslexic-Regular.otf') format('opentype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
      }
      @font-face {
        font-family: 'OpenDyslexic';
        src: url('https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/OpenDyslexic-Bold.otf') format('opentype');
        font-weight: 700;
        font-style: normal;
        font-display: swap;
      }

      body.dyslexic-mode,
      body.dyslexic-mode * {
        font-family: 'OpenDyslexic', 'Comic Sans MS', Verdana, sans-serif !important;
        letter-spacing: 0.06em !important;
        word-spacing: 0.16em !important;
      }
      body.dyslexic-mode p,
      body.dyslexic-mode li,
      body.dyslexic-mode span,
      body.dyslexic-mode a,
      body.dyslexic-mode label {
        line-height: 1.85 !important;
      }

      body.easy-reading-mode {
        letter-spacing: 0.04em !important;
        word-spacing: 0.14em !important;
      }
      body.easy-reading-mode p,
      body.easy-reading-mode li {
        font-size: 1.08rem !important;
        line-height: 1.9 !important;
        max-width: 72ch;
      }

      #global-irlen-overlay {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 9998;
        transition: background-color 0.25s ease;
      }

      #assistiva-magnifier {
        position: fixed;
        width: 240px;
        height: 110px;
        border-radius: 14px;
        border: 2px solid #7c3aed;
        background: rgba(255, 255, 255, 0.96);
        color: #1e1b4b;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
        padding: 12px 14px;
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.4;
        pointer-events: none;
        z-index: 10000;
        display: none;
        overflow: hidden;
      }
      body[data-theme="dark"] #assistiva-magnifier {
        background: rgba(23, 20, 45, 0.97);
        color: #ffffff;
        border-color: #a855f7;
      }

      .pictogram-term {
        border-bottom: 2px dashed #7c3aed;
        cursor: help;
        position: relative;
        padding: 0 2px;
        border-radius: 4px;
        background: rgba(124, 58, 237, 0.08);
      }

      #pictogram-tooltip {
        position: fixed;
        z-index: 10001;
        background: #1e1b4b;
        color: #ffffff;
        border: 1px solid #8b5cf6;
        border-radius: 12px;
        padding: 10px 14px;
        max-width: 270px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
        font-size: 0.85rem;
        display: none;
        pointer-events: none;
      }
    `;
    document.head.appendChild(style);
  }

  const irlenColors = {
    none: 'transparent',
    blue: 'rgba(147, 197, 253, 0.22)',
    yellow: 'rgba(253, 224, 71, 0.22)',
    green: 'rgba(134, 239, 172, 0.22)',
    pink: 'rgba(249, 168, 212, 0.22)'
  };

  window.applyGlobalAssistivaPrefs = function () {
    const prefs = JSON.parse(localStorage.getItem(STORAGE_PREFS_KEY) || '{}');
    const theme = localStorage.getItem(STORAGE_THEME_KEY);

    if (theme && !document.body.getAttribute('data-theme')) {
      document.body.setAttribute('data-theme', theme);
    }

    document.body.classList.toggle('dyslexic-mode', !!prefs.dyslexic);
    document.body.classList.toggle('easy-reading-mode', !!prefs.easyReading);
    document.documentElement.style.fontSize = prefs.zoom125 ? '118%' : '100%';

    let overlay = document.getElementById('irlen-overlay') || document.getElementById('global-irlen-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'global-irlen-overlay';
      document.body.appendChild(overlay);
    }
    overlay.style.backgroundColor = irlenColors[prefs.irlen] || 'transparent';
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.applyGlobalAssistivaPrefs);
  } else {
    window.applyGlobalAssistivaPrefs();
  }
})();
