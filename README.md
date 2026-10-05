# TecnoValeGAS — Sistema de Gestão de Estoque e Obras

Sistema desenvolvido como Trabalho de Conclusão de Curso (TCC) para gerenciar o estoque de produtos, cadastro de clientes e controle de obras de uma empresa do setor de gás. Conta com API REST em Python/Flask, autenticação JWT e interface web em Vanilla JS.

---

## Tecnologias

| Camada | Stack |
|---|---|
| Backend | Python 3 + Flask + Flask-CORS |
| Banco de dados | MySQL (via XAMPP) + mysql-connector-python |
| Autenticação | JWT (HS256) — token de 60 dias |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla, SPA) |

---

## Funcionalidades

**Autenticação**
- Login com e-mail e senha
- Token JWT armazenado em `sessionStorage`
- Todas as rotas protegidas por middleware JWT

**Estoque / Produtos**
- Cadastro, edição e exclusão de produtos
- Controle de quantidade com alertas de estoque mínimo e máximo por produto
- Dashboard com gráfico dos produtos com menor estoque e notificações de alerta

**Clientes**
- Cadastro com CPF/CNPJ, telefone e endereço completo
- Busca de CEP automática via [ViaCEP](https://viacep.com.br)
- Máscaras de input para CPF/CNPJ, telefone e CEP

**Obras**
- Criação de obras vinculadas a clientes com data de início e data de fim
- Seleção de responsável (Mateus, Cauã, João)
- Vinculação de produtos utilizados com baixa automática de estoque
- Edição completa da obra (dados + adição de novos produtos com baixa de estoque)
- Filtro por status: Em andamento, Pausada, Concluída, Cancelada

---

## Estrutura do Projeto

```
TCC-TecnoValeGas/
├── app.py                   # Entry point — Flask + registro de blueprints
├── docs/
│   ├── codigo.sql           # Schema completo (recria o banco do zero)
│   ├── inserts.sql          # Dados de exemplo
│   └── migracao.sql         # Atualiza um banco já existente
├── view/                    # Frontend (SPA)
│   ├── login.html
│   ├── index.html
│   ├── index.css
│   ├── index.js
│   └── *-obra*.html         # Documentos imprimíveis da obra
└── src/
    ├── modelo/              # Entidades (Cliente, Produto, Obra...)
    ├── dao/                 # Acesso ao banco (SQL puro via mysql-connector)
    ├── controller/          # Regras de negócio
    ├── routers/             # Blueprints Flask — definição das rotas
    ├── middleware/          # Validação de body e token JWT / cargo
    ├── service/             # Leitura do XML de NF-e
    └── error_response.py    # Classe de erro padronizada
```

**Fluxo de uma requisição:**
```
Frontend → Router → Middleware → Controller → DAO → MySQL
```

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/login` | Autenticação — retorna JWT |
| GET | `/produto` | Lista todos os produtos |
| POST | `/produto` | Cadastra produto |
| PUT | `/produto/:id` | Edita produto |
| DELETE | `/produto/:id` | Remove produto |
| GET | `/cliente` | Lista todos os clientes |
| POST | `/cliente` | Cadastra cliente |
| PUT | `/cliente/:id` | Edita cliente |
| DELETE | `/cliente/:id` | Remove cliente |
| GET | `/obra` | Lista todas as obras |
| POST | `/obra` | Cadastra obra + produtos + baixa no estoque |
| PUT | `/obra/:id` | Edita obra (dados, status, equipe e material novo) |
| DELETE | `/obra/:id` | Remove obra e devolve o estoque |
| GET | `/obra/:id/produtos` | Lista produtos de uma obra |
| GET | `/obra/:id/servicos` | Lista serviços de uma obra |

As demais rotas (serviços, fotos, usuários, fields, histórico, relatórios e
importação de NF-e) seguem o mesmo padrão — ver `src/routers/`.

---

## Como Executar

### Pré-requisitos
- Python 3.10+
- XAMPP com MySQL rodando na porta padrão (3306)

### 1. Clonar o repositório

```bash
git clone https://github.com/cauaprs92/TCC-TecnoValeGas.git
cd TCC-TecnoValeGas
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar o banco de dados

Abra o phpMyAdmin (ou qualquer client MySQL) e execute, nesta ordem:

```
docs/codigo.sql    -- cria o banco do zero (apaga o banco 'tcc' se existir)
docs/inserts.sql   -- opcional: dados de exemplo
```

Já tem um banco `tcc` com dados de uma versão anterior? Em vez de recriar,
rode `docs/migracao.sql` para atualizá-lo.

A conexão usa as variáveis de ambiente `DB_HOST`, `DB_PORT`, `DB_USER`,
`DB_PASSWORD` e `DB_NAME` (padrão: `localhost`, `3306`, `root`, sem senha, `tcc`).

### 4. Iniciar o servidor

```bash
python app.py
```

O servidor sobe em `http://localhost:5000`.

### 5. Acessar o sistema

Abra `http://localhost:5000` no navegador.

**Credenciais padrão:**
```
E-mail: adm123@gmail.com
Senha:  adm123
```

---

## Banco de Dados

```sql
login               -- usuários do sistema e cargo (Administracao, Almoxarifado, Obra)
clientes            -- cadastro de clientes (CPF/CNPJ único + endereço completo)
produtos            -- estoque com qtdMinima e qtdMaxima por produto
obras               -- obras com datas, status, field responsável e valorObra
produtosObras       -- produtos avulsos usados em cada obra
servicos            -- catálogo de serviços (preço fixo)
servicoProdutos     -- receita de produtos de cada serviço
obraServicos        -- serviços vinculados a cada obra
obraServicoProdutos -- receita do serviço no momento do vínculo (o que saiu do estoque)
vw_consumo_obra     -- view: tudo o que cada obra consome do estoque
obraFuncionarios    -- equipe de cada obra (define o que o cargo Obra enxerga)
responsavel         -- fields (técnicos responsáveis)
historico           -- registro das ações dos usuários
produto_fotos       -- fotos e notas fiscais anexadas aos produtos
obra_fotos          -- fotos das obras
fornecedores        -- fornecedores (nome + CNPJ, usado na importação de NF-e)
notasFiscais        -- NF-e importadas por XML (chave de acesso única)
notaFiscalItens     -- itens da nota aguardando conferência (pendente/confirmado/ignorado)
```

---

## Autores

Desenvolvido por **Cauã Peres**, **Mateus Ricardo** e **João Vinicius**  
Trabalho de Conclusão de Curso — 2026
