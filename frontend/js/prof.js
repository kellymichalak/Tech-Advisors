window.onload = function () {
  const user = JSON.parse(localStorage.getItem('user'));

  if (!user || user.role !== 'professor') {
    alert('Acesso restrito a professores logados.');
    window.location.href = 'index.html';
    return;
  }

  const welcomeTitle = document.getElementById('prof-welcome-title');
  if (welcomeTitle) {
    welcomeTitle.innerText = `Bem-vindo(a), ${user.nome || 'Professor'}!`;
  }

  const nameNav = document.getElementById('prof-name-nav');
  if (nameNav && nameNav.querySelector('span')) {
    nameNav.querySelector('span').innerText = `Olá, ${user.nome || 'Professor'}`;
  }
};

function toggleUserMenu(event) {
  event.stopPropagation();
  const menu = document.getElementById('userMenu');
  if (menu) menu.classList.toggle('show');
}

window.addEventListener('click', function (e) {
  const menu = document.getElementById('userMenu');
  const navBtn = document.getElementById('prof-name-nav');
  if (menu && menu.classList.contains('show')) {
    if (!menu.contains(e.target) && navBtn && !navBtn.contains(e.target)) {
      menu.classList.remove('show');
    }
  }
});

function minhaConta() {
  window.location.href = 'config.html';
}

function configuracoes() {
  window.location.href = 'config.html';
}

function logout() {
  localStorage.removeItem('user');
  window.location.href = 'index.html';
}
