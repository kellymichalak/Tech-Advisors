/* =========================================================
  TECH ADVISORS - CONFIGURAÇÕES E ACESSIBILIDADE
  ========================================================= */


  let currentFontScale = 1.0;
  let currentBrightness = 100;
  let currentSaturation = 100;
  let isHighContrast = false;
 
  // Executa automaticamente ao carregar qualquer página que use este JS
  document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
  });
 
  // Carrega as configurações salvas do localStorage
  function loadSettings() {
    const saved = localStorage.getItem('tech_accessibility_settings');
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        currentFontScale = settings.fontScale || 1.0;
        currentBrightness = settings.brightness || 100;
        currentSaturation = settings.saturation || 100;
        isHighContrast = settings.highContrast || false;
      } catch (e) {
        console.error('Erro ao ler configurações:', e);
      }
    }
    applyAllSettings();
    syncUI();
  }
 
  // Aplica as variáveis CSS no HTML
  function applyAllSettings() {
    document.documentElement.style.setProperty('--font-scale-factor', currentFontScale);
    document.documentElement.style.setProperty('--page-brightness', currentBrightness + '%');
    document.documentElement.style.setProperty('--page-saturation', currentSaturation + '%');
 
    if (isHighContrast) {
      document.body.classList.add('high-contrast');
    } else {
      document.body.classList.remove('high-contrast');
    }
  }
 
  // Atualiza o valor dos sliders e toggles na tela de configurações (se existirem)
  function syncUI() {
    const fontLabel = document.getElementById('font-size-label');
    if (fontLabel) fontLabel.innerText = Math.round(currentFontScale * 100) + '%';
 
    const bLabel = document.getElementById('brightness-label');
    if (bLabel) bLabel.innerText = currentBrightness + '%';
 
    const bRange = document.getElementById('brightness-range');
    if (bRange) bRange.value = currentBrightness;
 
    const sLabel = document.getElementById('saturation-label');
    if (sLabel) sLabel.innerText = currentSaturation + '%';
 
    const sRange = document.getElementById('saturation-range');
    if (sRange) sRange.value = currentSaturation;
 
    const contrastCheck = document.getElementById('toggle-contrast');
    if (contrastCheck) contrastCheck.checked = isHighContrast;
  }
 
  // Salva o estado atual no localStorage
  function saveSettings() {
    const settings = {
      fontScale: currentFontScale,
      brightness: currentBrightness,
      saturation: currentSaturation,
      highContrast: isHighContrast
    };
    localStorage.setItem('tech_accessibility_settings', JSON.stringify(settings));
  }
 
  // --- FUNÇÕES DOS CONTROLES ---
 
  function changeFontSize(delta) {
    currentFontScale = parseFloat((Math.min(Math.max(currentFontScale + delta, 0.8), 2.0)).toFixed(1));
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  function resetFontSize() {
    currentFontScale = 1.0;
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  function updateBrightness(val) {
    currentBrightness = val;
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  function updateSaturation(val) {
    currentSaturation = val;
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  function toggleHighContrast(enabled) {
    isHighContrast = Boolean(enabled);
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  function resetAllSettings() {
    currentFontScale = 1.0;
    currentBrightness = 100;
    currentSaturation = 100;
    isHighContrast = false;
    applyAllSettings();
    syncUI();
    saveSettings();
  }
 
  // --- NAVEGAÇÃO E DRAWER ---
 
  function navigateTo(screenName) {
    if (screenName === 'home') {
      const user = JSON.parse(localStorage.getItem('user'));
      if (user && user.role === 'aluno') {
        window.location.href = 'alunos.html';
        return;
      } else {
        window.location.href = '../index.html';
        return;
      }
    }
 
    if (screenName === 'login') {
      window.location.href = '../index.html';
      return;
    }
 
    document.getElementById('screen-home').classList.remove('active');
    document.getElementById('screen-login').classList.remove('active');
    document.getElementById('screen-register').classList.remove('active');
   
    const screenTurmas = document.getElementById('screen-turmas');
    if (screenTurmas) screenTurmas.classList.remove('active');
 
    if (screenName === 'register') {
      document.getElementById('screen-register').classList.add('active');
    } else if (screenName === 'turmas' && screenTurmas) {
      screenTurmas.classList.add('active');
    }
 
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
 
  function toggleModalTurma(show) {
    const modal = document.getElementById('modal-turma');
    if (modal) {
      if (show) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      } else {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
      }
    }
  }
  function toggleSettingsDrawer(open) {
   const drawer = document.getElementById('settings-drawer');
   const overlay = document.getElementById('settings-overlay');
    if (!drawer || !overlay) return;
    if (open) {
     overlay.classList.remove('hidden');
     drawer.classList.remove('hidden');
     // Adiciona suporte às duas abordagens (Tailwind e CSS puro)
     overlay.classList.add('open');
     drawer.classList.add('open');
   } else {
     overlay.classList.add('hidden');
     drawer.classList.add('hidden');
     overlay.classList.remove('open');
     drawer.classList.remove('open');
   }
 }

