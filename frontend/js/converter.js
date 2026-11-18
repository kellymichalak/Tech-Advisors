const fs = require('fs');
const path = require('path');
const os = require('os');

// Pasta onde estão seus arquivos .md (padrão: Downloads do seu usuário)
// Se salvou em outra pasta (ex: Documents ou Desktop), basta trocar 'Downloads' abaixo
const PASTA_BUSCA = path.join(os.homedir(), 'Downloads');

// Pasta onde os arquivos leves serão criados automaticamente
const PASTA_SAIDA = path.join(__dirname, 'js', 'conteudos');

// Caminho do seu arquivo resumos.js atual
const CAMINHO_RESUMOS_JS = path.join(__dirname, 'js', 'resumos.js');

if (!fs.existsSync(PASTA_SAIDA)) {
  fs.mkdirSync(PASTA_SAIDA, { recursive: true });
}

if (!fs.existsSync(CAMINHO_RESUMOS_JS)) {
  console.error('❌ Erro: Não encontrei o arquivo js/resumos.js. Verifique se o converter.js está na pasta raiz do projeto.');
  process.exit(1);
}

// Lê a lista oficial de tópicos do seu resumos.js
const resumosCode = fs.readFileSync(CAMINHO_RESUMOS_JS, 'utf8');
const matchLista = resumosCode.match(/window\.listaConteudosGlobal\s*=\s*(\[[\s\S]*?\]);/);

if (!matchLista) {
  console.error('❌ Erro: Não consegui ler window.listaConteudosGlobal dentro de js/resumos.js.');
  process.exit(1);
}

const listaTopicos = eval(matchLista[1]);

const ORDEM_FORMATOS = [
  "texto_teorico", "resumo_narrativo", "topicos_bullet", "glossario_conteudo", "texto_lacunas",
  "mapa_mental", "infografico_ilustrado", "fluxograma_decisao", "linha_tempo", "tabela_comparativa",
  "audioaula_podcast", "video_whiteboard", "storytelling_caso",
  "simulador_virtual", "flashcards_memorizacao", "quiz_justificado", "roteiro_projeto"
];

function normalizar(str) {
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]/g, "");
}

function mdParaHtml(md) {
  let html = md
    .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>').replace(/<\/ul>\s*<ul>/g, '');
  
  return html.split('\n\n').map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<table') || p.startsWith('<div')) return p;
    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
  }).join('\n');
}

// Varre a pasta e subpastas buscando todos os arquivos .md
function listarTodosMd(dir, lista = []) {
  if (!fs.existsSync(dir)) return lista;
  const itens = fs.readdirSync(dir, { withFileTypes: true });
  for (const item of itens) {
    const caminhoCompleto = path.join(dir, item.name);
    try {
      if (item.isDirectory()) {
        listarTodosMd(caminhoCompleto, lista);
      } else if (item.name.toLowerCase().endsWith('.md')) {
        lista.push(caminhoCompleto);
      }
    } catch (e) {
      // Ignora pastas sem permissão de leitura
    }
  }
  return lista;
}

console.log(`🔍 Buscando arquivos .md das suas matérias em: ${PASTA_BUSCA}...`);

const agrupadoPorArquivo = {};
const topicosJaProcessados = new Set();
const todosMd = listarTodosMd(PASTA_BUSCA);

todosMd.forEach(caminhoArquivo => {
  const conteudo = fs.readFileSync(caminhoArquivo, 'utf8');

  // Ignora qualquer .md do computador que não tenha os formatos (### 1. e ### 2.)
  if (!/###\s*1[\.\)\-\s]+/.test(conteudo) || !/###\s*2[\.\)\-\s]+/.test(conteudo)) {
    return;
  }

  // Divide os capítulos dentro do arquivo
  const blocosTopicos = conteudo.split(/\n(?=#{1,2}\s+(?:Tópico|Capítulo|\d+\.))/i);

  blocosTopicos.forEach(bloco => {
    const linhas = bloco.trim().split('\n');
    const tituloBruto = linhas[0].replace(/^#+\s*(?:Tópico\s*\d+[:.-]?\s*)?/i, '').trim();
    if (!tituloBruto) return;

    const alvoNorm = normalizar(tituloBruto);
    const topicoMatch = listaTopicos.find(t => 
      normalizar(t.nome).includes(alvoNorm) || alvoNorm.includes(normalizar(t.nome))
    );

    // Ignora se não pertencer às 13 disciplinas ou se já tiver sido importado de outro arquivo repetido
    if (!topicoMatch || topicosJaProcessados.has(topicoMatch.id)) return;

    const formatosObj = {};
    const partesFormatos = bloco.split(/\n###\s*(\d+)[\.\)\-\s]+/);
    
    for (let i = 1; i < partesFormatos.length; i += 2) {
      const num = parseInt(partesFormatos[i], 10);
      const textoFormato = partesFormatos[i + 1] || '';
      const corpo = textoFormato.split('\n').slice(1).join('\n').trim();
      const fmtId = ORDEM_FORMATOS[num - 1];
      if (fmtId && corpo) {
        formatosObj[fmtId] = mdParaHtml(corpo);
      }
    }

    if (Object.keys(formatosObj).length > 0) {
      topicosJaProcessados.add(topicoMatch.id);
      const chaveArquivo = `${topicoMatch.serie}_${topicoMatch.materiaId}`;
      if (!agrupadoPorArquivo[chaveArquivo]) agrupadoPorArquivo[chaveArquivo] = {};

      agrupadoPorArquivo[chaveArquivo][topicoMatch.id] = {
        titulo: topicoMatch.nome,
        materia: topicoMatch.materiaId.toUpperCase(),
        serie: topicoMatch.serie.toUpperCase(),
        formatos: formatosObj
      };
    }
  });
});

const chavesGeradas = Object.keys(agrupadoPorArquivo);

if (chavesGeradas.length === 0) {
  console.log('\n⚠️ Nenhum conteúdo foi extraído.');
  console.log('Verifique se os arquivos .md estão realmente na pasta Downloads ou cole as primeiras 15 linhas de um .md no chat para ajustarmos o padrão.');
} else {
  chavesGeradas.forEach(chave => {
    const conteudoJs = `window.bancoConteudosModulares = Object.assign(window.bancoConteudosModulares || {}, ${JSON.stringify(agrupadoPorArquivo[chave], null, 2)});\n`;
    fs.writeFileSync(path.join(PASTA_SAIDA, `${chave}.js`), conteudoJs, 'utf8');
    console.log(`✔ Criado: js/conteudos/${chave}.js`);
  });
  console.log(`\n✅ Concluído! ${topicosJaProcessados.size} tópicos de ${listaTopicos.length} foram importados sem repetição.`);
}