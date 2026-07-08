# Handoff Backend → Frontend — Módulo de Serviços + Valor da Obra

## Contexto geral

Foi criado um módulo de **Serviços** (com preço fixo e receita de produtos) que pode ser vinculado a uma **Obra**. Quando uma obra é marcada como **"Concluida"**, o backend calcula automaticamente o valor total da obra somando o preço dos serviços vinculados a ela, e salva isso em `obras.valorObra`.

Todo o backend já está pronto e testado. Este documento existe para o frontend consumir essas APIs corretamente — **em especial há uma regra de negócio (marcada como ⚠️ CRÍTICO abaixo) que, se não for seguida, quebra o cálculo do valor da obra silenciosamente.**

---

## 1. Modelo de dados (para entender o domínio)

```
servicos            → catálogo de serviços (nome + preço fixo)
servicoProdutos     → "receita" de um serviço: quais produtos ele consome do estoque e em que quantidade
obraServicos        → vínculo N:N entre obras e serviços (um serviço vinculado a uma obra)
produtosObras       → produtos AVULSOS vinculados diretamente a uma obra (sem passar por um serviço)
obras.valorObra     → DECIMAL(10,2), NULL por padrão. Só é preenchido quando a obra está "Concluida".
```

**Regra de negócio importante:** `valorObra` = soma do `precoServico` de todos os serviços vinculados via `obraServicos`. Produtos avulsos (`produtosObras`) **não entram nesse valor** — eles só afetam estoque, não têm preço na obra.

Uma obra pode ter produtos avulsos, serviços, ou os dois — mas precisa ter pelo menos um dos dois para ser cadastrada.

---

## 2. Ciclo de vida do `valorObra` (o que o front precisa exibir)

| Situação                                          | valorObra              |
|----------------------------------------------------|-------------------------|
| Obra recém-criada / em qualquer status ≠ Concluida  | `null`                  |
| Obra muda para `"Concluida"` com serviços vinculados | soma dos preços dos serviços |
| Obra muda para `"Concluida"` sem nenhum serviço      | `0.00` (não é `null`)   |
| Obra que estava `"Concluida"` muda para outro status | volta a `null`          |

Ou seja: **`valorObra == null` significa "obra ainda não fechada / valor não é definitivo"**. O front deve tratar isso explicitamente na UI (ex: mostrar "—" ou "Valor definido ao concluir a obra" em vez de "R$ 0,00" quando for `null`).

Status válidos da obra (exatamente essas strings, com esse acento/grafia):
```
"À iniciar", "Em andamento", "Concluida", "Cancelada", "Pausada"
```
(repare que "Concluida" não tem acento)

---

## 3. ⚠️ CRÍTICO — Como mudar o status da obra

Existem **duas rotas diferentes** que tocam na obra, e elas **não são intercambiáveis**:

- `PATCH /obra/<idObra>/status` → **use sempre esta para mudar o status.** É a única rota que recalcula `valorObra` corretamente (soma os serviços ao concluir, zera ao reverter).
- `PUT /obra/<idObra>` → edita os dados gerais da obra (descrição, datas, responsável, etc.). Esse endpoint **também aceita um campo `statusObra` no corpo**, mas se o front mandar um `statusObra` diferente do atual por aqui, o status muda só na coluna, **sem recalcular `valorObra`** — isso deixaria o valor da obra desincronizado do status real.

**Regra para o front:** o campo de status na tela de edição de obra deve ser somente leitura (ou desabilitado), e a troca de status deve acontecer só pelo botão/ação dedicada que chama `PATCH /obra/<idObra>/status`. Nunca envie um `statusObra` alterado dentro do payload do `PUT /obra/<idObra>`.

---

## 4. Endpoints — Obras

Todas as rotas exigem header `Authorization: Bearer <token>` (JWT do login).

### `POST /obra` — cadastrar obra
```json
{
  "obra": {
    "codCliente": 1,
    "descObra": "Instalação de gás residencial",
    "dataInicio": "2026-01-10",
    "dataFim": null,
    "statusObra": "Em andamento",
    "respObra": "Carlos",
    "obsObra": null,
    "orientacaoObra": null,
    "tipoObra": null,
    "fieldObra": null,
    "unidadeObra": null,
    "emailContato": null,
    "celular1": null,
    "celular2": null
  },
  "produtosUsados": [
    { "idProduto": 1, "quantidade": 5 }
  ],
  "servicosVinculados": [1, 5]
}
```
- `produtosUsados` e `servicosVinculados` são opcionais (default `[]`), mas **pelo menos um dos dois precisa ter item**.
- `servicosVinculados` é só uma lista de IDs de serviço (`int[]`), não objetos.
- Response: `{ "status": true, "msg": "Obra cadastrada com sucesso!" }` (201). **Não retorna o `idObra` criado** — se precisar do ID logo em seguida, dê um `GET /obra` ou `GET /obra/cliente/<idCliente>` e pegue pelo maior `idObra` com o `descObra` esperado (é uma limitação atual do backend, não um bug seu).

### `GET /obra` — listar todas
```json
{ "status": true, "obras": [ { ...ver shape abaixo... } ] }
```

### `GET /obra/<idObra>` — buscar uma obra
```json
{
  "status": true,
  "obra": {
    "idObra": 31,
    "codCliente": 1,
    "descObra": "Instalação de gás residencial",
    "dataInicio": "2026-01-10",
    "dataFim": null,
    "statusObra": "Concluida",
    "respObra": "Carlos",
    "obsObra": null,
    "orientacaoObra": null,
    "tipoObra": null,
    "fieldObra": null,
    "unidadeObra": null,
    "emailContato": null,
    "celular1": null,
    "celular2": null,
    "valorObra": 1060.0
  }
}
```
(`valorObra` foi adicionado agora nesse shape — se você já tinha código consumindo esse endpoint antes, ele só ganha um campo novo, nada quebra.)

### `GET /obra/cliente/<idCliente>` — obras de um cliente
Mesmo shape de `obra`, dentro de `{ "status": true, "msg": "...", "obras": [...] }`.

### `GET /obra/<idObra>/produtos` — produtos avulsos da obra
```json
{ "status": true, "produtos": [ { "idProduto": 1, "nomeProduto": "Tubo Aço Galvanizado 1\"", "qtdProdutosObra": 5 } ] }
```

### `GET /obra/<idObra>/servicos` — serviços vinculados à obra
Use este para listar/exibir os serviços de uma obra (ex: numa aba "Serviços" do modal de obra):
```json
{
  "status": true,
  "servicos": [
    { "idServico": 1, "nomeServico": "Instalação de Ramal Residencial", "precoServico": 850.0 },
    { "idServico": 5, "nomeServico": "Troca de Registro e Conector", "precoServico": 210.0 }
  ]
}
```
Útil para o front montar uma prévia de "valor estimado" antes de concluir (soma esses `precoServico` na UI, sem esperar o backend — mas o valor oficial/gravado só existe depois do `PATCH .../status` para "Concluida").

### `PUT /obra/<idObra>` — editar obra
```json
{
  "obra": { /* mesmo shape do POST, incluindo statusObra (mas não mude o status por aqui, ver seção 3) */ },
  "produtosNovos": [ { "idProduto": 2, "quantidade": 3 } ],
  "servicosNovos": [8]
}
```
- `produtosNovos` / `servicosNovos` são **adições incrementais** (itens novos a vincular), não a lista completa — não é um "replace".

### `PATCH /obra/<idObra>/status` — mudar status (única forma correta)
```json
{ "statusObra": "Concluida" }
```
Response: `{ "status": true, "msg": "Status atualizado com sucesso!" }`. Depois disso, um `GET /obra/<idObra>` já retorna o `valorObra` recalculado.

### `PATCH /obra/<idObra>/produto/<idProduto>` — mudar quantidade de um produto avulso
```json
{ "quantidade": 4 }
```

### `DELETE /obra/<idObra>/produto/<idProduto>` — remover produto avulso da obra

### `DELETE /obra/<idObra>` — deletar obra (repõe estoque)

### `GET /obra/<idObra>/relatorio` — gera o PDF "Relatório de Obra" (já implementado, sem relação com valorObra)

---

## 5. Endpoints — Serviços (catálogo)

### `POST /servico` — cadastrar serviço
```json
{
  "servico": {
    "nomeServico": "Instalação de Ramal Residencial",
    "precoServico": 850.00,
    "produtos": [
      { "idProduto": 1, "quantidade": 10 },
      { "idProduto": 2, "quantidade": 1 }
    ]
  }
}
```
- `nomeServico`: mínimo 3 caracteres.
- `precoServico`: número > 0.
- `produtos`: a "receita" do serviço (produtos que o estoque vai debitar quando o serviço for vinculado a uma obra). Pode ser `[]` (serviço só de mão de obra, sem consumo de estoque — ex: "Vistoria e Laudo Técnico").
- Response inclui `idServico` criado: `{ "status": true, "msg": "...", "idServico": 9 }`.

### `GET /servico` — listar catálogo de serviços
```json
{
  "status": true,
  "servicos": [
    {
      "idServico": 1,
      "nomeServico": "Instalação de Ramal Residencial",
      "precoServico": 850.0,
      "produtos": [ { "idProduto": 1, "nomeProduto": "...", "quantidade": 10 }, ... ]
    }
  ]
}
```
Esse é o endpoint para popular o combo/lista de "vincular serviço" na tela de obra.

### `GET /servico/<idServico>` — buscar um serviço (mesmo shape acima, sem array)

### `PUT /servico/<idServico>` — editar (mesmo shape do POST)

### `DELETE /servico/<idServico>` — deletar

### `GET /servico/<idServico>/produtos` — só a receita de produtos do serviço

---

## 6. Resumo do que o frontend precisa fazer

1. **Tela/CRUD de Serviços** (nova): listar, criar, editar, excluir serviços do catálogo (nome, preço, receita de produtos).
2. **Tela de Obra — cadastro/edição**: permitir selecionar serviços do catálogo (multi-select, via `GET /servico`) além dos produtos avulsos já existentes, mandando os IDs em `servicosVinculados` (criar) / `servicosNovos` (editar).
3. **Tela de Obra — exibição**: mostrar `valorObra` formatado em R$ quando não for `null`; mostrar algo como "Valor definido ao concluir a obra" quando for `null`.
4. **Aba "Serviços" da obra** (se aplicável ao layout atual, ver `abaDocumentos`/`abaHistorico` já existentes no modal): usar `GET /obra/<idObra>/servicos` para listar os serviços vinculados com nome e preço.
5. **Ação de concluir obra**: deve chamar exclusivamente `PATCH /obra/<idObra>/status` com `{"statusObra": "Concluida"}` — nunca via `PUT /obra/<idObra>`.
6. Todas as chamadas precisam do header `Authorization: Bearer <token>` (mesmo padrão já usado nas outras telas).

---

## 7. Arquivos backend relevantes (para referência/dúvidas)

- `src/routers/servicoRoteador.py` — rotas de serviço
- `src/routers/obraRoteador.py` — rotas de obra (inclui `_serializar`, que define o shape JSON)
- `src/controller/obraController.py` — regra de negócio de obra (`atualizar_status` valida status e delega ao DAO)
- `src/dao/obraDAO.py` — `atualizar_status` é onde o cálculo de `valorObra` acontece
- `src/dao/produtosObrasDAO.py` — `buscar_servicos_da_obra` (usado pela rota de serviços da obra)
- `teste_valor_obra.py` (raiz do projeto) — script que valida os cenários de cálculo, útil como referência de comportamento esperado
