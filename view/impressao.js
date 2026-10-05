// Comum às páginas imprimíveis da obra (relatorio-obra, produtos-obra e
// produtos-obra-grande): busca a obra do ?id= da URL e preenche os campos.

function _txt(id, valor) {
  if (valor !== null && valor !== undefined && valor !== '') {
    document.getElementById(id).textContent = valor;
  }
}

// "2026-07-10" ou "2026-07-10 00:00:00" → "10/07/2026"
function _fmtData(s) {
  if (!s) return '';
  const d = String(s).split(' ')[0].split('T')[0].split('-');
  return d.length === 3 ? `${d[2]}/${d[1]}/${d[0]}` : s;
}

// Chama preencher(obra, cliente) com os dados da obra da URL. cliente vem
// pela rota da própria obra, que todo cargo com acesso à obra pode ler.
async function carregarObraDaUrl(tituloDocumento, preencher) {
  const token  = sessionStorage.getItem('token');
  const idObra = new URLSearchParams(location.search).get('id');

  const aviso = msg => { document.body.innerHTML = `<p style="color:#fff;padding:20px">${msg}</p>`; };
  if (!token)  return aviso('Sessão expirada. Faça login novamente.');
  if (!idObra) return aviso('Obra não informada.');

  const api = async endpoint => {
    const res = await fetch(endpoint, { headers: { 'Authorization': `Bearer ${token}` } });
    if (!res.ok) throw new Error(`Erro ${res.status} em ${endpoint}`);
    return res.json();
  };

  try {
    const { obra } = await api(`/obra/${idObra}`);
    document.title = `${tituloDocumento} ${obra.idObra}`;
    const cliente = obra.codCliente ? (await api(`/obra/${idObra}/cliente`)).cliente : null;
    preencher(obra, cliente);
  } catch (e) {
    alert('Erro ao carregar os dados da obra: ' + e.message);
  }
}
