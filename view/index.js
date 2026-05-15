// =====================================================
// CONSTROESTOQUE — index.js
// Integração completa com a API Flask + JWT
// =====================================================


// ══════════════════════════════════════════════════
// CONFIGURAÇÃO DA API + TOKEN JWT
// ══════════════════════════════════════════════════

const API_BASE_URL = 'http://localhost:5000';

function getToken() {
  return sessionStorage.getItem('token');
}

function verificarAutenticacao() {
  if (!getToken()) {
    window.location.href = '/';
  }
}

async function apiFetch(endpoint, method = 'GET', body = null) {
  const token = getToken();
  if (!token) { window.location.href = '/'; return; }

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE_URL}${endpoint}`, options);

  if (res.status === 401) {
    sessionStorage.clear();
    window.location.href = '/';
    return;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ msg: 'Erro desconhecido' }));
    throw new Error(err.msg || err.message || `HTTP ${res.status}`);
  }
  return res.json();
}


// ══════════════════════════════════════════════════
// INICIALIZAÇÃO
// ══════════════════════════════════════════════════

let fpInicio, fpFim;

document.addEventListener('DOMContentLoaded', () => {
  verificarAutenticacao();
  carregarAdministrador();
  carregarTodos();

  const fpOpts = { dateFormat: 'd/m/Y', locale: 'pt', allowInput: true };
  fpInicio = flatpickr('#obraDataInicio', fpOpts);
  fpFim    = flatpickr('#obraDataFim',    fpOpts);

  const fpFiltroOpts = { ...fpOpts, onChange: filtrarObras };
  flatpickr('#obraFiltroDe',  fpFiltroOpts);
  flatpickr('#obraFiltroAte', fpFiltroOpts);
});

async function carregarTodos() {
  await Promise.allSettled([
    carregarProdutos(),
    carregarObras(),
    carregarClientes(),
    carregarAdmins(),
    carregarResponsaveis(),
  ]);
  renderGraficoObras();
}

function carregarAdministrador() {
  const nome = sessionStorage.getItem('nomeLogin') || 'Administrador';
  const avatarEl = document.getElementById('userAvatar');
  const nameEl   = document.getElementById('userName');
  if (nameEl)   nameEl.textContent   = nome;
  if (avatarEl) avatarEl.textContent = nome.charAt(0).toUpperCase();
}


// ══════════════════════════════════════════════════
// PRODUTOS  →  GET/POST/PUT/DELETE /produto
// ══════════════════════════════════════════════════

let cacheProdutos = [];

async function carregarProdutos() {
  try {
    const res = await apiFetch('/produto');
    cacheProdutos = res.produtos || [];
    renderTabelaProdutos(cacheProdutos);
    renderAlertas(cacheProdutos);
    renderNotificacoes(cacheProdutos);
    atualizarKPI();
  } catch (e) {
    document.getElementById('bodyProdutos').innerHTML =
      `<tr><td colspan="6" class="empty-row">Erro ao carregar produtos: ${e.message}</td></tr>`;
    console.error('carregarProdutos:', e);
  }
}

function renderTabelaProdutos(produtos) {
  const q        = filtros.produtos;
  const filtrado = q ? produtos.filter(p =>
    `${p.idProduto} ${p.nomeProduto} ${p.descProduto || ''}`.toLowerCase().includes(q)
  ) : produtos;

  const total = filtrado.length;
  const totalPags = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.produtos > totalPags) PAG_STATE.produtos = 1;
  const inicio = (PAG_STATE.produtos - 1) * PER_PAGE;
  const pagina = filtrado.slice(inicio, inicio + PER_PAGE);

  const tbody = document.getElementById('bodyProdutos');
  if (!pagina.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">${total === 0 && q ? 'Nenhum resultado para a busca.' : 'Nenhum produto cadastrado.'}</td></tr>`;
  } else {
    tbody.innerHTML = pagina.map(p => {
      const { cls, label } = statusEstoque(p);
      return `
        <tr>
          <td>${p.idProduto}</td>
          <td>${p.nomeProduto}</td>
          <td>${p.descProduto || '—'}</td>
          <td><span class="qty-badge ${cls}">${p.qtdProduto}</span></td>
          <td>${label}</td>
          <td class="actions">
            <button class="btn-icon" title="Editar" onclick="abrirModalEditarProduto(${p.idProduto})">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button class="btn-icon danger" title="Excluir" onclick="deletarItem('produto', ${p.idProduto}, '${p.nomeProduto}')">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>`;
    }).join('');
  }
  renderPaginacao('paginacaoProdutos', total, PAG_STATE.produtos, 'mudarPaginaProdutos');
}

function abrirModalNovoProduto() {
  ['prodIdEdicao','prodNome','prodQtd','prodQtdMin','prodQtdMax','prodDesc']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('modalProdutoTitle').innerHTML =
    '<i class="fa-solid fa-boxes-stacked"></i> Novo Produto';
  abrirModal('modalProduto');
}

function abrirModalEditarProduto(idProduto) {
  const p = cacheProdutos.find(x => x.idProduto == idProduto);
  if (!p) { showToast('Produto não encontrado.', 'error'); return; }
  document.getElementById('prodIdEdicao').value = p.idProduto;
  document.getElementById('prodNome').value     = p.nomeProduto;
  document.getElementById('prodQtd').value      = p.qtdProduto;
  document.getElementById('prodQtdMin').value   = p.qtdMinima ?? '';
  document.getElementById('prodQtdMax').value   = p.qtdMaxima ?? '';
  document.getElementById('prodDesc').value     = p.descProduto || '';
  document.getElementById('modalProdutoTitle').innerHTML =
    '<i class="fa-solid fa-pen"></i> Editar Produto';
  abrirModal('modalProduto');
}

async function salvarProduto() {
  const idEdicao = document.getElementById('prodIdEdicao').value;
  const nome   = document.getElementById('prodNome').value.trim();
  const qtd    = document.getElementById('prodQtd').value.trim();
  const qtdMin = document.getElementById('prodQtdMin').value.trim();
  const qtdMax = document.getElementById('prodQtdMax').value.trim();
  const desc   = document.getElementById('prodDesc').value.trim();

  if (!nome || qtd === '') { showToast('Nome e quantidade são obrigatórios.', 'error'); return; }
  if (nome.length < 3)    { showToast('Nome deve ter ao menos 3 caracteres.', 'error'); return; }
  if (parseInt(qtd) < 0) { showToast('Quantidade não pode ser negativa.', 'error'); return; }
  if (qtdMax !== '' && qtd !== '' && parseInt(qtd) > parseInt(qtdMax)) {
    showToast('Quantidade atual não pode superar a máxima.', 'error'); return;
  }
  if (qtdMin !== '' && qtdMax !== '' && parseInt(qtdMin) > parseInt(qtdMax)) {
    showToast('Quantidade mínima não pode ser maior que a máxima.', 'error'); return;
  }

  const payload = {
    produto: {
      nomeProduto: nome,
      qtdProduto:  parseInt(qtd),
      qtdMinima:   qtdMin !== '' ? parseInt(qtdMin) : 0,
      qtdMaxima:   qtdMax !== '' ? parseInt(qtdMax) : 9999,
      descProduto: desc,
    }
  };

  try {
    let res;
    if (idEdicao) {
      res = await apiFetch(`/produto/${idEdicao}`, 'PUT', payload);
    } else {
      res = await apiFetch('/produto', 'POST', payload);
    }
    fecharModal('modalProduto');
    await carregarProdutos();
    if (res?.aviso) showToast(res.aviso, 'warning');
    else showToast(idEdicao ? 'Produto atualizado!' : `Produto "${nome}" cadastrado!`, 'success');
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// OBRAS  →  GET/POST/PATCH/DELETE /obra
// ══════════════════════════════════════════════════

let cacheObras = [];

async function carregarObras() {
  try {
    const res = await apiFetch('/obra');
    cacheObras = res.obras || [];
    renderTabelaObras(cacheObras);
    renderObrasRecentes(cacheObras);
    atualizarKPI();
  } catch (e) {
    document.getElementById('bodyObras').innerHTML =
      `<tr><td colspan="6" class="empty-row">Erro ao carregar obras: ${e.message}</td></tr>`;
    console.error('carregarObras:', e);
  }
}

function renderTabelaObras(obras) {
  let filtrado = obras;
  const tipo   = filtros.obraTipo;
  const s      = filtros.obraStatus;
  const de     = filtros.obraDe;
  const ate    = filtros.obraAte;

  if (tipo) filtrado = filtrado.filter(o =>
    `${o.tipoObra || ''} ${o.descObra || ''}`.toLowerCase().includes(tipo)
  );
  if (s)   filtrado = filtrado.filter(o => o.statusObra === s);
  if (de)  filtrado = filtrado.filter(o => o.dataInicio && o.dataInicio >= de);
  if (ate) filtrado = filtrado.filter(o => o.dataInicio && o.dataInicio <= ate);

  const total     = filtrado.length;
  const totalPags = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.obras > totalPags) PAG_STATE.obras = 1;
  const inicio = (PAG_STATE.obras - 1) * PER_PAGE;
  const pagina = filtrado.slice(inicio, inicio + PER_PAGE);

  const fmtData = d => { if (!d) return '—'; const [y,m,dia] = d.split('-'); return `${dia}/${m}/${y}`; };
  const tbody   = document.getElementById('bodyObras');
  const temFiltro = tipo || s || de || ate;

  if (!pagina.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">${temFiltro ? 'Nenhum resultado para a busca.' : 'Nenhuma obra cadastrada.'}</td></tr>`;
  } else {
    tbody.innerHTML = pagina.map(o => {
      const badge       = badgeStatus(o.statusObra);
      const cliente     = cacheClientes.find(c => c.idCliente === o.codCliente);
      const nomeCliente = cliente ? cliente.nomeCliente : (o.codCliente ? `Cliente #${o.codCliente}` : '—');
      const contatoParts = [o.emailContato, o.celular1, o.celular2].filter(Boolean);
      const contatoStr   = contatoParts.length ? contatoParts.join(' | ') : '';
      const descEsc = (o.descObra || '').replace(/'/g, "\\'");
      return `
        <tr>
          <td>${o.idObra}</td>
          <td>${o.codCliente || '—'}</td>
          <td>
            <div class="obra-cell">
              <span class="obra-cell-nome">${nomeCliente}</span>
              ${o.descObra    ? `<span class="obra-cell-desc">${o.descObra}</span>`       : ''}
              ${contatoStr    ? `<span class="obra-cell-contato">${contatoStr}</span>`    : ''}
              ${o.obsObra     ? `<span class="obra-cell-obs">${o.obsObra}</span>`         : ''}
            </div>
          </td>
          <td>${fmtData(o.dataInicio)}</td>
          <td>${badge}</td>
          <td class="actions">
            <button class="btn-icon" title="Ver produtos" onclick="verProdutosObra(${o.idObra})">
              <i class="fa-solid fa-eye"></i>
            </button>
            <button class="btn-icon" title="Editar" onclick="abrirModalEditarObra(${o.idObra})">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button class="btn-icon danger" title="Excluir" onclick="deletarItem('obra', ${o.idObra}, '${descEsc}')">
              <i class="fa-solid fa-trash"></i>
            </button>
          </td>
        </tr>`;
    }).join('');
  }
  renderPaginacao('paginacaoObras', total, PAG_STATE.obras, 'mudarPaginaObras');
}

function _novaProdutoObraRow() {
  const opts = cacheProdutos.map(p =>
    `<option value="${p.idProduto}" data-estoque="${p.qtdProduto}" data-min="${p.qtdMinima}">${p.nomeProduto} (estoque: ${p.qtdProduto})</option>`
  ).join('');
  return `
    <div class="produto-obra-row">
      <select class="prod-select" onchange="selecionarProdutoObraRow(this)">
        <option value="">Selecione um produto...</option>
        ${opts}
      </select>
      <input type="text" placeholder="Estoque" class="prod-estoque-input" readonly />
      <input type="number" placeholder="Qtd." class="prod-qtd-input" min="1" />
      <button class="btn-icon danger" onclick="removerProdutoObra(this)">
        <i class="fa-solid fa-minus"></i>
      </button>
    </div>`;
}

function selecionarProdutoObraRow(sel) {
  const row      = sel.closest('.produto-obra-row');
  const estoqueEl = row.querySelector('.prod-estoque-input');
  const opt      = sel.selectedOptions[0];
  if (!sel.value) { estoqueEl.value = ''; estoqueEl.style.color = ''; return; }
  const qtd = parseInt(opt.dataset.estoque) || 0;
  const min = parseInt(opt.dataset.min)     || 0;
  estoqueEl.value = `${qtd} em estoque`;
  estoqueEl.style.color = qtd <= 0 ? '#DC2626' : (min > 0 && qtd <= min) ? '#D97706' : '#16A34A';
}

function _limparCamposObra() {
  const ids = [
    'obraIdEdicao','obraIdDisplay','obraCodCliente','obraTipo',
    'obraClienteCNPJ','obraClienteNome','obraClienteRua','obraClienteNumero',
    'obraClienteComplemento','obraClienteBairro','obraClienteCEP',
    'obraClienteCidade','obraClienteEstado',
    'obraContato','obraEmail','obraCelular1','obraCelular2',
    'obraDesc','obraObs','obraOrientacao','obraDataInicio','obraDataFim'
  ];
  ids.forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  if (fpInicio) fpInicio.clear();
  if (fpFim)    fpFim.clear();
  document.getElementById('obraStatus').value   = 'Em andamento';
  document.getElementById('obraResp').value     = '';
  document.getElementById('obraUnidade').value  = '';
}

function abrirModalNovaObra() {
  _limparCamposObra();
  const el = document.createElement('div');
  el.innerHTML = _novaProdutoObraRow();
  document.getElementById('produtosObraList').innerHTML = '';
  document.getElementById('produtosObraList').appendChild(el.firstElementChild);
  document.getElementById('obraSecaoProdutos').classList.remove('hidden');
  document.getElementById('obraSecaoProdutosVer').classList.add('hidden');
  document.getElementById('modalObraTitle').innerHTML =
    '<i class="fa-solid fa-hard-hat"></i> Nova Obra';
  abrirModal('modalObra');
}

function abrirModalEditarObra(idObra) {
  const o = cacheObras.find(x => x.idObra == idObra);
  if (!o) { showToast('Obra não encontrada.', 'error'); return; }
  _limparCamposObra();
  document.getElementById('obraIdEdicao').value          = o.idObra;
  document.getElementById('obraIdDisplay').value         = o.idObra;
  document.getElementById('obraStatus').value            = o.statusObra || 'Em andamento';
  document.getElementById('obraResp').value              = o.respObra || '';
  fpInicio.setDate(o.dataInicio || '', false);
  fpFim.setDate(o.dataFim    || '', false);
  document.getElementById('obraCodCliente').value        = o.codCliente || '';
  document.getElementById('obraTipo').value              = o.tipoObra || '';
  document.getElementById('obraUnidade').value           = o.unidadeObra || '';
  document.getElementById('obraEmail').value             = o.emailContato || '';
  document.getElementById('obraCelular1').value          = o.celular1 || '';
  document.getElementById('obraCelular2').value          = o.celular2 || '';
  document.getElementById('obraDesc').value              = o.descObra || '';
  document.getElementById('obraObs').value               = o.obsObra || '';
  document.getElementById('obraOrientacao').value        = o.orientacaoObra || '';
  buscarClienteObra(document.getElementById('obraCodCliente'));
  document.getElementById('obraSecaoProdutos').classList.add('hidden');
  document.getElementById('obraSecaoProdutosVer').classList.remove('hidden');
  document.getElementById('produtosObraEdList').innerHTML = '';

  const listEl = document.getElementById('obraProdutosVerList');
  listEl.innerHTML = '<div class="loading-row"><i class="fa-solid fa-spinner fa-spin"></i> Carregando...</div>';

  apiFetch(`/obra/${o.idObra}/produtos`).then(res => {
    const produtos = res.produtos || [];
    if (!produtos.length) {
      listEl.innerHTML = '<div style="font-size:.84rem;color:var(--gray-500);padding:6px 0">Nenhum produto vinculado.</div>';
      return;
    }
    listEl.innerHTML = produtos.map(p => `
      <div class="produto-obra-row" style="pointer-events:none">
        <input type="number" class="prod-id-input" value="${p.idProduto}" readonly />
        <input type="text" class="prod-nome-input" value="${p.nomeProduto}" readonly />
        <input type="text" class="prod-estoque-input" value="Qtd: ${p.qtdProdutosObra}" readonly />
        <input type="number" class="prod-qtd-input" value="${p.qtdProdutosObra}" readonly />
      </div>`).join('');
  }).catch(() => {
    listEl.innerHTML = '<div style="font-size:.84rem;color:#DC2626;padding:6px 0">Erro ao carregar produtos.</div>';
  });

  document.getElementById('modalObraTitle').innerHTML =
    '<i class="fa-solid fa-pen"></i> Editar Obra';
  abrirModal('modalObra');
}

function buscarClienteObra(input) {
  const id = parseInt(input.value);
  if (!id || id <= 0) return;
  const c = cacheClientes.find(x => x.idCliente === id);
  if (!c) return;
  const set = (id, val) => { const el = document.getElementById(id); if (el && !el.value) el.value = val || ''; };
  set('obraClienteNome',        c.nomeCliente);
  set('obraClienteCNPJ',        c.CNPJCPF);
  set('obraClienteRua',         c.rua);
  set('obraClienteNumero',      c.numero);
  set('obraClienteComplemento', c.complemento);
  set('obraClienteBairro',      c.bairro);
  set('obraClienteCEP',         c.cep);
  set('obraClienteCidade',      c.cidade);
  set('obraClienteEstado',      c.estado);
  set('obraEmail',              c.emailCliente);
  set('obraCelular1',           c.contatoCliente);
  set('obraCelular2',           c.telefone2);
}

function buscarProdutoObra(input) {
  const row       = input.closest('.produto-obra-row');
  const nomeEl    = row.querySelector('.prod-nome-input');
  const estoqueEl = row.querySelector('.prod-estoque-input');
  const id        = parseInt(input.value);

  if (!id || id <= 0) {
    nomeEl.value          = '';
    estoqueEl.value       = '';
    estoqueEl.style.color = '';
    return;
  }

  const p = cacheProdutos.find(x => x.idProduto === id);
  if (!p) {
    nomeEl.value          = 'Produto não encontrado';
    estoqueEl.value       = '';
    estoqueEl.style.color = '';
    return;
  }

  const cor = p.qtdProduto <= 0        ? '#DC2626'
            : (p.qtdMinima > 0 && p.qtdProduto < p.qtdMinima) ? '#D97706'
            : '#16A34A';

  nomeEl.value          = p.nomeProduto;
  estoqueEl.value       = `${p.qtdProduto} em estoque`;
  estoqueEl.style.color = cor;
}

async function salvarObra() {
  const idEdicao   = document.getElementById('obraIdEdicao').value;
  const status     = document.getElementById('obraStatus').value;
  const resp       = document.getElementById('obraResp').value;
  const dataInicio = _brParaIso(document.getElementById('obraDataInicio').value.trim());
  const dataFim    = _brParaIso(document.getElementById('obraDataFim').value.trim()) || null;
  const cod        = document.getElementById('obraCodCliente').value.trim();
  const desc       = document.getElementById('obraDesc').value.trim();
  const obs        = document.getElementById('obraObs').value.trim() || null;
  const orientacao = document.getElementById('obraOrientacao').value.trim() || null;
  const tipoObra   = document.getElementById('obraTipo').value.trim() || null;
  const unidade    = document.getElementById('obraUnidade').value || null;
  const email      = document.getElementById('obraEmail').value.trim() || null;
  const cel1       = document.getElementById('obraCelular1').value.trim() || null;
  const cel2       = document.getElementById('obraCelular2').value.trim() || null;

  if (!resp)       { showToast('Selecione o field.', 'error'); return; }
  if (!cod)        { showToast('ID do cliente é obrigatório.', 'error'); return; }
  if (!dataInicio) { showToast('Data de início é obrigatória.', 'error'); return; }
  if (!desc)       { showToast('Descrição da obra é obrigatória.', 'error'); return; }

  const clienteOk = cacheClientes.find(x => x.idCliente === parseInt(cod));
  if (!clienteOk) { showToast('Cliente não encontrado. Verifique o ID.', 'error'); return; }

  const obra = {
    descObra: desc, respObra: resp, codCliente: parseInt(cod),
    dataInicio, dataFim, statusObra: status,
    obsObra: obs, orientacaoObra: orientacao,
    tipoObra, unidadeObra: unidade,
    emailContato: email, celular1: cel1, celular2: cel2,
  };

  // Modo edição — PUT completo + produtos novos opcionais
  if (idEdicao) {
    const produtosNovos = [];
    document.querySelectorAll('#produtosObraEdList .produto-obra-row').forEach(row => {
      const pid = row.querySelector('.prod-select')?.value.trim();
      const pqt = row.querySelector('.prod-qtd-input').value.trim();
      if (pid && pqt) produtosNovos.push({ idProduto: parseInt(pid), quantidade: parseInt(pqt) });
    });

    try {
      await apiFetch(`/obra/${idEdicao}`, 'PUT', { obra, produtosNovos });
      fecharModal('modalObra');
      await Promise.all([carregarObras(), carregarProdutos()]);
      showToast('Obra atualizada!', 'success');
    } catch (e) {
      showToast(`Erro: ${e.message}`, 'error');
    }
    return;
  }

  // Modo criação — valida produtos e POST
  const produtosUsados = [];
  document.querySelectorAll('#produtosObraList .produto-obra-row').forEach(row => {
    const pid = row.querySelector('.prod-select')?.value.trim();
    const pqt = row.querySelector('.prod-qtd-input').value.trim();
    if (pid && pqt) produtosUsados.push({ idProduto: parseInt(pid), quantidade: parseInt(pqt) });
  });
  if (!produtosUsados.length) {
    showToast('Informe ao menos um produto para a obra.', 'error'); return;
  }

  try {
    await apiFetch('/obra', 'POST', { obra, produtosUsados });
    fecharModal('modalObra');
    await Promise.all([carregarObras(), carregarProdutos()]);
    showToast(`Obra "${desc}" cadastrada!`, 'success');
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}

async function verProdutosObra(idObra) {
  const body = document.getElementById('modalVerObraBody');
  body.innerHTML = '<div class="loading-row"><i class="fa-solid fa-spinner fa-spin"></i> Carregando...</div>';
  abrirModal('modalVerObra');
  try {
    const res = await apiFetch(`/obra/${idObra}/produtos`);
    const produtos = res.produtos || [];
    if (!produtos.length) {
      body.innerHTML = '<div class="empty-row">Nenhum produto vinculado a esta obra.</div>';
      return;
    }
    body.innerHTML = `
      <p style="color:var(--gray-500);font-size:.85rem;margin-bottom:14px;">
        Produtos vinculados à obra <strong>#${idObra}</strong>:
      </p>
      <table class="data-table">
        <thead><tr><th>ID</th><th>Nome</th><th>Quantidade</th><th>Ações</th></tr></thead>
        <tbody>
          ${produtos.map(p => `
            <tr>
              <td>${p.idProduto}</td>
              <td>${p.nomeProduto || '—'}</td>
              <td>${p.qtdProdutosObra}</td>
              <td class="actions">
                <button class="btn-icon" title="Editar quantidade"
                  onclick="abrirModalEditarProdObra(${idObra},${p.idProduto},'${(p.nomeProduto||'').replace(/'/g,"\\'")}',${p.qtdProdutosObra})">
                  <i class="fa-solid fa-pen"></i>
                </button>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>`;
  } catch (e) {
    body.innerHTML = `<div class="empty-row">Erro ao carregar produtos: ${e.message}</div>`;
  }
}

function adicionarProdutoObra() {
  const el = document.createElement('div');
  el.innerHTML = _novaProdutoObraRow();
  document.getElementById('produtosObraList').appendChild(el.firstElementChild);
}

function removerProdutoObra(btn) {
  const list = document.getElementById('produtosObraList');
  if (list.children.length > 1) btn.closest('.produto-obra-row').remove();
  else showToast('A obra precisa de ao menos um produto.', 'warning');
}

function adicionarProdutoObraEd() {
  const el = document.createElement('div');
  el.innerHTML = _novaProdutoObraRowEd();
  document.getElementById('produtosObraEdList').appendChild(el.firstElementChild);
}

function removerProdutoObraEd(btn) {
  btn.closest('.produto-obra-row').remove();
}

function _novaProdutoObraRowEd() {
  const opts = cacheProdutos.map(p =>
    `<option value="${p.idProduto}" data-estoque="${p.qtdProduto}" data-min="${p.qtdMinima}">${p.nomeProduto} (estoque: ${p.qtdProduto})</option>`
  ).join('');
  return `
    <div class="produto-obra-row">
      <select class="prod-select" onchange="selecionarProdutoObraRow(this)">
        <option value="">Selecione um produto...</option>
        ${opts}
      </select>
      <input type="text" placeholder="Estoque" class="prod-estoque-input" readonly />
      <input type="number" placeholder="Qtd." class="prod-qtd-input" min="1" />
      <button class="btn-icon danger" onclick="removerProdutoObraEd(this)">
        <i class="fa-solid fa-minus"></i>
      </button>
    </div>`;
}


// ══════════════════════════════════════════════════
// MÁSCARAS DE INPUT
// ══════════════════════════════════════════════════

function mascaraCpfCnpj(input) {
  let v = input.value.replace(/\D/g, '').slice(0, 14);
  if (v.length <= 11) {
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d)/, '$1.$2');
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
  } else {
    v = v.replace(/^(\d{2})(\d)/, '$1.$2');
    v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
    v = v.replace(/\.(\d{3})(\d)/, '.$1/$2');
    v = v.replace(/(\d{4})(\d{1,2})$/, '$1-$2');
  }
  input.value = v;
}

function mascaraTelefone(input) {
  let v = input.value.replace(/\D/g, '').slice(0, 11);
  v = v.replace(/^(\d{2})(\d)/, '($1) $2');
  v = v.replace(/(\d{5})(\d{1,4})$/, '$1-$2');
  input.value = v;
}

function mascaraData(input) {
  let v = input.value.replace(/\D/g, '').slice(0, 8);
  if (v.length > 4) v = v.replace(/(\d{2})(\d{2})(\d{0,4})/, '$1/$2/$3');
  else if (v.length > 2) v = v.replace(/(\d{2})(\d{0,2})/, '$1/$2');
  input.value = v;
}

function _isoParaBr(d) {
  if (!d) return '';
  const [y, m, dia] = d.split('-');
  return `${dia}/${m}/${y}`;
}

function _brParaIso(d) {
  if (!d || d.length < 10) return '';
  const [dia, m, y] = d.split('/');
  return `${y}-${m}-${dia}`;
}

function mascaraCep(input) {
  let v = input.value.replace(/\D/g, '').slice(0, 8);
  v = v.replace(/(\d{5})(\d{1,3})$/, '$1-$2');
  input.value = v;
  if (v.replace(/\D/g,'').length === 8) buscarCEP(v.replace(/\D/g,''));
}

async function buscarCEP(cep) {
  try {
    const res  = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await res.json();
    if (data.erro) { showToast('CEP não encontrado.', 'warning'); return; }
    document.getElementById('cliRua').value    = data.logradouro || '';
    document.getElementById('cliBairro').value = data.bairro     || '';
    document.getElementById('cliCidade').value = data.localidade || '';
    document.getElementById('cliEstado').value = data.uf         || '';
    document.getElementById('cliNumero').focus();
  } catch {
    showToast('Erro ao buscar CEP.', 'error');
  }
}


// ══════════════════════════════════════════════════
// CLIENTES  →  GET/POST/PUT/DELETE /cliente
// ══════════════════════════════════════════════════

let cacheClientes = [];

const PAG_STATE = { produtos: 1, obras: 1, clientes: 1 };
const PER_PAGE  = 10;
const filtros   = { produtos: '', obras: '', obraStatus: '', obraTipo: '', obraDe: '', obraAte: '', clientes: '' };

async function carregarClientes() {
  try {
    const res = await apiFetch('/cliente');
    cacheClientes = res.clientes || [];
    renderTabelaClientes(cacheClientes);
    atualizarKPI();
  } catch (e) {
    document.getElementById('bodyClientes').innerHTML =
      `<tr><td colspan="6" class="empty-row">Erro ao carregar clientes: ${e.message}</td></tr>`;
    console.error('carregarClientes:', e);
  }
}

function _enderecoCliente(c) {
  const linha1 = [c.rua, c.numero ? `nº ${c.numero}` : null].filter(Boolean).join(', ');
  const linha2 = [c.bairro, c.cidade && c.estado ? `${c.cidade}/${c.estado}` : c.cidade].filter(Boolean).join(', ');
  if (!linha1 && !linha2) return '—';
  return [linha1, linha2].filter(Boolean).join('<br>');
}

function renderTabelaClientes(clientes) {
  const q        = filtros.clientes;
  const filtrado = q ? clientes.filter(c =>
    `${c.idCliente} ${c.nomeCliente} ${c.CNPJCPF} ${c.contatoCliente || ''} ${c.emailCliente || ''} ${c.telefone2 || ''}`.toLowerCase().includes(q)
  ) : clientes;

  const total     = filtrado.length;
  const totalPags = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.clientes > totalPags) PAG_STATE.clientes = 1;
  const inicio = (PAG_STATE.clientes - 1) * PER_PAGE;
  const pagina = filtrado.slice(inicio, inicio + PER_PAGE);

  const tbody = document.getElementById('bodyClientes');
  if (!pagina.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">${total === 0 && q ? 'Nenhum resultado para a busca.' : 'Nenhum cliente cadastrado.'}</td></tr>`;
  } else {
    tbody.innerHTML = pagina.map(c => `
      <tr>
        <td>${c.idCliente}</td>
        <td>${c.nomeCliente}</td>
        <td>${c.CNPJCPF}</td>
        <td style="white-space:normal;min-width:160px">${_enderecoCliente(c)}</td>
        <td style="line-height:1.7">
          ${c.contatoCliente ? `<div><i class="fa-solid fa-phone fa-xs" style="color:var(--gray-400);width:14px"></i> ${c.contatoCliente}</div>` : ''}
          ${c.telefone2      ? `<div><i class="fa-solid fa-phone fa-xs" style="color:var(--gray-400);width:14px"></i> ${c.telefone2}</div>` : ''}
          ${c.emailCliente   ? `<div><i class="fa-regular fa-envelope fa-xs" style="color:var(--gray-400);width:14px"></i> ${c.emailCliente}</div>` : ''}
          ${!c.contatoCliente && !c.telefone2 && !c.emailCliente ? '—' : ''}
        </td>
        <td class="actions">
          <button class="btn-icon" title="Editar" onclick="abrirModalEditarCliente(${c.idCliente})">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn-icon danger" title="Excluir" onclick="deletarItem('cliente', ${c.idCliente}, '${c.nomeCliente}')">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>`).join('');
  }
  renderPaginacao('paginacaoClientes', total, PAG_STATE.clientes, 'mudarPaginaClientes');
}

function _limparModalCliente() {
  ['cliIdEdicao','cliNome','cliCpfCnpj','cliContato','cliEmail','cliTelefone2',
   'cliCep','cliRua','cliNumero','cliComplemento','cliBairro','cliCidade','cliEstado']
    .forEach(id => { document.getElementById(id).value = ''; });
}

function abrirModalNovoCliente() {
  _limparModalCliente();
  document.getElementById('modalClienteTitle').innerHTML =
    '<i class="fa-solid fa-user-plus"></i> Novo Cliente';
  abrirModal('modalCliente');
}

function abrirModalEditarCliente(idCliente) {
  const c = cacheClientes.find(x => x.idCliente == idCliente);
  if (!c) { showToast('Cliente não encontrado.', 'error'); return; }
  _limparModalCliente();
  document.getElementById('cliIdEdicao').value    = c.idCliente;
  document.getElementById('cliNome').value        = c.nomeCliente;
  document.getElementById('cliCpfCnpj').value     = c.CNPJCPF;
  document.getElementById('cliContato').value    = c.contatoCliente || '';
  document.getElementById('cliEmail').value      = c.emailCliente   || '';
  document.getElementById('cliTelefone2').value  = c.telefone2      || '';
  document.getElementById('cliCep').value        = c.cep            || '';
  document.getElementById('cliRua').value         = c.rua           || '';
  document.getElementById('cliNumero').value      = c.numero        || '';
  document.getElementById('cliComplemento').value = c.complemento   || '';
  document.getElementById('cliBairro').value      = c.bairro        || '';
  document.getElementById('cliCidade').value      = c.cidade        || '';
  document.getElementById('cliEstado').value      = c.estado        || '';
  document.getElementById('modalClienteTitle').innerHTML =
    '<i class="fa-solid fa-pen"></i> Editar Cliente';
  abrirModal('modalCliente');
}

async function salvarCliente() {
  const idEdicao     = document.getElementById('cliIdEdicao').value;
  const nome         = document.getElementById('cliNome').value.trim();
  const cpfcnpj      = document.getElementById('cliCpfCnpj').value.trim();
  const contato      = document.getElementById('cliContato').value.trim();
  const email        = document.getElementById('cliEmail').value.trim();
  const telefone2    = document.getElementById('cliTelefone2').value.trim();
  const cep          = document.getElementById('cliCep').value.trim();
  const rua          = document.getElementById('cliRua').value.trim();
  const numero       = document.getElementById('cliNumero').value.trim();
  const complemento  = document.getElementById('cliComplemento').value.trim();
  const bairro       = document.getElementById('cliBairro').value.trim();
  const cidade       = document.getElementById('cliCidade').value.trim();
  const estado       = document.getElementById('cliEstado').value.trim();

  if (!nome)   { showToast('Nome é obrigatório.', 'error'); return; }
  if (nome.length < 3) { showToast('Nome deve ter ao menos 3 caracteres.', 'error'); return; }
  if (/\d/.test(nome)) { showToast('Nome não pode conter números.', 'error'); return; }
  if (!cpfcnpj) { showToast('CPF/CNPJ é obrigatório.', 'error'); return; }
  const digitos = cpfcnpj.replace(/\D/g,'');
  if (digitos.length !== 11 && digitos.length !== 14) {
    showToast('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos.', 'error'); return;
  }
  if (!rua)    { showToast('Rua é obrigatória.', 'error'); return; }
  if (!numero) { showToast('Número é obrigatório.', 'error'); return; }
  if (!cidade) { showToast('Cidade é obrigatória.', 'error'); return; }
  if (!estado) { showToast('Estado é obrigatório.', 'error'); return; }

  const payload = {
    cliente: { nomeCliente: nome, CNPJCPF: cpfcnpj, contatoCliente: contato,
               emailCliente: email, telefone2,
               cep, rua, numero, complemento, bairro, cidade, estado }
  };

  try {
    if (idEdicao) {
      await apiFetch(`/cliente/${idEdicao}`, 'PUT', payload);
      showToast('Cliente atualizado!', 'success');
    } else {
      await apiFetch('/cliente', 'POST', payload);
      showToast(`Cliente "${nome}" cadastrado!`, 'success');
    }
    fecharModal('modalCliente');
    await carregarClientes();
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// EXCLUSÃO GENÉRICA
// ══════════════════════════════════════════════════

const endpointExclusao = { produto: '/produto', obra: '/obra', cliente: '/cliente', admin: '/admin' };

function deletarItem(tipo, id, nome) {
  document.getElementById('confirmarMsg').textContent =
    `Tem certeza que deseja excluir "${nome}"?`;
  document.getElementById('btnConfirmarExcluir').onclick = () =>
    confirmarExclusao(tipo, id);
  abrirModal('modalConfirmar');
}

async function confirmarExclusao(tipo, id) {
  fecharModal('modalConfirmar');
  try {
    await apiFetch(`${endpointExclusao[tipo]}/${id}`, 'DELETE');
    showToast('Item excluído com sucesso.', 'success');
    if (tipo === 'produto')  await carregarProdutos();
    if (tipo === 'obra')     await carregarObras();
    if (tipo === 'cliente')  await carregarClientes();
    if (tipo === 'admin')    await carregarAdmins();
  } catch (e) {
    showToast(`Erro ao excluir: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// DASHBOARD — renders
// ══════════════════════════════════════════════════

function _limiteAlerta(p) {
  return p.qtdMinima > 0 ? Math.ceil(p.qtdMinima * 1.10) : 0;
}

function _produtoEmAlerta(p) {
  return p.qtdProduto <= 0 || (p.qtdMinima > 0 && p.qtdProduto <= _limiteAlerta(p));
}

function renderAlertas(produtos) {
  const alertas = produtos.filter(_produtoEmAlerta);
  const el = document.getElementById('alertList');
  if (!alertas.length) {
    el.innerHTML = '<div class="empty-row">Nenhum alerta de estoque.</div>';
    return;
  }
  el.innerHTML = alertas.map(p => {
    const critico = p.qtdProduto <= 0;
    const info = critico
      ? 'Sem estoque'
      : `Estoque baixo: ${p.qtdProduto}/${p.qtdMinima} unidades`;
    return `
      <div class="alert-item ${critico ? 'critical' : 'warning'}">
        <div class="alert-dot"></div>
        <div class="alert-info">
          <strong>${p.nomeProduto}</strong>
          <span>${info}</span>
        </div>
        <span class="badge ${critico ? 'badge-red' : 'badge-yellow'}">${critico ? 'Crítico' : 'Atenção'}</span>
      </div>`;
  }).join('');
}

function renderObrasRecentes(obras) {
  const el = document.getElementById('obraRecentList');
  const recentes = [...obras].sort((a,b) => b.idObra - a.idObra).slice(0, 5);
  if (!recentes.length) {
    el.innerHTML = '<div class="empty-row">Nenhuma obra cadastrada.</div>';
    return;
  }
  const statusCls = { 'Em andamento': 'em-andamento', 'Pausada': 'pausada', 'Concluida': 'concluida', 'Cancelada': 'cancelada' };
  el.innerHTML = recentes.map(o => `
    <div class="obra-item">
      <div class="obra-status ${statusCls[o.statusObra] || 'concluida'}"></div>
      <div class="obra-info"><strong>${o.descObra}</strong><span>Cliente #${o.codCliente}</span></div>
      ${badgeStatus(o.statusObra)}
    </div>`).join('');
}

let _obraChart = null;

async function renderGraficoObras() {
  const canvas = document.getElementById('obraChartCanvas');
  if (!canvas) return;

  let dados = [];
  try {
    const res = await apiFetch('/relatorio/obras-produtos');
    dados = res.dados || [];
  } catch {
    dados = [];
  }

  if (_obraChart) { _obraChart.destroy(); _obraChart = null; }

  if (!dados.length) {
    canvas.closest('.chart-container').innerHTML =
      '<div class="empty-row" style="height:100%;display:flex;align-items:center;justify-content:center">Nenhuma obra cadastrada ainda.</div>';
    return;
  }

  const labels = dados.map(d => d.descObra.length > 22 ? d.descObra.slice(0, 22) + '…' : d.descObra);
  const values = dados.map(d => d.totalConsumido);
  const colors = dados.map(d =>
    d.totalConsumido === 0 ? 'rgba(200,197,190,0.6)' : 'rgba(232,82,10,0.82)'
  );

  _obraChart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Qtd. total de produtos',
        data: values,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.82', '1').replace('0.6', '1')),
        borderWidth: 1,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.y} unidades consumidas`,
          }
        }
      },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(0,0,0,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderNotificacoes(produtos) {
  const alertas  = produtos.filter(_produtoEmAlerta);
  const criticos = alertas.filter(p => p.qtdProduto <= 0);
  const badge = document.getElementById('notifBadge');
  if (criticos.length) { badge.textContent = criticos.length; badge.classList.remove('hidden'); }
  else badge.classList.add('hidden');
  const list = document.getElementById('notifList');
  if (!alertas.length) {
    list.innerHTML = '<div class="notif-item"><i class="fa-solid fa-circle-check" style="color:#16A34A"></i><div><strong>Tudo certo!</strong><p>Nenhum produto abaixo do mínimo.</p></div></div>';
    return;
  }
  list.innerHTML = alertas.map(p => {
    const critico = p.qtdProduto <= 0;
    return `
      <div class="notif-item ${critico ? 'alert' : 'warn'}">
        <i class="fa-solid ${critico ? 'fa-triangle-exclamation' : 'fa-circle-info'}"></i>
        <div><strong>${critico ? 'Sem estoque' : 'Estoque baixo'}</strong><p>${p.nomeProduto}: ${p.qtdProduto} unidades</p></div>
      </div>`;
  }).join('');
}

function atualizarKPI() {
  document.getElementById('kpi-produtos').textContent = cacheProdutos.length;
  document.getElementById('kpi-obras').textContent    = cacheObras.filter(o => o.statusObra === 'Em andamento').length;
  document.getElementById('kpi-clientes').textContent = cacheClientes.length;
  document.getElementById('kpi-alertas').textContent  = cacheProdutos.filter(_produtoEmAlerta).length;
}


// ══════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════

function statusEstoque(p) {
  if (p.qtdProduto <= 0)
    return { cls: 'critical', label: '<span class="badge badge-red">Sem estoque</span>' };
  if (p.qtdMinima > 0 && p.qtdProduto <= _limiteAlerta(p))
    return { cls: 'warning',  label: '<span class="badge badge-yellow">Alerta</span>' };
  return   { cls: 'ok',        label: '<span class="badge badge-green">Normal</span>' };
}

function badgeStatus(status) {
  const map = {
    'Em andamento': '<span class="badge badge-green">Em andamento</span>',
    'Pausada':       '<span class="badge badge-yellow">Pausada</span>',
    'Concluida':     '<span class="badge badge-gray">Concluída</span>',
    'Cancelada':     '<span class="badge badge-red">Cancelada</span>',
  };
  return map[status] || `<span class="badge badge-gray">${status}</span>`;
}


// ══════════════════════════════════════════════════
// UI — NAVEGAÇÃO, MODAIS, SEARCH, TOAST
// ══════════════════════════════════════════════════

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();
    const page = item.dataset.page;
    if (!page) return;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    item.classList.add('active');
    document.getElementById(`page-${page}`).classList.add('active');
    const labels = { dashboard: 'Dashboard', estoque: 'Estoque / Produtos', obras: 'Obras / Projetos', clientes: 'Clientes', admins: 'Administradores' };
    document.getElementById('breadcrumb').textContent = labels[page] || page;
  });
});

document.getElementById('sidebarToggle').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.querySelector('.main-content').classList.toggle('expanded');
});

document.getElementById('btnNotif').addEventListener('click', e => {
  e.stopPropagation();
  document.getElementById('notifDropdown').classList.toggle('hidden');
});
document.addEventListener('click', () => {
  document.getElementById('notifDropdown').classList.add('hidden');
});

function abrirModal(id)  { document.getElementById(id).classList.remove('hidden'); }
function fecharModal(id) { document.getElementById(id).classList.add('hidden'); }
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => { if (e.target === overlay) fecharModal(overlay.id); });
});

function filtrarProdutos(q) {
  filtros.produtos   = q.toLowerCase();
  PAG_STATE.produtos = 1;
  renderTabelaProdutos(cacheProdutos);
}

function filtrarObras() {
  filtros.obraTipo   = (document.getElementById('obraFiltroTipo')?.value   || '').toLowerCase().trim();
  filtros.obraStatus = (document.getElementById('obraFiltroStatus')?.value || '');
  filtros.obraDe     = _brParaIso(document.getElementById('obraFiltroDe')?.value  || '');
  filtros.obraAte    = _brParaIso(document.getElementById('obraFiltroAte')?.value || '');
  PAG_STATE.obras    = 1;
  renderTabelaObras(cacheObras);
}

function filtrarClientes(q) {
  filtros.clientes   = q.toLowerCase();
  PAG_STATE.clientes = 1;
  renderTabelaClientes(cacheClientes);
}

function filtrarStatusObra(status) { filtros.obraStatus = status; PAG_STATE.obras = 1; renderTabelaObras(cacheObras); }

function mudarPaginaProdutos(pg) { PAG_STATE.produtos = pg; renderTabelaProdutos(cacheProdutos); }
function mudarPaginaObras(pg)    { PAG_STATE.obras    = pg; renderTabelaObras(cacheObras); }
function mudarPaginaClientes(pg) { PAG_STATE.clientes = pg; renderTabelaClientes(cacheClientes); }

function renderPaginacao(containerId, total, paginaAtual, callbackNome) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const totalPags = Math.ceil(total / PER_PAGE);
  if (totalPags <= 1) { container.innerHTML = ''; return; }

  const inicio = (paginaAtual - 1) * PER_PAGE + 1;
  const fim    = Math.min(paginaAtual * PER_PAGE, total);

  const btn = (label, pg, extraClass = '') => {
    const isActive   = pg === paginaAtual && extraClass !== 'ellipsis' ? 'active' : '';
    const isDisabled = extraClass === 'ellipsis' ? 'disabled' : '';
    const click      = pg !== null && extraClass !== 'ellipsis' ? `onclick="${callbackNome}(${pg})"` : '';
    return `<button class="page-btn ${isActive} ${extraClass}" ${isDisabled} ${click}>${label}</button>`;
  };

  const pages = [];
  if (totalPags <= 7) {
    for (let i = 1; i <= totalPags; i++) pages.push(btn(i, i));
  } else {
    pages.push(btn(1, 1));
    if (paginaAtual > 3) pages.push(btn('…', null, 'ellipsis'));
    const s = Math.max(2, paginaAtual - 1);
    const e = Math.min(totalPags - 1, paginaAtual + 1);
    for (let i = s; i <= e; i++) pages.push(btn(i, i));
    if (paginaAtual < totalPags - 2) pages.push(btn('…', null, 'ellipsis'));
    pages.push(btn(totalPags, totalPags));
  }

  container.innerHTML = `
    <div class="pagination">
      <span class="pagination-info">Exibindo ${inicio}–${fim} de ${total}</span>
      <div class="pagination-controls">
        <button class="page-btn" ${paginaAtual === 1 ? 'disabled' : `onclick="${callbackNome}(${paginaAtual - 1})"`}>
          <i class="fa-solid fa-chevron-left"></i>
        </button>
        ${pages.join('')}
        <button class="page-btn" ${paginaAtual === totalPags ? 'disabled' : `onclick="${callbackNome}(${paginaAtual + 1})"`}>
          <i class="fa-solid fa-chevron-right"></i>
        </button>
      </div>
    </div>`;
}

// (barra de busca global removida — cada módulo tem sua própria busca)

function showToast(msg, type = 'success') {
  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.success}"></i><span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity='0'; toast.style.transform='translateY(10px)'; toast.style.transition='.3s'; }, 2800);
  setTimeout(() => toast.remove(), 3200);
}


// ══════════════════════════════════════════════════
// ADMINISTRADORES  →  GET/POST/PUT/DELETE /admin
// ══════════════════════════════════════════════════

let cacheAdmins = [];

async function carregarAdmins() {
  try {
    const res = await apiFetch('/admin');
    cacheAdmins = res.admins || [];
    renderTabelaAdmins(cacheAdmins);
  } catch (e) {
    document.getElementById('bodyAdmins').innerHTML =
      `<tr><td colspan="4" class="empty-row">Erro ao carregar administradores: ${e.message}</td></tr>`;
  }
}

function renderTabelaAdmins(admins) {
  const tbody = document.getElementById('bodyAdmins');
  if (!admins.length) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-row">Nenhum administrador cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = admins.map(a => `
    <tr>
      <td>${a.idLogin}</td>
      <td>${a.nomeLogin}</td>
      <td>${a.email}</td>
      <td class="actions">
        <button class="btn-icon" title="Editar" onclick="abrirModalEditarAdmin(${a.idLogin})">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="btn-icon danger" title="Excluir" onclick="deletarItem('admin', ${a.idLogin}, '${a.nomeLogin}')">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>`).join('');
}

function abrirModalNovoAdmin() {
  document.getElementById('adminIdEdicao').value = '';
  document.getElementById('adminNome').value     = '';
  document.getElementById('adminEmail').value    = '';
  document.getElementById('adminSenha').value      = '';
  document.getElementById('adminSenhaAtual').value = '';
  document.getElementById('adminNovaSenha').value  = '';
  document.getElementById('adminSenhaGroup').classList.remove('hidden');
  document.getElementById('adminSenhaAtualGroup').classList.add('hidden');
  document.getElementById('adminNovaSenhaGroup').classList.add('hidden');
  document.getElementById('modalAdminTitle').innerHTML =
    '<i class="fa-solid fa-user-shield"></i> Novo Administrador';
  abrirModal('modalAdmin');
}

function abrirModalEditarAdmin(idLogin) {
  const a = cacheAdmins.find(x => x.idLogin == idLogin);
  if (!a) { showToast('Administrador não encontrado.', 'error'); return; }
  document.getElementById('adminIdEdicao').value  = a.idLogin;
  document.getElementById('adminNome').value      = a.nomeLogin;
  document.getElementById('adminEmail').value     = a.email;
  document.getElementById('adminSenha').value      = '';
  document.getElementById('adminSenhaAtual').value = '';
  document.getElementById('adminNovaSenha').value  = '';
  document.getElementById('adminSenhaGroup').classList.add('hidden');
  document.getElementById('adminSenhaAtualGroup').classList.remove('hidden');
  document.getElementById('adminNovaSenhaGroup').classList.remove('hidden');
  document.getElementById('modalAdminTitle').innerHTML =
    '<i class="fa-solid fa-pen"></i> Editar Administrador';
  abrirModal('modalAdmin');
}

async function salvarAdmin() {
  const idEdicao  = document.getElementById('adminIdEdicao').value;
  const nome      = document.getElementById('adminNome').value.trim();
  const email     = document.getElementById('adminEmail').value.trim();
  const senha     = document.getElementById('adminSenha').value;
  const novaSenha = document.getElementById('adminNovaSenha').value;

  if (!nome)  { showToast('Nome é obrigatório.', 'error'); return; }
  if (!email) { showToast('Email é obrigatório.', 'error'); return; }

  const loggedId = parseInt(sessionStorage.getItem('idAdmin') || '0');

  try {
    if (idEdicao) {
      // Bloqueio de edição cruzada no frontend
      if (loggedId && loggedId !== parseInt(idEdicao)) {
        showToast('Você só pode editar seu próprio perfil.', 'error'); return;
      }
      const senhaAtual = document.getElementById('adminSenhaAtual').value;
      if (!senhaAtual) { showToast('Informe sua senha atual para confirmar.', 'error'); return; }
      const payload = { admin: { email, nomeLogin: nome, novaSenha: novaSenha || undefined, senhaAtual } };
      await apiFetch(`/admin/${idEdicao}`, 'PUT', payload);
      showToast('Administrador atualizado!', 'success');
    } else {
      if (!senha) { showToast('Senha é obrigatória.', 'error'); return; }
      const payload = { admin: { email, nomeLogin: nome, senha } };
      await apiFetch('/admin', 'POST', payload);
      showToast(`Administrador "${nome}" criado!`, 'success');
    }
    fecharModal('modalAdmin');
    await carregarAdmins();
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// EXPORTAÇÃO EXCEL (SheetJS)
// ══════════════════════════════════════════════════

function _downloadXLSX(nomeArquivo, cabecalhos, linhas) {
  const ws = XLSX.utils.aoa_to_sheet([cabecalhos, ...linhas]);

  // Largura automática por coluna
  const colWidths = cabecalhos.map((h, i) => {
    const max = Math.max(h.length, ...linhas.map(r => String(r[i] ?? '').length));
    return { wch: Math.min(max + 2, 50) };
  });
  ws['!cols'] = colWidths;

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Dados');
  XLSX.writeFile(wb, nomeArquivo);
}

function exportarProdutos() {
  if (!cacheProdutos.length) { showToast('Nenhum produto para exportar.', 'warning'); return; }
  const cabecalhos = ['ID', 'Nome', 'Descrição', 'Qtd. Atual', 'Qtd. Mínima', 'Qtd. Máxima', 'Status'];
  const linhas = cacheProdutos.map(p => {
    const statusTxt = p.qtdProduto <= 0 ? 'Sem estoque'
                    : (p.qtdMinima > 0 && p.qtdProduto < p.qtdMinima) ? 'Atenção'
                    : 'Normal';
    return [p.idProduto, p.nomeProduto, p.descProduto || '', p.qtdProduto, p.qtdMinima, p.qtdMaxima, statusTxt];
  });
  _downloadXLSX(`produtos_${_dataHoje()}.xlsx`, cabecalhos, linhas);
  showToast('Exportação concluída!', 'success');
}

function exportarObras() {
  if (!cacheObras.length) { showToast('Nenhuma obra para exportar.', 'warning'); return; }
  const cabecalhos = ['ID', 'Descrição', 'Field', 'ID Cliente', 'Cliente', 'Data Início', 'Data Fim', 'Status', 'Observações', 'Orientações'];
  const fmtData    = d => { if (!d) return ''; const [y,m,dia] = d.split('-'); return `${dia}/${m}/${y}`; };
  const linhas = cacheObras.map(o => {
    const cliente = cacheClientes.find(c => c.idCliente === o.codCliente);
    return [
      o.idObra, o.descObra, o.respObra || '', o.codCliente,
      cliente ? cliente.nomeCliente : '',
      fmtData(o.dataInicio), fmtData(o.dataFim), o.statusObra,
      o.obsObra || '', o.orientacaoObra || '',
    ];
  });
  _downloadXLSX(`obras_${_dataHoje()}.xlsx`, cabecalhos, linhas);
  showToast('Exportação concluída!', 'success');
}

function exportarClientes() {
  if (!cacheClientes.length) { showToast('Nenhum cliente para exportar.', 'warning'); return; }
  const cabecalhos = ['ID', 'Nome', 'CPF/CNPJ', 'Contato', 'CEP', 'Rua', 'Número', 'Complemento', 'Bairro', 'Cidade', 'Estado'];
  const linhas = cacheClientes.map(c => [
    c.idCliente, c.nomeCliente, c.CNPJCPF, c.contatoCliente || '',
    c.cep || '', c.rua || '', c.numero || '', c.complemento || '',
    c.bairro || '', c.cidade || '', c.estado || '',
  ]);
  _downloadXLSX(`clientes_${_dataHoje()}.xlsx`, cabecalhos, linhas);
  showToast('Exportação concluída!', 'success');
}

function _dataHoje() {
  return new Date().toISOString().slice(0, 10);
}


// ══════════════════════════════════════════════════
// LOGOUT
// ══════════════════════════════════════════════════

function logout() {
  sessionStorage.clear();
  showToast('Sessão encerrada. Redirecionando...', 'info');
  setTimeout(() => { window.location.href = '/'; }, 1200);
}


// ══════════════════════════════════════════════════
// NAVEGAÇÃO POR KPI
// ══════════════════════════════════════════════════

function navegarPara(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const navItem = document.querySelector(`.nav-item[data-page="${page}"]`);
  const pageEl  = document.getElementById(`page-${page}`);
  if (navItem) navItem.classList.add('active');
  if (pageEl)  pageEl.classList.add('active');
  const labels = { dashboard: 'Dashboard', estoque: 'Estoque / Produtos', obras: 'Obras / Projetos', clientes: 'Clientes', admins: 'Administradores' };
  document.getElementById('breadcrumb').textContent = labels[page] || page;
}


// ══════════════════════════════════════════════════
// SUB-TABS (Admins / Responsáveis)
// ══════════════════════════════════════════════════

function mudarSubtab(section, btn) {
  const panel = btn.dataset.subtab;
  document.querySelectorAll(`#page-${section} .subtab`).forEach(b => b.classList.remove('active'));
  document.querySelectorAll(`#page-${section} .subtab-panel`).forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(panel).classList.add('active');
}


// ══════════════════════════════════════════════════
// TOGGLE SENHA — ADMIN MODAL
// ══════════════════════════════════════════════════

function toggleAdminSenha(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon  = btn.querySelector('i');
  if (input.type === 'password') {
    input.type = 'text';
    icon.className = 'fa-regular fa-eye-slash';
  } else {
    input.type = 'password';
    icon.className = 'fa-regular fa-eye';
  }
}


// ══════════════════════════════════════════════════
// FILTRO DE ADMINS
// ══════════════════════════════════════════════════

function filtrarAdmins(q) {
  const lower = q.toLowerCase();
  const tbody = document.getElementById('bodyAdmins');
  cacheAdmins.forEach((a, i) => {
    const row = tbody.rows[i];
    if (!row) return;
    const match = `${a.idLogin} ${a.nomeLogin} ${a.email}`.toLowerCase().includes(lower);
    row.style.display = match ? '' : 'none';
  });
}


// ══════════════════════════════════════════════════
// EXPORTAÇÃO ADMINS
// ══════════════════════════════════════════════════

function exportarAdmins() {
  if (!cacheAdmins.length) { showToast('Nenhum administrador para exportar.', 'warning'); return; }
  const cabecalhos = ['ID', 'Nome', 'Email'];
  const linhas = cacheAdmins.map(a => [a.idLogin, a.nomeLogin, a.email]);
  _downloadXLSX(`admins_${_dataHoje()}.xlsx`, cabecalhos, linhas);
  showToast('Exportação concluída!', 'success');
}


// ══════════════════════════════════════════════════
// RESPONSÁVEIS — GET/POST/PUT/DELETE /responsavel
// ══════════════════════════════════════════════════

let cacheResponsaveis = [];

async function carregarResponsaveis() {
  try {
    const res = await apiFetch('/responsavel');
    cacheResponsaveis = res.responsaveis || [];
    renderTabelaResponsaveis(cacheResponsaveis);
    popularSelectResponsaveis();
  } catch (e) {
    console.error('carregarResponsaveis:', e);
  }
}

function popularSelectResponsaveis() {
  const sel = document.getElementById('obraResp');
  if (!sel) return;
  const valorAtual = sel.value;
  sel.innerHTML = '<option value="">Selecione o responsável...</option>';
  cacheResponsaveis.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r.nomeResponsavel;
    opt.textContent = r.nomeResponsavel;
    sel.appendChild(opt);
  });
  if (valorAtual) sel.value = valorAtual;
}

function renderTabelaResponsaveis(lista) {
  const tbody = document.getElementById('bodyResponsaveis');
  if (!tbody) return;
  if (!lista.length) {
    tbody.innerHTML = `<tr><td colspan="3" class="empty-row">Nenhum responsável cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = lista.map(r => `
    <tr>
      <td>${r.idResponsavel}</td>
      <td>${r.nomeResponsavel}</td>
      <td class="actions">
        <button class="btn-icon" title="Editar" onclick="abrirModalEditarResponsavel(${r.idResponsavel})">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button class="btn-icon danger" title="Excluir" onclick="confirmarExcluirResponsavel(${r.idResponsavel}, '${r.nomeResponsavel}')">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>`).join('');
}

function filtrarResponsaveis(q) {
  const lower = q.toLowerCase();
  const tbody = document.getElementById('bodyResponsaveis');
  cacheResponsaveis.forEach((r, i) => {
    const row = tbody.rows[i];
    if (!row) return;
    row.style.display = `${r.idResponsavel} ${r.nomeResponsavel}`.toLowerCase().includes(lower) ? '' : 'none';
  });
}

function abrirModalNovoResponsavel() {
  document.getElementById('respIdEdicao').value = '';
  document.getElementById('respNome').value     = '';
  document.getElementById('modalResponsavelTitle').innerHTML =
    '<i class="fa-solid fa-id-badge"></i> Novo Responsável';
  abrirModal('modalResponsavel');
}

function abrirModalEditarResponsavel(id) {
  const r = cacheResponsaveis.find(x => x.idResponsavel == id);
  if (!r) { showToast('Responsável não encontrado.', 'error'); return; }
  document.getElementById('respIdEdicao').value = r.idResponsavel;
  document.getElementById('respNome').value     = r.nomeResponsavel;
  document.getElementById('modalResponsavelTitle').innerHTML =
    '<i class="fa-solid fa-pen"></i> Editar Responsável';
  abrirModal('modalResponsavel');
}

async function salvarResponsavel() {
  const idEdicao = document.getElementById('respIdEdicao').value;
  const nome     = document.getElementById('respNome').value.trim();
  if (!nome) { showToast('Nome é obrigatório.', 'error'); return; }

  try {
    if (idEdicao) {
      await apiFetch(`/responsavel/${idEdicao}`, 'PUT', { nomeResponsavel: nome });
      showToast('Responsável atualizado!', 'success');
    } else {
      await apiFetch('/responsavel', 'POST', { nomeResponsavel: nome });
      showToast(`Responsável "${nome}" criado!`, 'success');
    }
    fecharModal('modalResponsavel');
    await carregarResponsaveis();
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}

function confirmarExcluirResponsavel(id, nome) {
  document.getElementById('confirmarMsg').textContent = `Tem certeza que deseja excluir "${nome}"?`;
  document.getElementById('btnConfirmarExcluir').onclick = () => excluirResponsavel(id);
  abrirModal('modalConfirmar');
}

async function excluirResponsavel(id) {
  fecharModal('modalConfirmar');
  try {
    await apiFetch(`/responsavel/${id}`, 'DELETE');
    showToast('Responsável excluído.', 'success');
    await carregarResponsaveis();
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// EDITAR PRODUTO DA OBRA (modal)
// ══════════════════════════════════════════════════

function abrirModalEditarProdObra(idObra, idProduto, nomeProduto, qtdAtual) {
  document.getElementById('editProdObraIdObra').value    = idObra;
  document.getElementById('editProdObraIdProduto').value = idProduto;
  document.getElementById('editProdObraNome').textContent = nomeProduto;
  document.getElementById('editProdObraQtd').value        = qtdAtual;
  abrirModal('modalEditarProdObra');
}

async function confirmarEditarProdObra() {
  const idObra    = document.getElementById('editProdObraIdObra').value;
  const idProduto = document.getElementById('editProdObraIdProduto').value;
  const qtd       = parseInt(document.getElementById('editProdObraQtd').value);
  if (!qtd || qtd < 1) { showToast('Informe uma quantidade válida.', 'error'); return; }
  try {
    await apiFetch(`/obra/${idObra}/produto/${idProduto}`, 'PATCH', { quantidade: qtd });
    fecharModal('modalEditarProdObra');
    showToast('Quantidade atualizada!', 'success');
    await Promise.all([carregarObras(), carregarProdutos()]);
    // Re-abre o modal de ver produtos com dados atualizados
    verProdutosObra(parseInt(idObra));
  } catch (e) {
    showToast(`Erro: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// RELATÓRIO DE CONSUMO
// ══════════════════════════════════════════════════

async function gerarRelatorio() {
  try {
    const res  = await apiFetch('/relatorio/produtos-consumidos');
    const data = res.dados || [];
    if (!data.length) { showToast('Nenhum dado de consumo registrado.', 'warning'); return; }

    const cabecalhos = ['ID', 'Produto', 'Total Consumido', 'Estoque Atual', 'Qtd. Mínima'];
    const linhas = data.map(d => [d.idProduto, d.nomeProduto, d.totalConsumido, d.estoqueAtual, d.qtdMinima]);
    _downloadXLSX(`relatorio_consumo_${_dataHoje()}.xlsx`, cabecalhos, linhas);
    showToast('Relatório exportado com sucesso!', 'success');
  } catch (e) {
    showToast(`Erro ao gerar relatório: ${e.message}`, 'error');
  }
}
