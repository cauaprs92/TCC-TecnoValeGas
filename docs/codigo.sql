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


    SELECT * FROM produtos;
    SELECT * FROM clientes;
    SELECT * FROM produtosObras;


    ## para reiniciar o banco
    SET FOREIGN_KEY_CHECKS = 0;

    TRUNCATE TABLE produtosObras;
    TRUNCATE TABLE obras;
    TRUNCATE TABLE produtos;
    TRUNCATE TABLE clientes;

    SET FOREIGN_KEY_CHECKS = 1;
