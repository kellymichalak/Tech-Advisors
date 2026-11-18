window.onload = function () {
  // Busca as informações do usuário salvo no localStorage
  const user = JSON.parse(localStorage.getItem('user'));

  // 1. Trava de segurança: se não estiver logado ou não for professor, redireciona para o index.html
  if (!user || user.role !== 'professor') {
    alert('Acesso restrito a professores logados.');
    window.location.href = 'index.html';
    return;
  }

  // 2. Preenche o título de boas-vindas do painel
  const welcomeTitle = document.getElementById('prof-welcome-title');
  if (welcomeTitle) {
    welcomeTitle.innerText = `Bem-vindo(a), ${user.nome || 'Professor'}!`;
  }

  // 3. Preenche o nome do professor no menu superior (Navbar)
  const nameNav = document.getElementById('prof-name-nav');
  if (nameNav && nameNav.querySelector('span')) {
    nameNav.querySelector('span').innerText = `👨‍🏫 ${user.nome || 'Professor'}`;
  }
};

// 4. Função para abrir/fechar o menu dropdown do usuário
function toggleUserMenu(event) {
  event.stopPropagation();
  const menu = document.getElementById('userMenu');
  if (menu) {
    menu.classList.toggle('show');
  }
}

// 5. Fecha o menu dropdown ao clicar em qualquer área fora dele
window.addEventListener('click', function (e) {
  const menu = document.getElementById('userMenu');
  const navBtn = document.getElementById('prof-name-nav');
  if (menu && menu.classList.contains('show')) {
    if (!menu.contains(e.target) && navBtn && !navBtn.contains(e.target)) {
      menu.classList.remove('show');
    }
  }
});

// 6. Ação do menu: Minha Conta
function minhaConta() {
  const menu = document.getElementById('userMenu');
  if (menu) menu.classList.remove('show');
  
  // Abre a seção de configurações/perfil
  configuracoes();
}

// 7. Ação do menu: Configurações (Alternância de telas internas do Dashboard)
function configuracoes() {
  // Oculta o menu dropdown
  const menu = document.getElementById('userMenu');
  if (menu) menu.classList.remove('show');

  // Elementos do DOM
  const secaoDashboard = document.getElementById('secao-dashboard');
  const secaoConfig = document.getElementById('secao-configuracoes');

  // Oculta o painel principal e exibe as configurações
  if (secaoDashboard) {
    secaoDashboard.classList.add('hidden');
    secaoDashboard.classList.remove('active');
  }

  if (secaoConfig) {
    secaoConfig.classList.remove('hidden');
    secaoConfig.classList.add('active');
  } else {
    console.warn('Atenção: Elemento "secao-configuracoes" não foi encontrado no HTML.');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 8. Função para voltar ao Dashboard a partir de telas internas (ex: botão Voltar nas Configurações)
function voltarAoDashboard() {
  const secaoDashboard = document.getElementById('secao-dashboard');
  const secaoConfig = document.getElementById('secao-configuracoes');

  if (secaoConfig) {
    secaoConfig.classList.add('hidden');
    secaoConfig.classList.remove('active');
  }

  if (secaoDashboard) {
    secaoDashboard.classList.remove('hidden');
    secaoDashboard.classList.add('active');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function configuracoes() {
  window.location.href = 'config.html';
}

// 9. Encerra a sessão do usuário
function logout() {
  localStorage.removeItem('user');
  window.location.href = 'index.html';
}
