    DROP SCHEMA IF EXISTS tcc;
    create database tcc;
    use tcc;

    create table login(
    idLogin int primary key NOT NULL,
    email VARCHAR(45) NOT NULL,
    senha VARCHAR(45)NOT NULL,
    nomeLogin VARCHAR(45) 
    );
    
    insert into login value(
    1, "adm123@gmail.com", "adm123", "adm"
    );

    create table produtos(
    idProduto int primary key NOT NULL,
    qtdProduto int,
    nomeProduto VARCHAR(255),
    descProduto VARCHAR(255) 
    );

    create table clientes(
    idCliente int primary key NOT NULL,
    nomeCliente VARCHAR(45) NOT NULL,
    CNPJCPF VARCHAR(255) NOT NULL,
    enderecoCliente VARCHAR(255) NOT NULL,
    contatoCliente VARCHAR(255) 
    );

    create table obras(
    idObra int primary key,
    codCliente int 	NOT NULL,
    codProduto int NOT NULL,
    descObra VARCHAR(255) NOT NULL,
    dataObra DATE NOT NULL,
    statusObra VARCHAR(255),
    respObra VARCHAR(255),
    obsObra VARCHAR(255),
    orientacaoObra VARCHAR(255),
    FOREIGN KEY (codCliente) REFERENCES clientes(idCliente)
    );
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