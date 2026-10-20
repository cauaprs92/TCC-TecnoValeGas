# Handoff — TecnoValeGas

---

# Sessão 30/07/2026 — Responsividade para celular

## Objetivo
Deixar o sistema utilizável no celular e melhorar a visualização. O front-end era
desktop-only: sidebar fixa de 240px, tabelas de 5–7 colunas, modais grandes e
toolbars em linha única, com apenas 3 media queries pontuais.

**Escopo aprovado:** tópicos 1 a 10 (fundação, sidebar, topbar, toolbars, KPIs,
tabelas, modais, dashboard, toasts, login).
**Fora do escopo por decisão do usuário:** as páginas A4 de impressão
(`relatorio-obra.html`, `produtos-obra.html`, `produtos-obra-grande.html`)
seguem intactas.

## Status: concluído e no ar

Tudo commitado e com push em `main`. Um commit por etapa:

| Commit | O que entrou |
|---|---|
| `59971da` | Sidebar vira gaveta deslizante no celular |
| `2983c6e` | Topbar, cabeçalhos e barras de filtro responsivos |
| `76e9128` | KPIs e barras de estatísticas em grade |
| `de54c97` | Tabelas viram cartões empilhados |
| `e29f7f8` | Modais em tela cheia e formulários em coluna única |
| `76b2a31` | Dashboard e gráficos adaptados |
| `5c1c0d1` | Toasts, notificações e dropdowns dentro da tela |
| `e468553` | Tela de login responsiva |
| `c4642e2` | Correções: linhas de produto e abas da obra |
| `071b9f5` | Acabamento do dashboard e cabeçalho |
| `ebd0906` | Histórico responsivo e barra de filtros sem estourar a tela |

## Como está estruturado

Todo o CSS responsivo está num bloco único no fim de `view/index.css`, a partir do
comentário `RESPONSIVO — TABLET E CELULAR`. Breakpoints: **1200 / 900 / 820 / 768 /
700 / 600 / 460 / 420px**.

- **900px** — sidebar vira gaveta (`.sidebar.open` + `body.sidebar-open` + `.sidebar-backdrop`).
  JS em `view/index.js`: `alternarSidebar()`, `abrirSidebarMobile()`, `fecharSidebarMobile()`.
  Fecha no backdrop, no ESC, ao escolher item do menu e ao voltar para o desktop (resize).
- **820px** — tabelas viram cartões. `thead` some, cada `<tr>` é um cartão com
  `#ID + nome` no topo, `rótulo → valor` no meio e ações no pé.
- **600px** — modais em tela cheia; `.modal-small` (confirmação, editar quantidade)
  continua centralizado de propósito.

### Detalhe importante: rótulos dos cartões
`_marcarCelulasTabela()` em `view/index.js` copia os textos do `<thead>` para
`data-label` de cada `<td>`, marca `data-col` e a classe `td-actions`. Roda via
`MutationObserver` nos 7 `tbody` (lista `_TABELAS_CARTAO`), então **nenhuma das
funções de render precisou ser alterada**. Tabela nova entra no modo cartão só de
ser adicionada à lista. As tabelas geradas dentro de modais (`verProdutosObra`,
`_renderHistoricoObra`) chamam a função direto após montar o HTML.

Linhas com `colspan` (carregando / estado vazio) recebem a classe `row-plain` e
ficam fora do modo cartão.

## Regra que causou 3 bugs — vale lembrar

**Flex item tem `min-width: auto` por padrão e não encolhe abaixo do min-content
dos filhos.** Um `<input>` sem `size` tem largura intrínseca de ~186px e um
`<select>` tem a largura da maior opção. Isso apareceu em três lugares:

1. `.main-content` (flex item do `body`) esticava **a página inteira** para 426px
   por causa da faixa de datas do Histórico → resolvido com `min-width: 0` na
   regra base, em `view/index.css`.
2. Wrappers de filtro (`.search-inline`, `.select-filter`, `.filtro-periodo`,
   `.filtro-group`) esticavam a barra de filtros → `min-width: 0` no bloco ≤700px.
   Isso valia também para a aba Obras, que usa a mesma faixa de datas.
3. As linhas de produto/serviço dos modais quebravam um campo por linha →
   `min-width: 0` em `.produto-obra-row input, select`.

Se aparecer overflow horizontal novo, esse é o primeiro suspeito.

## Como conferir o layout sem subir o app

O app precisa do MySQL remoto (variáveis de ambiente) e não há Playwright no
ambiente. A conferência foi feita com **Edge headless + screenshot**:

```
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new \
  --disable-gpu --no-sandbox --user-data-dir=<tmp> --hide-scrollbars \
  --allow-file-access-from-files --virtual-time-budget=6000 \
  --window-size=420,1400 --screenshot=<saida.png> <url>
```

Dois detalhes:
- **`--window-size` não desce abaixo de ~500px** (pedir 390 dá viewport de 496).
  Para testar largura de celular, aponte o screenshot para uma página wrapper com
  `<iframe src="mock.html" width="390" height="1400">` — o iframe cria viewport
  real de 390px.
- Os mocks foram montados extraindo o markup real de `view/index.html` com Python
  (fatiando pelos comentários `<!-- ===== MODAL: X ===== -->`) e linkando
  `view/index.css` por `file:///`. Markup inventado esconde bugs de layout.

Telas conferidas a 390px: Estoque (cartões), Obras (7 colunas), Histórico,
Dashboard, modal de Obra (topo e rolado até Produtos), gaveta aberta e Login.
Desktop reconferido a 1280px sem regressão.

## Pendências para amanhã

1. **Nada em aberto do escopo aprovado** — os 10 tópicos foram entregues.
2. **Páginas A4 no celular** (opcional, ficou de fora): encaixar a folha na
   largura da tela com um wrapper em escala, sem afetar a impressão.
3. **`install.py` tem alteração local não commitada** (1 linha) — decidir se entra
   ou se descarta.
4. **Este `handoff.md` não está no git** (não está no `.gitignore`, só nunca foi
   adicionado). Atenção: a seção da sessão anterior tem a senha do banco em texto
   puro — se for commitar, tirar a senha antes.
5. Vale testar num aparelho real, principalmente: teclado virtual abrindo sobre o
   dropdown de busca de produto, e o modal de Obra em tela cheia no iOS.

## Arquivos modificados nesta sessão

| Arquivo | O que mudou |
|---|---|
| `view/index.css` | Bloco responsivo completo no fim + `min-width: 0` em `.main-content` |
| `view/index.js` | Gaveta da sidebar, `_marcarCelulasTabela` e `_iniciarTabelasResponsivas` |
| `view/index.html` | `.sidebar-backdrop`, classe `.page-header-actions` |
| `view/login.html` | Media queries de 1024 / 768 / 380px |

---

# Sessão anterior — Abas de Obra e relatório em PDF

## O que foi feito

### 1. Senha do banco de dados
- Adicionada a senha `Mateus2009#` em `install.py` (estava vazia).
- `src/dao/conexao.py` já tinha a senha correta.

### 2. Padronização de fontes nas abas de Obras
- Os botões das abas **Projeto**, **Documentos e Formulários** e **Histórico** agora usam a mesma fonte dos labels dos campos do formulário.
- Arquivo: `view/index.css` → classe `.obra-tab`
  - `font-size: .78rem`, `font-weight: 600`, `color: var(--gray-700)`, `text-transform: uppercase`, `letter-spacing: .4px`

### 3. Estrutura de abas no modal de Obras
- O conteúdo do formulário foi envolvido em `<div id="abaProjeto" class="obra-tab-content active">`.
- Criadas as divs vazias: `abaDocumentos` e `abaHistorico`.
- Funções JS adicionadas em `view/index.js`:
  - `trocarAbaObra(e, abaId)` — alterna a aba ativa.
  - `_resetAbasObra()` — chamada ao abrir o modal (nova obra e editar obra) para sempre iniciar na aba Projeto.

### 4. Botão "Relatório de Obra" em Documentos e Formulários
- Botão adicionado no HTML (`view/index.html`) dentro de `#abaDocumentos`.
- Função `gerarRelatorioObra()` em `view/index.js`:
  - Verifica se a obra está salva (precisa de ID).
  - Faz fetch autenticado com JWT para `GET /obra/<id>/relatorio`.
  - Recebe o PDF como blob e abre em nova aba (sem forçar download).

### 5. Preenchimento automático do PDF (FOLHA DE ROSTO 2.pdf)
- **Bibliotecas instaladas:** `pypdf`, `reportlab`, `pillow`.
- **Rota backend:** `GET /obra/<idObra>/relatorio` em `src/routers/obraRoteador.py`.
  - Faz JOIN entre `obras` e `clientes` para buscar todos os dados necessários.
  - Usa `reportlab` para criar overlay de texto sobre o PDF original.
  - Usa `pypdf` para mesclar overlay com `uploads/FOLHA DE ROSTO 2.pdf`.
  - Retorna o PDF preenchido inline (navegador/OS decide como abrir).

#### Campos preenchidos no PDF:
| Campo no PDF         | Fonte                         | Observação                            |
|----------------------|-------------------------------|---------------------------------------|
| FIELD: SA-           | `respObra`                    | Nome do field                         |
| CÓD.CLIENTE          | `codCliente`                  |                                       |
| DATA INÍCIO          | `dataInicio`                  | Formato dd/mm/aaaa                    |
| TÉRMINO              | `dataFim`                     | Formato dd/mm/aaaa                    |
| ENDEREÇO             | `clientes.rua`                |                                       |
| Nº                   | `clientes.numero`             |                                       |
| BAIRRO               | `clientes.bairro`             |                                       |
| CEP                  | `clientes.cep`                |                                       |
| CIDADE               | `clientes.cidade`             |                                       |
| CNPJ ou CPF          | `clientes.CNPJCPF`            | Auto-detecta: >11 dígitos = CNPJ      |
| CONTATO              | `clientes.contatoCliente`     |                                       |
| TELEFONE             | `celular1`                    |                                       |
| DESCRIÇÃO DA OBRA    | `descObra`                    | Quebra de linha automática (3 linhas) |
| TÉCNICO RESPONSÁVEL  | `respObra`                    | Rodapé da página                      |
| ESTADO               | *(não preenchido)*            | "SÃO PAULO" pré-impresso fica como está|
| CLIENTE              | *(não preenchido ainda)*      | Ver próximos passos                   |

## Próximos passos dessa sessão (ainda válidos)

### 1. Campo "Cliente" no formulário de Obras — PRIORITÁRIO
- O campo `CLIENTE:` no PDF não é preenchido ainda pois o formulário de obra ainda não tem um campo dedicado ao nome do cliente para exibição no relatório.
- **O que fazer:** Adicionar um campo (provavelmente `nomeCliente` visível no form, vindo do lookup de `codCliente`) e depois incluí-lo no preenchimento do PDF em `gerar_relatorio_obra`.
- O nome do cliente virá de `clientes.nomeCliente` (já disponível via JOIN no backend).

### 2. Aba Histórico de Obras
- ~~A `abaHistorico` está em branco.~~ Já implementada (`_renderHistoricoObra`).

### 3. Aba Documentos e Formulários — outros documentos
- Já tem Relatório de Obra, Produtos Obra e Produtos Obra Grande.
- Definir se haverá upload de arquivos, outros PDFs, etc.

### 4. Ajuste fino de coordenadas do PDF (se necessário)
- As coordenadas foram calibradas com base na extração de texto do PDF.
- Se algum campo ainda estiver deslocado após testes, ajustar os valores `x, y` em `gerar_relatorio_obra` no arquivo `src/routers/obraRoteador.py`.
