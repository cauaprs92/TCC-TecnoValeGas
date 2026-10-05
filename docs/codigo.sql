-- =============================================================================
-- Schema do banco `tcc`. APAGA e recria o banco do zero — para atualizar um
-- banco que já tem dados, use docs/migracao.sql.
-- Depois deste script, docs/inserts.sql popula dados de exemplo.
-- =============================================================================
DROP SCHEMA IF EXISTS tcc;
create database tcc;
use tcc;

-- cargoLogin define o que cada usuário pode acessar. Três valores fechados,
-- gravados sem acento e exibidos com acento no front:
--   'Administracao' → acesso total
--   'Almoxarifado'  → estoque, produtos, notas fiscais e fornecedores
--   'Obra'          → apenas as obras em que o usuário está na equipe
create table login(
    idLogin    int primary key NOT NULL AUTO_INCREMENT,
    email      VARCHAR(45)  NOT NULL UNIQUE,
    senha      VARCHAR(60)  NOT NULL,
    nomeLogin  VARCHAR(45),
    cargoLogin VARCHAR(20)  NOT NULL DEFAULT 'Administracao',
    CONSTRAINT ck_login_cargo CHECK (cargoLogin IN ('Administracao', 'Almoxarifado', 'Obra'))
);

-- senha: adm123 (bcrypt hash)
insert into login (email, senha, nomeLogin, cargoLogin) values(
    "adm123@gmail.com", "$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO", "adm", "Administracao"
);

-- cnpjFornecedor é usado pela importação de NF-e: o fornecedor da nota é
-- identificado pelo CNPJ do <emit>, evitando duplicar fornecedores com
-- grafias diferentes.
create table fornecedores (
    idFornecedor   int primary key NOT NULL AUTO_INCREMENT,
    nomeFornecedor VARCHAR(150) NOT NULL UNIQUE,
    cnpjFornecedor VARCHAR(18)  DEFAULT NULL UNIQUE
);

create table produtos(
    idProduto     int primary key NOT NULL AUTO_INCREMENT,
    nomeProduto   VARCHAR(255),
    qtdProduto    int          DEFAULT 0,
    descProduto   TEXT,
    qtdMinima     int          DEFAULT 0,
    qtdMaxima     int          DEFAULT 9999,
    idFornecedor  int          DEFAULT NULL,
    FOREIGN KEY (idFornecedor) REFERENCES fornecedores(idFornecedor)
);

create table clientes(
    idCliente      int primary key NOT NULL AUTO_INCREMENT,
    nomeCliente    VARCHAR(45)  NOT NULL,
    CNPJCPF        VARCHAR(18)  NOT NULL UNIQUE,
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

-- clientePrimario: empresa "guarda-chuva" para quem a TecnoValeGas presta o
-- serviço (ex.: Supergásbras). clientePrimario e setorObra são listas fechadas
-- por enquanto, editáveis nos <select> do formulário de obra.
-- valorObra só é preenchido com a obra Concluida (soma dos serviços).
create table obras(
    idObra          int primary key AUTO_INCREMENT,
    codCliente      int          NOT NULL,
    descObra        VARCHAR(255) NOT NULL,
    dataInicio      DATE         NOT NULL,
    dataFim         DATE,
    statusObra      VARCHAR(255),
    respObra        VARCHAR(255),
    obsObra         VARCHAR(255),
    orientacaoObra  VARCHAR(255),
    tipoObra        VARCHAR(100),
    clientePrimario VARCHAR(100),
    fieldObra       VARCHAR(100),
    unidadeObra     VARCHAR(20),
    emailContato    VARCHAR(100),
    celular1        VARCHAR(20),
    celular2        VARCHAR(20),
    valorObra       DECIMAL(10,2) DEFAULT NULL,
    setorObra       VARCHAR(20),
    FOREIGN KEY (codCliente) REFERENCES clientes(idCliente),
    CONSTRAINT ck_obras_status
        CHECK (statusObra IN ('À iniciar', 'Em andamento', 'Concluida', 'Cancelada', 'Pausada'))
);

create table produtosObras(
    idProdutosObra  int primary key AUTO_INCREMENT,
    idObra          int NOT NULL,
    idProduto       int NOT NULL,
    qtdProdutosObra int NOT NULL,

    UNIQUE KEY uq_obra_produto (idObra, idProduto),
    FOREIGN KEY (idObra)    REFERENCES obras(idObra),
    FOREIGN KEY (idProduto) REFERENCES produtos(idProduto)
);

-- Equipe da obra: quais usuários de cargo 'Obra' trabalham em cada obra.
-- É por essa tabela que o sistema decide quais obras cada funcionário vê.
-- Não confundir com obras.respObra, que é o Field (técnico responsável) e
-- vem da tabela responsavel — são pessoas de origens diferentes.
-- ON DELETE CASCADE só no idObra: excluir uma obra leva junto a equipe dela,
-- mas excluir um usuário é barrado enquanto ele estiver vinculado a alguma
-- obra — o vínculo é registro de quem trabalhou onde.
create table obraFuncionarios (
    idObraFuncionario int primary key NOT NULL AUTO_INCREMENT,
    idObra            int NOT NULL,
    idLogin           int NOT NULL,
    UNIQUE KEY uq_obra_login (idObra, idLogin),
    FOREIGN KEY (idObra)  REFERENCES obras(idObra) ON DELETE CASCADE,
    FOREIGN KEY (idLogin) REFERENCES login(idLogin)
);

create table responsavel (
    idResponsavel   int primary key NOT NULL AUTO_INCREMENT,
    nomeResponsavel VARCHAR(100) NOT NULL UNIQUE
);

create table historico (
    idHistorico INT PRIMARY KEY AUTO_INCREMENT,
    idAdmin     INT          DEFAULT NULL,
    nomeAdmin   VARCHAR(45)  NOT NULL,
    acao        VARCHAR(20)  NOT NULL,
    entidade    VARCHAR(30)  NOT NULL,
    descricao   TEXT         NOT NULL,
    dataHora    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    -- O nome fica gravado em nomeAdmin, então o registro continua legível
    -- depois que o usuário é excluído. Só o vínculo vira NULL.
    FOREIGN KEY (idAdmin) REFERENCES login(idLogin) ON DELETE SET NULL
);

create table produto_fotos (
    idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    idProduto    INT NOT NULL,
    tipoFoto     VARCHAR(20)  NOT NULL DEFAULT 'produto',
    nomeArquivo  VARCHAR(255) NOT NULL,
    nomeOriginal VARCHAR(255) NOT NULL,
    dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idProduto) REFERENCES produtos(idProduto) ON DELETE CASCADE
);

create table obra_fotos (
    idFoto       INT PRIMARY KEY AUTO_INCREMENT,
    idObra       INT NOT NULL,
    nomeArquivo  VARCHAR(255) NOT NULL,
    nomeOriginal VARCHAR(255) NOT NULL,
    dataUpload   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idObra) REFERENCES obras(idObra) ON DELETE CASCADE
);

-- fornecedorServico: lista fechada por enquanto (apenas "Tecnovale Gás"),
-- editável no <select id="servFornecedor"> do formulário de serviço.
create table servicos(
    idServico         int          primary key NOT NULL AUTO_INCREMENT,
    nomeServico       VARCHAR(255) NOT NULL,
    precoServico      DECIMAL(10,2) NOT NULL,
    fornecedorServico VARCHAR(150) NOT NULL DEFAULT 'Tecnovale Gás'
);

-- Receita do serviço: quais produtos ele consome do estoque.
create table servicoProdutos(
    idServicoProduto int primary key NOT NULL AUTO_INCREMENT,
    idServico        int NOT NULL,
    idProduto        int NOT NULL,
    quantidade       int NOT NULL,

    FOREIGN KEY (idServico) REFERENCES servicos(idServico),
    FOREIGN KEY (idProduto) REFERENCES produtos(idProduto)
);

create table obraServicos(
    idObraServico int primary key NOT NULL AUTO_INCREMENT,
    idObra        int NOT NULL,
    idServico     int NOT NULL,

    UNIQUE KEY uq_obra_servico (idObra, idServico),
    FOREIGN KEY (idObra)    REFERENCES obras(idObra),
    FOREIGN KEY (idServico) REFERENCES servicos(idServico)
);

-- Receita do serviço no momento em que ele foi vinculado à obra. É o que
-- saiu do estoque e o que volta se o vínculo for desfeito, mesmo que a
-- receita em servicoProdutos seja editada depois.
create table obraServicoProdutos(
    idObraServicoProduto int primary key NOT NULL AUTO_INCREMENT,
    idObraServico        int NOT NULL,
    idProduto            int NOT NULL,
    quantidade           int NOT NULL,

    FOREIGN KEY (idObraServico) REFERENCES obraServicos(idObraServico) ON DELETE CASCADE,
    FOREIGN KEY (idProduto)     REFERENCES produtos(idProduto)
);

-- Tudo o que cada obra tira do estoque: produtos avulsos + receita dos
-- serviços vinculados. Usada na baixa/devolução e nos relatórios.
create view vw_consumo_obra as
    select idObra, idProduto, qtdProdutosObra as quantidade
    from produtosObras
    union all
    select os.idObra, osp.idProduto, osp.quantidade
    from obraServicoProdutos osp
    join obraServicos os on os.idObraServico = osp.idObraServico;

create table notasFiscais(
    idNotaFiscal   int          primary key NOT NULL AUTO_INCREMENT,
    chaveAcesso    VARCHAR(44)  NOT NULL UNIQUE,
    numero         VARCHAR(20)  NOT NULL,
    serie          VARCHAR(10),
    idFornecedor   int          NOT NULL,
    dataEmissao    DATETIME,
    valorTotal     DECIMAL(10,2) NOT NULL,
    nomeArquivo    VARCHAR(255),
    dataImportacao DATETIME     DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (idFornecedor) REFERENCES fornecedores(idFornecedor)
);

create table notaFiscalItens(
    idItem               int          primary key NOT NULL AUTO_INCREMENT,
    idNotaFiscal         int          NOT NULL,
    idProduto            int          DEFAULT NULL,
    codProdutoFornecedor VARCHAR(60),
    nomeProdutoNota      VARCHAR(255) NOT NULL,
    quantidade           DECIMAL(10,3) NOT NULL,
    valorUnitario        DECIMAL(10,4),
    valorTotal           DECIMAL(10,2),
    statusItem           VARCHAR(20)  NOT NULL DEFAULT 'pendente',

    FOREIGN KEY (idNotaFiscal) REFERENCES notasFiscais(idNotaFiscal),
    FOREIGN KEY (idProduto)    REFERENCES produtos(idProduto)
);
