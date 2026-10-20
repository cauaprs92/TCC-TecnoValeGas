-- =============================================================================
-- Dados de exemplo. Executar APÓS docs/codigo.sql (que cria o schema e o banco).
-- Gerados para desenvolvimento e apresentação do TCC — nomes, documentos,
-- custos e preços são FICTÍCIOS e devem ser trocados pelos reais da TecnoVale.
--
-- Resumo: 8 usuários | 6 fields | 6 fornecedores | 40 clientes | 50 produtos
--         13 serviços | 60 obras | 11 notas fiscais
-- =============================================================================
USE tcc;

-- As datas das obras, do histórico e das notas são RELATIVAS a @hoje: assim os
-- filtros do dashboard ("Este mês", "Últimos 12 meses"...) sempre têm dados.
-- Para congelar numa data (ex.: prints do TCC): SET @hoje = '2026-10-05';
SET @hoje = CURDATE();

-- ── Login ─────────────────────────────────────────────────────────────────────
-- Todos com a senha adm123. INSERT IGNORE: o adm já é criado pelo codigo.sql.
-- idLogin 1 adm | 2 João (Administração) | 3 Marcos, 5 Juliana (Almoxarifado)
--         4 Pedro, 6 Rafael, 7 Thiago, 8 Larissa (Obra)
INSERT IGNORE INTO login (idLogin, email, senha, nomeLogin, cargoLogin) VALUES
(1, 'adm123@gmail.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'adm', 'Administracao'),
(2, 'joao@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'João', 'Administracao'),
(3, 'marcos@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Marcos', 'Almoxarifado'),
(4, 'pedro@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Pedro', 'Obra'),
(5, 'juliana@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Juliana', 'Almoxarifado'),
(6, 'rafael@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Rafael', 'Obra'),
(7, 'thiago@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Thiago', 'Obra'),
(8, 'larissa@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Larissa', 'Obra');

-- ── Fields (técnicos responsáveis) ──────────────────────────────────────────
INSERT INTO responsavel (idResponsavel, nomeResponsavel) VALUES
(1, 'Carlos Souza'),
(2, 'Beatriz Almeida'),
(3, 'Renato Pereira'),
(4, 'Ana Carolina'),
(5, 'Diego Fernandes'),
(6, 'Patrícia Lima');

-- ── Fornecedores ──────────────────────────────────────────────────────────────
-- CNPJ só com dígitos (como a importação de NF-e grava). prazoEntregaDias entra
-- no cálculo do estoque mínimo dos produtos de cada um.
INSERT INTO fornecedores (idFornecedor, nomeFornecedor, cnpjFornecedor, prazoEntregaDias) VALUES
(1, 'Metalúrgica Vale do Aço', '11222333000181', 15),
(2, 'Fersol Equipamentos de Gás', '22333444000172', 10),
(3, 'Conexão Flex Indústria e Comércio', '33444555000163', 7),
(4, 'SafeWork Proteção Industrial', '44555666000154', 5),
(5, 'QuimGás Insumos Técnicos', '55666777000145', 12),
(6, 'Distribuidora ABC Conexões', '66777888000136', 4);

-- ── Clientes ──────────────────────────────────────────────────────────────────
-- contatoCliente e telefone2 são telefones. 33 a 40 ficam na região do ABC e
-- são atendidos pela unidade Mauá; os demais, pela unidade SJC.
INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, contatoCliente, emailCliente, telefone2, cep, rua, numero, complemento, bairro, cidade, estado) VALUES
(1, 'Caua Silva', '123.456.789-00', '(12) 98811-2233', 'caua.silva@sjcgas.com.br', '(12) 3921-4400', '12245-000', 'Rua São Sebastião', '112', 'Apto 101', 'Jardim Aquarius', 'São José dos Campos', 'SP'),
(2, 'João Vinicius Oliveira', '234.567.890-11', '(12) 99777-4455', 'joao.vinicius@sjcgas.com.br', '(12) 3878-1020', '12244-550', 'Avenida Cassiano Ricardo', '4300', 'Sala 4', 'Jardim Aquarius', 'São José dos Campos', 'SP'),
(3, 'Mateus Alves', '345.678.901-22', '(12) 99666-7788', 'mateus.alves@sjcgas.com.br', NULL, '12226-280', 'Rua Padre Francisco', '98', NULL, 'Jardim das Indústrias', 'São José dos Campos', 'SP'),
(4, 'Lúcia Martins', '456.789.012-33', '(12) 98123-4567', 'lucia.martins@sjcgas.com.br', '(12) 3207-9911', '12234-010', 'Rua Câmara', '428', NULL, 'Vila Adyana', 'São José dos Campos', 'SP'),
(5, 'Fabrício Rocha', '567.890.123-44', '(12) 98222-3344', 'fabricio.rocha@sjcgas.com.br', NULL, '12227-110', 'Rua Miguel Petroni', '78', NULL, 'Parque Industrial', 'São José dos Campos', 'SP'),
(6, 'Marina Nunes', '678.901.234-55', '(12) 98111-2233', 'marina.nunes@sjcgas.com.br', '(12) 3949-2210', '12232-150', 'Avenida Andrômeda', '5250', 'Casa 12', 'Urbanova', 'São José dos Campos', 'SP'),
(7, 'Restaurante Bom Sabor Ltda', '12.345.678/0001-90', '(12) 3234-5678', 'contato@bomsabor.com.br', '(12) 99702-1188', '12301-000', 'Rua das Flores', '123', NULL, 'Centro', 'Jacareí', 'SP'),
(8, 'Padaria São Benedito', '23.456.789/0001-01', '(12) 3123-4567', 'padaria@saobenedito.com.br', NULL, '12020-010', 'Av. Nove de Julho', '456', 'Loja A', 'Jardim Satélite', 'São José dos Campos', 'SP'),
(9, 'Indústria Têxtil Vale Ltda', '34.567.890/0001-12', '(12) 3456-7890', 'industria@textilvale.com.br', '(12) 99611-1111', '12060-000', 'Rua Industrial Norte', '789', 'Galpão 3', 'Distrito Industrial', 'São José dos Campos', 'SP'),
(10, 'Hospital Santa Casa Taubaté', '45.678.901/0001-23', '(12) 3332-1000', 'adm@santacasataubate.org.br', '(12) 99820-4455', '12020-100', 'Rua Floriano Peixoto', '100', NULL, 'Centro', 'Taubaté', 'SP'),
(11, 'Supermercado Bom Preço', '56.789.012/0001-34', '(12) 3251-8900', 'gerencia@supbompreco.com.br', '(12) 99388-0000', '12070-000', 'Av. Presidente Vargas', '1500', NULL, 'Vila Industrial', 'Taubaté', 'SP'),
(12, 'Frigorífico Vale Carnes', '67.890.123/0001-45', '(12) 3612-5400', 'compras@valecames.com.br', '(12) 99166-8800', '12400-000', 'Rod. Presidente Dutra', 'km 85', 'Galpão A', 'Zona Rural', 'Pindamonhangaba', 'SP'),
(13, 'Hotel Fazenda do Vale', '78.901.234/0001-56', '(12) 3101-2200', 'reservas@hotelfazendavale.com.br', NULL, '12220-000', 'Estrada do Vale', '5', NULL, 'Zona Rural', 'Jacareí', 'SP'),
(14, 'Colégio Dom Bosco', '89.012.345/0001-67', '(12) 3231-3300', 'secretaria@colegiodombosco.com.br', NULL, '12050-000', 'Av. João XXIII', '200', NULL, 'Centro', 'Taubaté', 'SP'),
(15, 'Churrascaria do Compadre', '90.123.456/0001-78', '(12) 3153-8700', 'churrascaria@compadre.com.br', '(12) 98389-9900', '12100-000', 'Av. Euzébio Ferreira', '900', NULL, 'Jardim Esplanada', 'Pindamonhangaba', 'SP'),
(16, 'Metalúrgica Aço Forte Ltda', '01.234.567/0001-89', '(12) 3944-7600', 'producao@acoforte.com.br', '(12) 98167-9000', '12240-000', 'Rua José Humberto Preto', '1200', 'Barracão 2', 'Distrito Industrial', 'São José dos Campos', 'SP'),
(17, 'Panificadora Delícia', '12.345.670/0001-91', '(12) 3153-4400', 'panificadora@delicia.com.br', NULL, '12600-000', 'Rua Coronel Rodrigues', '78', NULL, 'Centro', 'Lorena', 'SP'),
(18, 'Cerâmica São Paulo Ind.', '23.456.781/0001-02', '(12) 3241-9800', 'ceramica@ceramicasp.com.br', '(12) 98944-6700', '12500-000', 'Rua das Cerâmicas', '1000', NULL, 'Distrito Industrial', 'Guaratinguetá', 'SP'),
(19, 'Escola Municipal Boa Vista', '34.567.892/0001-13', '(12) 3278-4500', 'escola@boavista.edu.br', NULL, '12320-000', 'Rua José Alves', '5', NULL, 'Jardim das Palmeiras', 'Jacareí', 'SP'),
(20, 'Distribuidora GLP Norte', '45.678.903/0001-24', '(12) 3627-9000', 'distribuidora@glpnorte.com.br', '(12) 97834-5600', '12570-000', 'Av. Dom Pedro I', '350', 'Galpão 1', 'Parque Industrial', 'Guaratinguetá', 'SP'),
(21, 'Rafaela Monteiro', '567.123.890-55', '(12) 99145-2030', 'rafaela.monteiro@gmail.com', NULL, '12242-010', 'Rua Paulo Setúbal', '210', 'Casa 2', 'Jardim Esplanada', 'São José dos Campos', 'SP'),
(22, 'Gustavo Henrique Prado', '678.234.901-66', '(12) 99233-8741', 'gustavo.prado@hotmail.com', '(12) 3912-6650', '12243-260', 'Rua Icatu', '55', NULL, 'Vila Ema', 'São José dos Campos', 'SP'),
(23, 'Condomínio Residencial Aquarius', '11.987.654/0001-10', '(12) 3941-7700', 'sindico@resaquarius.com.br', '(12) 99701-3300', '12246-001', 'Av. Cassiano Ricardo', '1000', 'Bloco A', 'Jardim Aquarius', 'São José dos Campos', 'SP'),
(24, 'Pizzaria Forno a Lenha', '12.876.543/0001-21', '(12) 3916-2020', 'pedidos@fornoalenha.com.br', NULL, '12230-000', 'Rua Siqueira Campos', '321', NULL, 'Centro', 'São José dos Campos', 'SP'),
(25, 'Lavanderia Industrial Clean', '13.765.432/0001-32', '(12) 3653-1180', 'operacao@cleanlav.com.br', '(12) 98810-5522', '12280-000', 'Rua Prof. Carlos Gomes', '88', 'Galpão 1', 'Vila São Geraldo', 'Caçapava', 'SP'),
(26, 'Academia Corpo em Forma', '14.654.321/0001-43', '(12) 3354-9090', 'contato@corpoemforma.com.br', NULL, '12400-010', 'Rua Deputado Claro César', '450', NULL, 'Centro', 'Pindamonhangaba', 'SP'),
(27, 'Clínica Veterinária Bicho Feliz', '15.543.210/0001-54', '(12) 3622-4141', 'clinica@bichofeliz.vet.br', '(12) 99134-7070', '12030-000', 'Av. Independência', '1700', NULL, 'Independência', 'Taubaté', 'SP'),
(28, 'Restaurante Sabor da Serra', '16.432.109/0001-65', '(12) 3663-3030', 'saborserra@gmail.com', NULL, '12460-000', 'Av. Dr. Januário Miráglia', '2100', NULL, 'Vila Capivari', 'Campos do Jordão', 'SP'),
(29, 'Pousada Recanto das Águas', '17.321.098/0001-76', '(12) 3662-8080', 'reservas@recantodasaguas.com.br', '(12) 99611-2323', '12460-000', 'Rua Djalma Forjaz', '93', NULL, 'Vila Abernéssia', 'Campos do Jordão', 'SP'),
(30, 'Hamburgueria Brasa Viva', '18.210.987/0001-87', '(12) 3022-5656', 'contato@brasaviva.com.br', NULL, '12215-000', 'Av. Dr. Nelson D''Ávila', '389', 'Loja 3', 'Centro', 'São José dos Campos', 'SP'),
(31, 'Bruno Carvalho', '789.345.012-77', '(12) 98877-1102', 'bruno.carvalho@outlook.com', NULL, '12305-100', 'Rua Alfredo Schurig', '64', NULL, 'Jardim Paraíba', 'Jacareí', 'SP'),
(32, 'Mercado Família Costa', '19.109.876/0001-98', '(12) 3958-1414', 'compras@familiacosta.com.br', '(12) 99245-3131', '12236-000', 'Estrada Velha Rio-SP', '5800', NULL, 'Eugênio de Melo', 'São José dos Campos', 'SP'),
(33, 'Indústria Química Paulista', '20.098.765/0001-09', '(11) 4544-7000', 'manutencao@quimpaulista.com.br', '(11) 98111-7000', '09370-000', 'Av. Capitão João', '2301', 'Galpão 5', 'Jardim Zaíra', 'Mauá', 'SP'),
(34, 'Padaria Pão Dourado', '21.987.654/0001-10', '(11) 4513-2626', 'paodourado@gmail.com', NULL, '09310-000', 'Rua Rio Branco', '112', NULL, 'Centro', 'Mauá', 'SP'),
(35, 'Hospital Municipal de Mauá', '22.876.543/0001-21', '(11) 4555-9000', 'engenharia@hmmaua.sp.gov.br', '(11) 98222-9000', '09330-000', 'Av. Dom José Gaspar', '2000', NULL, 'Matriz', 'Mauá', 'SP'),
(36, 'Restaurante Cantina Italiana', '23.765.432/0001-32', '(11) 4427-3838', 'cantina@cantinaitaliana.com.br', NULL, '09015-000', 'Rua Senador Fláquer', '450', NULL, 'Centro', 'Santo André', 'SP'),
(37, 'Metalúrgica São Bernardo', '24.654.321/0001-43', '(11) 4351-6600', 'producao@metalsbc.com.br', '(11) 98333-6600', '09750-000', 'Av. Prestes Maia', '1500', 'Barracão 3', 'Centro', 'São Bernardo do Campo', 'SP'),
(38, 'Escola Estadual Prof. Lima', '25.543.210/0001-54', '(11) 4823-1010', 'escola.lima@educacao.sp.gov.br', NULL, '09400-000', 'Rua Boa Vista', '300', NULL, 'Centro', 'Ribeirão Pires', 'SP'),
(39, 'Fernanda Ribeiro', '890.456.123-88', '(11) 99412-5050', 'fernanda.ribeiro@gmail.com', NULL, '09380-000', 'Rua Manoel Pedro Júnior', '77', 'Apto 34', 'Vila Bocaina', 'Mauá', 'SP'),
(40, 'Churrascaria Gaúcha Diadema', '26.432.109/0001-65', '(11) 4057-7272', 'gerencia@gauchadiadema.com.br', '(11) 98444-7272', '09910-000', 'Av. Antônio Piranga', '900', NULL, 'Centro', 'Diadema', 'SP');

-- ── Produtos ──────────────────────────────────────────────────────────────────
-- qtdProduto = estoque atual | o estoque mínimo é calculado (ver docs/codigo.sql)
-- custoUnitario e margemPercentual são FICTÍCIOS — substituir pelos valores
-- reais da TecnoVale Gás. Preço de venda = custo × (1 + margem).
-- Margem NULL = margem padrão do sistema (30%): os EPIs 39–42 usam a padrão,
-- os demais têm margem própria. O produto 45 fica sem custo de propósito,
-- para mostrar na tela um produto ainda sem preço de venda.
INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMaxima, custoUnitario, margemPercentual) VALUES
(1,  'Tubo Aço Galvanizado 1"',           180, 'Tubo rígido galvanizado para rede de gás', 500,   22.00, 35),
(2,  'Registro de Esfera 3/4"',            95, 'Registro de esfera para gás com vedação reforçada', 300,   32.00, 40),
(3,  'Medidor de Gás Industrial G16',       8, 'Medidor para instalação industrial de gás natural',  50,  380.00, 25),
(4,  'Válvula Redutora de Pressão',         55, 'Válvula reguladora de pressão para rede de gás', 200,   85.00, 35),
(5,  'Mangueira Flexível 3/4"',             42, 'Mangueira flexível para conexão de gás', 300,   28.00, 40),
(6,  'Cinta de Fixação Metálica',          150, 'Cinta metálica para fixação de tubulações', 500,    4.50, 50),
(7,  'Tubo PPR 32mm',                       63, 'Tubo de polipropileno para água e gás', 200,   18.00, 35),
(8,  'Filtro de Linha para Gás',            67, 'Filtro de linha de proteção para rede de gás', 150,   65.00, 35),
(9,  'Conector Curvo 90° 1/2"',            120, 'Conector em curva para tubulação de gás', 300,    9.00, 45),
(10, 'Adaptador Rosca 1/2" x 3/4"',       144, 'Adaptador de rosca para composições mistas', 500,    7.50, 45),
(11, 'Lanterna de Inspeção Antichama',      18, 'Lanterna para inspeção com proteção antichama',  80,  120.00, 30),
(12, 'Detector de Vazão Portátil',           4, 'Detector portátil para vazamentos de gás',  40,  650.00, 25),
(13, 'Regulador de Pressão 1ª Família',     72, 'Regulador para GLP residencial, saída 2,8 kPa', 200,   48.00, 40),
(14, 'Regulador de Pressão 2ª Família',     48, 'Regulador para GLP industrial, saída 15 kPa', 150,  135.00, 35),
(15, 'Mangueira GLP 1,20m Certificada',     85, 'Mangueira certificada INMETRO para botijão residencial', 300,   22.00, 45),
(16, 'Abraçadeira Metálica 3/4"',          200, 'Abraçadeira para fixação de mangueiras e tubos 3/4"', 600,    3.20, 50),
(17, 'Válvula de Alívio 1/2" 1,5 kgf',     36, 'Válvula de alívio de segurança para sistemas de GLP', 100,   58.00, 35),
(18, 'Luva de Redução 3/4" x 1/2"',       160, 'Luva de redução roscada galvanizada', 500,    6.80, 45),
(19, 'Niple Duplo 1/2"',                   175, 'Niple duplo galvanizado para conexões de gás', 600,    5.40, 45),
(20, 'Tê 1/2" Galvanizado',               130, 'Tê roscado para ramificações em redes de gás', 400,    7.90, 45),
(21, 'Joelho 90° 1/2" Galvanizado',       145, 'Joelho 90° roscado para mudança de direção', 500,    6.50, 45),
(22, 'Joelho 90° 3/4" Galvanizado',       110, 'Joelho 90° roscado 3/4" para tubulações de gás', 400,    9.80, 45),
(23, 'Tampão Macho 1/2"',                  90, 'Tampão macho roscado para fechamento de pontos de gás', 300,    4.10, 45),
(24, 'Fita Veda Rosca 18mm x 50m',         95, 'Fita PTFE para vedação de roscas em instalações de gás', 300,    6.90, 50),
(25, 'Selante para GLP 250ml',              58, 'Selante líquido específico para vedação de conexões GLP', 200,   34.00, 40),
(26, 'Detector de Gás Natural/GLP',         22, 'Detector fixo de vazamento de gás para ambientes internos', 100,  210.00, 30),
(27, 'Extintor CO2 6kg',                    15, 'Extintor de dióxido de carbono para áreas de equipamentos',  50,  480.00, 20),
(28, 'Extintor Pó Químico Seco 4kg',        19, 'Extintor ABC 4kg para uso geral em obras e instalações',  60,  145.00, 25),
(29, 'Manômetro 0-4 kgf/cm² 1/4"',         33, 'Manômetro para aferição de pressão em redes de GLP', 100,   72.00, 35),
(30, 'Manifold GLP 4 Saídas',              17, 'Manifold para distribuição simultânea de GLP, 4 saídas',  40,  390.00, 30),
(31, 'Tubo Flexível Metálico 1m',           38, 'Tubo flexível de aço inox corrugado para fogões industriais', 100,   68.00, 35),
(32, 'Tubo Flexível Metálico 2m',           25, 'Tubo flexível de aço inox corrugado 2m para uso geral',  80,  112.00, 35),
(33, 'Conector Rápido GLP 1/2"',            62, 'Engate rápido para mangueiras de GLP, 1/2"', 200,   39.00, 40),
(34, 'Válvula Solenóide GLP 1/2" 220V',    13, 'Válvula solenóide 220V para corte automático de GLP',  30,  320.00, 30),
(35, 'Filtro de GLP Inline 3/4"',           40, 'Filtro de impurezas inline para linhas de GLP 3/4"', 120,   88.00, 35),
(36, 'Queimador Industrial 50.000 BTU',     11, 'Queimador a gás para uso industrial, 50.000 BTU/h',  30,  980.00, 25),
(37, 'Queimador Industrial 100.000 BTU',     7, 'Queimador a gás de alta potência para fornos industriais',  20, 1650.00, 25),
(38, 'Kit Reparo de Regulador GLP',         42, 'Kit com vedações e mola para manutenção de reguladores', 150,   45.00, 40),
(39, 'Capacete de Segurança CA',            28, 'Capacete de proteção com certificado INMETRO',  60,   38.00, NULL),
(40, 'Óculos de Segurança Incolor',         35, 'Óculos de proteção com lente incolor e vedação lateral',  80,   14.00, NULL),
(41, 'Luva de Couro Cano Longo',            20, 'Luva de couro para trabalhos com gás e maçarico',  50,   29.00, NULL),
(42, 'Bota de Segurança Bico de Aço',       16, 'Bota impermeável com bico de aço para trabalhos em campo',  40,  145.00, NULL),
(43, 'Tubo de Cobre 1/2" (metro)',          220, 'Tubo de cobre mole 1/2" para instalações de gás, por metro', 800,   42.00, 35),
(44, 'Cano de Aço Preto 1/2" (metro)',     185, 'Cano de aço preto 1/2" para redes internas, por metro', 600,   19.00, 35),
(45, 'Medidor de Gás Residencial G4',       30, 'Medidor volumétrico para instalações residenciais e comerciais', 100,    NULL, NULL),
(46, 'Central GLP Compacta P13 (2 cilindros)', 9, 'Abrigo e coletor para 2 cilindros P13, uso residencial', 30, 640.00, 30),
(47, 'Abrigo Metálico para Medidor', 24, 'Caixa metálica com visor para proteção de medidor', 80, 95.00, 40),
(48, 'Tubo Multicamada PEX-AL-PEX 16mm (m)', 300, 'Tubo multicamada para gás, por metro', 900, 14.50, 40),
(49, 'Conexão Prensar PEX 16mm', 210, 'Conexão de prensar para tubo multicamada 16mm', 600, 11.20, 45),
(50, 'Placa de Sinalização "Gás Inflamável"', 60, 'Placa de advertência para centrais de GLP', 150, 18.00, 50);

-- ── Fornecedor de cada produto ────────────────────────────────────────────────
-- Vincula por nomeProduto/nomeFornecedor para não depender da ordem/IDs de quem
-- rodar este script (mesmo padrão usado na receita de servicoProdutos abaixo).
-- SQL_SAFE_UPDATES desligado pelo mesmo motivo do UPDATE de valorObra no fim
-- deste arquivo: o WHERE usa nomeProduto, não a chave primária.
SET SQL_SAFE_UPDATES = 0;

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'Metalúrgica Vale do Aço'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Tubo Aço Galvanizado 1"', 'Cinta de Fixação Metálica', 'Tubo PPR 32mm',
  'Conector Curvo 90° 1/2"', 'Adaptador Rosca 1/2" x 3/4"', 'Abraçadeira Metálica 3/4"',
  'Luva de Redução 3/4" x 1/2"', 'Niple Duplo 1/2"', 'Tê 1/2" Galvanizado',
  'Joelho 90° 1/2" Galvanizado', 'Joelho 90° 3/4" Galvanizado', 'Tampão Macho 1/2"',
  'Tubo de Cobre 1/2" (metro)', 'Cano de Aço Preto 1/2" (metro)'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'Fersol Equipamentos de Gás'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Registro de Esfera 3/4"', 'Medidor de Gás Industrial G16', 'Válvula Redutora de Pressão',
  'Filtro de Linha para Gás', 'Detector de Vazão Portátil', 'Regulador de Pressão 1ª Família',
  'Regulador de Pressão 2ª Família', 'Válvula de Alívio 1/2" 1,5 kgf', 'Detector de Gás Natural/GLP',
  'Manômetro 0-4 kgf/cm² 1/4"', 'Manifold GLP 4 Saídas', 'Válvula Solenóide GLP 1/2" 220V',
  'Filtro de GLP Inline 3/4"', 'Queimador Industrial 50.000 BTU', 'Queimador Industrial 100.000 BTU',
  'Medidor de Gás Residencial G4', 'Central GLP Compacta P13 (2 cilindros)', 'Abrigo Metálico para Medidor'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'Conexão Flex Indústria e Comércio'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Mangueira Flexível 3/4"', 'Mangueira GLP 1,20m Certificada', 'Tubo Flexível Metálico 1m',
  'Tubo Flexível Metálico 2m', 'Conector Rápido GLP 1/2"', 'Tubo Multicamada PEX-AL-PEX 16mm (m)',
  'Conexão Prensar PEX 16mm'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'SafeWork Proteção Industrial'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Lanterna de Inspeção Antichama', 'Extintor CO2 6kg', 'Extintor Pó Químico Seco 4kg',
  'Capacete de Segurança CA', 'Óculos de Segurança Incolor', 'Luva de Couro Cano Longo',
  'Bota de Segurança Bico de Aço', 'Placa de Sinalização "Gás Inflamável"'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'QuimGás Insumos Técnicos'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Fita Veda Rosca 18mm x 50m', 'Selante para GLP 250ml', 'Kit Reparo de Regulador GLP'
);

SET SQL_SAFE_UPDATES = 1;

-- Prazo de entrega próprio (sobrepõe o do fornecedor) — itens importados ou
-- sob encomenda demoram mais que o resto do catálogo do fornecedor.
UPDATE produtos SET prazoEntregaDias = 30 WHERE idProduto IN (36, 37);
UPDATE produtos SET prazoEntregaDias = 20 WHERE idProduto IN (3, 30, 46);

-- ── Serviços ──────────────────────────────────────────────────────────────────
-- fornecedorServico usa o DEFAULT da tabela ('Tecnovale Gás'). Todos os preços
-- cobrem o custo do material da receita (o sistema não aceita margem negativa).
INSERT INTO servicos (idServico, nomeServico, precoServico) VALUES
(1, 'Instalação de Ramal Residencial', 850.00),
(2, 'Instalação de Ramal Comercial', 1450.00),
(3, 'Manutenção Preventiva de Medidor', 320.00),
(4, 'Correção de Vazamento', 480.00),
(5, 'Troca de Registro e Conector', 210.00),
(6, 'Extensão de Rede Comercial', 1200.00),
(7, 'Instalação de Medidor Privativo', 690.00),
(8, 'Vistoria e Laudo Técnico', 380.00),
(9, 'Instalação de Central GLP P45', 2400.00),
(10, 'Instalação de Fogão Industrial', 650.00),
(11, 'Instalação de Detector com Corte Automático', 890.00),
(12, 'Teste de Estanqueidade', 290.00),
(13, 'Substituição de Regulador GLP', 260.00);

-- Receita de cada serviço (o que ele consome do estoque). 8 e 12 são só mão de obra.
INSERT INTO servicoProdutos (idServico, idProduto, quantidade) VALUES
-- 1 Instalação de Ramal Residencial
(1, 1, 10), (1, 2, 1), (1, 4, 1), (1, 5, 2), (1, 6, 4),
-- 2 Instalação de Ramal Comercial
(2, 1, 25), (2, 2, 2), (2, 3, 1), (2, 4, 1), (2, 6, 10),
-- 3 Manutenção Preventiva de Medidor
(3, 8, 1),
-- 4 Correção de Vazamento
(4, 5, 1), (4, 6, 3), (4, 2, 1),
-- 5 Troca de Registro e Conector
(5, 2, 1), (5, 9, 1),
-- 6 Extensão de Rede Comercial
(6, 1, 18), (6, 7, 8), (6, 6, 12), (6, 4, 1),
-- 7 Instalação de Medidor Privativo
(7, 3, 1), (7, 2, 1), (7, 8, 1),
-- 9 Instalação de Central GLP P45
(9, 30, 1), (9, 14, 2), (9, 43, 12), (9, 17, 1), (9, 29, 1), (9, 50, 1),
-- 10 Instalação de Fogão Industrial
(10, 31, 2), (10, 33, 2), (10, 2, 1), (10, 24, 1),
-- 11 Instalação de Detector com Corte Automático
(11, 26, 1), (11, 34, 1),
-- 13 Substituição de Regulador GLP
(13, 13, 1), (13, 15, 1), (13, 16, 2);

-- ── Obras ─────────────────────────────────────────────────────────────────────
-- tipoObra, unidadeObra, clientePrimario e setorObra usam exatamente as opções
-- dos <select> do formulário de obra. emailContato e celulares vêm do cliente.
-- Status: Concluida(38) | Em andamento(10) | Pausada(6) | À iniciar(4) | Cancelada(2)
INSERT INTO obras (idObra, codCliente, descObra, dataInicio, dataFim, statusObra, respObra, obsObra, orientacaoObra, tipoObra, clientePrimario, fieldObra, unidadeObra, emailContato, celular1, celular2, setorObra) VALUES
-- 1 — Concluida
(1, 1, 'Instalação de ramal de gás em condomínio residencial', @hoje - INTERVAL 214 DAY, @hoje - INTERVAL 191 DAY, 'Concluida', 'Carlos Souza', 'Testes de estanqueidade aprovados', 'Revisar juntas e conexões', 'Instalação', 'Supergásbras', 'Gás Canalizado', 'SJC', 'caua.silva@sjcgas.com.br', '(12) 98811-2233', '(12) 3921-4400', 'Residencial'),
-- 2 — Concluida
(2, 1, 'Manutenção preventiva em medidor industrial', @hoje - INTERVAL 207 DAY, @hoje - INTERVAL 193 DAY, 'Concluida', 'Beatriz Almeida', 'Relatório enviado ao cliente', 'Confirmar próxima visita em 6 meses', 'Manutenção', 'Supergásbras', 'Medidor', 'SJC', 'caua.silva@sjcgas.com.br', '(12) 98811-2233', '(12) 3921-4400', 'Industrial'),
-- 3 — Concluida
(3, 2, 'Extensão de rede de gás em restaurante na região central', @hoje - INTERVAL 199 DAY, @hoje - INTERVAL 155 DAY, 'Concluida', 'Renato Pereira', 'Liberação da prefeitura obtida', 'Agendar início após autorização', 'Instalação', 'Supergásbras', 'Rede de Gás', 'SJC', 'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', '(12) 3878-1020', 'Comercial'),
-- 4 — Concluida
(4, 2, 'Correção de vazamento em cozinha industrial', @hoje - INTERVAL 191 DAY, @hoje - INTERVAL 163 DAY, 'Concluida', 'Ana Carolina', 'Válvula substituída e teste OK', 'Registrar em manutenção preventiva', 'Manutenção', 'Supergásbras', 'Gás Natural', 'SJC', 'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', '(12) 3878-1020', 'Industrial'),
-- 5 — Concluida
(5, 3, 'Instalação de medidor privativo em prédio comercial', @hoje - INTERVAL 183 DAY, @hoje - INTERVAL 133 DAY, 'Concluida', 'Carlos Souza', 'Peças entregues e instalação concluída', 'Revisar cronograma com fornecedor', 'Instalação', 'Supergásbras', 'Medidor', 'SJC', 'mateus.alves@sjcgas.com.br', '(12) 99666-7788', NULL, 'Comercial'),
-- 6 — Concluida
(6, 3, 'Troca de registro e conector em unidade logística', @hoje - INTERVAL 175 DAY, @hoje - INTERVAL 154 DAY, 'Concluida', 'Beatriz Almeida', 'Obra entregue com novo certificado', 'Enviar notas fiscais', 'Troca de Equipamento', 'Supergásbras', 'Conector', 'SJC', 'mateus.alves@sjcgas.com.br', '(12) 99666-7788', NULL, 'Comercial'),
-- 7 — Pausada
(7, 4, 'Instalação de ramal de gás para cozinha de pizzaria', @hoje - INTERVAL 166 DAY, NULL, 'Pausada', 'Renato Pereira', 'Aguardando liberação do alvará de obra', 'Retomar após regularização', 'Instalação', 'Supergásbras', 'Gás Canalizado', 'SJC', 'lucia.martins@sjcgas.com.br', '(12) 98123-4567', '(12) 3207-9911', 'Comercial'),
-- 8 — Concluida
(8, 5, 'Revisão geral de rede de gás na unidade fabril', @hoje - INTERVAL 157 DAY, @hoje - INTERVAL 117 DAY, 'Concluida', 'Ana Carolina', 'Painel de controle atualizado', 'Arquivar laudos de teste', 'Manutenção', 'Supergásbras', 'Rede de Gás', 'SJC', 'fabricio.rocha@sjcgas.com.br', '(12) 98222-3344', NULL, 'Ambiental'),
-- 9 — Em andamento
(9, 6, 'Projeto de ramal de gás para nova loja de estética', @hoje - INTERVAL 147 DAY, NULL, 'Em andamento', 'Carlos Souza', 'Levantamento concluído, execução em curso', 'Enviar orçamento final ao cliente', 'Instalação', 'Supergásbras', 'Projeto', 'SJC', 'marina.nunes@sjcgas.com.br', '(12) 98111-2233', '(12) 3949-2210', 'Comercial'),
-- 10 — Concluida
(10, 7, 'Instalação de rede GLP para cozinha industrial', @hoje - INTERVAL 137 DAY, @hoje - INTERVAL 123 DAY, 'Concluida', 'Renato Pereira', 'Instalação conforme ABNT NBR 15526', 'Utilizar tubulação de cobre 1/2"', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'contato@bomsabor.com.br', '(12) 3234-5678', '(12) 99702-1188', 'Comercial'),
-- 11 — Em andamento
(11, 8, 'Substituição de reguladores e mangueiras GLP', @hoje - INTERVAL 122 DAY, NULL, 'Em andamento', 'Carlos Souza', 'Aguardando chegada dos reguladores novos', 'Confirmar entrega com fornecedor', 'Troca de Equipamento', 'Supergásbras', 'GLP', 'SJC', 'padaria@saobenedito.com.br', '(12) 3123-4567', NULL, 'Comercial'),
-- 12 — Concluida
(12, 9, 'Projeto de instalação GLP industrial - fase 1', @hoje - INTERVAL 108 DAY, @hoje - INTERVAL 65 DAY, 'Concluida', 'Beatriz Almeida', 'Projeto aprovado pela concessionária', 'Pressão de operação: 0,5 kgf/cm²', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'industria@textilvale.com.br', '(12) 3456-7890', '(12) 99611-1111', 'Industrial'),
-- 13 — Concluida
(13, 10, 'Vistoria anual da central de GLP hospitalar', @hoje - INTERVAL 94 DAY, @hoje - INTERVAL 94 DAY, 'Concluida', 'Ana Carolina', 'Aprovada; válvula de segurança substituída', NULL, 'Vistoria', 'Supergásbras', 'GLP', 'SJC', 'adm@santacasataubate.org.br', '(12) 3332-1000', '(12) 99820-4455', 'Judicial'),
-- 14 — Pausada
(14, 11, 'Adequação da rede GLP - setor de padaria', @hoje - INTERVAL 76 DAY, NULL, 'Pausada', 'Carlos Souza', 'Obra suspensa por reforma no teto do setor', 'Retomar após conclusão da reforma', 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'gerencia@supbompreco.com.br', '(12) 3251-8900', '(12) 99388-0000', 'Comercial'),
-- 15 — Concluida
(15, 12, 'Instalação industrial GLP - câmara fria', @hoje - INTERVAL 62 DAY, @hoje - INTERVAL 12 DAY, 'Concluida', 'Renato Pereira', 'Sistema de aquecimento de câmara fria OK', 'Pressão industrial: 1,5 kgf/cm²', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'compras@valecames.com.br', '(12) 3612-5400', '(12) 99166-8800', 'Industrial'),
-- 16 — Em andamento
(16, 13, 'Revisão e adequação central GLP - hotel', @hoje - INTERVAL 51 DAY, NULL, 'Em andamento', 'Beatriz Almeida', 'Substituição de válvulas em curso', 'Adequar conforme NR-13', 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'reservas@hotelfazendavale.com.br', '(12) 3101-2200', NULL, 'Comercial'),
-- 17 — Concluida
(17, 14, 'Instalação de rede GLP para cantina escolar', @hoje - INTERVAL 42 DAY, @hoje - INTERVAL 4 DAY, 'Concluida', 'Ana Carolina', 'Fogão 6 bocas instalado', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'secretaria@colegiodombosco.com.br', '(12) 3231-3300', NULL, 'Comercial'),
-- 18 — Cancelada
(18, 15, 'Instalação de rede GLP para churrasqueiras - lote 1', @hoje - INTERVAL 37 DAY, NULL, 'Cancelada', 'Carlos Souza', 'Cliente cancelou por mudança no projeto', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'churrascaria@compadre.com.br', '(12) 3153-8700', '(12) 98389-9900', 'Comercial'),
-- 19 — Concluida
(19, 16, 'Instalação de rede GLP para solda a gás', @hoje - INTERVAL 33 DAY, @hoje - INTERVAL 3 DAY, 'Concluida', 'Renato Pereira', 'Pontos de GLP para 6 postos de solda', 'Alta pressão de operação', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'producao@acoforte.com.br', '(12) 3944-7600', '(12) 98167-9000', 'Industrial'),
-- 20 — Pausada
(20, 17, 'Instalação de fornos e fogões a GLP', @hoje - INTERVAL 30 DAY, NULL, 'Pausada', 'Beatriz Almeida', 'Equipamentos aguardando entrega do fornecedor', 'Confirmar prazo de entrega', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'panificadora@delicia.com.br', '(12) 3153-4400', NULL, 'Comercial'),
-- 21 — Concluida
(21, 18, 'Instalação de forno industrial a gás cerâmica', @hoje - INTERVAL 27 DAY, @hoje - INTERVAL 1 DAY, 'Concluida', 'Carlos Souza', 'Queimadores de 100.000 BTU/h instalados', 'Temp. máxima: 1200°C', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'ceramica@ceramicasp.com.br', '(12) 3241-9800', '(12) 98944-6700', 'Industrial'),
-- 22 — Em andamento
(22, 19, 'Instalação de GLP para cozinha escolar', @hoje - INTERVAL 20 DAY, NULL, 'Em andamento', 'Ana Carolina', 'Tubulação instalada, aguardando ligação final', 'Coordenar com equipe elétrica', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'escola@boavista.edu.br', '(12) 3278-4500', NULL, 'Comercial'),
-- 23 — Concluida
(23, 20, 'Ampliação da central de GLP - depósito 2', @hoje - INTERVAL 14 DAY, @hoje, 'Concluida', 'Renato Pereira', 'Nova central com capacidade 12 botijões P45', NULL, 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'distribuidora@glpnorte.com.br', '(12) 3627-9000', '(12) 97834-5600', 'Industrial'),
-- 24 — Em andamento
(24, 1, 'Manutenção corretiva - revisão geral pós-vistoria', @hoje - INTERVAL 8 DAY, NULL, 'Em andamento', 'Carlos Souza', 'Aguardando laudo de estanqueidade', 'Emitir relatório técnico ao cliente', 'Manutenção', 'Supergásbras', 'GLP', 'SJC', 'caua.silva@sjcgas.com.br', '(12) 98811-2233', '(12) 3921-4400', 'Industrial'),
-- 25 — À iniciar
(25, 10, 'Revisão semestral central de GLP hospitalar', @hoje + INTERVAL 10 DAY, NULL, 'À iniciar', 'Beatriz Almeida', 'Agendada; aguardando confirmação do hospital', 'Verificar normas ANVISA vigentes', 'Vistoria', 'Supergásbras', 'GLP', 'SJC', 'adm@santacasataubate.org.br', '(12) 3332-1000', '(12) 99820-4455', 'ART'),
-- 26 — Em andamento
(26, 9, 'Projeto de instalação GLP industrial - fase 2', @hoje - INTERVAL 4 DAY, NULL, 'Em andamento', 'Ana Carolina', 'Execução do setor de acabamento em curso', 'Integrar com rede existente da fase 1', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'industria@textilvale.com.br', '(12) 3456-7890', '(12) 99611-1111', 'Industrial'),
-- 27 — À iniciar
(27, 12, 'Manutenção preventiva anual - frigorífico', @hoje + INTERVAL 17 DAY, NULL, 'À iniciar', 'Carlos Souza', 'Programada; aguardando confirmação do cliente', 'Revisar todo o sistema de GLP', 'Manutenção', 'Supergásbras', 'GLP', 'SJC', 'compras@valecames.com.br', '(12) 3612-5400', '(12) 99166-8800', 'Industrial'),
-- 28 — Pausada
(28, 11, 'Instalação GLP - nova seção de frios supermercado', @hoje - INTERVAL 2 DAY, NULL, 'Pausada', 'Renato Pereira', 'Obra embargada por fiscalização municipal', 'Resolver pendência com a prefeitura', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'gerencia@supbompreco.com.br', '(12) 3251-8900', '(12) 99388-0000', 'Comercial'),
-- 29 — Em andamento
(29, 16, 'Ampliação da rede de GLP industrial - novo setor', @hoje - INTERVAL 1 DAY, NULL, 'Em andamento', 'Beatriz Almeida', 'Integrar com rede existente', 'Novo setor de produção em expansão', 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'producao@acoforte.com.br', '(12) 3944-7600', '(12) 98167-9000', 'Industrial'),
-- 30 — Pausada
(30, 15, 'Instalação de novo setor de churrasco - expansão', @hoje, NULL, 'Pausada', 'Carlos Souza', 'Cliente solicitou pausa para adequação civil', 'Aguardar liberação do cliente', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'churrascaria@compadre.com.br', '(12) 3153-8700', '(12) 98389-9900', 'Comercial'),
-- 31 — Concluida
(31, 21, 'Instalação de ramal residencial em casa térrea', @hoje - INTERVAL 350 DAY, @hoje - INTERVAL 338 DAY, 'Concluida', 'Beatriz Almeida', 'Serviço entregue e testado', 'Combinar horário com a moradora', 'Instalação', 'Supergásbras', 'Gás Canalizado', 'SJC', 'rafaela.monteiro@gmail.com', '(12) 99145-2030', NULL, 'Residencial'),
-- 32 — Concluida
(32, 22, 'Troca de regulador e mangueira em apartamento', @hoje - INTERVAL 330 DAY, @hoje - INTERVAL 327 DAY, 'Concluida', 'Renato Pereira', 'Cliente assinou o termo de entrega', NULL, 'Troca de Equipamento', 'Supergásbras', 'GLP', 'SJC', 'gustavo.prado@hotmail.com', '(12) 99233-8741', '(12) 3912-6650', 'Residencial'),
-- 33 — Concluida
(33, 23, 'Instalação de medidores individuais no condomínio', @hoje - INTERVAL 318 DAY, @hoje - INTERVAL 273 DAY, 'Concluida', 'Ana Carolina', 'Instalação conforme NBR 15526', 'Executar por bloco, um por semana', 'Instalação', 'Supergásbras', 'Medidor', 'SJC', 'sindico@resaquarius.com.br', '(12) 3941-7700', '(12) 99701-3300', 'Residencial'),
-- 34 — Concluida
(34, 24, 'Instalação de forno de pizza a gás', @hoje - INTERVAL 301 DAY, @hoje - INTERVAL 295 DAY, 'Concluida', 'Diego Fernandes', 'Instalação conforme NBR 15526', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'pedidos@fornoalenha.com.br', '(12) 3916-2020', NULL, 'Comercial'),
-- 35 — Concluida
(35, 25, 'Rede de gás para secadoras industriais', @hoje - INTERVAL 288 DAY, @hoje - INTERVAL 258 DAY, 'Concluida', 'Patrícia Lima', 'Serviço entregue e testado', 'Pressão de operação: 1,0 kgf/cm²', 'Instalação', 'Supergásbras', 'Gás Natural', 'SJC', 'operacao@cleanlav.com.br', '(12) 3653-1180', '(12) 98810-5522', 'Industrial'),
-- 36 — Concluida
(36, 26, 'Instalação de aquecedor de água a gás - vestiários', @hoje - INTERVAL 270 DAY, @hoje - INTERVAL 261 DAY, 'Concluida', 'Carlos Souza', 'Teste de estanqueidade aprovado', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'contato@corpoemforma.com.br', '(12) 3354-9090', NULL, 'Comercial'),
-- 37 — Concluida
(37, 27, 'Instalação de detector de vazamento com corte automático', @hoje - INTERVAL 255 DAY, @hoje - INTERVAL 251 DAY, 'Concluida', 'Beatriz Almeida', 'Instalação conforme NBR 15526', 'Testar o corte com o técnico da clínica', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'clinica@bichofeliz.vet.br', '(12) 3622-4141', '(12) 99134-7070', 'Comercial'),
-- 38 — Concluida
(38, 28, 'Vistoria anual da central de GLP', @hoje - INTERVAL 240 DAY, @hoje - INTERVAL 239 DAY, 'Concluida', 'Renato Pereira', 'Instalação conforme NBR 15526', NULL, 'Vistoria', 'Supergásbras', 'GLP', 'SJC', 'saborserra@gmail.com', '(12) 3663-3030', NULL, 'Comercial'),
-- 39 — Concluida
(39, 29, 'Central GLP P45 para cozinha da pousada', @hoje - INTERVAL 226 DAY, @hoje - INTERVAL 211 DAY, 'Concluida', 'Ana Carolina', 'Instalação conforme NBR 15526', 'Acesso pela rua dos fundos', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'reservas@recantodasaguas.com.br', '(12) 3662-8080', '(12) 99611-2323', 'Comercial'),
-- 40 — Concluida
(40, 30, 'Instalação de chapa e fritadeiras a gás', @hoje - INTERVAL 212 DAY, @hoje - INTERVAL 205 DAY, 'Concluida', 'Diego Fernandes', 'Laudo entregue ao cliente', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'contato@brasaviva.com.br', '(12) 3022-5656', NULL, 'Comercial'),
-- 41 — Concluida
(41, 31, 'Instalação de fogão e aquecedor residencial', @hoje - INTERVAL 198 DAY, @hoje - INTERVAL 193 DAY, 'Concluida', 'Patrícia Lima', 'Instalação conforme NBR 15526', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'bruno.carvalho@outlook.com', '(12) 98877-1102', NULL, 'Residencial'),
-- 42 — Cancelada
(42, 32, 'Adequação da rede de gás da padaria do mercado', @hoje - INTERVAL 185 DAY, NULL, 'Cancelada', 'Carlos Souza', 'Cliente desistiu do serviço', 'Trabalhar fora do horário de pico', 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'compras@familiacosta.com.br', '(12) 3958-1414', '(12) 99245-3131', 'Comercial'),
-- 43 — Concluida
(43, 33, 'Rede de gás natural para caldeira - linha 2', @hoje - INTERVAL 171 DAY, @hoje - INTERVAL 136 DAY, 'Concluida', 'Beatriz Almeida', 'Instalação conforme NBR 15526', 'Pressão de operação: 2,0 kgf/cm²', 'Instalação', 'Supergásbras', 'Gás Natural', 'Mauá', 'manutencao@quimpaulista.com.br', '(11) 4544-7000', '(11) 98111-7000', 'Industrial'),
-- 44 — Concluida
(44, 34, 'Troca de reguladores da central de GLP', @hoje - INTERVAL 160 DAY, @hoje - INTERVAL 156 DAY, 'Concluida', 'Renato Pereira', 'Laudo entregue ao cliente', NULL, 'Troca de Equipamento', 'Supergásbras', 'GLP', 'Mauá', 'paodourado@gmail.com', '(11) 4513-2626', NULL, 'Comercial'),
-- 45 — Concluida
(45, 35, 'Manutenção preventiva das redes de gás hospitalares', @hoje - INTERVAL 148 DAY, @hoje - INTERVAL 138 DAY, 'Concluida', 'Ana Carolina', 'Teste de estanqueidade aprovado', 'Seguir protocolo de acesso da CCIH', 'Manutenção', 'Supergásbras', 'GLP', 'Mauá', 'engenharia@hmmaua.sp.gov.br', '(11) 4555-9000', '(11) 98222-9000', 'Comercial'),
-- 46 — Concluida
(46, 36, 'Instalação de fogões industriais na cantina', @hoje - INTERVAL 133 DAY, @hoje - INTERVAL 125 DAY, 'Concluida', 'Diego Fernandes', 'Serviço entregue e testado', NULL, 'Instalação', 'Supergásbras', 'GLP', 'Mauá', 'cantina@cantinaitaliana.com.br', '(11) 4427-3838', NULL, 'Comercial'),
-- 47 — Concluida
(47, 37, 'Rede de gás para estufa de pintura', @hoje - INTERVAL 120 DAY, @hoje - INTERVAL 92 DAY, 'Concluida', 'Patrícia Lima', 'Instalação conforme NBR 15526', 'Integrar com a automação da estufa', 'Instalação', 'Supergásbras', 'Gás Natural', 'Mauá', 'producao@metalsbc.com.br', '(11) 4351-6600', '(11) 98333-6600', 'Industrial'),
-- 48 — Concluida
(48, 38, 'Instalação de gás na cozinha da escola', @hoje - INTERVAL 104 DAY, @hoje - INTERVAL 92 DAY, 'Concluida', 'Carlos Souza', 'Serviço entregue e testado', NULL, 'Instalação', 'Supergásbras', 'GLP', 'Mauá', 'escola.lima@educacao.sp.gov.br', '(11) 4823-1010', NULL, 'Comercial'),
-- 49 — Concluida
(49, 39, 'Conversão de fogão para gás natural', @hoje - INTERVAL 92 DAY, @hoje - INTERVAL 90 DAY, 'Concluida', 'Beatriz Almeida', 'Serviço entregue e testado', NULL, 'Outros', 'Supergásbras', 'Gás Natural', 'Mauá', 'fernanda.ribeiro@gmail.com', '(11) 99412-5050', NULL, 'Residencial'),
-- 50 — Concluida
(50, 40, 'Laudo de estanqueidade para renovação do AVCB', @hoje - INTERVAL 80 DAY, @hoje - INTERVAL 79 DAY, 'Concluida', 'Renato Pereira', 'Cliente assinou o termo de entrega', 'Entregar laudo assinado com ART', 'Vistoria', 'Supergásbras', 'GLP', 'Mauá', 'gerencia@gauchadiadema.com.br', '(11) 4057-7272', '(11) 98444-7272', 'Judicial'),
-- 51 — Concluida
(51, 1, 'Revisão do ramal após reforma da cozinha', @hoje - INTERVAL 66 DAY, @hoje - INTERVAL 60 DAY, 'Concluida', 'Ana Carolina', 'Serviço entregue e testado', NULL, 'Manutenção', 'Supergásbras', 'Gás Canalizado', 'SJC', 'caua.silva@sjcgas.com.br', '(12) 98811-2233', '(12) 3921-4400', 'Residencial'),
-- 52 — Pausada
(52, 7, 'Ampliação da rede para novo salão', @hoje - INTERVAL 52 DAY, NULL, 'Pausada', 'Diego Fernandes', 'Aguardando aprovação do orçamento complementar', NULL, 'Reforma', 'Supergásbras', 'GLP', 'SJC', 'contato@bomsabor.com.br', '(12) 3234-5678', '(12) 99702-1188', 'Comercial'),
-- 53 — Concluida
(53, 9, 'Rede de gás para novo setor de tingimento', @hoje - INTERVAL 45 DAY, @hoje - INTERVAL 25 DAY, 'Concluida', 'Patrícia Lima', 'Serviço entregue e testado', 'Pressão de operação: 0,8 kgf/cm²', 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'industria@textilvale.com.br', '(12) 3456-7890', '(12) 99611-1111', 'Industrial'),
-- 54 — Em andamento
(54, 10, 'Instalação de detectores na central hospitalar', @hoje - INTERVAL 38 DAY, NULL, 'Em andamento', 'Carlos Souza', 'Aguardando ligação final', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'adm@santacasataubate.org.br', '(12) 3332-1000', '(12) 99820-4455', 'Comercial'),
-- 55 — Concluida
(55, 13, 'Troca dos fogões da cozinha do hotel', @hoje - INTERVAL 29 DAY, @hoje - INTERVAL 24 DAY, 'Concluida', 'Beatriz Almeida', 'Laudo entregue ao cliente', NULL, 'Troca de Equipamento', 'Supergásbras', 'GLP', 'SJC', 'reservas@hotelfazendavale.com.br', '(12) 3101-2200', NULL, 'Comercial'),
-- 56 — Em andamento
(56, 16, 'Manutenção corretiva nos pontos de solda', @hoje - INTERVAL 21 DAY, NULL, 'Em andamento', 'Renato Pereira', 'Aguardando ligação final', NULL, 'Manutenção', 'Supergásbras', 'GLP', 'SJC', 'producao@acoforte.com.br', '(12) 3944-7600', '(12) 98167-9000', 'Industrial'),
-- 57 — Concluida
(57, 20, 'Laudo técnico da central de GLP do depósito', @hoje - INTERVAL 12 DAY, @hoje - INTERVAL 11 DAY, 'Concluida', 'Ana Carolina', 'Cliente assinou o termo de entrega', 'Emitir ART junto com o laudo', 'Vistoria', 'Supergásbras', 'GLP', 'SJC', 'distribuidora@glpnorte.com.br', '(12) 3627-9000', '(12) 97834-5600', 'ART'),
-- 58 — Em andamento
(58, 3, 'Instalação de aquecedor de passagem', @hoje - INTERVAL 6 DAY, NULL, 'Em andamento', 'Diego Fernandes', 'Tubulação em execução', NULL, 'Instalação', 'Supergásbras', 'Gás Canalizado', 'SJC', 'mateus.alves@sjcgas.com.br', '(12) 99666-7788', NULL, 'Residencial'),
-- 59 — À iniciar
(59, 5, 'Ampliação da rede de gás da fábrica', @hoje + INTERVAL 5 DAY, NULL, 'À iniciar', 'Patrícia Lima', 'Material separado no almoxarifado', 'Aguardar licença ambiental', 'Reforma', 'Supergásbras', 'Gás Natural', 'SJC', 'fabricio.rocha@sjcgas.com.br', '(12) 98222-3344', NULL, 'Ambiental'),
-- 60 — À iniciar
(60, 12, 'Rede de gás para nova câmara de defumação', @hoje + INTERVAL 25 DAY, NULL, 'À iniciar', 'Carlos Souza', 'Material separado no almoxarifado', NULL, 'Instalação', 'Supergásbras', 'GLP', 'SJC', 'compras@valecames.com.br', '(12) 3612-5400', '(12) 99166-8800', 'Industrial');

-- ── Equipe das obras ─────────────────────────────────────────────────────────
-- Cada funcionário de cargo Obra só enxerga as obras em que está na equipe.
INSERT INTO obraFuncionarios (idObra, idLogin) VALUES
(3, 7),
(6, 6), (6, 7),
(7, 4),
(9, 4), (9, 7),
(11, 4),
(12, 6), (12, 7),
(14, 4), (14, 8),
(15, 7),
(16, 4), (16, 7),
(18, 6), (18, 7),
(20, 6), (20, 8),
(21, 4),
(22, 4), (22, 7), (22, 8),
(24, 4), (24, 8),
(25, 8),
(26, 4), (26, 6), (26, 8),
(27, 7),
(28, 7), (28, 8),
(29, 4), (29, 8),
(30, 4), (30, 7),
(33, 6),
(36, 4), (36, 6),
(39, 4),
(42, 6), (42, 8),
(45, 6),
(48, 4), (48, 8),
(51, 4),
(52, 7), (52, 8),
(54, 7), (54, 8),
(56, 7), (56, 8),
(57, 8),
(58, 7), (58, 8),
(59, 8),
(60, 6), (60, 8);

-- ── Produtos avulsos por obra ────────────────────────────────────────────────
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
-- 1 Instalação de ramal de gás em condomínio residencial
(1, 1, 20), (1, 5, 10), (1, 6, 15),
-- 2 Manutenção preventiva em medidor industrial
(2, 3, 1), (2, 11, 2),
-- 3 Extensão de rede de gás em restaurante na região central
(3, 2, 8), (3, 4, 5), (3, 9, 12),
-- 4 Correção de vazamento em cozinha industrial
(4, 8, 3), (4, 10, 6),
-- 5 Instalação de medidor privativo em prédio comercial
(5, 2, 4), (5, 5, 16), (5, 12, 1),
-- 6 Troca de registro e conector em unidade logística
(6, 1, 6), (6, 9, 3),
-- 7 Instalação de ramal de gás para cozinha de pizzaria
(7, 7, 22), (7, 5, 8),
-- 8 Revisão geral de rede de gás na unidade fabril
(8, 1, 5), (8, 4, 10),
-- 9 Projeto de ramal de gás para nova loja de estética
(9, 1, 4), (9, 2, 2), (9, 9, 5),
-- 10 Instalação de rede GLP para cozinha industrial
(10, 13, 2), (10, 15, 3), (10, 21, 8),
-- 11 Substituição de reguladores e mangueiras GLP
(11, 13, 2), (11, 15, 3), (11, 38, 1),
-- 12 Projeto de instalação GLP industrial - fase 1
(12, 1, 30), (12, 18, 20), (12, 20, 15), (12, 24, 5),
-- 13 Vistoria anual da central de GLP hospitalar
(13, 17, 2), (13, 29, 1), (13, 38, 2),
-- 14 Adequação da rede GLP - setor de padaria
(14, 1, 15), (14, 21, 10), (14, 33, 6),
-- 15 Instalação industrial GLP - câmara fria
(15, 14, 1), (15, 19, 20), (15, 22, 12), (15, 35, 2),
-- 16 Revisão e adequação central GLP - hotel
(16, 17, 3), (16, 25, 2), (16, 38, 3),
-- 17 Instalação de rede GLP para cantina escolar
(17, 5, 10), (17, 16, 20), (17, 21, 6),
-- 18 Instalação de rede GLP para churrasqueiras - lote 1
(18, 1, 20), (18, 19, 10), (18, 33, 8),
-- 19 Instalação de rede GLP para solda a gás
(19, 43, 30), (19, 20, 10), (19, 29, 2),
-- 20 Instalação de fornos e fogões a GLP
(20, 31, 4), (20, 13, 2), (20, 24, 3),
-- 21 Instalação de forno industrial a gás cerâmica
(21, 37, 2), (21, 14, 1), (21, 43, 15),
-- 22 Instalação de GLP para cozinha escolar
(22, 15, 2), (22, 21, 4), (22, 16, 10),
-- 23 Ampliação da central de GLP - depósito 2
(23, 14, 2), (23, 17, 4), (23, 30, 2),
-- 24 Manutenção corretiva - revisão geral pós-vistoria
(24, 15, 1), (24, 38, 1),
-- 25 Revisão semestral central de GLP hospitalar
(25, 17, 2), (25, 29, 1), (25, 38, 2),
-- 26 Projeto de instalação GLP industrial - fase 2
(26, 1, 25), (26, 18, 15), (26, 20, 12), (26, 44, 20),
-- 27 Manutenção preventiva anual - frigorífico
(27, 35, 2), (27, 25, 2), (27, 38, 3),
-- 28 Instalação GLP - nova seção de frios supermercado
(28, 1, 18), (28, 33, 6), (28, 21, 8),
-- 29 Ampliação da rede de GLP industrial - novo setor
(29, 44, 40), (29, 20, 15), (29, 22, 10),
-- 30 Instalação de novo setor de churrasco - expansão
(30, 1, 25), (30, 15, 4), (30, 36, 3),
-- 31 Instalação de ramal residencial em casa térrea
(31, 15, 1),
-- 33 Instalação de medidores individuais no condomínio
(33, 47, 12), (33, 2, 12),
-- 34 Instalação de forno de pizza a gás
(34, 13, 1),
-- 35 Rede de gás para secadoras industriais
(35, 35, 2), (35, 29, 1),
-- 36 Instalação de aquecedor de água a gás - vestiários
(36, 48, 25), (36, 49, 10), (36, 2, 2),
-- 39 Central GLP P45 para cozinha da pousada
(39, 31, 2),
-- 40 Instalação de chapa e fritadeiras a gás
(40, 33, 2),
-- 41 Instalação de fogão e aquecedor residencial
(41, 46, 1),
-- 42 Adequação da rede de gás da padaria do mercado
(42, 26, 1),
-- 43 Rede de gás natural para caldeira - linha 2
(43, 29, 2), (43, 17, 2),
-- 44 Troca de reguladores da central de GLP
(44, 14, 2),
-- 45 Manutenção preventiva das redes de gás hospitalares
(45, 38, 2),
-- 46 Instalação de fogões industriais na cantina
(46, 31, 2),
-- 47 Rede de gás para estufa de pintura
(47, 36, 1),
-- 49 Conversão de fogão para gás natural
(49, 10, 2), (49, 24, 1),
-- 51 Revisão do ramal após reforma da cozinha
(51, 5, 1),
-- 52 Ampliação da rede para novo salão
(52, 33, 2),
-- 53 Rede de gás para novo setor de tingimento
(53, 44, 30),
-- 54 Instalação de detectores na central hospitalar
(54, 26, 2),
-- 56 Manutenção corretiva nos pontos de solda
(56, 33, 4),
-- 58 Instalação de aquecedor de passagem
(58, 31, 1), (58, 2, 1),
-- 59 Ampliação da rede de gás da fábrica
(59, 8, 2),
-- 60 Rede de gás para nova câmara de defumação
(60, 37, 1);

-- Custo e preço de venda congelados no vínculo — no sistema eles são copiados
-- do produto no momento em que ele entra na obra.
SET SQL_SAFE_UPDATES = 0;
UPDATE produtosObras po
JOIN produtos p ON p.idProduto = po.idProduto
SET po.custoUnitario = p.custoUnitario,
    -- margem NULL = margem padrão (30%, MARGEM_PADRAO em precificacao.py)
    po.precoVenda    = ROUND(p.custoUnitario * (1 + COALESCE(p.margemPercentual, 30) / 100), 2);
SET SQL_SAFE_UPDATES = 1;

-- ── Serviços por obra ────────────────────────────────────────────────────────
INSERT INTO obraServicos (idObra, idServico) VALUES
(1, 1),
(2, 3),
(3, 6),
(4, 4),
(5, 7),
(6, 5),
(7, 2),
(8, 8),
(9, 2),
(10, 6),
(11, 5),
(12, 2),
(13, 8),
(14, 6),
(15, 2),
(16, 8),
(17, 6),
(18, 6),
(19, 2),
(20, 6),
(21, 2),
(22, 1),
(23, 6),
(24, 3),
(25, 8),
(26, 2),
(27, 3),
(28, 6),
(29, 6),
(30, 1),
(31, 1),
(32, 13),
(33, 7),
(34, 10),
(35, 6),
(37, 11),
(38, 8), (38, 12),
(39, 9),
(40, 10),
(41, 1),
(42, 6),
(43, 2),
(44, 13),
(45, 3), (45, 12),
(46, 10),
(47, 2),
(48, 9),
(50, 8), (50, 12),
(51, 12),
(52, 6),
(53, 2), (53, 9),
(54, 11),
(55, 10),
(56, 4),
(57, 8),
(59, 6),
(60, 2);

-- Receita que cada vínculo consumiu, com o custo do produto — no sistema ela é
-- copiada de servicoProdutos no momento em que o serviço entra na obra.
INSERT INTO obraServicoProdutos (idObraServico, idProduto, quantidade, custoUnitario)
SELECT os.idObraServico, sp.idProduto, sp.quantidade, p.custoUnitario
FROM obraServicos os
JOIN servicoProdutos sp ON sp.idServico = os.idServico
JOIN produtos p         ON p.idProduto  = sp.idProduto;

-- Valor e custo das obras concluídas, replicando ProdutosObrasDAO.recalcular_valor:
--   valorObra = serviços + produtos avulsos × preço de venda congelado
--   custoObra = todo o material × custo congelado (NULL se algum item não
--               tiver custo, para o lucro não sair inflado)
-- SQL_SAFE_UPDATES desligado temporariamente: o MySQL Workbench bloqueia
-- UPDATE sem a chave primária no WHERE.
SET SQL_SAFE_UPDATES = 0;

UPDATE obras o
SET o.valorObra =
        (SELECT COALESCE(SUM(s.precoServico), 0)
         FROM obraServicos os
         JOIN servicos s ON s.idServico = os.idServico
         WHERE os.idObra = o.idObra)
      + (SELECT COALESCE(SUM(po.qtdProdutosObra * po.precoVenda), 0)
         FROM produtosObras po
         WHERE po.idObra = o.idObra),
    o.custoObra = (
        SELECT IF(COUNT(*) = COUNT(c.custo), COALESCE(SUM(c.quantidade * c.custo), 0), NULL)
        FROM (
            SELECT idObra, qtdProdutosObra AS quantidade, custoUnitario AS custo
            FROM produtosObras
            UNION ALL
            SELECT os.idObra, osp.quantidade, osp.custoUnitario
            FROM obraServicoProdutos osp
            JOIN obraServicos os ON os.idObraServico = osp.idObraServico
        ) c
        WHERE c.idObra = o.idObra
    )
WHERE o.statusObra = 'Concluida';

SET SQL_SAFE_UPDATES = 1;

-- ── Notas fiscais ─────────────────────────────────────────────────────────────
-- As 10 primeiras já foram conferidas (itens vinculados a produtos). A última,
-- de um fornecedor novo, chegou há 3 dias e está pendente de conferência.
INSERT INTO notasFiscais (idNotaFiscal, chaveAcesso, numero, serie, idFornecedor, dataEmissao, valorTotal, nomeArquivo, dataImportacao) VALUES
(1, '35260111222333000181550010000011371726335221', '1137', '1', 1, @hoje - INTERVAL 340 DAY, 3331.80, 'NFe35260111222333000181550010000011371726335221.xml', @hoje - INTERVAL 338 DAY),
(2, '35260222333444000172550010000012741791453942', '1274', '1', 2, @hoje - INTERVAL 300 DAY, 23866.60, 'NFe35260222333444000172550010000012741791453942.xml', @hoje - INTERVAL 298 DAY),
(3, '35260433444555000163550010000014111596778433', '1411', '1', 3, @hoje - INTERVAL 260 DAY, 6075.60, 'NFe35260433444555000163550010000014111596778433.xml', @hoje - INTERVAL 258 DAY),
(4, '35260555666777000145550010000015481211488714', '1548', '1', 5, @hoje - INTERVAL 220 DAY, 1312.60, 'NFe35260555666777000145550010000015481211488714.xml', @hoje - INTERVAL 218 DAY),
(5, '35260622333444000172550010000016851281012185', '1685', '1', 2, @hoje - INTERVAL 180 DAY, 14174.70, 'NFe35260622333444000172550010000016851281012185.xml', @hoje - INTERVAL 178 DAY),
(6, '35260811222333000181550010000018221886555066', '1822', '1', 1, @hoje - INTERVAL 140 DAY, 754.60, 'NFe35260811222333000181550010000018221886555066.xml', @hoje - INTERVAL 138 DAY),
(7, '35260944555666000154550010000019591565759467', '1959', '1', 4, @hoje - INTERVAL 100 DAY, 644.50, 'NFe35260944555666000154550010000019591565759467.xml', @hoje - INTERVAL 98 DAY),
(8, '35261033444555000163550010000020961262903878', '2096', '1', 3, @hoje - INTERVAL 60 DAY, 2282.70, 'NFe35261033444555000163550010000020961262903878.xml', @hoje - INTERVAL 58 DAY),
(9, '35261222333444000172550010000022331193292699', '2233', '1', 2, @hoje - INTERVAL 25 DAY, 86694.60, 'NFe35261222333444000172550010000022331193292699.xml', @hoje - INTERVAL 23 DAY),
(10, '35261211222333000181550010000023701164676110', '2370', '1', 1, @hoje - INTERVAL 8 DAY, 1292.60, 'NFe35261211222333000181550010000023701164676110.xml', @hoje - INTERVAL 6 DAY),
(11, '35261266777888000136550010000025071706423681', '2507', '1', 6, @hoje - INTERVAL 3 DAY, 840.00, 'NFe35261266777888000136550010000025071706423681.xml', @hoje - INTERVAL 1 DAY);

INSERT INTO notaFiscalItens (idNotaFiscal, idProduto, codProdutoFornecedor, nomeProdutoNota, quantidade, valorUnitario, valorTotal, statusItem) VALUES
(1, 9, '10009', 'CONECTOR CURVO 90° 1/2"', 10, 9.14, 91.40, 'confirmado'),
(1, 10, '10010', 'ADAPTADOR ROSCA 1/2" X 3/4"', 50, 7.85, 392.50, 'confirmado'),
(1, 43, '10043', 'TUBO DE COBRE 1/2" (METRO)', 50, 43.79, 2189.50, 'confirmado'),
(1, 1, '10001', 'TUBO AÇO GALVANIZADO 1"', 20, 22.93, 458.60, 'confirmado'),
(1, 22, '10022', 'JOELHO 90° 3/4" GALVANIZADO', 20, 9.99, 199.80, 'confirmado'),
(2, 46, '20046', 'CENTRAL GLP COMPACTA P13 (2 CILINDROS)', 5, 661.21, 3306.05, 'confirmado'),
(2, 36, '20036', 'QUEIMADOR INDUSTRIAL 50.000 BTU', 20, 975.85, 19517.00, 'confirmado'),
(2, 26, '20026', 'DETECTOR DE GÁS NATURAL/GLP', 5, 208.71, 1043.55, 'confirmado'),
(3, 31, '30031', 'TUBO FLEXÍVEL METÁLICO 1M', 30, 70.33, 2109.90, 'confirmado'),
(3, 32, '30032', 'TUBO FLEXÍVEL METÁLICO 2M', 30, 116.93, 3507.90, 'confirmado'),
(3, 15, '30015', 'MANGUEIRA GLP 1,20M CERTIFICADA', 20, 22.89, 457.80, 'confirmado'),
(4, 24, '50024', 'FITA VEDA ROSCA 18MM X 50M', 10, 6.87, 68.70, 'confirmado'),
(4, 38, '50038', 'KIT REPARO DE REGULADOR GLP', 5, 43.16, 215.80, 'confirmado'),
(4, 25, '50025', 'SELANTE PARA GLP 250ML', 30, 34.27, 1028.10, 'confirmado'),
(5, 14, '20014', 'REGULADOR DE PRESSÃO 2ª FAMÍLIA', 50, 141.16, 7058.00, 'confirmado'),
(5, 17, '20017', 'VÁLVULA DE ALÍVIO 1/2" 1,5 KGF', 20, 56.00, 1120.00, 'confirmado'),
(5, 8, '20008', 'FILTRO DE LINHA PARA GÁS', 20, 66.07, 1321.40, 'confirmado'),
(5, 29, '20029', 'MANÔMETRO 0-4 KGF/CM² 1/4"', 50, 73.94, 3697.00, 'confirmado'),
(5, 2, '20002', 'REGISTRO DE ESFERA 3/4"', 30, 32.61, 978.30, 'confirmado'),
(6, 20, '10020', 'TÊ 1/2" GALVANIZADO', 10, 8.26, 82.60, 'confirmado'),
(6, 9, '10009', 'CONECTOR CURVO 90° 1/2"', 50, 8.81, 440.50, 'confirmado'),
(6, 19, '10019', 'NIPLE DUPLO 1/2"', 30, 5.49, 164.70, 'confirmado'),
(6, 21, '10021', 'JOELHO 90° 1/2" GALVANIZADO', 10, 6.68, 66.80, 'confirmado'),
(7, 40, '40040', 'ÓCULOS DE SEGURANÇA INCOLOR', 10, 14.03, 140.30, 'confirmado'),
(7, 50, '40050', 'PLACA DE SINALIZAÇÃO "GÁS INFLAMÁVEL"', 10, 17.78, 177.80, 'confirmado'),
(7, 39, '40039', 'CAPACETE DE SEGURANÇA CA', 5, 37.58, 187.90, 'confirmado'),
(7, 41, '40041', 'LUVA DE COURO CANO LONGO', 5, 27.70, 138.50, 'confirmado'),
(8, 48, '30048', 'TUBO MULTICAMADA PEX-AL-PEX 16MM (M)', 5, 14.52, 72.60, 'confirmado'),
(8, 31, '30031', 'TUBO FLEXÍVEL METÁLICO 1M', 20, 69.24, 1384.80, 'confirmado'),
(8, 5, '30005', 'MANGUEIRA FLEXÍVEL 3/4"', 30, 27.51, 825.30, 'confirmado'),
(9, 37, '20037', 'QUEIMADOR INDUSTRIAL 100.000 BTU', 50, 1653.24, 82662.00, 'confirmado'),
(9, 13, '20013', 'REGULADOR DE PRESSÃO 1ª FAMÍLIA', 30, 48.59, 1457.70, 'confirmado'),
(9, 4, '20004', 'VÁLVULA REDUTORA DE PRESSÃO', 30, 85.83, 2574.90, 'confirmado'),
(10, 20, '10020', 'TÊ 1/2" GALVANIZADO', 10, 8.02, 80.20, 'confirmado'),
(10, 18, '10018', 'LUVA DE REDUÇÃO 3/4" X 1/2"', 10, 6.49, 64.90, 'confirmado'),
(10, 1, '10001', 'TUBO AÇO GALVANIZADO 1"', 50, 22.95, 1147.50, 'confirmado'),
(11, NULL, '60988', 'CONEXAO LATAO 1/2 X 3/8 GAS', 40, 6.10, 244.00, 'pendente'),
(11, NULL, '60872', 'REGISTRO GAVETA 1/2 GLP', 15, 27.40, 411.00, 'pendente'),
(11, NULL, '60756', 'ABRACADEIRA ROSCA SEM FIM 13-19MM', 100, 1.85, 185.00, 'pendente');

-- ── Movimentações de estoque ──────────────────────────────────────────────────
-- Entradas pelas notas conferidas, na data em que foram importadas.
INSERT INTO movimentacoesEstoque (idProduto, idObra, tipo, origem, quantidade, dataMov)
SELECT i.idProduto, NULL, 'entrada', 'nota_fiscal', i.quantidade, n.dataImportacao
FROM notaFiscalItens i
JOIN notasFiscais n ON n.idNotaFiscal = i.idNotaFiscal
WHERE i.statusItem = 'confirmado';

-- No sistema, cada baixa de material numa obra grava uma saída com a data do
-- momento. Para os dados de exemplo, a saída é datada no início da obra (ou
-- hoje, se a obra ainda vai começar). Obras canceladas já devolveram o
-- material, então não entram. É desse histórico que sai o consumo médio diário.
INSERT INTO movimentacoesEstoque (idProduto, idObra, tipo, origem, quantidade, dataMov)
SELECT v.idProduto, v.idObra, 'saida', 'obra', v.quantidade, LEAST(o.dataInicio, CURDATE())
FROM vw_consumo_obra v
JOIN obras o ON o.idObra = v.idObra
WHERE o.statusObra <> 'Cancelada';

-- ── Histórico ─────────────────────────────────────────────────────────────────
-- Mesmos textos que o sistema grava. idEntidade liga o registro à obra.
INSERT INTO historico (idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao, dataHora) VALUES
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "João" (Administração)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:16:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Marcos" (Almoxarifado)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:19:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Pedro" (Obra)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:22:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Juliana" (Almoxarifado)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:25:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Rafael" (Obra)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:28:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Thiago" (Obra)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:31:00')),
(1, 'adm', 'Inseriu', 'Usuário', NULL, 'Inseriu o usuário "Larissa" (Obra)', TIMESTAMP(@hoje - INTERVAL 400 DAY, '08:34:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Carlos Souza"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Beatriz Almeida"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:05:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Renato Pereira"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:10:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Ana Carolina"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:15:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Diego Fernandes"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:20:00')),
(1, 'adm', 'Inseriu', 'Field', NULL, 'Inseriu o field "Patrícia Lima"', TIMESTAMP(@hoje - INTERVAL 400 DAY, '09:25:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "Metalúrgica Vale do Aço"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:00:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "Fersol Equipamentos de Gás"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:06:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "Conexão Flex Indústria e Comércio"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:12:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "SafeWork Proteção Industrial"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:18:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "QuimGás Insumos Técnicos"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:24:00')),
(1, 'adm', 'Inseriu', 'Fornecedor', NULL, 'Inseriu o fornecedor "Distribuidora ABC Conexões"', TIMESTAMP(@hoje - INTERVAL 399 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo Aço Galvanizado 1""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '09:07:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Registro de Esfera 3/4""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '09:14:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Medidor de Gás Industrial G16"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '10:21:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Válvula Redutora de Pressão"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '10:28:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Mangueira Flexível 3/4""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '10:35:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Cinta de Fixação Metálica"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '11:42:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo PPR 32mm"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '11:49:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Filtro de Linha para Gás"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '11:56:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Conector Curvo 90° 1/2""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '12:03:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Adaptador Rosca 1/2" x 3/4""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '12:10:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Lanterna de Inspeção Antichama"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '12:17:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Detector de Vazão Portátil"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '13:24:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Regulador de Pressão 1ª Família"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '13:31:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Regulador de Pressão 2ª Família"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '13:38:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Mangueira GLP 1,20m Certificada"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '14:45:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Abraçadeira Metálica 3/4""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '14:52:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Válvula de Alívio 1/2" 1,5 kgf"', TIMESTAMP(@hoje - INTERVAL 398 DAY, '14:59:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Luva de Redução 3/4" x 1/2""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '15:06:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Niple Duplo 1/2""', TIMESTAMP(@hoje - INTERVAL 398 DAY, '15:13:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tê 1/2" Galvanizado"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '09:20:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Joelho 90° 1/2" Galvanizado"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '09:27:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Joelho 90° 3/4" Galvanizado"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '09:34:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tampão Macho 1/2""', TIMESTAMP(@hoje - INTERVAL 397 DAY, '10:41:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Fita Veda Rosca 18mm x 50m"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '10:48:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Selante para GLP 250ml"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '10:55:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Detector de Gás Natural/GLP"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '11:02:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Extintor CO2 6kg"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '11:09:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Extintor Pó Químico Seco 4kg"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '11:16:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Manômetro 0-4 kgf/cm² 1/4""', TIMESTAMP(@hoje - INTERVAL 397 DAY, '12:23:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Manifold GLP 4 Saídas"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '12:30:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo Flexível Metálico 1m"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '12:37:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo Flexível Metálico 2m"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '13:44:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Conector Rápido GLP 1/2""', TIMESTAMP(@hoje - INTERVAL 397 DAY, '13:51:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Válvula Solenóide GLP 1/2" 220V"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '13:58:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Filtro de GLP Inline 3/4""', TIMESTAMP(@hoje - INTERVAL 397 DAY, '14:05:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Queimador Industrial 50.000 BTU"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '14:12:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Queimador Industrial 100.000 BTU"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '14:19:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Kit Reparo de Regulador GLP"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '15:26:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Capacete de Segurança CA"', TIMESTAMP(@hoje - INTERVAL 397 DAY, '15:33:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Óculos de Segurança Incolor"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '09:40:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Luva de Couro Cano Longo"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '09:47:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Bota de Segurança Bico de Aço"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '09:54:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo de Cobre 1/2" (metro)"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '10:01:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Cano de Aço Preto 1/2" (metro)"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '10:08:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Medidor de Gás Residencial G4"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '10:15:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Central GLP Compacta P13 (2 cilindros)"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '11:22:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Abrigo Metálico para Medidor"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '11:29:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Tubo Multicamada PEX-AL-PEX 16mm (m)"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '11:36:00')),
(1, 'adm', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Conexão Prensar PEX 16mm"', TIMESTAMP(@hoje - INTERVAL 396 DAY, '12:43:00')),
(2, 'João', 'Inseriu', 'Produto', NULL, 'Inseriu o produto "Placa de Sinalização "Gás Inflamável""', TIMESTAMP(@hoje - INTERVAL 396 DAY, '12:50:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Ramal Residencial"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:04:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Ramal Comercial"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:08:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Manutenção Preventiva de Medidor"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:12:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Correção de Vazamento"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:16:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Troca de Registro e Conector"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:20:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Extensão de Rede Comercial"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:24:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Medidor Privativo"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:28:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Vistoria e Laudo Técnico"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:32:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Central GLP P45"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:36:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Fogão Industrial"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:40:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Instalação de Detector com Corte Automático"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:44:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Teste de Estanqueidade"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:48:00')),
(2, 'João', 'Inseriu', 'Serviço', NULL, 'Inseriu o serviço "Substituição de Regulador GLP"', TIMESTAMP(@hoje - INTERVAL 395 DAY, '14:52:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Rafaela Monteiro"', TIMESTAMP(@hoje - INTERVAL 353 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 31, 'Inseriu a obra "Instalação de ramal residencial em casa térrea"', TIMESTAMP(@hoje - INTERVAL 352 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1137 de "Metalúrgica Vale do Aço" (XML, 5 itens)', TIMESTAMP(@hoje - INTERVAL 338 DAY, '11:20:00')),
(1, 'adm', 'Editou', 'Obra', 31, 'Editou a obra "Instalação de ramal residencial em casa térrea"', TIMESTAMP(@hoje - INTERVAL 338 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Gustavo Henrique Prado"', TIMESTAMP(@hoje - INTERVAL 333 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 32, 'Inseriu a obra "Troca de regulador e mangueira em apartamento"', TIMESTAMP(@hoje - INTERVAL 332 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 32, 'Editou a obra "Troca de regulador e mangueira em apartamento"', TIMESTAMP(@hoje - INTERVAL 327 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Condomínio Residencial Aquarius"', TIMESTAMP(@hoje - INTERVAL 321 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 33, 'Inseriu a obra "Instalação de medidores individuais no condomínio" — equipe: Rafael', TIMESTAMP(@hoje - INTERVAL 320 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Pizzaria Forno a Lenha"', TIMESTAMP(@hoje - INTERVAL 304 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 34, 'Inseriu a obra "Instalação de forno de pizza a gás"', TIMESTAMP(@hoje - INTERVAL 303 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1274 de "Fersol Equipamentos de Gás" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 298 DAY, '11:20:00')),
(2, 'João', 'Editou', 'Obra', 34, 'Editou a obra "Instalação de forno de pizza a gás"', TIMESTAMP(@hoje - INTERVAL 295 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Lavanderia Industrial Clean"', TIMESTAMP(@hoje - INTERVAL 291 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 35, 'Inseriu a obra "Rede de gás para secadoras industriais"', TIMESTAMP(@hoje - INTERVAL 290 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Academia Corpo em Forma"', TIMESTAMP(@hoje - INTERVAL 273 DAY, '10:30:00')),
(1, 'adm', 'Editou', 'Obra', 33, 'Editou a obra "Instalação de medidores individuais no condomínio"', TIMESTAMP(@hoje - INTERVAL 273 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 36, 'Inseriu a obra "Instalação de aquecedor de água a gás - vestiários" — equipe: Pedro, Rafael', TIMESTAMP(@hoje - INTERVAL 272 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 36, 'Editou a obra "Instalação de aquecedor de água a gás - vestiários"', TIMESTAMP(@hoje - INTERVAL 261 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Clínica Veterinária Bicho Feliz"', TIMESTAMP(@hoje - INTERVAL 258 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1411 de "Conexão Flex Indústria e Comércio" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 258 DAY, '11:20:00')),
(1, 'adm', 'Editou', 'Obra', 35, 'Editou a obra "Rede de gás para secadoras industriais"', TIMESTAMP(@hoje - INTERVAL 258 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 37, 'Inseriu a obra "Instalação de detector de vazamento com corte automático"', TIMESTAMP(@hoje - INTERVAL 257 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 37, 'Editou a obra "Instalação de detector de vazamento com corte automático"', TIMESTAMP(@hoje - INTERVAL 251 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Restaurante Sabor da Serra"', TIMESTAMP(@hoje - INTERVAL 243 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 38, 'Inseriu a obra "Vistoria anual da central de GLP"', TIMESTAMP(@hoje - INTERVAL 242 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 38, 'Editou a obra "Vistoria anual da central de GLP"', TIMESTAMP(@hoje - INTERVAL 239 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Pousada Recanto das Águas"', TIMESTAMP(@hoje - INTERVAL 229 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 39, 'Inseriu a obra "Central GLP P45 para cozinha da pousada" — equipe: Pedro', TIMESTAMP(@hoje - INTERVAL 228 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1548 de "QuimGás Insumos Técnicos" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 218 DAY, '11:20:00')),
(1, 'adm', 'Inseriu', 'Obra', 1, 'Inseriu a obra "Instalação de ramal de gás em condomínio residencial"', TIMESTAMP(@hoje - INTERVAL 216 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Hamburgueria Brasa Viva"', TIMESTAMP(@hoje - INTERVAL 215 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 40, 'Inseriu a obra "Instalação de chapa e fritadeiras a gás"', TIMESTAMP(@hoje - INTERVAL 214 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 39, 'Editou a obra "Central GLP P45 para cozinha da pousada"', TIMESTAMP(@hoje - INTERVAL 211 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Fornecedor', NULL, 'Editou o fornecedor "Fersol Equipamentos de Gás": prazo de entrega de 10 dias', TIMESTAMP(@hoje - INTERVAL 210 DAY, '15:40:00')),
(2, 'João', 'Inseriu', 'Obra', 2, 'Inseriu a obra "Manutenção preventiva em medidor industrial"', TIMESTAMP(@hoje - INTERVAL 209 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 40, 'Editou a obra "Instalação de chapa e fritadeiras a gás"', TIMESTAMP(@hoje - INTERVAL 205 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 3, 'Inseriu a obra "Extensão de rede de gás em restaurante na região central" — equipe: Thiago', TIMESTAMP(@hoje - INTERVAL 201 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Bruno Carvalho"', TIMESTAMP(@hoje - INTERVAL 201 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 41, 'Inseriu a obra "Instalação de fogão e aquecedor residencial"', TIMESTAMP(@hoje - INTERVAL 200 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "João Vinicius Oliveira"', TIMESTAMP(@hoje - INTERVAL 194 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 4, 'Inseriu a obra "Correção de vazamento em cozinha industrial"', TIMESTAMP(@hoje - INTERVAL 193 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 2, 'Editou a obra "Manutenção preventiva em medidor industrial"', TIMESTAMP(@hoje - INTERVAL 193 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 41, 'Editou a obra "Instalação de fogão e aquecedor residencial"', TIMESTAMP(@hoje - INTERVAL 193 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 1, 'Editou a obra "Instalação de ramal de gás em condomínio residencial"', TIMESTAMP(@hoje - INTERVAL 191 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Mercado Família Costa"', TIMESTAMP(@hoje - INTERVAL 188 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 42, 'Inseriu a obra "Adequação da rede de gás da padaria do mercado" — equipe: Rafael, Larissa', TIMESTAMP(@hoje - INTERVAL 187 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 5, 'Inseriu a obra "Instalação de medidor privativo em prédio comercial"', TIMESTAMP(@hoje - INTERVAL 185 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1685 de "Fersol Equipamentos de Gás" (XML, 5 itens)', TIMESTAMP(@hoje - INTERVAL 178 DAY, '11:20:00')),
(2, 'João', 'Inseriu', 'Obra', 6, 'Inseriu a obra "Troca de registro e conector em unidade logística" — equipe: Rafael, Thiago', TIMESTAMP(@hoje - INTERVAL 177 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 42, 'Editou a obra "Adequação da rede de gás da padaria do mercado"', TIMESTAMP(@hoje - INTERVAL 175 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Indústria Química Paulista"', TIMESTAMP(@hoje - INTERVAL 174 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 43, 'Inseriu a obra "Rede de gás natural para caldeira - linha 2"', TIMESTAMP(@hoje - INTERVAL 173 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Lúcia Martins"', TIMESTAMP(@hoje - INTERVAL 169 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 7, 'Inseriu a obra "Instalação de ramal de gás para cozinha de pizzaria" — equipe: Pedro', TIMESTAMP(@hoje - INTERVAL 168 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Padaria Pão Dourado"', TIMESTAMP(@hoje - INTERVAL 163 DAY, '10:30:00')),
(2, 'João', 'Editou', 'Obra', 4, 'Editou a obra "Correção de vazamento em cozinha industrial"', TIMESTAMP(@hoje - INTERVAL 163 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 44, 'Inseriu a obra "Troca de reguladores da central de GLP"', TIMESTAMP(@hoje - INTERVAL 162 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Obra', 8, 'Inseriu a obra "Revisão geral de rede de gás na unidade fabril"', TIMESTAMP(@hoje - INTERVAL 159 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 7, 'Editou a obra "Instalação de ramal de gás para cozinha de pizzaria"', TIMESTAMP(@hoje - INTERVAL 156 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 44, 'Editou a obra "Troca de reguladores da central de GLP"', TIMESTAMP(@hoje - INTERVAL 156 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 3, 'Editou a obra "Extensão de rede de gás em restaurante na região central"', TIMESTAMP(@hoje - INTERVAL 155 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 6, 'Editou a obra "Troca de registro e conector em unidade logística"', TIMESTAMP(@hoje - INTERVAL 154 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Hospital Municipal de Mauá"', TIMESTAMP(@hoje - INTERVAL 151 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 45, 'Inseriu a obra "Manutenção preventiva das redes de gás hospitalares" — equipe: Rafael', TIMESTAMP(@hoje - INTERVAL 150 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Marina Nunes"', TIMESTAMP(@hoje - INTERVAL 150 DAY, '10:30:00')),
(2, 'João', 'Editou', 'Produto', NULL, 'Editou o produto "Tubo Aço Galvanizado 1""', TIMESTAMP(@hoje - INTERVAL 150 DAY, '11:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 9, 'Inseriu a obra "Projeto de ramal de gás para nova loja de estética" — equipe: Pedro, Thiago', TIMESTAMP(@hoje - INTERVAL 149 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Obra', 10, 'Inseriu a obra "Instalação de rede GLP para cozinha industrial"', TIMESTAMP(@hoje - INTERVAL 139 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1822 de "Metalúrgica Vale do Aço" (XML, 4 itens)', TIMESTAMP(@hoje - INTERVAL 138 DAY, '11:20:00')),
(1, 'adm', 'Editou', 'Obra', 45, 'Editou a obra "Manutenção preventiva das redes de gás hospitalares"', TIMESTAMP(@hoje - INTERVAL 138 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Restaurante Cantina Italiana"', TIMESTAMP(@hoje - INTERVAL 136 DAY, '10:30:00')),
(1, 'adm', 'Editou', 'Obra', 43, 'Editou a obra "Rede de gás natural para caldeira - linha 2"', TIMESTAMP(@hoje - INTERVAL 136 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 46, 'Inseriu a obra "Instalação de fogões industriais na cantina"', TIMESTAMP(@hoje - INTERVAL 135 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 5, 'Editou a obra "Instalação de medidor privativo em prédio comercial"', TIMESTAMP(@hoje - INTERVAL 133 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Padaria São Benedito"', TIMESTAMP(@hoje - INTERVAL 125 DAY, '10:30:00')),
(2, 'João', 'Editou', 'Obra', 46, 'Editou a obra "Instalação de fogões industriais na cantina"', TIMESTAMP(@hoje - INTERVAL 125 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 11, 'Inseriu a obra "Substituição de reguladores e mangueiras GLP" — equipe: Pedro', TIMESTAMP(@hoje - INTERVAL 124 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Metalúrgica São Bernardo"', TIMESTAMP(@hoje - INTERVAL 123 DAY, '10:30:00')),
(2, 'João', 'Editou', 'Obra', 10, 'Editou a obra "Instalação de rede GLP para cozinha industrial"', TIMESTAMP(@hoje - INTERVAL 123 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 47, 'Inseriu a obra "Rede de gás para estufa de pintura"', TIMESTAMP(@hoje - INTERVAL 122 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 8, 'Editou a obra "Revisão geral de rede de gás na unidade fabril"', TIMESTAMP(@hoje - INTERVAL 117 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 12, 'Inseriu a obra "Projeto de instalação GLP industrial - fase 1" — equipe: Rafael, Thiago', TIMESTAMP(@hoje - INTERVAL 110 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Escola Estadual Prof. Lima"', TIMESTAMP(@hoje - INTERVAL 107 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 48, 'Inseriu a obra "Instalação de gás na cozinha da escola" — equipe: Pedro, Larissa', TIMESTAMP(@hoje - INTERVAL 106 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 1959 de "SafeWork Proteção Industrial" (XML, 4 itens)', TIMESTAMP(@hoje - INTERVAL 98 DAY, '11:20:00')),
(1, 'adm', 'Inseriu', 'Obra', 13, 'Inseriu a obra "Vistoria anual da central de GLP hospitalar"', TIMESTAMP(@hoje - INTERVAL 96 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Fernanda Ribeiro"', TIMESTAMP(@hoje - INTERVAL 95 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 49, 'Inseriu a obra "Conversão de fogão para gás natural"', TIMESTAMP(@hoje - INTERVAL 94 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 13, 'Editou a obra "Vistoria anual da central de GLP hospitalar"', TIMESTAMP(@hoje - INTERVAL 94 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 47, 'Editou a obra "Rede de gás para estufa de pintura"', TIMESTAMP(@hoje - INTERVAL 92 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 48, 'Editou a obra "Instalação de gás na cozinha da escola"', TIMESTAMP(@hoje - INTERVAL 92 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Serviço', NULL, 'Editou o serviço "Instalação de Central GLP P45"', TIMESTAMP(@hoje - INTERVAL 90 DAY, '16:10:00')),
(1, 'adm', 'Editou', 'Obra', 49, 'Editou a obra "Conversão de fogão para gás natural"', TIMESTAMP(@hoje - INTERVAL 90 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Churrascaria Gaúcha Diadema"', TIMESTAMP(@hoje - INTERVAL 83 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 50, 'Inseriu a obra "Laudo de estanqueidade para renovação do AVCB"', TIMESTAMP(@hoje - INTERVAL 82 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 50, 'Editou a obra "Laudo de estanqueidade para renovação do AVCB"', TIMESTAMP(@hoje - INTERVAL 79 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 14, 'Inseriu a obra "Adequação da rede GLP - setor de padaria" — equipe: Pedro, Larissa', TIMESTAMP(@hoje - INTERVAL 78 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Cliente', NULL, 'Editou o cliente "Fabrício Rocha"', TIMESTAMP(@hoje - INTERVAL 75 DAY, '10:05:00')),
(1, 'adm', 'Inseriu', 'Obra', 51, 'Inseriu a obra "Revisão do ramal após reforma da cozinha" — equipe: Pedro', TIMESTAMP(@hoje - INTERVAL 68 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 14, 'Editou a obra "Adequação da rede GLP - setor de padaria"', TIMESTAMP(@hoje - INTERVAL 66 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 12, 'Editou a obra "Projeto de instalação GLP industrial - fase 1"', TIMESTAMP(@hoje - INTERVAL 65 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 15, 'Inseriu a obra "Instalação industrial GLP - câmara fria" — equipe: Thiago', TIMESTAMP(@hoje - INTERVAL 64 DAY, '09:00:00')),
(2, 'João', 'Deletou', 'Produto', NULL, 'Deletou o produto "Bucha de Redução 1/2""', TIMESTAMP(@hoje - INTERVAL 60 DAY, '15:00:00')),
(1, 'adm', 'Editou', 'Obra', 51, 'Editou a obra "Revisão do ramal após reforma da cozinha"', TIMESTAMP(@hoje - INTERVAL 60 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 2096 de "Conexão Flex Indústria e Comércio" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 58 DAY, '11:20:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Restaurante Bom Sabor Ltda"', TIMESTAMP(@hoje - INTERVAL 55 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 52, 'Inseriu a obra "Ampliação da rede para novo salão" — equipe: Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 54 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Obra', 16, 'Inseriu a obra "Revisão e adequação central GLP - hotel" — equipe: Pedro, Thiago', TIMESTAMP(@hoje - INTERVAL 53 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 53, 'Inseriu a obra "Rede de gás para novo setor de tingimento"', TIMESTAMP(@hoje - INTERVAL 47 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Colégio Dom Bosco"', TIMESTAMP(@hoje - INTERVAL 45 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 17, 'Inseriu a obra "Instalação de rede GLP para cantina escolar"', TIMESTAMP(@hoje - INTERVAL 44 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 52, 'Editou a obra "Ampliação da rede para novo salão"', TIMESTAMP(@hoje - INTERVAL 42 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 54, 'Inseriu a obra "Instalação de detectores na central hospitalar" — equipe: Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 40 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Usuário', NULL, 'Editou o usuário "Juliana" (Almoxarifado)', TIMESTAMP(@hoje - INTERVAL 40 DAY, '09:45:00')),
(2, 'João', 'Inseriu', 'Obra', 18, 'Inseriu a obra "Instalação de rede GLP para churrasqueiras - lote 1" — equipe: Rafael, Thiago', TIMESTAMP(@hoje - INTERVAL 39 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 19, 'Inseriu a obra "Instalação de rede GLP para solda a gás"', TIMESTAMP(@hoje - INTERVAL 35 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Panificadora Delícia"', TIMESTAMP(@hoje - INTERVAL 33 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 20, 'Inseriu a obra "Instalação de fornos e fogões a GLP" — equipe: Rafael, Larissa', TIMESTAMP(@hoje - INTERVAL 32 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Hotel Fazenda do Vale"', TIMESTAMP(@hoje - INTERVAL 32 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 55, 'Inseriu a obra "Troca dos fogões da cozinha do hotel"', TIMESTAMP(@hoje - INTERVAL 31 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Cerâmica São Paulo Ind."', TIMESTAMP(@hoje - INTERVAL 30 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 21, 'Inseriu a obra "Instalação de forno industrial a gás cerâmica" — equipe: Pedro', TIMESTAMP(@hoje - INTERVAL 29 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 18, 'Editou a obra "Instalação de rede GLP para churrasqueiras - lote 1"', TIMESTAMP(@hoje - INTERVAL 27 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 53, 'Editou a obra "Rede de gás para novo setor de tingimento"', TIMESTAMP(@hoje - INTERVAL 25 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 55, 'Editou a obra "Troca dos fogões da cozinha do hotel"', TIMESTAMP(@hoje - INTERVAL 24 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 56, 'Inseriu a obra "Manutenção corretiva nos pontos de solda" — equipe: Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 23 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Escola Municipal Boa Vista"', TIMESTAMP(@hoje - INTERVAL 23 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 2233 de "Fersol Equipamentos de Gás" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 23 DAY, '11:20:00')),
(2, 'João', 'Inseriu', 'Obra', 22, 'Inseriu a obra "Instalação de GLP para cozinha escolar" — equipe: Pedro, Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 22 DAY, '09:00:00')),
(2, 'João', 'Editou', 'Obra', 20, 'Editou a obra "Instalação de fornos e fogões a GLP"', TIMESTAMP(@hoje - INTERVAL 20 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 23, 'Inseriu a obra "Ampliação da central de GLP - depósito 2"', TIMESTAMP(@hoje - INTERVAL 16 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Distribuidora GLP Norte"', TIMESTAMP(@hoje - INTERVAL 15 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Obra', 57, 'Inseriu a obra "Laudo técnico da central de GLP do depósito" — equipe: Larissa', TIMESTAMP(@hoje - INTERVAL 14 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 15, 'Editou a obra "Instalação industrial GLP - câmara fria"', TIMESTAMP(@hoje - INTERVAL 12 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Caua Silva"', TIMESTAMP(@hoje - INTERVAL 11 DAY, '10:30:00')),
(1, 'adm', 'Editou', 'Obra', 57, 'Editou a obra "Laudo técnico da central de GLP do depósito"', TIMESTAMP(@hoje - INTERVAL 11 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 24, 'Inseriu a obra "Manutenção corretiva - revisão geral pós-vistoria" — equipe: Pedro, Larissa', TIMESTAMP(@hoje - INTERVAL 10 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Mateus Alves"', TIMESTAMP(@hoje - INTERVAL 9 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 58, 'Inseriu a obra "Instalação de aquecedor de passagem" — equipe: Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 8 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Indústria Têxtil Vale Ltda"', TIMESTAMP(@hoje - INTERVAL 7 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 26, 'Inseriu a obra "Projeto de instalação GLP industrial - fase 2" — equipe: Pedro, Rafael, Larissa', TIMESTAMP(@hoje - INTERVAL 6 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 2370 de "Metalúrgica Vale do Aço" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 6 DAY, '11:20:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Fabrício Rocha"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Hospital Santa Casa Taubaté"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Supermercado Bom Preço"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Frigorífico Vale Carnes"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(1, 'adm', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Churrascaria do Compadre"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Cliente', NULL, 'Inseriu o cliente "Metalúrgica Aço Forte Ltda"', TIMESTAMP(@hoje - INTERVAL 5 DAY, '10:30:00')),
(2, 'João', 'Inseriu', 'Obra', 28, 'Inseriu a obra "Instalação GLP - nova seção de frios supermercado" — equipe: Thiago, Larissa', TIMESTAMP(@hoje - INTERVAL 4 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 17, 'Editou a obra "Instalação de rede GLP para cantina escolar"', TIMESTAMP(@hoje - INTERVAL 4 DAY, '17:15:00')),
(1, 'adm', 'Inseriu', 'Obra', 29, 'Inseriu a obra "Ampliação da rede de GLP industrial - novo setor" — equipe: Pedro, Larissa', TIMESTAMP(@hoje - INTERVAL 3 DAY, '09:00:00')),
(1, 'adm', 'Editou', 'Obra', 19, 'Editou a obra "Instalação de rede GLP para solda a gás"', TIMESTAMP(@hoje - INTERVAL 3 DAY, '17:15:00')),
(2, 'João', 'Inseriu', 'Obra', 30, 'Inseriu a obra "Instalação de novo setor de churrasco - expansão" — equipe: Pedro, Thiago', TIMESTAMP(@hoje - INTERVAL 2 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 25, 'Inseriu a obra "Revisão semestral central de GLP hospitalar" — equipe: Larissa', TIMESTAMP(@hoje - INTERVAL 1 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 27, 'Inseriu a obra "Manutenção preventiva anual - frigorífico" — equipe: Thiago', TIMESTAMP(@hoje - INTERVAL 1 DAY, '09:00:00')),
(1, 'adm', 'Inseriu', 'Obra', 59, 'Inseriu a obra "Ampliação da rede de gás da fábrica" — equipe: Larissa', TIMESTAMP(@hoje - INTERVAL 1 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Obra', 60, 'Inseriu a obra "Rede de gás para nova câmara de defumação" — equipe: Rafael, Larissa', TIMESTAMP(@hoje - INTERVAL 1 DAY, '09:00:00')),
(2, 'João', 'Inseriu', 'Nota Fiscal', NULL, 'Inseriu a nota fiscal nº 2507 de "Distribuidora ABC Conexões" (XML, 3 itens)', TIMESTAMP(@hoje - INTERVAL 1 DAY, '11:20:00')),
(1, 'adm', 'Editou', 'Obra', 21, 'Editou a obra "Instalação de forno industrial a gás cerâmica"', TIMESTAMP(@hoje - INTERVAL 1 DAY, '17:15:00')),
(1, 'adm', 'Editou', 'Obra', 23, 'Editou a obra "Ampliação da central de GLP - depósito 2"', TIMESTAMP(@hoje - INTERVAL 1 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 28, 'Editou a obra "Instalação GLP - nova seção de frios supermercado"', TIMESTAMP(@hoje - INTERVAL 1 DAY, '17:15:00')),
(2, 'João', 'Editou', 'Obra', 30, 'Editou a obra "Instalação de novo setor de churrasco - expansão"', TIMESTAMP(@hoje - INTERVAL 1 DAY, '17:15:00'));

-- ── Valor e custo das obras concluídas ───────────────────────────────────────
--   valorObra = serviços + produtos avulsos × preço de venda congelado
--   custoObra = todo o material × custo congelado (NULL se algum item não
--               tiver custo, para o lucro não sair inflado)
-- SQL_SAFE_UPDATES desligado temporariamente: o MySQL Workbench bloqueia
-- UPDATE sem a chave primária no WHERE.
SET SQL_SAFE_UPDATES = 0;

UPDATE obras o
SET o.valorObra =
        (SELECT COALESCE(SUM(s.precoServico), 0)
         FROM obraServicos os
         JOIN servicos s ON s.idServico = os.idServico
         WHERE os.idObra = o.idObra)
      + (SELECT COALESCE(SUM(po.qtdProdutosObra * po.precoVenda), 0)
         FROM produtosObras po
         WHERE po.idObra = o.idObra),
    o.custoObra = (
        SELECT IF(COUNT(*) = COUNT(c.custo), COALESCE(SUM(c.quantidade * c.custo), 0), NULL)
        FROM (
            SELECT idObra, qtdProdutosObra AS quantidade, custoUnitario AS custo
            FROM produtosObras
            UNION ALL
            SELECT os.idObra, osp.quantidade, osp.custoUnitario
            FROM obraServicoProdutos osp
            JOIN obraServicos os ON os.idObraServico = osp.idObraServico
        ) c
        WHERE c.idObra = o.idObra
    )
WHERE o.statusObra = 'Concluida';

SET SQL_SAFE_UPDATES = 1;

-- ── Ajustes do estoque mínimo ─────────────────────────────────────────────────
-- Produtos ainda sem uso em obra, para mostrar as outras origens do cálculo:
--   26 → estimativa informada no cadastro (uso aproximado de 8 por mês)
--   27 → mínimo definido manualmente (ex.: quantidade exigida por norma)
UPDATE produtos SET consumoEstimado = 8, periodoEstimativa = 'mes' WHERE idProduto = 26;
UPDATE produtos SET qtdMinimaManual = 5 WHERE idProduto = 27;

-- Estoque atual abaixo do mínimo calculado, para o dashboard ter alertas:
--   1 → abaixo do mínimo | 6 → abaixo do mínimo | 3 → esgotado
UPDATE produtos SET qtdProduto = 40 WHERE idProduto = 1;
UPDATE produtos SET qtdProduto = 15 WHERE idProduto = 6;
UPDATE produtos SET qtdProduto = 0  WHERE idProduto = 3;
