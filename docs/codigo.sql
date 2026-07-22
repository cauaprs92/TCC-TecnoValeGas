DROP SCHEMA IF EXISTS tcc;
    create database tcc;
    use tcc;

    create table login(
    idLogin   int primary key NOT NULL AUTO_INCREMENT,
    email     VARCHAR(45)  NOT NULL UNIQUE,
    senha     VARCHAR(60)  NOT NULL,
    nomeLogin VARCHAR(45)
    );

    -- senha: adm123 (bcrypt hash)
    insert into login (email, senha, nomeLogin) values(
    "adm123@gmail.com", "$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO", "adm"
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- ALTER TABLE login
    --   MODIFY COLUMN idLogin int NOT NULL AUTO_INCREMENT,
    --   MODIFY COLUMN email VARCHAR(45) NOT NULL,
    --   MODIFY COLUMN senha VARCHAR(60) NOT NULL,
    --   ADD UNIQUE (email);

    create table produtos(
    idProduto   int primary key NOT NULL,
    nomeProduto VARCHAR(255),
    qtdProduto  int          DEFAULT 0,
    descProduto TEXT,
    qtdMinima   int          DEFAULT 0,
    qtdMaxima   int          DEFAULT 9999
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- ALTER TABLE produtos
    --   MODIFY COLUMN descProduto TEXT,
    --   ADD COLUMN qtdMinima int DEFAULT 0,
    --   ADD COLUMN qtdMaxima int DEFAULT 9999;

    create table clientes(
    idCliente      int primary key NOT NULL,
    nomeCliente    VARCHAR(45)  NOT NULL,
    CNPJCPF        VARCHAR(18)  NOT NULL,
    contatoCliente VARCHAR(15),
    emailCliente   VARCHAR(255),
    telefone2      VARCHAR(15),
    cep            VARCHAR(9),
    rua            VARCHAR(255),
    numero         VARCHAR(20),
    complemento    VARCHAR(100),
    bairro         VARCHAR(100),
    cidade         VARCHAR(100),
    estado         VARCHAR(2)
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- ALTER TABLE clientes
    --   DROP COLUMN enderecoCliente,
    --   MODIFY COLUMN contatoCliente VARCHAR(15),
    --   ADD COLUMN cep         VARCHAR(9),
    --   ADD COLUMN rua         VARCHAR(255),
    --   ADD COLUMN numero      VARCHAR(20),
    --   ADD COLUMN complemento VARCHAR(100),
    --   ADD COLUMN bairro      VARCHAR(100),
    --   ADD COLUMN cidade      VARCHAR(100),
    --   ADD COLUMN estado      VARCHAR(2);

    -- ── MIGRAÇÃO — campos de contato (rodar se a tabela já existir) ──────────
    -- ALTER TABLE clientes
    --   ADD COLUMN emailCliente VARCHAR(255) AFTER contatoCliente,
    --   ADD COLUMN telefone2    VARCHAR(15)  AFTER emailCliente;

    create table obras(
    idObra         int primary key AUTO_INCREMENT,
    codCliente     int          NOT NULL,
    descObra       VARCHAR(255) NOT NULL,
    dataInicio     DATE         NOT NULL,
    dataFim        DATE,
    statusObra     VARCHAR(255),
    respObra       VARCHAR(255),
    obsObra        VARCHAR(255),
    orientacaoObra VARCHAR(255),
    tipoObra       VARCHAR(100),
    clientePrimario VARCHAR(100),
    fieldObra      VARCHAR(100),
    unidadeObra    VARCHAR(20),
    emailContato   VARCHAR(100),
    celular1       VARCHAR(20),
    celular2       VARCHAR(20),
    valorObra      DECIMAL(10,2) DEFAULT NULL,
    FOREIGN KEY (codCliente) REFERENCES clientes(idCliente)
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- ALTER TABLE obras
    --   DROP COLUMN codProduto,
    --   ADD COLUMN dataInicio DATE NOT NULL AFTER descObra,
    --   ADD COLUMN dataFim    DATE         AFTER dataInicio;
    -- -- Se a coluna dataObra ainda existir:
    -- ALTER TABLE obras DROP COLUMN dataObra;
    -- -- Adicionar AUTO_INCREMENT ao idObra:
    -- ALTER TABLE obras MODIFY COLUMN idObra int NOT NULL AUTO_INCREMENT;

    create table produtosObras(
        idProdutosObra  int primary key AUTO_INCREMENT,
        idObra          int NOT NULL,
        idProduto       int NOT NULL,
        qtdProdutosObra int NOT NULL,

        FOREIGN KEY (idObra)    REFERENCES obras(idObra),
        FOREIGN KEY (idProduto) REFERENCES produtos(idProduto)
    );

     create table responsavel (
    idResponsavel   int primary key NOT NULL AUTO_INCREMENT,
    nomeResponsavel VARCHAR(100) NOT NULL UNIQUE
    );

    create table historico (
    idHistorico INT PRIMARY KEY AUTO_INCREMENT,
    idAdmin     INT          NOT NULL,
    nomeAdmin   VARCHAR(45)  NOT NULL,
    acao        VARCHAR(20)  NOT NULL,
    entidade    VARCHAR(30)  NOT NULL,
    descricao   TEXT         NOT NULL,
    dataHora    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idAdmin) REFERENCES login(idLogin)
    );

    -- ── MIGRAÇÃO (rodar se as tabelas já existirem) ───────────────────────────
    -- CREATE TABLE IF NOT EXISTS historico (
    --   idHistorico INT PRIMARY KEY AUTO_INCREMENT,
    --   idAdmin     INT          NOT NULL,
    --   nomeAdmin   VARCHAR(45)  NOT NULL,
    --   acao        VARCHAR(20)  NOT NULL,
    --   entidade    VARCHAR(30)  NOT NULL,
    --   descricao   TEXT         NOT NULL,
    --   dataHora    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    --   FOREIGN KEY (idAdmin) REFERENCES login(idLogin)
    -- );

    -- ── MIGRAÇÃO obras — valorObra (rodar se a tabela já existir) ──────────────
    -- ALTER TABLE obras
    --   ADD COLUMN valorObra DECIMAL(10,2) DEFAULT NULL;

    -- ── MIGRAÇÃO obras — novos campos (já incluídos no CREATE TABLE acima) ─────
    -- ALTER TABLE obras
    --   ADD COLUMN tipoObra     VARCHAR(100),
    --   ADD COLUMN fieldObra    VARCHAR(100),
    --   ADD COLUMN unidadeObra  VARCHAR(20),
    --   ADD COLUMN emailContato VARCHAR(100),
    --   ADD COLUMN celular1     VARCHAR(20),
    --   ADD COLUMN celular2     VARCHAR(20);

    -- ── MIGRAÇÃO obras — clientePrimario (rodar se a tabela já existir) ────────
    -- Empresa "guarda-chuva" para quem a TecnoValeGas presta serviço nessa obra
    -- (ex.: Supergásbras). Lista fechada por enquanto, editável no HTML do
    -- <select id="obraClientePrimario"> conforme novos parceiros forem surgindo.
    -- ALTER TABLE obras
    --   ADD COLUMN clientePrimario VARCHAR(100) AFTER tipoObra;

    create table produto_fotos (
    idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    idProduto    INT NOT NULL,
    tipoFoto     VARCHAR(20)  NOT NULL DEFAULT 'produto',
    nomeArquivo  VARCHAR(255) NOT NULL,
    nomeOriginal VARCHAR(255) NOT NULL,
    dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idProduto) REFERENCES produtos(idProduto) ON DELETE CASCADE
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- CREATE TABLE IF NOT EXISTS produto_fotos (
    --   idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    --   idProduto    INT NOT NULL,
    --   tipoFoto     VARCHAR(20)  NOT NULL DEFAULT 'produto',
    --   nomeArquivo  VARCHAR(255) NOT NULL,
    --   nomeOriginal VARCHAR(255) NOT NULL,
    --   dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    --   FOREIGN KEY (idProduto) REFERENCES produtos(idProduto) ON DELETE CASCADE
    -- );

    create table obra_fotos (
    idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    idObra       INT NOT NULL,
    nomeArquivo  VARCHAR(255) NOT NULL,
    nomeOriginal VARCHAR(255) NOT NULL,
    dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idObra) REFERENCES obras(idObra) ON DELETE CASCADE
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- CREATE TABLE IF NOT EXISTS obra_fotos (
    --   idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    --   idObra       INT NOT NULL,
    --   nomeArquivo  VARCHAR(255) NOT NULL,
    --   nomeOriginal VARCHAR(255) NOT NULL,
    --   dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    --   FOREIGN KEY (idObra) REFERENCES obras(idObra) ON DELETE CASCADE
    -- );

    create table servicos(
        idServico    int          primary key NOT NULL AUTO_INCREMENT,
        nomeServico  VARCHAR(255) NOT NULL,
        precoServico DECIMAL(10,2) NOT NULL
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- CREATE TABLE IF NOT EXISTS servicos (
    --   idServico    INT           PRIMARY KEY NOT NULL AUTO_INCREMENT,
    --   nomeServico  VARCHAR(255)  NOT NULL,
    --   precoServico DECIMAL(10,2) NOT NULL
    -- );

    create table servicoProdutos(
        idServicoProduto int primary key NOT NULL AUTO_INCREMENT,
        idServico        int NOT NULL,
        idProduto        int NOT NULL,
        quantidade       int NOT NULL,

        FOREIGN KEY (idServico) REFERENCES servicos(idServico),
        FOREIGN KEY (idProduto) REFERENCES produtos(idProduto)
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- CREATE TABLE IF NOT EXISTS servicoProdutos (
    --   idServicoProduto INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    --   idServico        INT NOT NULL,
    --   idProduto        INT NOT NULL,
    --   quantidade       INT NOT NULL,
    --   FOREIGN KEY (idServico) REFERENCES servicos(idServico),
    --   FOREIGN KEY (idProduto) REFERENCES produtos(idProduto)
    -- );

    create table obraServicos(
        idObraServico int primary key NOT NULL AUTO_INCREMENT,
        idObra        int NOT NULL,
        idServico     int NOT NULL,

        FOREIGN KEY (idObra)    REFERENCES obras(idObra),
        FOREIGN KEY (idServico) REFERENCES servicos(idServico)
    );

    -- ── MIGRAÇÃO (rodar se a tabela já existir) ───────────────────────────────
    -- CREATE TABLE IF NOT EXISTS obraServicos (
    --   idObraServico INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    --   idObra        INT NOT NULL,
    --   idServico     INT NOT NULL,
    --   FOREIGN KEY (idObra)    REFERENCES obras(idObra),
    --   FOREIGN KEY (idServico) REFERENCES servicos(idServico)
    -- );


    SELECT * FROM produtos;
    SELECT * FROM clientes;
    SELECT * FROM produtosObras;
    SELECT * FROM obras;
    SELECT * FROM responsavel;
    SELECT * FROM servicos;
    SELECT * FROM servicoProdutos;
    SELECT * FROM obraServicos;


    ## para reiniciar o banco
    SET FOREIGN_KEY_CHECKS = 0;

    TRUNCATE TABLE obraServicos;
    TRUNCATE TABLE servicoProdutos;
    TRUNCATE TABLE servicos;
    TRUNCATE TABLE produtosObras;
    TRUNCATE TABLE obras;
    TRUNCATE TABLE produtos;
    TRUNCATE TABLE clientes;
    TRUNCATE TABLE responsavel;

    SET FOREIGN_KEY_CHECKS = 1;