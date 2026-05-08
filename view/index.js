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

document.addEventListener('DOMContentLoaded', () => {
  verificarAutenticacao();
  carregarAdministrador();
  carregarTodos();
});

async function carregarTodos() {
  await Promise.allSettled([carregarProdutos(), carregarObras(), carregarClientes()]);
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
    renderGraficoEstoque(cacheProdutos);
    renderNotificacoes(cacheProdutos);
    atualizarKPI();
  } catch (e) {
    document.getElementById('bodyProdutos').innerHTML =
      `<tr><td colspan="6" class="empty-row">Erro ao carregar produtos: ${e.message}</td></tr>`;
    console.error('carregarProdutos:', e);
  }
}

function renderTabelaProdutos(produtos) {
  const tbody = document.getElementById('bodyProdutos');
  if (!produtos.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Nenhum produto cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = produtos.map(p => {
    const { cls, label } = statusEstoque(p);
    return `
      <tr>
        <td>${String(p.idProduto).padStart(3,'0')}</td>
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
      `<tr><td colspan="8" class="empty-row">Erro ao carregar obras: ${e.message}</td></tr>`;
    console.error('carregarObras:', e);
  }
}

function renderTabelaObras(obras) {
  const tbody = document.getElementById('bodyObras');
  if (!obras.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="empty-row">Nenhuma obra cadastrada.</td></tr>`;
    return;
  }
  tbody.innerHTML = obras.map(o => {
    const badge      = badgeStatus(o.statusObra);
    const fmtData    = d => d ? new Date(d + 'T00:00:00').toLocaleDateString('pt-BR') : '—';
    const cliente    = cacheClientes.find(c => c.idCliente === o.codCliente);
    const nomeCliente = cliente ? cliente.nomeCliente : `#${o.codCliente}`;
    return `
      <tr>
        <td>${String(o.idObra).padStart(3,'0')}</td>
        <td>${o.descObra}</td>
        <td>${o.respObra || '—'}</td>
        <td>${nomeCliente}</td>
        <td>${fmtData(o.dataInicio)}</td>
        <td>${fmtData(o.dataFim)}</td>
        <td>${badge}</td>
        <td class="actions">
          <button class="btn-icon" title="Ver produtos" onclick="verProdutosObra(${o.idObra})">
            <i class="fa-solid fa-eye"></i>
          </button>
          <button class="btn-icon" title="Editar" onclick="abrirModalEditarObra(${o.idObra})">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="btn-icon danger" title="Excluir" onclick="deletarItem('obra', ${o.idObra}, '${o.descObra}')">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>`;
  }).join('');
}

function _novaProdutoObraRow() {
  return `
    <div class="produto-obra-row">
      <input type="number" placeholder="ID" class="prod-id-input" min="1"
        oninput="buscarProdutoObra(this)" />
      <input type="text" placeholder="Nome do produto" class="prod-nome-input" readonly />
      <input type="text" placeholder="Estoque" class="prod-estoque-input" readonly />
      <input type="number" placeholder="Qtd. a usar" class="prod-qtd-input" min="1" />
      <button class="btn-icon danger" onclick="removerProdutoObra(this)">
        <i class="fa-solid fa-minus"></i>
      </button>
    </div>`;
}

function abrirModalNovaObra() {
  document.getElementById('obraIdEdicao').value         = '';
  document.getElementById('obraStatus').value           = 'Em andamento';
  document.getElementById('obraResp').value             = '';
  document.getElementById('obraDataInicio').value       = '';
  document.getElementById('obraDataFim').value          = '';
  document.getElementById('obraCodCliente').value       = '';
  document.getElementById('obraClienteNome').value      = '';
  document.getElementById('obraClienteEndereco').value  = '';
  document.getElementById('obraDesc').value             = '';
  document.getElementById('produtosObraList').innerHTML = _novaProdutoObraRow();
  document.getElementById('obraSecaoProdutos').classList.remove('hidden');
  document.getElementById('obraSecaoProdutosVer').classList.add('hidden');
  document.getElementById('modalObraTitle').innerHTML =
    '<i class="fa-solid fa-hard-hat"></i> Nova Obra';
  abrirModal('modalObra');
}

function abrirModalEditarObra(idObra) {
  const o = cacheObras.find(x => x.idObra == idObra);
  if (!o) { showToast('Obra não encontrada.', 'error'); return; }
  document.getElementById('obraIdEdicao').value        = o.idObra;
  document.getElementById('obraStatus').value          = o.statusObra;
  document.getElementById('obraResp').value            = o.respObra || '';
  document.getElementById('obraDataInicio').value      = o.dataInicio || '';
  document.getElementById('obraDataFim').value         = o.dataFim || '';
  document.getElementById('obraCodCliente').value      = o.codCliente;
  document.getElementById('obraDesc').value            = o.descObra || '';
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
  const id    = parseInt(input.value);
  const nomeEl = document.getElementById('obraClienteNome');
  const endEl  = document.getElementById('obraClienteEndereco');
  if (!id || id <= 0) { nomeEl.value = ''; endEl.value = ''; return; }
  const c = cacheClientes.find(x => x.idCliente === id);
  if (!c) {
    nomeEl.value = 'Cliente não encontrado';
    endEl.value  = '';
    return;
  }
  nomeEl.value = c.nomeCliente;
  endEl.value  = _enderecoCliente(c);
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
  const dataInicio = document.getElementById('obraDataInicio').value.trim();
  const dataFim    = document.getElementById('obraDataFim').value.trim() || null;
  const cod        = document.getElementById('obraCodCliente').value.trim();
  const desc       = document.getElementById('obraDesc').value.trim();

  if (!resp)       { showToast('Selecione o responsável.', 'error'); return; }
  if (!cod)        { showToast('ID do cliente é obrigatório.', 'error'); return; }
  if (!dataInicio) { showToast('Data de início é obrigatória.', 'error'); return; }
  if (!desc)       { showToast('Descrição da obra é obrigatória.', 'error'); return; }

  const clienteOk = cacheClientes.find(x => x.idCliente === parseInt(cod));
  if (!clienteOk) { showToast('Cliente não encontrado. Verifique o ID.', 'error'); return; }

  const obra = { descObra: desc, respObra: resp, codCliente: parseInt(cod), dataInicio, dataFim, statusObra: status };

  // Modo edição — PUT completo + produtos novos opcionais
  if (idEdicao) {
    const produtosNovos = [];
    document.querySelectorAll('#produtosObraEdList .produto-obra-row').forEach(row => {
      const pid = row.querySelector('.prod-id-input').value.trim();
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
    const pid = row.querySelector('.prod-id-input').value.trim();
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
        Produtos vinculados à obra <strong>#${String(idObra).padStart(3,'0')}</strong>:
      </p>
      <table class="data-table">
        <thead><tr><th>ID Produto</th><th>Nome</th><th>Quantidade Utilizada</th></tr></thead>
        <tbody>
          ${produtos.map(p => `
            <tr>
              <td>${String(p.idProduto).padStart(3,'0')}</td>
              <td>${p.nomeProduto || '—'}</td>
              <td>${p.qtdProdutosObra}</td>
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
  return `
    <div class="produto-obra-row">
      <input type="number" placeholder="ID" class="prod-id-input" min="1"
        oninput="buscarProdutoObra(this)" />
      <input type="text" placeholder="Nome do produto" class="prod-nome-input" readonly />
      <input type="text" placeholder="Estoque" class="prod-estoque-input" readonly />
      <input type="number" placeholder="Qtd. a usar" class="prod-qtd-input" min="1" />
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
  return [c.rua, c.numero ? `nº ${c.numero}` : null, c.bairro, c.cidade && c.estado ? `${c.cidade}/${c.estado}` : c.cidade]
    .filter(Boolean).join(', ') || '—';
}

function renderTabelaClientes(clientes) {
  const tbody = document.getElementById('bodyClientes');
  if (!clientes.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Nenhum cliente cadastrado.</td></tr>`;
    return;
  }
  tbody.innerHTML = clientes.map(c => `
    <tr>
      <td>${String(c.idCliente).padStart(3,'0')}</td>
      <td>${c.nomeCliente}</td>
      <td>${c.CNPJCPF}</td>
      <td>${_enderecoCliente(c)}</td>
      <td>${c.contatoCliente || '—'}</td>
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

function _limparModalCliente() {
  ['cliIdEdicao','cliNome','cliCpfCnpj','cliContato',
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
  document.getElementById('cliContato').value     = c.contatoCliente || '';
  document.getElementById('cliCep').value         = c.cep           || '';
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

const endpointExclusao = { produto: '/produto', obra: '/obra', cliente: '/cliente' };

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
  } catch (e) {
    showToast(`Erro ao excluir: ${e.message}`, 'error');
  }
}


// ══════════════════════════════════════════════════
// DASHBOARD — renders
// ══════════════════════════════════════════════════

function _produtoEmAlerta(p) {
  return p.qtdProduto <= 0 || (p.qtdMinima > 0 && p.qtdProduto < p.qtdMinima);
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

function renderGraficoEstoque(produtos) {
  const el = document.getElementById('barChart');
  const lista = [...produtos].sort((a,b) => a.qtdProduto - b.qtdProduto).slice(0, 5);
  if (!lista.length) { el.innerHTML = '<div class="empty-row">Nenhum produto cadastrado.</div>'; return; }
  const max = Math.max(...lista.map(p => p.qtdProduto), 1);
  el.innerHTML = lista.map(p => {
    const pct = Math.round((p.qtdProduto / max) * 100);
    const cls = p.qtdProduto <= 0 ? 'critical'
              : (p.qtdMinima > 0 && p.qtdProduto < p.qtdMinima) ? 'warning'
              : 'ok';
    return `
      <div class="bar-row">
        <span class="bar-label">${p.nomeProduto}</span>
        <div class="bar-track"><div class="bar-fill ${cls}" style="width:${pct}%"></div></div>
        <span class="bar-val">${p.qtdProduto}</span>
      </div>`;
  }).join('');
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
  if (p.qtdMinima > 0 && p.qtdProduto < p.qtdMinima)
    return { cls: 'warning',  label: '<span class="badge badge-yellow">Atenção</span>' };
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
    const labels = { dashboard: 'Dashboard', estoque: 'Estoque / Produtos', obras: 'Obras / Projetos', clientes: 'Clientes' };
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

function filtrarTabela(tableId, query) {
  const q = query.toLowerCase();
  document.querySelectorAll(`#${tableId} tbody tr`).forEach(row => {
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}

function filtrarStatus(status) {
  document.querySelectorAll('#tabelaObras tbody tr').forEach(row => {
    if (!status) { row.style.display = ''; return; }
    const badge = row.querySelector('.badge');
    row.style.display = (badge && badge.textContent.toLowerCase().includes(status.toLowerCase())) ? '' : 'none';
  });
}

document.getElementById('globalSearch').addEventListener('input', function () {
  const q = this.value;
  filtrarTabela('tabelaProdutos', q);
  filtrarTabela('tabelaObras', q);
  filtrarTabela('tabelaClientes', q);
});

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
// LOGOUT
// ══════════════════════════════════════════════════

function logout() {
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('nomeLogin');
  showToast('Sessão encerrada. Redirecionando...', 'info');
  setTimeout(() => { window.location.href = '/'; }, 1200);
}
