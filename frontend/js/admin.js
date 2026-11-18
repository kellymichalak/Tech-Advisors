(function () {
  function aplicarTemaSalvo() {
    const tema = localStorage.getItem('techadvisors_assistiva_theme');
    if (tema === 'dark') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    aplicarTemaSalvo();
    try {
      const user = JSON.parse(localStorage.getItem('user') || 'null');
      const navSpan = document.getElementById('admin-name-text') || document.querySelector('#admin-name-nav span');
      if (navSpan) {
        const primeiroNome = (user && user.nome) ? user.nome.split(' ')[0] : 'Administrador';
        navSpan.textContent = `Olá, ${primeiroNome}`;
      }
    } catch (e) {}
  });

  window.addEventListener('storage', (e) => {
    if (e.key === 'techadvisors_assistiva_theme') aplicarTemaSalvo();
  });
})();

function toggleUserMenu(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById('userMenu');
  if (menu) menu.classList.toggle('show');
}

window.addEventListener('click', (e) => {
  const menu = document.getElementById('userMenu');
  if (menu && menu.classList.contains('show') && !e.target.closest('.user-menu-container')) {
    menu.classList.remove('show');
  }
});

function minhaConta() { window.location.href = 'config.html'; }
function configuracoes() { if (typeof toggleSettingsDrawer === 'function') toggleSettingsDrawer(true); else window.location.href = 'config.html'; }
function logout() { localStorage.removeItem('user'); window.location.href = 'index.html'; }
