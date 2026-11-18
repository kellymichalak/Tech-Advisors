window.onload = function() {
   // Busca as informações do usuário salvo no localStorage
   const user = JSON.parse(localStorage.getItem('user'));
    // 1. Trava de segurança: se não estiver logado ou não for aluno, redireciona diretamente (sem alert)
   if (!user || user.role !== 'aluno') {
     window.location.href = 'index.html';
     return;
   }
    // 2. Preenche o título de boas-vindas do banner com o nome do aluno
   const welcomeTitle = document.getElementById('student-welcome-title');
   if (welcomeTitle) {
     welcomeTitle.innerText = `Bem-vindo(a), ${user.nome || 'Aluno'}!`;
   }
    // 3. Preenche o nome do aluno no menu superior (Navbar)
   const nameNav = document.getElementById('student-name-nav');
   if (nameNav && nameNav.querySelector('span')) {
     nameNav.querySelector('span').innerText = `🎓 ${user.nome || 'Aluno'}`;
   }
 };
  // 4. Função para abrir/fechar o menu dropdown
 function toggleUserMenu(event) {
   event.stopPropagation();
   const menu = document.getElementById('userMenu');
   if (menu) {
     menu.classList.toggle('show');
   }
 }
  // 5. Fecha o menu dropdown ao clicar em qualquer área fora dele
 window.addEventListener('click', function(e) {
   const menu = document.getElementById('userMenu');
   const navBtn = document.getElementById('student-name-nav');
    if (menu && menu.classList.contains('show')) {
     if (!menu.contains(e.target) && navBtn && !navBtn.contains(e.target)) {
       menu.classList.remove('show');
     }
   }
 });
  // 6. Ações das opções do menu (sem alerts)
 function minhaConta() {
   // Adicione a navegação ou lógica desejada para o perfil
 }
  function configuracoes() {
   // Adicione a navegação ou lógica desejada para as configurações
 }
  // 7. Função de logout: limpa a sessão e retorna ao login
 function logout() {
   localStorage.removeItem('user');
   window.location.href = 'index.html';
 }



