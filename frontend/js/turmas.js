const API_URL = 'http://127.0.0.1:8000';
let currentProfId = 1;
let currentProfName = 'Professor';

window.onload = function () {
  const user = JSON.parse(localStorage.getItem('user'));
  if (!user || user.role !== 'professor') {
    alert('Acesso restrito a professores logados.');
    window.location.href = 'index.html';
    return;
  }
  currentProfId = user.id_professor || user.id || 1;
  currentProfName = user.nome || 'Professor';
  const navSpan = document.getElementById('prof-name-nav')?.querySelector('span');
  if (navSpan) navSpan.innerText = `Olá, ${currentProfName}`;
  carregarTurmas();
};

function toggleUserMenu(e) { e.stopPropagation(); document.getElementById('userMenu')?.classList.toggle('show'); }
window.addEventListener('click', (e) => { const m = document.getElementById('userMenu'); if (m && m.classList.contains('show') && !e.target.closest('.user-menu-container')) m.classList.remove('show'); });
function minhaConta() { window.location.href = 'config.html'; }
function configuracoes() { window.location.href = 'config.html'; }
function logout() { localStorage.removeItem('user'); window.location.href = 'index.html'; }

async function carregarTurmas() {
  const tbody = document.getElementById('lista-turmas-body');
  if (!tbody) return;
  try {
    const r = await fetch(`${API_URL}/turmas?id_professor=${currentProfId}`);
    if (r.ok) {
      const turmas = await r.json();
      if (!turmas.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="p-6 text-center text-slate-500">Nenhuma turma vinculada ao seu perfil até o momento. Solicite o vínculo à coordenação/administração.</td></tr>';
        return;
      }
      tbody.innerHTML = turmas.map(t => `
        <tr class="hover:bg-slate-50/80 transition-colors">
          <td class="p-4 font-mono text-xs font-bold text-indigo-600">${t.codigo_turma}</td>
          <td class="p-4 font-semibold text-slate-800">${t.nome_turma}</td>
          <td class="p-4">${t.serie_ano}</td>
          <td class="p-4 font-medium text-slate-700">${t.disciplina}</td>
          <td class="p-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">${t.turno}</span></td>
          <td class="p-4">${t.ano_letivo}</td>
          <td class="p-4 font-mono text-xs">${t.nome_professor || '#' + t.id_professor}</td>
          <td class="p-4"><span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">${t.status_turma}</span></td>
        </tr>`).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="8" class="p-6 text-center text-red-500">Erro ao carregar lista de turmas.</td></tr>';
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="8" class="p-6 text-center text-red-500">Servidor FastAPI indisponível na porta 8000.</td></tr>';
  }
}
