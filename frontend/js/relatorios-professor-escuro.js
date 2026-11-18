const API_URL = 'http://127.0.0.1:8000';
let turmasConsolidadas = [];
let dadosDisciplinas = [];
let ultimaListaFiltrada = [];
const dadosMensaisBase = [
  { mes: 'Fev', valor: 93 }, { mes: 'Mar', valor: 91 }, { mes: 'Abr', valor: 89 },
  { mes: 'Mai', valor: 92 }, { mes: 'Jun', valor: 84 }, { mes: 'Ago', valor: 94 }
];
const turmasFallback = [
  {
    id: 'T1', serie: '1º Ano', letra: 'A', nome: '1º Ano EM - Turma A', turno: 'Matutino',
    alunos: 32, frequencia: 93.8, atividades: 89, notaGeral: 7.9, alunosApoio: 2,
    materias: [{ nome: 'Matemática', prof: 'Docente Titular', atividades: 92, nota: 8.1, duvidasIA: 48 }]
  }
];
function obterUsuarioLogado() { try { return JSON.parse(localStorage.getItem('user')) || null; } catch (e) { return null; } }
function toggleUserMenu(e) { if (e) e.stopPropagation(); const m = document.getElementById('userMenu'); if (m) m.classList.toggle('hidden'); }
document.addEventListener('click', (e) => { const m = document.getElementById('userMenu'); if (m && !m.classList.contains('hidden') && !e.target.closest('.user-menu-container')) m.classList.add('hidden'); });
function minhaConta() { window.location.href = 'config.html'; }
function logout() { localStorage.removeItem('user'); window.location.href = 'index.html'; }
function showToast(msg) {
  const t = document.getElementById('toast-notification'), l = document.getElementById('toast-message');
  if (!t || !l) return;
  l.innerText = msg; t.classList.remove('translate-x-full', 'opacity-0'); t.classList.add('translate-x-0', 'opacity-100');
  setTimeout(() => { t.classList.remove('translate-x-0', 'opacity-100'); t.classList.add('translate-x-full', 'opacity-0'); }, 3000);
}
function extrairSerieBase(s) { const t = String(s || ''); if (t.includes('1')) return '1º Ano'; if (t.includes('2')) return '2º Ano'; if (t.includes('3')) return '3º Ano'; return t || '1º Ano'; }
function extrairLetraTurma(s, n) { const m1 = String(s || '').match(/\(([A-Za-z0-9]+)\)/); if (m1) return m1[1]; const m2 = String(n || '').match(/Turma\s+([A-Za-z0-9]+)/i); return m2 ? m2[1] : 'A'; }

async function carregarDadosDoBackend() {
  const user = obterUsuarioLogado();
  if (!user || user.role !== 'professor') { alert('Acesso restrito a professores logados.'); window.location.href = 'index.html'; return; }
  const idProf = user.id_professor || user.id;
  const nomeProf = user.nome || 'Professor';
  const navSpan = document.querySelector('#prof-name-nav span'); if (navSpan) navSpan.innerText = `Olá, ${nomeProf}`;
  const titleEl = document.getElementById('prof-relatorio-title'); if (titleEl) titleEl.innerText = `Relatórios & Notas • ${nomeProf}`;
  const badgeFonte = document.getElementById('badge-fonte-dados');

  try {
    const [resTurmas, resAlunos, resAtividades, resRespostas] = await Promise.all([
      fetch(`${API_URL}/turmas?id_professor=${idProf}`), fetch(`${API_URL}/alunos`),
      fetch(`${API_URL}/atividades`), fetch(`${API_URL}/respostas`)
    ]);
    if (!resTurmas.ok) throw new Error('Erro API');
    const turmasApi = await resTurmas.json();
    const alunosApi = resAlunos.ok ? await resAlunos.json() : [];
    const atividadesApi = resAtividades.ok ? await resAtividades.json() : [];
    const respostasApi = resRespostas.ok ? await resRespostas.json() : [];

    if (!Array.isArray(turmasApi) || turmasApi.length === 0) {
      turmasConsolidadas = []; dadosDisciplinas = [];
      if (badgeFonte) badgeFonte.innerText = 'Banco conectado • 0 turmas cadastradas';
      atualizarIndicadores(); return;
    }

    const mapaGrupos = new Map();
    turmasApi.forEach((t, idx) => {
      const alunosDaTurma = alunosApi.filter(a => Number(a.id_turma) === Number(t.id_turma));
      const idsAlunos = new Set(alunosDaTurma.map(a => Number(a.id_aluno)));
      const respostasTurma = respostasApi.filter(r => idsAlunos.has(Number(r.id_aluno)));
      const notasValidas = respostasTurma.map(r => parseFloat(r.nota ?? r.pontuacao ?? r.valor_nota)).filter(n => !isNaN(n));
      const mediaNota = notasValidas.length ? +(notasValidas.reduce((a, b) => a + b, 0) / notasValidas.length).toFixed(1) : 7.8;
      const totalAtiv = Math.max(1, atividadesApi.length);
      const taxaAtiv = (alunosDaTurma.length && respostasTurma.length) ? Math.min(100, Math.round((respostasTurma.length / (alunosDaTurma.length * totalAtiv)) * 100)) : 88;
      const freqEst = alunosDaTurma.length ? Math.min(100, +(86 + taxaAtiv * 0.1).toFixed(1)) : 90.0;
      const emApoio = alunosDaTurma.filter(a => {
        const ra = respostasTurma.filter(r => Number(r.id_aluno) === Number(a.id_aluno));
        if (!ra.length) return false;
        return (ra.reduce((acc, r) => acc + (parseFloat(r.nota ?? r.pontuacao ?? 7) || 7), 0) / ra.length) < 6.0;
      }).length;

      const chave = `${t.nome_turma}__${t.turno}`;
      if (!mapaGrupos.has(chave)) {
        mapaGrupos.set(chave, {
          id: `T-${t.id_turma || idx}`, serie: extrairSerieBase(t.serie_ano), letra: extrairLetraTurma(t.serie_ano, t.nome_turma),
          nome: t.nome_turma, turno: t.turno || 'Matutino', alunos: alunosDaTurma.length,
          frequencia: freqEst, atividades: taxaAtiv, notaGeral: mediaNota, alunosApoio: emApoio, materias: []
        });
      }
      mapaGrupos.get(chave).materias.push({ nome: t.disciplina || 'Geral', prof: t.nome_professor || nomeProf, atividades: taxaAtiv, nota: mediaNota, duvidasIA: respostasTurma.length });
    });

    turmasConsolidadas = Array.from(mapaGrupos.values());
    const mapaDisc = new Map();
    turmasConsolidadas.forEach(t => t.materias.forEach(m => {
      if (!mapaDisc.has(m.nome)) mapaDisc.set(m.nome, { nome: m.nome, soma: 0, qtd: 0 });
      const it = mapaDisc.get(m.nome); it.soma += m.atividades; it.qtd += 1;
    }));
    dadosDisciplinas = Array.from(mapaDisc.values()).map(d => ({ nome: d.nome, percentual: Math.round(d.soma / d.qtd) }));
    if (badgeFonte) badgeFonte.innerText = `Conectado ao Banco (${turmasApi.length} turma(s))`;
  } catch (err) {
    turmasConsolidadas = turmasFallback;
    dadosDisciplinas = [{ nome: 'Matemática', percentual: 91 }];
    if (badgeFonte) badgeFonte.innerText = 'Modo Demonstração (API offline)';
  }
  atualizarIndicadores();
}

function atualizarIndicadores() {
  const periodo = document.getElementById('filtroPeriodo').value;
  const serie = document.getElementById('filtroSerie').value;
  const turno = document.getElementById('filtroTurno').value;
  let fator = periodo === 'bimestre1' ? 1.5 : (periodo === 'bimestre2' ? -1.2 : 0);

  const filtrados = turmasConsolidadas.filter(t => (serie === 'todas' || t.serie === serie) && (turno === 'todos' || t.turno === turno));
  ultimaListaFiltrada = filtrados;

  const totalAlunos = filtrados.reduce((acc, t) => acc + t.alunos, 0);
  const mediaFreq = filtrados.length ? (filtrados.reduce((acc, t) => acc + t.frequencia, 0) / filtrados.length + fator).toFixed(1) : '0.0';
  const mediaNota = filtrados.length ? (filtrados.reduce((acc, t) => acc + t.notaGeral, 0) / filtrados.length).toFixed(1) : '0.0';
  const totalApoio = filtrados.reduce((acc, t) => acc + t.alunosApoio, 0);

  document.getElementById('kpi-alunos').innerText = totalAlunos;
  document.getElementById('kpi-turmas-sub').innerText = `Distribuídos em ${filtrados.length} turma(s)`;
  document.getElementById('kpi-frequencia').innerText = `${String(mediaFreq).replace('.', ',')}%`;
  document.getElementById('kpi-nota').innerText = String(mediaNota).replace('.', ',');
  document.getElementById('kpi-alertas').innerText = totalApoio;

  const gf = document.getElementById('grafico-frequencia'); gf.innerHTML = '';
  dadosMensaisBase.forEach(item => {
    const val = Math.min(100, Math.max(60, Math.round(item.valor + fator)));
    const cor = val < 80 ? 'bg-rose-500' : (val < 90 ? 'bg-purple-500' : 'bg-emerald-500');
    gf.innerHTML += `<div class="flex flex-col items-center justify-end h-full gap-1.5"><span class="text-xs font-bold text-white">${val}%</span><div class="w-full max-w-[44px] ${cor} rounded-t-lg" style="height:${val}%;"></div><span class="text-xs font-semibold text-purple-300 mt-1">${item.mes}</span></div>`;
  });

  const ld = document.getElementById('lista-disciplinas-indicadores'); ld.innerHTML = '';
  if (!dadosDisciplinas.length) {
    ld.innerHTML = '<p class="text-xs text-purple-300/70">Cadastre uma turma em "Minhas Turmas" para ver os indicadores.</p>';
  } else {
    dadosDisciplinas.forEach(d => {
      const pct = Math.min(100, Math.max(50, Math.round(d.percentual + fator)));
      ld.innerHTML += `<div><div class="flex justify-between text-xs font-semibold mb-1"><span class="text-purple-100">${d.nome}</span><span class="text-purple-300 font-bold">${pct}%</span></div><div class="w-full h-2.5 progress-bg"><div class="bg-purple-500 h-full rounded-full" style="width:${pct}%"></div></div></div>`;
    });
  }

  const tbody = document.getElementById('tabelaRelatoriosBody'); tbody.innerHTML = '';
  if (!filtrados.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-8 text-purple-300/80">Nenhuma turma encontrada. <a href="turmas.html" class="text-yellow-300 underline font-semibold ml-1">Ir para Minhas Turmas</a></td></tr>';
    return;
  }
  filtrados.forEach(t => {
    const freq = Math.min(100, Math.max(50, +(t.frequencia + fator).toFixed(1)));
    const badge = freq < 80 ? '<span class="bg-rose-900/60 text-rose-300 text-xs px-2.5 py-1 rounded-full font-semibold">Precisa de Apoio</span>' : (freq < 90 ? '<span class="bg-amber-900/60 text-amber-300 text-xs px-2.5 py-1 rounded-full font-semibold">Acompanhar</span>' : '<span class="bg-emerald-900/60 text-emerald-300 text-xs px-2.5 py-1 rounded-full font-semibold">Ótimo Ritmo</span>');
    const barra = freq < 80 ? 'bg-rose-500' : (freq < 90 ? 'bg-amber-500' : 'bg-emerald-500');
    tbody.innerHTML += `<tr>
      <td><div class="font-bold text-white">${t.nome}</div><div class="text-xs text-purple-300/80">${t.materias.map(m => m.nome).join(', ')}</div></td>
      <td><span class="bg-blue-900/60 text-blue-300 text-xs px-2 py-1 rounded">${t.turno}</span></td>
      <td class="font-semibold">${t.alunos} aluno(s)</td>
      <td><span class="bg-purple-950/80 text-purple-200 border border-purple-700/50 text-xs px-2.5 py-1 rounded-md font-semibold">${t.materias.length} disciplina(s)</span></td>
      <td><div class="flex items-center gap-2"><div class="w-16 h-2 progress-bg"><div class="${barra} h-full rounded-full" style="width:${freq}%"></div></div><span class="text-xs font-bold text-white">${String(freq).replace('.', ',')}%</span></div></td>
      <td class="font-semibold text-purple-100">${t.atividades}%</td>
      <td class="font-bold text-white">${String(t.notaGeral).replace('.', ',')}</td>
      <td>${badge}</td>
      <td class="text-center"><button onclick="abrirModalDetalhes('${t.id}')" class="text-xs bg-purple-900/60 hover:bg-purple-700 text-purple-200 border border-purple-500/30 font-semibold px-3 py-1.5 rounded-lg cursor-pointer">Notas & Detalhes</button></td>
    </tr>`;
  });
}

function filtrarTabelaRelatorio() {
  const termo = document.getElementById('buscaTabelaRelatorio').value.toLowerCase();
  document.querySelectorAll('#tabelaRelatoriosBody tr').forEach(tr => { tr.style.display = tr.innerText.toLowerCase().includes(termo) ? '' : 'none'; });
}
function abrirModalDetalhes(id) {
  const t = turmasConsolidadas.find(x => x.id === id); if (!t) return;
  document.getElementById('detalheTituloTurma').innerText = t.nome;
  document.getElementById('detalheSubtituloTurma').innerText = `Turno: ${t.turno} • ${t.alunos} aluno(s) • ${t.materias.length} disciplina(s)`;
  document.getElementById('detalheResumoTopo').innerHTML = `
    <div class="bg-purple-950/60 border border-purple-800/60 rounded-xl p-3 text-center"><span class="text-[11px] text-purple-300/80 block">Frequência</span><strong class="text-base text-purple-300">${String(t.frequencia).replace('.', ',')}%</strong></div>
    <div class="bg-emerald-950/50 border border-emerald-700/40 rounded-xl p-3 text-center"><span class="text-[11px] text-emerald-300/80 block">Atividades</span><strong class="text-base text-emerald-400">${t.atividades}%</strong></div>
    <div class="bg-sky-950/50 border border-sky-700/40 rounded-xl p-3 text-center"><span class="text-[11px] text-sky-300/80 block">Média</span><strong class="text-base text-sky-400">${String(t.notaGeral).replace('.', ',')}</strong></div>`;
  const tb = document.getElementById('detalheTabelaMaterias'); tb.innerHTML = '';
  t.materias.forEach(m => { tb.innerHTML += `<tr><td class="font-bold text-white">${m.nome}</td><td class="text-xs text-purple-200/80">${m.prof}</td><td class="font-semibold">${m.atividades}%</td><td class="font-bold text-purple-300">${String(m.nota).replace('.', ',')}</td><td class="text-xs text-purple-300/70">${m.duvidasIA} registro(s)</td></tr>`; });
  document.getElementById('detalheAlertaApoio').innerHTML = `<span>Alunos recomendados para reforço/monitoria:</span><strong class="text-sm">${t.alunosApoio} aluno(s)</strong>`;
  document.getElementById('modalDetalhesRelatorioOverlay').classList.remove('hidden');
}
function fecharModalDetalhes() { document.getElementById('modalDetalhesRelatorioOverlay').classList.add('hidden'); }
function exportarRelatorioCSV() {
  const linhas = [['Turma', 'Turno', 'Alunos', 'Disciplinas', 'Frequencia', 'Atividades', 'Media']];
  ultimaListaFiltrada.forEach(t => linhas.push([`"${t.nome}"`, t.turno, t.alunos, `"${t.materias.map(m => m.nome).join(', ')}"`, t.frequencia, t.atividades, t.notaGeral]));
  const a = document.createElement('a'); a.href = encodeURI('data:text/csv;charset=utf-8,' + linhas.map(e => e.join(';')).join('
'));
  a.download = 'relatorio_notas_professor_2026.csv'; document.body.appendChild(a); a.click(); document.body.removeChild(a);
  showToast('Planilha CSV exportada com sucesso!');
}
window.addEventListener('DOMContentLoaded', carregarDadosDoBackend);
