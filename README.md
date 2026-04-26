# 📦 Sistema de Controle de Estoque

Sistema desenvolvido como Trabalho de Conclusão de Curso (TCC) com o objetivo de gerenciar produtos, clientes e obras de forma eficiente, utilizando uma API REST com autenticação segura e organização em arquitetura em camadas.

---

## 🚀 Tecnologias Utilizadas

* 🐍 Python
* 🌐 API REST
* 🔐 JWT (JSON Web Token)
* 🗄️ Banco de Dados SQL
* 💻 HTML, CSS e JavaScript (interface web)

---

## 🏗️ Estrutura do Projeto

O projeto segue uma arquitetura organizada em camadas, facilitando manutenção e escalabilidade:

```
src/
 ├── controller/    # Recebe as requisições e chama os serviços
 ├── service/       # Contém as regras de negócio
 ├── dao/           # Responsável pelo acesso ao banco de dados
 ├── modelo/        # Representação das entidades do sistema
 ├── routers/       # Definição das rotas da API
 ├── middleware/    # Validações e autenticação (JWT)
 ├── http/          # Configurações HTTP e segurança
```

Outros diretórios importantes:

```
view/               # Interface web (HTML, CSS, JS)
codigo.sql          # Script de criação do banco de dados
```

---

## ⚙️ Funcionalidades

* 🔐 Sistema de autenticação com JWT
* 📦 Cadastro, edição e exclusão de produtos
* 👤 Gerenciamento de clientes
* 👷 Controle de obras
* 🔗 Relacionamento entre produtos e obras
* 🌐 Interface web para interação com o sistema

---

## 🧠 Arquitetura

O sistema utiliza o padrão em camadas:

```
Controller → Service → DAO → Banco de Dados
```

### ✔️ Vantagens:

* Melhor organização do código
* Separação de responsabilidades
* Facilidade para manutenção e testes
* Maior escalabilidade

---

## 🗄️ Banco de Dados

O banco de dados é configurado a partir do arquivo:

```
codigo.sql
```

Esse arquivo contém toda a estrutura necessária para o funcionamento do sistema.

---

## ▶️ Como Executar o Projeto

### 1. Clonar o repositório

```
git clone https://github.com/seu-usuario/seu-repositorio.git
```

### 2. Acessar a pasta do projeto

```
cd seu-repositorio
```

### 3. Configurar o banco de dados

* Execute o script `codigo.sql` no seu SGBD (MySQL, PostgreSQL, etc.)

### 4. Instalar dependências (se necessário)

```
pip install -r requirements.txt
```

### 5. Executar a aplicação

```
python app.py
```

### 6. Acessar o sistema

* Abra os arquivos da pasta `view/` no navegador

---

## 🔐 Autenticação

O sistema utiliza **JWT (JSON Web Token)** para proteger rotas e garantir segurança no acesso.

* Login gera um token
* Token deve ser enviado nas requisições protegidas

---

## 📌 Objetivo do Projeto

Este projeto foi desenvolvido com o objetivo de aplicar na prática conceitos como:

* Desenvolvimento de APIs REST
* Arquitetura em camadas
* Integração com banco de dados
* Autenticação e segurança
* Organização de código

---

## 📷 Interface

A interface do sistema foi desenvolvida utilizando HTML, CSS e JavaScript, permitindo interação simples com a API.

---


## 👨‍💻 Autor

Desenvolvido por **Cauã Peres**, **Mateus Ricardo** e **João Vinicius** como Trabalho de Conclusão de Curso.

