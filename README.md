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
│   └── codigo.sql           # Schema completo do banco de dados
├── view/                    # Frontend (SPA)
│   ├── login.html
│   ├── index.html
│   ├── index.css
│   └── index.js
└── src/
    ├── modelo/              # Entidades (Cliente, Produto, Obra...)
    ├── dao/                 # Acesso ao banco (SQL puro via mysql-connector)
    ├── controller/          # Regras de negócio
    ├── routers/             # Blueprints Flask — definição das rotas
    ├── middleware/          # Validação de body, params e token JWT
    ├── http/                # Geração e validação do token JWT
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
| PUT | `/obra/:id` | Edita obra (dados + adiciona novos produtos) |
| DELETE | `/obra/:id` | Remove obra |
| GET | `/obra/:id/produtos` | Lista produtos de uma obra |
| PATCH | `/obra/:id/status` | Atualiza apenas o status |

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
pip install flask flask-cors mysql-connector-python PyJWT
```

### 3. Criar o banco de dados

Abra o phpMyAdmin (ou qualquer client MySQL) e execute o script:

```
docs/codigo.sql
```

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
login          -- usuários do sistema
clientes       -- cadastro de clientes (CPF/CNPJ + endereço completo)
produtos       -- estoque com qtdMinima e qtdMaxima por produto
obras          -- obras com dataInicio, dataFim, responsável e status
produtosObras  -- relação N:N entre obras e produtos (quantidade utilizada)
```

---

## Autores

Desenvolvido por **Cauã Peres**, **Mateus Ricardo** e **João Vinicius**  
Trabalho de Conclusão de Curso — 2026
