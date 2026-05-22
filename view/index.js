// =====================================================
// CONSTROESTOQUE — index.js
// Integração completa com a API Flask + JWT
// =====================================================


// ══════════════════════════════════════════════════
// CONFIGURAÇÃO DA API + TOKEN JWT
// ══════════════════════════════════════════════════

const API_BASE_URL = 'http://localhost:5000';

// Escapa string para uso seguro em atributo onclick="func('...')"
// Trata: & → &amp;  |  " → &quot;  |  ' → \'
function _esc(s) {
  return (s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, "\\'");
}

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
    const apiError = new Error(err.msg || err.message || `HTTP ${res.status}`);
    apiError.apiField = err.error || null;
    throw apiError;
  }
  return res.json();
}


// ══════════════════════════════════════════════════
// INICIALIZAÇÃO
// ══════════════════════════════════════════════════

let fpInicio, fpFim;

document.addEventListener('DOMContentLoaded', () => {
  verificarAutenticacao();

  const snapRaw = sessionStorage.getItem('domSnapshot');
  if (snapRaw) {
    sessionStorage.removeItem('domSnapshot');
    try {
      const snap = JSON.parse(snapRaw);
      Object.entries(snap).forEach(([id, html]) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = html;
      });
    } catch (_) {}
  }
  const abaAtual = sessionStorage.getItem('abaAtual');
  if (abaAtual) {
    sessionStorage.removeItem('abaAtual');
    navegarPara(abaAtual);
  }
  document.documentElement.classList.remove('restoring-tab');

  carregarAdministrador();
  carregarTodos();
  _setupValidacaoProduto();

  fpInicio = flatpickr('#obraDataInicio', {
    dateFormat: 'd/m/Y', locale: 'pt', allowInput: true,
    onChange: () => _obraClearError('obraDataInicio'),
  });
  fpFim = flatpickr('#obraDataFim', { dateFormat: 'd/m/Y', locale: 'pt', allowInput: true });

  // Blur validation — obra form
  document.getElementById('obraResp').addEventListener('change', () => {
    if (document.getElementById('obraResp').value) _obraClearError('obraResp');
    else _obraSetError('obraResp', 'Selecione o field responsável.');
  });
  document.getElementById('obraCodCliente').addEventListener('blur', _buscarClienteObra);
  document.getElementById('obraCodCliente').addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); _buscarClienteObra(); }
  });
  document.getElementById('obraDataInicio').addEventListener('blur', () => {
    if (!document.getElementById('obraDataInicio').value.trim())
      _obraSetError('obraDataInicio', 'Data de início é obrigatória.');
  });
  document.getElementById('obraDesc').addEventListener('blur', () => {
    if (!document.getElementById('obraDesc').value.trim())
      _obraSetError('obraDesc', 'A descrição da obra é obrigatória.');
    else _obraClearError('obraDesc');
  });
  document.getElementById('obraUnidade').addEventListener('change', () => {
    if (!document.getElementById('obraUnidade').value)
      _obraSetError('obraUnidade', 'Selecione a unidade.');
    else _obraClearError('obraUnidade');
  });
  document.getElementById('obraTipo').addEventListener('change', () => {
    if (!document.getElementById('obraTipo').value)
      _obraSetError('obraTipo', 'Selecione o tipo de obra.');
    else _obraClearError('obraTipo');
  });
  const _clienteBlurCfg = {
    obraClienteCNPJ:         'CNPJ / CPF é obrigatório.',
    obraClienteNome:         'Nome do cliente é obrigatório.',
    obraClienteRua:          'Endereço é obrigatório.',
    obraClienteNumero:       'Número é obrigatório.',
    obraClienteComplemento:  'Complemento é obrigatório.',
    obraClienteBairro:       'Bairro é obrigatório.',
  };
  Object.entries(_clienteBlurCfg).forEach(([id, msg]) => {
    document.getElementById(id).addEventListener('blur', () => {
      if (!document.getElementById(id).value.trim()) _obraSetError(id, msg);
      else _obraClearError(id);
    });
  });

  const fpFiltroOpts = { dateFormat: 'd/m/Y', locale: 'pt', allowInput: true, onChange: filtrarObras };
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
  if (nameEl) nameEl.textContent = nome;
}


// ══════════════════════════════════════════════════
// PRODUTOS  →  GET/POST/PUT/DELETE /produto
// ══════════════════════════════════════════════════

let cacheProdutos = [];
const _cacheReady = { produtos: false, obras: false, clientes: false, admins: false, responsaveis: false };

async function carregarProdutos() {
  try {
    const res = await apiFetch('/produto');
    cacheProdutos = res.produtos || [];
    _cacheReady.produtos = true;
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
  const q             = filtros.produtos;
  const statusFiltro  = filtros.produtosStatus;

  const filtradoPorStatus = statusFiltro === 'ok'
    ? produtos.filter(p => !_produtoEmAlerta(p) && p.qtdProduto > 0)
    : statusFiltro === 'alerta'
      ? produtos.filter(p => _produtoEmAlerta(p) && p.qtdProduto > 0)
      : statusFiltro === 'zero'
        ? produtos.filter(p => p.qtdProduto <= 0)
        : produtos;

  const filtrado = q ? filtradoPorStatus.filter(p =>
    `${p.idProduto} ${p.nomeProduto} ${p.descProduto || ''}`.toLowerCase().includes(q)
  ) : filtradoPorStatus;

  const ordenado   = ordenarLista(filtrado, 'produtos');
  const total       = ordenado.length;
  const totalPags   = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.produtos > totalPags) PAG_STATE.produtos = 1;
  const inicio      = (PAG_STATE.produtos - 1) * PER_PAGE;
  const pagina      = ordenado.slice(inicio, inicio + PER_PAGE);

  const tbody = document.getElementById('bodyProdutos');
  if (!pagina.length) {
    tbody.innerHTML = _emptyState(
      'boxes-stacked',
      total === 0 && q ? 'Nenhum resultado encontrado' : 'Nenhum produto cadastrado',
      total === 0 && q
        ? `A busca por "${q}" não retornou resultados.`
        : 'Comece cadastrando o primeiro produto do estoque.',
      !q ? 'Cadastrar Produto' : '', 'abrirModalNovoProduto()', 5
    );
  } else {
    tbody.innerHTML = pagina.map(p => {
      const { cls, label } = statusEstoque(p);
      const nomeSafe = _esc(p.nomeProduto);
      const limites  = [
        p.qtdMinima ? `Mín: ${p.qtdMinima}` : null,
        p.qtdMaxima && p.qtdMaxima < 9999 ? `Máx: ${p.qtdMaxima}` : null,
      ].filter(Boolean).join(' · ');
      return `
        <tr>
          <td><span class="cell-id">${p.idProduto}</span></td>
          <td>
            <div class="cell-stack">
              <span class="cell-primary">${p.nomeProduto}</span>
              ${p.descProduto ? `<span class="cell-secondary">${p.descProduto}</span>` : ''}
            </div>
          </td>
          <td>
            <div class="cell-stack">
              <span class="qty-badge ${cls}">${p.qtdProduto} un.</span>
              ${limites ? `<span class="cell-secondary" style="margin-top:5px">${limites}</span>` : ''}
            </div>
          </td>
          <td>${label}</td>
          <td>${_actionMenu([
            { icon:'fa-pen',   label:'Editar',  onclick:`abrirModalEditarProduto(${p.idProduto})` },
            { divider: true },
            { icon:'fa-trash', label:'Excluir', danger:true, onclick:`deletarItem('produto',${p.idProduto},'${nomeSafe}')` },
          ])}</td>
        </tr>`;
    }).join('');
  }
  renderPaginacao('paginacaoProdutos', total, PAG_STATE.produtos, 'mudarPaginaProdutos');
  atualizarIndicadoresOrdenacao('produtos');
}

// ── Validação inline — Modal de Produto ───────────────────────────────────────

function _erroProd(id, msg) {
  const span = document.getElementById(`err-${id}`);
  const input = document.getElementById(id);
  if (span)  { span.textContent = msg; span.classList.toggle('visible', !!msg); }
  if (input) input.classList.toggle('input-error', !!msg);
}

function _vProdNome(show = true) {
  const v = document.getElementById('prodNome').value.trim();
  let msg = '';
  if (!v)                msg = 'O nome do produto é obrigatório.';
  else if (v.length < 3) msg = 'O nome deve ter pelo menos 3 caracteres.';
  if (msg && show) _erroProd('prodNome', msg);
  else if (!msg)   _erroProd('prodNome', '');
  return !msg;
}

function _vProdQtd(show = true) {
  const v = document.getElementById('prodQtd').value.trim();
  let msg = '';
  if (v === '')                          msg = 'A quantidade em estoque é obrigatória.';
  else if (!Number.isInteger(Number(v))) msg = 'A quantidade deve ser um número inteiro.';
  else if (Number(v) < 0)               msg = 'A quantidade não pode ser negativa.';
  else if (Number(v) > 9999)            msg = 'A quantidade não pode ultrapassar 9999 unidades.';
  if (msg && show) _erroProd('prodQtd', msg);
  else if (!msg)   _erroProd('prodQtd', '');
  return !msg;
}

function _vProdQtdMin(show = true) {
  const vMin = document.getElementById('prodQtdMin').value.trim();
  const vMax = document.getElementById('prodQtdMax').value.trim();
  let msg = '';
  if (vMin === '')                                        msg = 'A quantidade mínima é obrigatória.';
  else if (!Number.isInteger(Number(vMin)) || Number(vMin) < 0) msg = 'A quantidade mínima deve ser um número inteiro positivo.';
  else if (vMax !== '' && Number(vMin) > Number(vMax))   msg = 'A quantidade mínima não pode ser maior que a máxima.';
  if (msg && show) _erroProd('prodQtdMin', msg);
  else if (!msg)   _erroProd('prodQtdMin', '');
  return !msg;
}

function _vProdQtdMax(show = true) {
  const vMax = document.getElementById('prodQtdMax').value.trim();
  const vMin = document.getElementById('prodQtdMin').value.trim();
  let msg = '';
  if (vMax === '')                                         msg = 'A quantidade máxima é obrigatória.';
  else if (!Number.isInteger(Number(vMax)) || Number(vMax) <= 0) msg = 'A quantidade máxima deve ser um número inteiro positivo.';
  else if (vMin !== '' && Number(vMax) <= Number(vMin))    msg = 'A quantidade máxima deve ser maior que a mínima.';
  if (msg && show) _erroProd('prodQtdMax', msg);
  else if (!msg)   _erroProd('prodQtdMax', '');
  return !msg;
}

function _vProdDesc(show = true) {
  const v = document.getElementById('prodDesc').value.trim();
  const msg = v ? '' : 'A descrição é obrigatória.';
  if (msg && show) _erroProd('prodDesc', msg);
  else if (!msg)   _erroProd('prodDesc', '');
  return !msg;
}

function _validarFormProduto() {
  return [_vProdNome(), _vProdQtd(), _vProdQtdMin(), _vProdQtdMax(), _vProdDesc()].every(Boolean);
}

function _atualizarBtnSalvarProduto() {
  const btn = document.getElementById('btnSalvarProduto');
  if (btn) btn.disabled = ![_vProdNome(false), _vProdQtd(false), _vProdQtdMin(false), _vProdQtdMax(false), _vProdDesc(false)].every(Boolean);
}

function _setupValidacaoProduto() {
  const bind = (id, fn, extras = []) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('blur',  () => { fn(true);  extras.forEach(f => f(false)); _atualizarBtnSalvarProduto(); });
    el.addEventListener('input', () => { fn(false); extras.forEach(f => f(false)); _atualizarBtnSalvarProduto(); });
  };
  bind('prodNome',   _vProdNome);
  bind('prodQtd',    _vProdQtd);
  bind('prodQtdMin', _vProdQtdMin, [_vProdQtdMax]);
  bind('prodQtdMax', _vProdQtdMax, [_vProdQtdMin]);
  bind('prodDesc',   _vProdDesc);
}

function _resetErrosProduto() {
  ['prodNome','prodQtd','prodQtdMin','prodQtdMax','prodDesc'].forEach(id => _erroProd(id, ''));
}

// ── Modal abrir / fechar ───────────────────────────────────────────────────────

function abrirModalNovoProduto() {
  ['prodIdEdicao','prodNome','prodQtd','prodQtdMin','prodQtdMax','prodDesc']
    .forEach(id => { document.getElementById(id).value = ''; });
  document.getElementById('modalProdutoTitle').innerHTML =
    '<i class="fa-solid fa-boxes-stacked"></i> Novo Produto';
  _resetErrosProduto();
  _atualizarBtnSalvarProduto();
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
  _resetErrosProduto();
  _atualizarBtnSalvarProduto();
  abrirModal('modalProduto');
}

async function salvarProduto() {
  if (!_validarFormProduto()) return;

  const idEdicao = document.getElementById('prodIdEdicao').value;
  const nome   = document.getElementById('prodNome').value.trim();
  const qtd    = parseInt(document.getElementById('prodQtd').value);
  const qtdMin = parseInt(document.getElementById('prodQtdMin').value);
  const qtdMax = parseInt(document.getElementById('prodQtdMax').value);
  const desc   = document.getElementById('prodDesc').value.trim();

  const payload = {
    produto: { nomeProduto: nome, qtdProduto: qtd, qtdMinima: qtdMin, qtdMaxima: qtdMax, descProduto: desc }
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
    _cacheReady.obras = true;
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

  const ordenado   = ordenarLista(filtrado, 'obras');
  const total       = ordenado.length;
  const totalPags   = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.obras > totalPags) PAG_STATE.obras = 1;
  const inicio      = (PAG_STATE.obras - 1) * PER_PAGE;
  const pagina      = ordenado.slice(inicio, inicio + PER_PAGE);

  const fmtData = d => { if (!d) return '—'; const [y,m,dia] = d.split('-'); return `${dia}/${m}/${y}`; };
  const tbody   = document.getElementById('bodyObras');
  const temFiltro = tipo || s || de || ate;

  if (!pagina.length) {
    tbody.innerHTML = _emptyState(
      'hard-hat',
      temFiltro ? 'Nenhuma obra encontrada' : 'Nenhuma obra cadastrada',
      temFiltro ? 'Tente ajustar os filtros de busca.' : 'Comece cadastrando a primeira obra.',
      !temFiltro ? 'Nova Obra' : '', 'abrirModalNovaObra()', 6
    );
  } else {
    tbody.innerHTML = pagina.map(o => {
      const badge       = badgeStatus(o.statusObra);
      const cliente     = cacheClientes.find(c => c.idCliente === o.codCliente);
      const nomeCliente = cliente ? cliente.nomeCliente : (o.codCliente ? `Cliente ${o.codCliente}` : '—');
      const descEsc = _esc(o.descObra);
      const tags = [o.tipoObra, o.respObra].filter(Boolean);
      return `
        <tr>
          <td><span class="cell-id">${o.idObra}</span></td>
          <td>
            <div class="cell-stack">
              <span class="cell-primary">${nomeCliente}</span>
              ${o.codCliente ? `<span class="cell-secondary">Cód. ${o.codCliente}</span>` : ''}
            </div>
          </td>
          <td>
            <div class="cell-stack">
              <span class="cell-primary">${o.descObra || '—'}</span>
              ${tags.length ? `<div style="display:flex;gap:5px;flex-wrap:wrap;margin-top:4px">${tags.map(t=>`<span class="cell-tag"><i class="fa-solid fa-tag"></i>${t}</span>`).join('')}</div>` : ''}
            </div>
          </td>
          <td><span class="cell-secondary">${fmtData(o.dataInicio)}</span></td>
          <td>${badge}</td>
          <td>${_actionMenu([
            { icon:'fa-eye',   label:'Ver Produtos', onclick:`verProdutosObra(${o.idObra})` },
            { icon:'fa-pen',   label:'Editar',       onclick:`abrirModalEditarObra(${o.idObra})` },
            { divider: true },
            { icon:'fa-trash', label:'Excluir', danger:true, onclick:`deletarItem('obra',${o.idObra},'${descEsc}')` },
          ])}</td>
        </tr>`;
    }).join('');
  }
  renderPaginacao('paginacaoObras', total, PAG_STATE.obras, 'mudarPaginaObras');
  atualizarIndicadoresOrdenacao('obras');
}

function _prodSearchHTML(btnRemove) {
  return `
    <div class="produto-obra-row">
      <div class="prod-search-wrap">
        <input type="text" class="prod-search" placeholder="Buscar produto (nome ou ID)..."
          oninput="buscarProdutoInput(this)"
          onfocus="buscarProdutoInput(this)"
          onblur="setTimeout(()=>fecharDropdownProduto(this),150)"
          autocomplete="off" />
        <input type="hidden" class="prod-select" />
        <div class="prod-dropdown hidden"></div>
      </div>
      <input type="text" placeholder="Estoque" class="prod-estoque-input" readonly />
      <input type="number" placeholder="Qtd." class="prod-qtd-input" min="1" />
      ${btnRemove}
    </div>`;
}

function _novaProdutoObraRow() {
  return _prodSearchHTML(`<button class="btn-icon danger" onclick="removerProdutoObra(this)"><i class="fa-solid fa-minus"></i></button>`);
}

function buscarProdutoInput(input) {
  const q    = input.value.toLowerCase().trim();
  const wrap = input.closest('.prod-search-wrap');
  const drop = wrap.querySelector('.prod-dropdown');
  const hidden = wrap.querySelector('.prod-select');

  const matches = q
    ? cacheProdutos.filter(p =>
        p.nomeProduto.toLowerCase().includes(q) || String(p.idProduto).includes(q)
      )
    : cacheProdutos;

  if (!matches.length) { drop.classList.add('hidden'); return; }

  drop.innerHTML = matches.map(p => {
    const cor = p.qtdProduto <= 0 ? '#DC2626' : (p.qtdMinima > 0 && p.qtdProduto <= p.qtdMinima) ? '#D97706' : '#16A34A';
    return `<div class="prod-dropdown-item" onmousedown="selecionarProdutoDropdown(this,${p.idProduto})">
      <span class="prod-id">${p.idProduto}</span>
      <span class="prod-name">${p.nomeProduto}</span>
      <span class="prod-stock" style="color:${cor}">${p.qtdProduto} em estoque</span>
    </div>`;
  }).join('');
  drop.classList.remove('hidden');
}

function selecionarProdutoDropdown(item, idProduto) {
  const wrap    = item.closest('.prod-search-wrap');
  const row     = wrap.closest('.produto-obra-row');
  const p       = cacheProdutos.find(x => x.idProduto === idProduto);
  if (!p) return;

  wrap.querySelector('.prod-search').value = `${p.idProduto} — ${p.nomeProduto}`;
  wrap.querySelector('.prod-select').value = p.idProduto;
  wrap.querySelector('.prod-dropdown').classList.add('hidden');

  const estoqueEl = row.querySelector('.prod-estoque-input');
  const cor = p.qtdProduto <= 0 ? '#DC2626' : (p.qtdMinima > 0 && p.qtdProduto <= p.qtdMinima) ? '#D97706' : '#16A34A';
  estoqueEl.value = `${p.qtdProduto} em estoque`;
  estoqueEl.style.color = cor;
}

function fecharDropdownProduto(input) {
  const drop = input.closest('.prod-search-wrap').querySelector('.prod-dropdown');
  drop.classList.add('hidden');
}

// Mapa: campo retornado pelo backend → id do elemento no HTML
const _OBRA_CAMPO_MAP = {
  codCliente:     'obraCodCliente',
  descObra:       'obraDesc',
  dataInicio:     'obraDataInicio',
  dataFim:        'obraDataFim',
  statusObra:     'obraStatus',
  respObra:       'obraResp',
  produtosUsados: 'produtosUsados',
  produtosNovos:  'produtosUsados',
};

function _obraSetError(fieldId, msg) {
  const errEl = document.getElementById(`err-${fieldId}`);
  const input = document.getElementById(fieldId);
  if (errEl) { errEl.textContent = msg; errEl.classList.add('visible'); }
  if (input) input.classList.add('input-error');
}

function _obraClearError(fieldId) {
  const errEl = document.getElementById(`err-${fieldId}`);
  const input = document.getElementById(fieldId);
  if (errEl) { errEl.textContent = ''; errEl.classList.remove('visible'); }
  if (input) input.classList.remove('input-error');
}

function _obraLimparErros() {
  ['obraResp', 'obraCodCliente', 'obraDataInicio', 'obraDataFim',
   'obraDesc', 'obraStatus', 'obraUnidade', 'obraTipo',
   'obraClienteCNPJ', 'obraClienteNome', 'obraClienteRua',
   'obraClienteNumero', 'obraClienteComplemento', 'obraClienteBairro',
   'produtosUsados'].forEach(_obraClearError);
}

function _obraExibirErroApi(e) {
  if (e.apiField?.campo) {
    const frontId = _OBRA_CAMPO_MAP[e.apiField.campo] || e.apiField.campo;
    _obraSetError(frontId, e.apiField.message || e.message);
  } else {
    showToast(`Erro: ${e.message}`, 'error');
  }
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
  _obraLimparErros();
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
  const _displayEl = document.getElementById('obraIdDisplay');
  if (_displayEl) _displayEl.value = o.idObra;
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

// Limpa todos os campos da seção Cliente e seus erros inline
function _limparCamposCliente() {
  [
    'obraClienteCNPJ', 'obraClienteNome', 'obraClienteRua', 'obraClienteNumero',
    'obraClienteComplemento', 'obraClienteBairro', 'obraClienteCEP',
    'obraClienteCidade', 'obraClienteEstado',
    'obraContato', 'obraEmail', 'obraCelular1', 'obraCelular2',
  ].forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  ['obraClienteCNPJ', 'obraClienteNome', 'obraClienteRua',
   'obraClienteNumero', 'obraClienteComplemento', 'obraClienteBairro'].forEach(_obraClearError);
}

// Preenche os campos da seção Cliente a partir de um objeto cliente (sem guard)
function _preencherCamposCliente(c) {
  const fill = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
  fill('obraClienteNome',        c.nomeCliente);
  fill('obraClienteCNPJ',        c.CNPJCPF);
  fill('obraClienteRua',         c.rua);
  fill('obraClienteNumero',      c.numero);
  fill('obraClienteComplemento', c.complemento);
  fill('obraClienteBairro',      c.bairro);
  fill('obraClienteCEP',         c.cep);
  fill('obraClienteCidade',      c.cidade);
  fill('obraClienteEstado',      c.estado);
  fill('obraEmail',              c.emailCliente);
  fill('obraCelular1',           c.contatoCliente);
  fill('obraCelular2',           c.telefone2);
}

// oninput no campo Código (Cliente): limpa imediatamente quando apagado
function _obraOnCodClienteInput(input) {
  if (!input.value.trim()) {
    _limparCamposCliente();
    _obraClearError('obraCodCliente');
  }
}

// Disparado no blur / Enter: busca via API e preenche ou exibe erro
async function _buscarClienteObra() {
  const id = parseInt(document.getElementById('obraCodCliente').value);
  _limparCamposCliente();
  _obraClearError('obraCodCliente');
  if (!id || id <= 0) return;
  try {
    const res = await apiFetch(`/cliente/${id}`);
    _preencherCamposCliente(res.cliente);
  } catch {
    _obraSetError('obraCodCliente', 'Cliente não encontrado.');
  }
}

// Usado apenas na abertura do modal de edição: preenche do cache sem sobrescrever
// campos de contato já vindos da obra (email, celulares)
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

  _obraLimparErros();

  const cnpj        = document.getElementById('obraClienteCNPJ').value.trim();
  const nomeCliente = document.getElementById('obraClienteNome').value.trim();
  const rua         = document.getElementById('obraClienteRua').value.trim();
  const numero      = document.getElementById('obraClienteNumero').value.trim();
  const complemento = document.getElementById('obraClienteComplemento').value.trim();
  const bairro      = document.getElementById('obraClienteBairro').value.trim();

  let temErro = false;
  if (!unidade)    { _obraSetError('obraUnidade',    'Selecione a unidade.');               temErro = true; }
  if (!tipoObra)   { _obraSetError('obraTipo',       'Selecione o tipo de obra.');          temErro = true; }
  if (!resp)       { _obraSetError('obraResp',       'Selecione o field responsável.');     temErro = true; }
  if (!cod)        { _obraSetError('obraCodCliente', 'ID do cliente é obrigatório.');       temErro = true; }
  else if (!cacheClientes.find(x => x.idCliente === parseInt(cod)))
                   { _obraSetError('obraCodCliente', 'Cliente não encontrado. Verifique o ID.'); temErro = true; }
  if (!cnpj)       { _obraSetError('obraClienteCNPJ',        'CNPJ / CPF é obrigatório.');       temErro = true; }
  if (!nomeCliente){ _obraSetError('obraClienteNome',        'Nome do cliente é obrigatório.');   temErro = true; }
  if (!rua)        { _obraSetError('obraClienteRua',         'Endereço é obrigatório.');          temErro = true; }
  if (!numero)     { _obraSetError('obraClienteNumero',      'Número é obrigatório.');            temErro = true; }
  if (!complemento){ _obraSetError('obraClienteComplemento', 'Complemento é obrigatório.');       temErro = true; }
  if (!bairro)     { _obraSetError('obraClienteBairro',      'Bairro é obrigatório.');            temErro = true; }
  if (!dataInicio) { _obraSetError('obraDataInicio',  'Data de início é obrigatória.');     temErro = true; }
  if (!desc)       { _obraSetError('obraDesc',        'A descrição da obra é obrigatória.'); temErro = true; }
  if (temErro) return;

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
      _obraExibirErroApi(e);
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
    _obraSetError('produtosUsados', 'Informe ao menos um produto para a obra.'); return;
  }

  try {
    await apiFetch('/obra', 'POST', { obra, produtosUsados });
    fecharModal('modalObra');
    await Promise.all([carregarObras(), carregarProdutos()]);
    showToast(`Obra "${desc}" cadastrada!`, 'success');
  } catch (e) {
    _obraExibirErroApi(e);
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
                <button class="btn-icon edit" title="Editar quantidade"
                  onclick="abrirModalEditarProdObra(${idObra},${p.idProduto},'${_esc(p.nomeProduto)}',${p.qtdProdutosObra})">
                  <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-icon danger" title="Remover produto"
                  onclick="excluirProdutoObra(${idObra},${p.idProduto},'${_esc(p.nomeProduto)}')">
                  <i class="fa-solid fa-trash"></i>
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
  return _prodSearchHTML(`<button class="btn-icon danger" onclick="removerProdutoObraEd(this)"><i class="fa-solid fa-minus"></i></button>`);
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
const filtros   = {
  produtos: '', produtosStatus: '', obras: '', obraStatus: '', obraTipo: '', obraDe: '', obraAte: '', clientes: '', clientesStatus: ''
};
const ORDER_STATE = {
  produtos: { key: 'id', dir: 'asc' },
  obras: { key: 'id', dir: 'asc' },
  clientes: { key: 'id', dir: 'asc' },
  admins: { key: 'id', dir: 'asc' },
  responsaveis: { key: 'id', dir: 'asc' },
};

function _compararValores(a, b, asc = true) {
  if (a === b) return 0;
  if (a === null || a === undefined || a === '') return asc ? 1 : -1;
  if (b === null || b === undefined || b === '') return asc ? -1 : 1;
  if (typeof a === 'number' && typeof b === 'number') return asc ? a - b : b - a;
  const av = String(a).toLowerCase();
  const bv = String(b).toLowerCase();
  return asc ? av.localeCompare(bv) : bv.localeCompare(av);
}

function _getSortValue(item, table, key) {
  switch (table) {
    case 'produtos':
      if (key === 'id') return item.idProduto;
      if (key === 'nome') return item.nomeProduto || '';
      if (key === 'estoque') return item.qtdProduto ?? 0;
      if (key === 'status') return item.qtdProduto <= 0 ? 'Sem estoque' : 'Em estoque';
      return '';
    case 'obras':
      if (key === 'id') return item.idObra;
      if (key === 'cliente') {
        const cliente = cacheClientes.find(c => c.idCliente === item.codCliente);
        return cliente ? cliente.nomeCliente : '';
      }
      if (key === 'obra') return item.descObra || '';
      if (key === 'inicio') return item.dataInicio || '';
      if (key === 'status') return item.statusObra || '';
      return '';
    case 'clientes':
      if (key === 'id') return item.idCliente;
      if (key === 'nome') return item.nomeCliente || '';
      if (key === 'documento') return item.CNPJCPF || '';
      if (key === 'localizacao') {
        const linha1 = [item.rua, item.numero ? `nº ${item.numero}` : null].filter(Boolean).join(', ');
        const linha2 = [item.bairro, item.cidade && item.estado ? `${item.cidade}/${item.estado}` : item.cidade].filter(Boolean).join(', ');
        return [linha1, linha2].filter(Boolean).join(' | ');
      }
      if (key === 'contato') return `${item.contatoCliente || ''} ${item.telefone2 || ''} ${item.emailCliente || ''}`.trim();
      return '';
    case 'admins':
      if (key === 'id') return item.idLogin;
      if (key === 'nome') return item.nomeLogin || '';
      if (key === 'acesso') return item.email || '';
      return '';
    case 'responsaveis':
      if (key === 'id') return item.idResponsavel;
      return item.nomeResponsavel || '';
    default:
      return '';
  }
}

function ordenarLista(lista, table) {
  const state = ORDER_STATE[table];
  if (!state) return lista;
  const asc = state.dir === 'asc';
  return [...lista].sort((a, b) => {
    const aVal = _getSortValue(a, table, state.key);
    const bVal = _getSortValue(b, table, state.key);
    return _compararValores(aVal, bVal, asc);
  });
}

function ordenarTabela(table, key) {
  const state = ORDER_STATE[table];
  if (!state) return;
  if (state.key === key) {
    state.dir = state.dir === 'asc' ? 'desc' : 'asc';
  } else {
    state.key = key;
    state.dir = 'asc';
  }
  if (table === 'produtos') renderTabelaProdutos(cacheProdutos);
  if (table === 'obras') renderTabelaObras(cacheObras);
  if (table === 'clientes') renderTabelaClientes(cacheClientes);
  if (table === 'admins') renderTabelaAdmins(cacheAdmins);
  if (table === 'responsaveis') renderTabelaResponsaveis(cacheResponsaveis);
}

function atualizarIndicadoresOrdenacao(table) {
  const tableId = {
    produtos: 'tabelaProdutos', obras: 'tabelaObras', clientes: 'tabelaClientes',
    admins: 'tabelaAdmins', responsaveis: 'tabelaResponsaveis'
  }[table];
  const state = ORDER_STATE[table];
  if (!tableId || !state) return;
  document.querySelectorAll(`#${tableId} th.sortable`).forEach(th => {
    const key = th.dataset.sortKey;
    const arrow = key === state.key ? (state.dir === 'asc' ? '↑' : '↓') : '';
    const span = th.querySelector('.sort-arrow');
    if (span) span.textContent = arrow;
  });
}

async function carregarClientes() {
  try {
    const res = await apiFetch('/cliente');
    cacheClientes = res.clientes || [];
    _cacheReady.clientes = true;
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
  const q             = filtros.clientes;
  const statusFiltro  = filtros.clientesStatus;
  const clientesComObraAtiva = new Set(
    cacheObras.filter(o => o.statusObra === 'Em andamento').map(o => String(o.codCliente))
  );

  const filtradoPorStatus = statusFiltro === 'comObraAtiva'
    ? clientes.filter(c => clientesComObraAtiva.has(String(c.idCliente)))
    : statusFiltro === 'comEmail'
      ? clientes.filter(c => c.emailCliente)
      : clientes;

  const filtrado = q ? filtradoPorStatus.filter(c =>
    `${c.idCliente} ${c.nomeCliente} ${c.CNPJCPF} ${c.contatoCliente || ''} ${c.emailCliente || ''} ${c.telefone2 || ''}`.toLowerCase().includes(q)
  ) : filtradoPorStatus;

  const ordenado   = ordenarLista(filtrado, 'clientes');
  const total       = ordenado.length;
  const totalPags   = Math.ceil(total / PER_PAGE) || 1;
  if (PAG_STATE.clientes > totalPags) PAG_STATE.clientes = 1;
  const inicio      = (PAG_STATE.clientes - 1) * PER_PAGE;
  const pagina      = ordenado.slice(inicio, inicio + PER_PAGE);

  const tbody = document.getElementById('bodyClientes');
  if (!pagina.length) {
    tbody.innerHTML = _emptyState(
      'users',
      total === 0 && q ? 'Nenhum cliente encontrado' : 'Nenhum cliente cadastrado',
      total === 0 && q
        ? `A busca por "${q}" não retornou resultados.`
        : 'Comece cadastrando o primeiro cliente.',
      !q ? 'Cadastrar Cliente' : '', 'abrirModalNovoCliente()', 6
    );
  } else {
    tbody.innerHTML = pagina.map(c => {
      const nomeSafe  = _esc(c.nomeCliente);
      const loc1 = [c.rua, c.numero ? `nº ${c.numero}` : null].filter(Boolean).join(', ');
      const loc2 = [c.bairro, c.cidade && c.estado ? `${c.cidade}/${c.estado}` : c.cidade].filter(Boolean).join(', ');
      const locHtml = [loc1, loc2].filter(Boolean).join('<br>') || '—';
      const contatoHtml = [
        c.contatoCliente ? `<span class="cell-secondary"><i class="fa-solid fa-phone fa-xs" style="width:13px;opacity:.45"></i> ${c.contatoCliente}</span>` : '',
        c.telefone2      ? `<span class="cell-secondary"><i class="fa-solid fa-phone fa-xs" style="width:13px;opacity:.45"></i> ${c.telefone2}</span>` : '',
        c.emailCliente   ? `<span class="cell-secondary"><i class="fa-regular fa-envelope fa-xs" style="width:13px;opacity:.45"></i> ${c.emailCliente}</span>` : '',
      ].filter(Boolean).join('') || '<span class="cell-secondary">—</span>';
      return `
        <tr>
          <td><span class="cell-id">${c.idCliente}</span></td>
          <td><span class="cell-primary">${c.nomeCliente}</span></td>
          <td><span class="cell-secondary">${c.CNPJCPF}</span></td>
          <td style="min-width:160px"><div class="cell-stack" style="line-height:1.6">${locHtml}</div></td>
          <td><div class="cell-stack" style="gap:4px">${contatoHtml}</div></td>
          <td>${_actionMenu([
            { icon:'fa-pen',   label:'Editar',  onclick:`abrirModalEditarCliente(${c.idCliente})` },
            { divider: true },
            { icon:'fa-trash', label:'Excluir', danger:true, onclick:`deletarItem('cliente',${c.idCliente},'${nomeSafe}')` },
          ])}</td>
        </tr>`;
    }).join('');
  }
  renderPaginacao('paginacaoClientes', total, PAG_STATE.clientes, 'mudarPaginaClientes');
  atualizarIndicadoresOrdenacao('clientes');
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
    el.innerHTML = `
      <div class="alert-item">
        <div class="alert-icon" style="background:#EAF7EE;color:#2D8A4E">
          <i class="fa-solid fa-circle-check"></i>
        </div>
        <div class="alert-info">
          <strong>Tudo em ordem!</strong>
          <span>Nenhum produto abaixo do estoque mínimo.</span>
        </div>
      </div>`;
    return;
  }
  el.innerHTML = alertas.map(p => {
    const critico = p.qtdProduto <= 0;
    const info    = critico
      ? 'Produto completamente esgotado'
      : `Atual: ${p.qtdProduto} un. · Mínimo: ${p.qtdMinima} un.`;
    return `
      <div class="alert-item ${critico ? 'critical' : 'warning'}" onclick="irParaProduto(${p.idProduto})" title="Abrir no Estoque">
        <div class="alert-icon">
          <i class="fa-solid ${critico ? 'fa-box-open' : 'fa-triangle-exclamation'}"></i>
        </div>
        <div class="alert-info">
          <strong>${p.nomeProduto}</strong>
          <span>${info}</span>
        </div>
        <span class="badge ${critico ? 'badge-red' : 'badge-yellow'}">${critico ? 'Esgotado' : 'Atenção'}</span>
      </div>`;
  }).join('');
}

function renderObrasRecentes(obras) {
  const el = document.getElementById('obraRecentList');
  const recentes = [...obras].sort((a,b) => b.idObra - a.idObra).slice(0, 5);
  if (!recentes.length) {
    el.innerHTML = `<div style="padding:32px;text-align:center;color:var(--gray-400);font-size:.84rem">Nenhuma obra cadastrada.</div>`;
    return;
  }
  const statusCls = {
    'Em andamento':'em-andamento','Pausada':'pausada',
    'Concluida':'concluida','Cancelada':'cancelada','À iniciar':'a-iniciar'
  };
  el.innerHTML = recentes.map(o => {
    const cliente     = cacheClientes.find(c => c.idCliente === o.codCliente);
    const nomeCliente = cliente ? cliente.nomeCliente : (o.codCliente ? `Cliente ${o.codCliente}` : '');
    return `
      <div class="obra-item" onclick="irParaObra(${o.idObra})" title="Abrir em Obras">
        <div class="status-dot ${statusCls[o.statusObra] || 'concluida'}"></div>
        <div style="flex:1;min-width:0">
          <div class="obra-item-nome">${o.descObra || '—'}</div>
          ${nomeCliente ? `<div class="obra-item-sub">${nomeCliente}</div>` : ''}
        </div>
        ${badgeStatus(o.statusObra)}
      </div>`;
  }).join('');
}

let _obraChart = null;

async function renderGraficoObras() {
  const canvas = document.getElementById('obraChartCanvas');
  if (!canvas) return;

  let dados = [];
  try {
    const res = await apiFetch('/relatorio/grafico-produtos');
    dados = res.dados || [];
  } catch {
    dados = [];
  }

  if (_obraChart) { _obraChart.destroy(); _obraChart = null; }

  if (!dados.length) {
    canvas.closest('.chart-container').innerHTML =
      '<div class="empty-row" style="height:100%;display:flex;align-items:center;justify-content:center">Nenhum produto utilizado em obras ainda.</div>';
    return;
  }

  const truncar = (str, n) => str.length > n ? str.slice(0, n) + '…' : str;
  const labels  = dados.map(d => `${d.idProduto} — ${truncar(d.nomeProduto, 18)}`);
  const values  = dados.map(d => d.totalConsumido);

  const getBarColor = total => {
    if (total <= 400) return 'rgba(239,68,68,0.85)';      // vermelho
    if (total <= 200) return 'rgba(249,115,22,0.85)';     // laranja
    if (total <= 100) return 'rgba(37,99,235,0.85)';      // azul
    return 'rgba(16,185,129,0.85)';                        // verde acima de 400
  };

  const getBarBorderColor = total => {
    if (total <= 400) return 'rgba(185,28,28,0.95)';
    if (total <= 200) return 'rgba(194,65,12,0.95)';
    if (total <= 100) return 'rgba(30,64,175,0.95)';
    return 'rgba(5,150,105,0.95)';
  };

  const backgroundColors = values.map(getBarColor);
  const borderColors = values.map(getBarBorderColor);

  _obraChart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Qtd. consumida',
        data: values,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#fff',
          titleColor: '#1A1D2E',
          bodyColor: '#7B8196',
          borderColor: '#E2E5EB',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            title: ctx => {
              const d = dados[ctx[0].dataIndex];
              return `${d.idProduto} — ${d.nomeProduto}`;
            },
            label: ctx => {
              const d = dados[ctx.dataIndex];
              const linhas = [`Total consumido: ${d.totalConsumido} un.`, ''];
              d.obras.forEach(o => {
                linhas.push(`Obra ${o.idObra} (${o.nomeCliente}): ${o.qtd} un.`);
              });
              return linhas;
            },
          },
          displayColors: false,
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0, color: '#7B8196', font: { size: 11 } },
          grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
          border: { display: false }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 }, color: '#7B8196' },
          border: { display: false }
        }
      }
    }
  });
}

function renderNotificacoes(produtos) {
  const alertas  = produtos.filter(_produtoEmAlerta);
  const badge = document.getElementById('notifBadge');
  if (alertas.length) {
    badge.textContent = alertas.length;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
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
  if (_cacheReady.produtos) {
    document.getElementById('kpi-produtos').textContent = cacheProdutos.length;
    document.getElementById('kpi-alertas').textContent  = cacheProdutos.filter(_produtoEmAlerta).length;
  }
  if (_cacheReady.obras)    document.getElementById('kpi-obras').textContent    = cacheObras.filter(o => o.statusObra === 'Em andamento').length;
  if (_cacheReady.clientes) document.getElementById('kpi-clientes').textContent = cacheClientes.length;
  atualizarStats();
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
    'À iniciar':     '<span class="badge badge-blue">À iniciar</span>',
  };
  return map[status] || `<span class="badge badge-gray">${status}</span>`;
}

// ── Action buttons helper ──
function _actionMenu(items) {
  const btns = items.filter(it => !it.divider).map(it => {
    const cls = it.danger ? 'danger' : 'edit';
    return `<button class="btn-icon ${cls}" onclick="${it.onclick}" title="${it.label}"><i class="fa-solid ${it.icon}"></i></button>`;
  }).join('');
  return `<div class="actions">${btns}</div>`;
}

// ── Empty state helper ──
function _emptyState(icon, title, desc, btnLabel, btnOnclick, colspan) {
  const btn = btnLabel
    ? `<button class="btn btn-primary" onclick="${btnOnclick}" style="margin-top:4px">
         <i class="fa-solid fa-plus"></i> ${btnLabel}
       </button>`
    : '';
  return `<tr><td colspan="${colspan || 6}">
    <div class="empty-state">
      <div class="empty-state-icon"><i class="fa-solid ${icon}"></i></div>
      <div class="empty-state-title">${title}</div>
      <div class="empty-state-desc">${desc}</div>
      ${btn}
    </div>
  </td></tr>`;
}

// ── Page stats helper ──
function _setStatEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function atualizarStats() {
  if (_cacheReady.produtos) {
    const okCount    = cacheProdutos.filter(p => !_produtoEmAlerta(p)).length;
    const alertCount = cacheProdutos.filter(p => _produtoEmAlerta(p) && p.qtdProduto > 0).length;
    const zeroCount  = cacheProdutos.filter(p => p.qtdProduto <= 0).length;
    _setStatEl('stat-prod-total', cacheProdutos.length);
    _setStatEl('stat-prod-ok',    okCount);
    _setStatEl('stat-prod-alert', alertCount);
    _setStatEl('stat-prod-zero',  zeroCount);
  }
  if (_cacheReady.obras) {
    _setStatEl('stat-obra-total',     cacheObras.length);
    _setStatEl('stat-obra-ainiciar',  cacheObras.filter(o => o.statusObra === 'À iniciar').length);
    _setStatEl('stat-obra-andamento', cacheObras.filter(o => o.statusObra === 'Em andamento').length);
    _setStatEl('stat-obra-pausada',   cacheObras.filter(o => o.statusObra === 'Pausada').length);
    _setStatEl('stat-obra-concluida', cacheObras.filter(o => o.statusObra === 'Concluida').length);
  }
  if (_cacheReady.clientes) {
    _setStatEl('stat-cli-total', cacheClientes.length);
    _setStatEl('stat-cli-email', cacheClientes.filter(c => c.emailCliente).length);
    if (_cacheReady.obras) {
      const clientesComObra = new Set(
        cacheObras.filter(o => o.statusObra === 'Em andamento').map(o => o.codCliente)
      );
      _setStatEl('stat-cli-ativos', clientesComObra.size);
    }
  }
  if (_cacheReady.admins)       _setStatEl('stat-admin-total', cacheAdmins.length);
  if (_cacheReady.responsaveis) _setStatEl('stat-resp-total',  cacheResponsaveis.length);
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


function filtrarProdutos(q) {
  filtros.produtos   = q.toLowerCase();
  PAG_STATE.produtos = 1;
  renderTabelaProdutos(cacheProdutos);
}

function filtrarProdutosStatus(status) {
  filtros.produtosStatus = status || '';
  PAG_STATE.produtos = 1;
  _realcarCartoesFiltro('produtos', filtros.produtosStatus);
  renderTabelaProdutos(cacheProdutos);
}

function filtrarClientesStatus(status) {
  filtros.clientesStatus = status || '';
  PAG_STATE.clientes = 1;
  _realcarCartoesFiltro('clientes', filtros.clientesStatus);
  renderTabelaClientes(cacheClientes);
}

function filtrarObras() {
  filtros.obraTipo   = (document.getElementById('obraFiltroTipo')?.value   || '').toLowerCase().trim();
  filtros.obraStatus = (document.getElementById('obraFiltroStatus')?.value || '');
  filtros.obraDe     = _brParaIso(document.getElementById('obraFiltroDe')?.value  || '');
  filtros.obraAte    = _brParaIso(document.getElementById('obraFiltroAte')?.value || '');
  PAG_STATE.obras    = 1;
  renderTabelaObras(cacheObras);
}

function _realcarCartoesFiltro(grupo, valor) {
  document.querySelectorAll(`.stat-item[data-filter-group="${grupo}"]`).forEach(el => {
    el.classList.toggle('active', el.dataset.filterValue === (valor || ''));
  });
}

function filtrarClientes(q) {
  filtros.clientes   = q.toLowerCase();
  PAG_STATE.clientes = 1;
  renderTabelaClientes(cacheClientes);
}

function filtrarStatusObra(status) {
  filtros.obraStatus = status;
  const select = document.getElementById('obraFiltroStatus');
  if (select) select.value = status || '';
  PAG_STATE.obras = 1;
  renderTabelaObras(cacheObras);
}

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
    _cacheReady.admins = true;
    renderTabelaAdmins(cacheAdmins);
    atualizarStats();
  } catch (e) {
    document.getElementById('bodyAdmins').innerHTML =
      `<tr><td colspan="4" class="empty-row">Erro ao carregar administradores: ${e.message}</td></tr>`;
  }
}

function renderTabelaAdmins(admins) {
  const tbody = document.getElementById('bodyAdmins');
  const ordenado = ordenarLista(admins, 'admins');
  if (!ordenado.length) {
    tbody.innerHTML = _emptyState(
      'user-shield', 'Nenhum administrador cadastrado',
      'Cadastre um administrador para gerenciar o sistema.',
      'Novo Administrador', 'abrirModalNovoAdmin()', 4
    );
    return;
  }
  tbody.innerHTML = ordenado.map(a => {
    const nomeSafe = _esc(a.nomeLogin);
    return `
      <tr>
        <td><span class="cell-id">${a.idLogin}</span></td>
        <td>
          <div class="cell-stack">
            <span class="cell-primary">${a.nomeLogin}</span>
          </div>
        </td>
        <td><span class="cell-secondary">${a.email}</span></td>
        <td>${_actionMenu([
          { icon:'fa-pen',   label:'Editar',  onclick:`abrirModalEditarAdmin(${a.idLogin})` },
          { divider: true },
          { icon:'fa-trash', label:'Excluir', danger:true, onclick:`deletarItem('admin',${a.idLogin},'${nomeSafe}')` },
        ])}</td>
      </tr>`;
  }).join('');
  atualizarIndicadoresOrdenacao('admins');
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

function recarregarAba() {
  const pagina = document.querySelector('.page.active');
  if (pagina) {
    sessionStorage.setItem('abaAtual', pagina.id.replace('page-', ''));
  }

  const snap = {};
  [
    'kpi-produtos', 'kpi-obras', 'kpi-clientes', 'kpi-alertas',
    'stat-prod-total', 'stat-prod-ok', 'stat-prod-alert', 'stat-prod-zero',
    'stat-obra-total', 'stat-obra-ainiciar', 'stat-obra-andamento', 'stat-obra-pausada', 'stat-obra-concluida',
    'stat-cli-total', 'stat-cli-ativos', 'stat-cli-email',
    'stat-admin-total', 'stat-resp-total',
    'bodyProdutos', 'bodyObras', 'bodyClientes', 'bodyAdmins', 'bodyResponsaveis',
    'alertList', 'obraRecentList',
    'paginacaoProdutos', 'paginacaoObras', 'paginacaoClientes',
  ].forEach(id => {
    const el = document.getElementById(id);
    if (el) snap[id] = el.innerHTML;
  });
  sessionStorage.setItem('domSnapshot', JSON.stringify(snap));

  window.location.reload();
}

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


function irParaProduto(idProduto) {
  navegarPara('estoque');
  if (_cacheReady.produtos) { abrirModalEditarProduto(idProduto); return; }
  const t = setInterval(() => {
    if (_cacheReady.produtos) { clearInterval(t); abrirModalEditarProduto(idProduto); }
  }, 80);
}

function irParaObra(idObra) {
  navegarPara('obras');
  if (_cacheReady.obras) { abrirModalEditarObra(idObra); return; }
  const t = setInterval(() => {
    if (_cacheReady.obras) { clearInterval(t); abrirModalEditarObra(idObra); }
  }, 80);
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
    _cacheReady.responsaveis = true;
    renderTabelaResponsaveis(cacheResponsaveis);
    popularSelectResponsaveis();
    atualizarStats();
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
  const ordenado = ordenarLista(lista, 'responsaveis');
  if (!ordenado.length) {
    tbody.innerHTML = _emptyState(
      'id-badge', 'Nenhum responsável cadastrado',
      'Cadastre os fields responsáveis pelas obras.',
      'Novo Responsável', 'abrirModalNovoResponsavel()', 3
    );
    return;
  }
  tbody.innerHTML = ordenado.map(r => {
    const nomeSafe = _esc(r.nomeResponsavel);
    return `
      <tr>
        <td><span class="cell-id">${r.idResponsavel}</span></td>
        <td><span class="cell-primary">${r.nomeResponsavel}</span></td>
        <td>${_actionMenu([
          { icon:'fa-pen',   label:'Editar',  onclick:`abrirModalEditarResponsavel(${r.idResponsavel})` },
          { divider: true },
          { icon:'fa-trash', label:'Excluir', danger:true, onclick:`confirmarExcluirResponsavel(${r.idResponsavel},'${nomeSafe}')` },
        ])}</td>
      </tr>`;
  }).join('');
  atualizarIndicadoresOrdenacao('responsaveis');
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


function excluirProdutoObra(idObra, idProduto, nomeProduto) {
  fecharModal('modalVerObra');
  document.getElementById('confirmarMsg').textContent =
    `Tem certeza que deseja remover "${nomeProduto}" desta obra?`;
  document.getElementById('btnConfirmarExcluir').onclick = () =>
    confirmarExcluirProdObra(idObra, idProduto);
  abrirModal('modalConfirmar');
}

async function confirmarExcluirProdObra(idObra, idProduto) {
  fecharModal('modalConfirmar');
  try {
    await apiFetch(`/obra/${idObra}/produto/${idProduto}`, 'DELETE');
    showToast('Produto removido da obra.', 'success');
    await Promise.all([carregarObras(), carregarProdutos()]);
    verProdutosObra(idObra);
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
