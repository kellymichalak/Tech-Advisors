// ============================================================================
// [DESTAQUE] CONTROLE DE TROCA ENTRE MODO CLARO E MODO ESCURO
// Altere estas funções caso mude a lógica de tema global do projeto no futuro
// ============================================================================
const CHAVE_TEMA_STORAGE = 'techadvisors_tema_acessibilidade';

function aplicarTema(tema) {
  const htmlEl = document.documentElement;
  const btnTema = document.getElementById('btn-toggle-tema');

  if (tema === 'dark') {
    htmlEl.classList.add('dark');
    if (btnTema) {
      btnTema.setAttribute('title', 'Mudar para Modo Claro');
      btnTema.innerHTML = '<i data-lucide="sun" size="20"></i>';
    }
  } else {
    htmlEl.classList.remove('dark');
    if (btnTema) {
      btnTema.setAttribute('title', 'Mudar para Modo Escuro');
      btnTema.innerHTML = '<i data-lucide="moon" size="20"></i>';
    }
  }

  localStorage.setItem(CHAVE_TEMA_STORAGE, tema);

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function alternarModoClaroEscuro() {
  const estaEscuro = document.documentElement.classList.contains('dark');
  aplicarTema(estaEscuro ? 'light' : 'dark');
}
// ============================================================================
// FIM DO BLOCO DESTACADO DE TROCA DE TEMA
// ============================================================================

window.addEventListener('DOMContentLoaded', () => {
  // 1. Aplica o tema salvo (padrão: light)
  const temaSalvo = localStorage.getItem(CHAVE_TEMA_STORAGE) || 'light';
  aplicarTema(temaSalvo);

  // 2. Exibe o nome do aluno logado, se existir no localStorage
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    const nomeSpan = document.getElementById('aluno-nome-nav');
    if (user && user.nome && nomeSpan) {
      nomeSpan.innerText = user.nome;
    }
  } catch (_) {}

  // 3. Renderiza os ícones Lucide
  if (window.lucide) {
    window.lucide.createIcons();
  }
});
