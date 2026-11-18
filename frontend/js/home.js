const API_URL = 'http://127.0.0.1:8000';
let selectedRole = 'aluno';


// Função para alternar visibilidade da senha (Olho Aberto / Olho Fechado)
function togglePasswordVisibility(inputId, eyeIconId) {
 const input = document.getElementById(inputId);
 const eyeIcon = document.getElementById(eyeIconId);
 if (!input || !eyeIcon) return;


 if (input.type === 'password') {
   input.type = 'text';
   // SVG Olho Aberto
   eyeIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />`;
 } else {
   input.type = 'password';
   // SVG Olho Fechado
   eyeIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M3 3l18 18"></path>`;
 }
}


// Navegação entre as telas internas do index.html (Home, Login e Cadastro) e externas (Sobre, Professor)
function navigateTo(screenName) {
 // REDIRECIONAMENTO PARA A PÁGINA SOBRE.HTML
 if (screenName === 'sobre') {
   window.location.href = 'sobre.html';
   // Se o seu arquivo sobre.html estiver dentro da pasta "pages", troque a linha acima por:
   // window.location.href = 'pages/sobre.html';
   return;
 }


 if (screenName === 'dashboard-professor' || screenName === 'professor') {
   window.location.href = 'professor.html';
   return;
 }


 if (screenName === 'register' || screenName === 'register-step1') {
   startRegistration();
   return;
 }


 // Oculta todas as telas internas do index.html
 const screenHome = document.getElementById('screen-home');
 const screenLogin = document.getElementById('screen-login');
 const screenReg1 = document.getElementById('screen-register-step1');
 const screenReg2 = document.getElementById('screen-register-step2');


 if (screenHome) screenHome.classList.remove('active');
 if (screenLogin) screenLogin.classList.remove('active');
 if (screenReg1) screenReg1.classList.remove('active');
 if (screenReg2) screenReg2.classList.remove('active');


 // Exibe a tela interna correspondente
 if (screenName === 'home' && screenHome) {
   screenHome.classList.add('active');
 } else if (screenName === 'login' && screenLogin) {
   screenLogin.classList.add('active');
 }


 window.scrollTo({ top: 0, behavior: 'smooth' });
}


// Inicia o fluxo de cadastro na Etapa 1
function startRegistration() {
 const screenHome = document.getElementById('screen-home');
 const screenLogin = document.getElementById('screen-login');
 const screenReg1 = document.getElementById('screen-register-step1');
 const screenReg2 = document.getElementById('screen-register-step2');


 if (screenHome) screenHome.classList.remove('active');
 if (screenLogin) screenLogin.classList.remove('active');
 if (screenReg2) screenReg2.classList.remove('active');
 if (screenReg1) screenReg1.classList.add('active');


 window.scrollTo({ top: 0, behavior: 'smooth' });
}


// Seleção de perfil no Cadastro (Aluno, Professor, Admin)
function selectRole(role) {
 selectedRole = role.toLowerCase();


 const cardAluno = document.getElementById('card-aluno');
 const cardProfessor = document.getElementById('card-professor');
 const cardAdmin = document.getElementById('card-admin');


 if (cardAluno) cardAluno.classList.remove('selected');
 if (cardProfessor) cardProfessor.classList.remove('selected');
 if (cardAdmin) cardAdmin.classList.remove('selected');


 const targetCard = document.getElementById(`card-${role}`);
 if (targetCard) targetCard.classList.add('selected');
}


// Avança para a Etapa 2 do cadastro adaptando os campos
function goToStep2() {
 const screenReg1 = document.getElementById('screen-register-step1');
 const screenReg2 = document.getElementById('screen-register-step2');


 if (screenReg1) screenReg1.classList.remove('active');
 if (screenReg2) screenReg2.classList.add('active');


 const iconEl = document.getElementById('header-role-icon');
 const titleEl = document.getElementById('header-role-title');
 const fieldsAluno = document.getElementById('fields-aluno');
 const fieldsProfessor = document.getElementById('fields-professor');
 const fieldsAdmin = document.getElementById('fields-admin');


 if (fieldsAluno) fieldsAluno.classList.add('hidden');
 if (fieldsProfessor) fieldsProfessor.classList.add('hidden');
 if (fieldsAdmin) fieldsAdmin.classList.add('hidden');


 if (selectedRole === 'aluno') {
   if (iconEl) iconEl.innerText = '🎓';
   if (titleEl) titleEl.innerText = 'CADASTRO DE ALUNO';
   if (fieldsAluno) fieldsAluno.classList.remove('hidden');
 } else if (selectedRole === 'professor') {
   if (iconEl) iconEl.innerText = '👨‍🏫';
   if (titleEl) titleEl.innerText = 'CADASTRO DE PROFESSOR';
   if (fieldsProfessor) fieldsProfessor.classList.remove('hidden');
 } else if (selectedRole === 'admin') {
   if (iconEl) iconEl.innerText = '⚙️';
   if (titleEl) titleEl.innerText = 'CADASTRO DE ADMIN';
   if (fieldsAdmin) fieldsAdmin.classList.remove('hidden');
 }


 window.scrollTo({ top: 0, behavior: 'smooth' });
}


// Volta para a seleção de perfil no cadastro
function goToStep1() {
 const screenReg1 = document.getElementById('screen-register-step1');
 const screenReg2 = document.getElementById('screen-register-step2');


 if (screenReg2) screenReg2.classList.remove('active');
 if (screenReg1) screenReg1.classList.add('active');


 window.scrollTo({ top: 0, behavior: 'smooth' });
}


// Envio do formulário de cadastro para a API FastAPI
async function handleFinalRegister(event) {
 event.preventDefault();
 const name = document.getElementById('reg-name')?.value;
 const email = document.getElementById('reg-email')?.value;
 const password = document.getElementById('reg-password')?.value;


 const discInput = document.getElementById('prof-disciplina');
 const disciplinaVal = discInput ? discInput.value.trim() : '';


 const serieSelect = document.getElementById('aluno-serie');
 const serieVal = serieSelect ? serieSelect.value : '';


 let endpoint = '/auth/register';
 let payload = { nome: name, email: email, senha: password };


 if (selectedRole === 'professor') {
   endpoint = '/auth/register';
   payload = {
     nome: name,
     email: email,
     senha: password,
     role: selectedRole, disciplinas: disciplinaVal,
     status: 'ativo'
   };
 } else if (selectedRole === 'aluno') {
   endpoint = '/auth/register';
   payload = {
     nome: name,
     email: email,
     senha: password,
     role: selectedRole, serie: serieVal
   };
 }


 try {
   const response = await fetch(`${API_URL}${endpoint}`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json'
     },
     body: JSON.stringify(payload)
   });


   if (response.ok) {
     const usuarioCriado = await response.json();
     const roleNormalizada = selectedRole.toLowerCase();


     localStorage.setItem('user', JSON.stringify({
       id: usuarioCriado.id_professor || usuarioCriado.id_responsavel,
       nome: name,
       email: email,
       disciplinas: usuarioCriado.disciplinas || disciplinaVal,
       serie: serieVal,
       role: roleNormalizada
     }));


     redirectUser(roleNormalizada);
   } else {
     const erro = await response.json();
     let msg = 'Verifique os dados informados.';
     if (typeof erro.detail === 'string') msg = erro.detail;
     else if (Array.isArray(erro.detail)) msg = erro.detail.map(e => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join('\n');


     alert(`Erro ao realizar cadastro:\n${msg}`);
   }
 } catch (error) {
   console.error('Erro na conexão com o servidor:', error);
   alert('Não foi possível conectar ao servidor FastAPI na porta 8000.');
 }
}


// Autenticação de Login na API FastAPI
async function handleLogin(event) {
 event.preventDefault();
 const emailInput = document.getElementById('login-email')?.value;
 const passwordInput = document.getElementById('login-password')?.value;


 try {
   const response = await fetch(`${API_URL}/login`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       email: emailInput,
       senha: passwordInput
     })
   });


   if (response.ok) {
     const usuarioBD = await response.json();


     let roleNormalizada = (usuarioBD.role || 'aluno').toLowerCase();
     if (roleNormalizada === 'responsavel') {
       roleNormalizada = 'aluno';
     }


     const usuarioParaSalvar = {
       ...usuarioBD,
       role: roleNormalizada
     };


     localStorage.setItem('user', JSON.stringify(usuarioParaSalvar));
     redirectUser(roleNormalizada);
   } else {
     const erro = await response.json();
     alert(`Falha no login: ${erro.detail || 'E-mail ou senha incorretos.'}`);
   }
 } catch (error) {
   console.error('Erro ao efetuar login:', error);
   alert('Erro ao conectar com o servidor FastAPI.');
 }
}


// Redireciona o usuário para a página correspondente ao seu papel
function redirectUser(role) {
 const userRole = role ? role.toLowerCase() : 'aluno';


 if (userRole === 'admin') {
   window.location.href = 'admin.html';
 } else if (userRole === 'professor') {
   window.location.href = 'professor.html';
 } else if (userRole === 'aluno' || userRole === 'responsavel') {
   window.location.href = 'alunos.html';
 } else {
   window.location.href = 'admin.html';
 }
}


// Verifica a sessão para navegação direta ao Dashboard
function handleDashboardNavigation() {
 const savedUser = JSON.parse(localStorage.getItem('user'));
 if (!savedUser) {
   navigateTo('login');
 } else {
   redirectUser(savedUser.role);
 }
}


// Encerra a sessão
function logout() {
 localStorage.removeItem('user');
 window.location.href = 'index.html';
}






// Resetar campos ao trocar de perfil e alternar blocos corretamente com emojis intactos
const _origSelectRole = typeof selectRole === 'function' ? selectRole : null;
window.selectRole = function(role) {
  if (_origSelectRole) _origSelectRole(role);
  selectedRole = role;
  document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById('card-' + role);
  if (card) card.classList.add('selected');

  const form = document.getElementById('form-professor');
  if (form) form.reset();
  document.querySelectorAll('input[name="disciplinas"]').forEach(cb => { cb.checked = false; });
  if (typeof atualizarTagsDisciplinas === 'function') atualizarTagsDisciplinas();
  const listaDisc = document.getElementById('dropdown-disciplinas-lista');
  if (listaDisc) listaDisc.classList.add('hidden');
};

const _origGoToStep2 = typeof goToStep2 === 'function' ? goToStep2 : null;
window.goToStep2 = function() {
  if (_origGoToStep2) _origGoToStep2();

  const fAluno = document.getElementById('fields-aluno');
  const fProf = document.getElementById('fields-professor');
  const fAdmin = document.getElementById('fields-admin');
  const iconEl = document.getElementById('header-role-icon');
  const titleEl = document.getElementById('header-role-title');

  if (fAluno) { fAluno.classList.add('hidden'); fAluno.style.display = 'none'; }
  if (fProf)  { fProf.classList.add('hidden');  fProf.style.display = 'none'; }
  if (fAdmin) { fAdmin.classList.add('hidden'); fAdmin.style.display = 'none'; }

  if (selectedRole === 'aluno') {
    if (fAluno) { fAluno.classList.remove('hidden'); fAluno.style.display = 'block'; }
    if (iconEl) iconEl.textContent = '\u{1F393}';
    if (titleEl) titleEl.textContent = 'CADASTRO DE ALUNO';
  } else if (selectedRole === 'professor') {
    if (fProf) { fProf.classList.remove('hidden'); fProf.style.display = 'block'; }
    if (iconEl) iconEl.textContent = '\u{1F468}\u200D\u{1F3EB}';
    if (titleEl) titleEl.textContent = 'CADASTRO DE PROFESSOR';
  } else if (selectedRole === 'admin') {
    if (fAdmin) { fAdmin.classList.remove('hidden'); fAdmin.style.display = 'block'; }
    if (iconEl) iconEl.textContent = '\u2699\uFE0F';
    if (titleEl) titleEl.textContent = 'CADASTRO DE ADMINISTRADOR';
  }
};


// ==================== GOOGLE SIGN-IN (3 PASSOS) ====================
let googleContaSelecionada = null;
let googleVeioDeLista = false;

const contasGooglePadrao = [
  { nome: 'Ana Clara Souza', email: 'ana.aluna@escola.edu.br', role: 'aluno', avatar: 'A' },
  { nome: 'Prof. Carlos Mendes', email: 'carlos.prof@escola.edu.br', role: 'professor', avatar: 'C' },
  { nome: 'Coordenação TechAdvisors', email: 'admin@techadvisors.edu.br', role: 'admin', avatar: 'T' }
];

function renderizarContasGoogle() {
  const lista = document.getElementById('google-lista-contas');
  if (!lista) return;

  const contasHtml = contasGooglePadrao.map((c, idx) => `
    <button type="button" onclick="selecionarContaGoogle(${idx})"
      class="w-full px-7 py-3.5 flex items-center gap-3.5 hover:bg-slate-50 transition-colors text-left">
      <div class="w-9 h-9 rounded-full bg-[#5b21b6] text-white font-bold text-sm flex items-center justify-center shrink-0">
        ${c.avatar}
      </div>
      <div class="min-w-0 flex-1">
        <div class="text-sm font-medium text-slate-800 truncate">${c.nome}</div>
        <div class="text-xs text-slate-500 truncate">${c.email}</div>
      </div>
    </button>
  `).join('');

  const outraContaHtml = `
    <button type="button" onclick="usarOutraContaGoogle()"
      class="w-full px-7 py-3.5 flex items-center gap-3.5 hover:bg-slate-50 transition-colors text-left">
      <div class="w-9 h-9 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center shrink-0">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <div class="text-sm font-medium text-slate-700">Usar outra conta</div>
    </button>
  `;

  lista.innerHTML = contasHtml + outraContaHtml;
}

function mostrarPassoGoogle(passo) {
  ['google-passo-1', 'google-passo-2', 'google-passo-3'].forEach((id, i) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('hidden', (i + 1) !== passo);
  });
}

function abrirModalGoogle() {
  const modal = document.getElementById('modal-google-auth');
  if (!modal) return;
  renderizarContasGoogle();
  mostrarPassoGoogle(1);
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function fecharModalGoogle() {
  const modal = document.getElementById('modal-google-auth');
  if (!modal) return;
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

function selecionarContaGoogle(idx) {
  const conta = contasGooglePadrao[idx];
  if (!conta) return;
  googleContaSelecionada = conta;
  googleVeioDeLista = true;
  const saudacao = document.getElementById('google-saudacao');
  const pill = document.getElementById('google-email-pill');
  const senhaInput = document.getElementById('google-senha-input');
  if (saudacao) saudacao.textContent = `Olá, ${conta.nome.split(' ')[0]}!`;
  if (pill) pill.textContent = conta.email;
  if (senhaInput) senhaInput.value = '';
  limparErroInputGoogle('senha');
  mostrarPassoGoogle(3);
}

function usarOutraContaGoogle() {
  googleVeioDeLista = false;
  const emailInput = document.getElementById('google-email-input');
  if (emailInput) emailInput.value = '';
  limparErroInputGoogle('email');
  mostrarPassoGoogle(2);
}

function voltarPasso1Google() {
  mostrarPassoGoogle(1);
}

function voltarParaEmailOuContas() {
  mostrarPassoGoogle(googleVeioDeLista ? 1 : 2);
}

function limparErroInputGoogle(tipo) {
  const erroEl = document.getElementById(`google-${tipo}-erro`);
  if (erroEl) erroEl.classList.add('hidden');
}

function avancarEmailGoogle(event) {
  event.preventDefault();
  const emailInput = document.getElementById('google-email-input');
  const email = emailInput?.value?.trim() || '';
  if (!email || !email.includes('@')) {
    const erroEl = document.getElementById('google-email-erro');
    if (erroEl) erroEl.classList.remove('hidden');
    return;
  }
  const nomeBase = email.split('@')[0].replace(/[._-]/g, ' ');
  const nomeFormatado = nomeBase.replace(/\w/g, l => l.toUpperCase());
  const roleInferida = email.includes('admin') ? 'admin' : (email.includes('prof') ? 'professor' : 'aluno');
  googleContaSelecionada = { nome: nomeFormatado, email, role: roleInferida };

  const saudacao = document.getElementById('google-saudacao');
  const pill = document.getElementById('google-email-pill');
  const senhaInput = document.getElementById('google-senha-input');
  if (saudacao) saudacao.textContent = `Olá, ${nomeFormatado.split(' ')[0]}!`;
  if (pill) pill.textContent = email;
  if (senhaInput) senhaInput.value = '';
  limparErroInputGoogle('senha');
  mostrarPassoGoogle(3);
}

function confirmarSenhaGoogle(event) {
  event.preventDefault();
  const senha = document.getElementById('google-senha-input')?.value || '';
  if (senha.length < 4) {
    const erroEl = document.getElementById('google-senha-erro');
    const txtEl = document.getElementById('google-senha-erro-texto');
    if (txtEl) txtEl.textContent = 'Digite sua senha do Google (mínimo 4 caracteres).';
    if (erroEl) erroEl.classList.remove('hidden');
    return;
  }
  const usuario = {
    nome: googleContaSelecionada?.nome || 'Usuário Google',
    email: googleContaSelecionada?.email || 'usuario@gmail.com',
    role: googleContaSelecionada?.role || 'aluno'
  };
  localStorage.setItem('user', JSON.stringify(usuario));
  fecharModalGoogle();
  redirectUser(usuario.role);
}

// ==================== REDEFINIR SENHA ====================
function abrirModalResetSenha() {
  const modal = document.getElementById('modal-reset-senha');
  if (!modal) return;
  const loginEmail = document.getElementById('login-email')?.value?.trim();
  const resetEmail = document.getElementById('reset-email');
  if (loginEmail && resetEmail && !resetEmail.value) {
    resetEmail.value = loginEmail;
  }
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

function fecharModalResetSenha() {
  const modal = document.getElementById('modal-reset-senha');
  if (!modal) return;
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

async function redefinirSenhaDireta(event) {
  event.preventDefault();
  const email = document.getElementById('reset-email')?.value?.trim();
  const nova_senha = document.getElementById('reset-nova-senha')?.value;
  const confirma = document.getElementById('reset-confirma-senha')?.value;

  if (nova_senha !== confirma) {
    alert('As senhas digitadas não coincidem.');
    return;
  }

  try {
    let resp = await fetch(`${API_URL}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, nova_senha })
    });
    if (resp.status === 404) {
      resp = await fetch(`${API_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, nova_senha })
      });
    }
    const data = await resp.json();
    if (resp.ok) {
      alert(data.message || 'Senha atualizada com sucesso!');
      const loginEmail = document.getElementById('login-email');
      if (loginEmail) loginEmail.value = email;
      fecharModalResetSenha();
    } else {
      alert(data.detail || 'E-mail não encontrado ou erro ao atualizar senha.');
    }
  } catch (err) {
    console.error(err);
    alert('Erro ao conectar com o servidor FastAPI na porta 8000.');
  }
}

// ==================== MULTI-DISCIPLINAS PROFESSOR ====================
function toggleDropdownDisciplinas() {
  const lista = document.getElementById('dropdown-disciplinas-lista');
  if (lista) lista.classList.toggle('hidden');
}

function atualizarTagsDisciplinas() {
  const selecionadas = Array.from(document.querySelectorAll('input[name="disciplinas"]:checked')).map(cb => cb.value);
  const hiddenInput = document.getElementById('prof-disciplina');
  if (hiddenInput) hiddenInput.value = selecionadas.join(', ');

  const display = document.getElementById('disciplinas-tags-display');
  if (!display) return;

  if (selecionadas.length === 0) {
    display.innerHTML = '<span class="text-sm text-slate-400">Selecione uma ou mais disciplinas</span>';
    return;
  }

  display.innerHTML = selecionadas.map(disc => `
    <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-100 text-[#5b21b6]">
      ${disc}
    </span>
  `).join('');
}

document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('multi-disciplina-wrapper');
  const lista = document.getElementById('dropdown-disciplinas-lista');
  if (wrapper && lista && !wrapper.contains(e.target)) {
    lista.classList.add('hidden');
  }
});
