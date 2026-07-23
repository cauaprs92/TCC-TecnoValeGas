-- Inserts para popular as tabelas com dados de exemplo
-- Executar APÓS codigo.sql (que cria o schema e o banco)
USE tcc;

-- ── Login ─────────────────────────────────────────────────────────────────────
-- senha: adm123 (bcrypt hash)  |  INSERT IGNORE evita erro se já existir
-- idLogin 1 → adm  |  idLogin 2 → João  (ordem garantida pelo AUTO_INCREMENT)
INSERT IGNORE INTO login (email, senha, nomeLogin) VALUES
('adm123@gmail.com',      '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'adm'),
('joao@tecnovalegas.com', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'João');

-- ── Responsáveis ──────────────────────────────────────────────────────────────
INSERT INTO responsavel (nomeResponsavel) VALUES
('Carlos Souza'),
('Beatriz Almeida'),
('Renato Pereira'),
('Ana Carolina');

-- ── Fornecedores ──────────────────────────────────────────────────────────────
INSERT INTO fornecedores (nomeFornecedor) VALUES
('Metalúrgica Vale do Aço'),
('Fersol Equipamentos de Gás'),
('Conexão Flex Indústria e Comércio'),
('SafeWork Proteção Industrial'),
('QuimGás Insumos Técnicos');

-- ── Clientes ──────────────────────────────────────────────────────────────────
INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, contatoCliente, emailCliente, telefone2, cep, rua, numero, complemento, bairro, cidade, estado) VALUES
(1,  'Caua Silva',                  '123.456.789-00',     'Caua',          'caua.silva@sjcgas.com.br',            '(12) 98811-2233', '12245-000', 'Rua São Sebastião',           '112',  'Apto 101', 'Jardim Aquarius',       'São José dos Campos', 'SP'),
(2,  'João Vinicius Oliveira',      '234.567.890-11',     'João Vinicius', 'joao.vinicius@sjcgas.com.br',        '(12) 99777-4455', '12244-550', 'Avenida Cassiano Ricardo',    '4300', 'Sala 4',   'Jardim Aquarius',       'São José dos Campos', 'SP'),
(3,  'Mateus Alves',                '345.678.901-22',     'Mateus',        'mateus.alves@sjcgas.com.br',          '(12) 99666-7788', '12226-280', 'Rua Padre Francisco',         '98',   NULL,       'Jardim das Indústrias', 'São José dos Campos', 'SP'),
(4,  'Lúcia Martins',               '456.789.012-33',     'Lúcia',         'lucia.martins@sjcgas.com.br',         '(12) 98123-4567', '12234-010', 'Rua Câmara',                  '428',  NULL,       'Vila Adyana',           'São José dos Campos', 'SP'),
(5,  'Fabrício Rocha',              '567.890.123-44',     'Fabrício',      'fabricio.rocha@sjcgas.com.br',        '(12) 98222-3344', '12227-110', 'Rua Miguel Petroni',          '78',   NULL,       'Parque Industrial',     'São José dos Campos', 'SP'),
(6,  'Marina Nunes',                '678.901.234-55',     'Marina',        'marina.nunes@sjcgas.com.br',          '(12) 98111-2233', '12232-150', 'Avenida Andrômeda',           '5250', 'Casa 12',  'Urbanova',              'São José dos Campos', 'SP'),
(7,  'Restaurante Bom Sabor Ltda',  '12.345.678/0001-90', 'Fernando',      'contato@bomsabor.com.br',             '(12) 3234-5678',  '12301-000', 'Rua das Flores',              '123',  NULL,       'Centro',                'Jacareí',             'SP'),
(8,  'Padaria São Benedito',        '23.456.789/0001-01', 'Roseli',        'padaria@saobenedito.com.br',          '(12) 3123-4567',  '12020-010', 'Av. Nove de Julho',           '456',  'Loja A',   'Jardim Satélite',       'São José dos Campos', 'SP'),
(9,  'Indústria Têxtil Vale Ltda',  '34.567.890/0001-12', 'Rodrigo',       'industria@textilvale.com.br',         '(12) 3456-7890',  '12060-000', 'Rua Industrial Norte',        '789',  'Galpão 3', 'Distrito Industrial',   'São José dos Campos', 'SP'),
(10, 'Hospital Santa Casa Taubaté', '45.678.901/0001-23', 'Andréa',        'adm@santacasataubate.org.br',         '(12) 3332-1000',  '12020-100', 'Rua Floriano Peixoto',        '100',  NULL,       'Centro',                'Taubaté',             'SP'),
(11, 'Supermercado Bom Preço',      '56.789.012/0001-34', 'Reinaldo',      'gerencia@supbompreco.com.br',         '(12) 3251-8900',  '12070-000', 'Av. Presidente Vargas',       '1500', NULL,       'Vila Industrial',       'Taubaté',             'SP'),
(12, 'Frigorífico Vale Carnes',     '67.890.123/0001-45', 'Marcelo',       'compras@valecames.com.br',            '(12) 3612-5400',  '12400-000', 'Rod. Presidente Dutra',       'km 85','Galpão A', 'Zona Rural',            'Pindamonhangaba',     'SP'),
(13, 'Hotel Fazenda do Vale',       '78.901.234/0001-56', 'Patrícia',      'reservas@hotelfazendavale.com.br',   '(12) 3101-2200',  '12220-000', 'Estrada do Vale',             '5',    NULL,       'Zona Rural',            'Jacareí',             'SP'),
(14, 'Colégio Dom Bosco',           '89.012.345/0001-67', 'Silvana',       'secretaria@colegiodombosco.com.br',  '(12) 3231-3300',  '12050-000', 'Av. João XXIII',              '200',  NULL,       'Centro',                'Taubaté',             'SP'),
(15, 'Churrascaria do Compadre',    '90.123.456/0001-78', 'Edson',         'churrascaria@compadre.com.br',        '(12) 3153-8700',  '12100-000', 'Av. Euzébio Ferreira',        '900',  NULL,       'Jardim Esplanada',      'Pindamonhangaba',     'SP'),
(16, 'Metalúrgica Aço Forte Ltda',  '01.234.567/0001-89', 'Cleber',        'producao@acoforte.com.br',            '(12) 3944-7600',  '12240-000', 'Rua José Humberto Preto',    '1200', 'Barracão 2','Distrito Industrial',  'São José dos Campos', 'SP'),
(17, 'Panificadora Delícia',        '12.345.670/0001-91', 'Glória',        'panificadora@delicia.com.br',         '(12) 3153-4400',  '12600-000', 'Rua Coronel Rodrigues',       '78',   NULL,       'Centro',                'Lorena',              'SP'),
(18, 'Cerâmica São Paulo Ind.',     '23.456.781/0001-02', 'Valdir',        'ceramica@ceramicasp.com.br',          '(12) 3241-9800',  '12500-000', 'Rua das Cerâmicas',           '1000', NULL,       'Distrito Industrial',   'Guaratinguetá',       'SP'),
(19, 'Escola Municipal Boa Vista',  '34.567.892/0001-13', 'Denise',        'escola@boavista.edu.br',              '(12) 3278-4500',  '12320-000', 'Rua José Alves',              '5',    NULL,       'Jardim das Palmeiras',  'Jacareí',             'SP'),
(20, 'Distribuidora GLP Norte',     '45.678.903/0001-24', 'Sérgio',        'distribuidora@glpnorte.com.br',       '(12) 3627-9000',  '12570-000', 'Av. Dom Pedro I',             '350',  'Galpão 1', 'Parque Industrial',     'Guaratinguetá',       'SP');

-- ── Produtos ──────────────────────────────────────────────────────────────────
-- qtdProduto = estoque atual | Produtos 3, 5, 12 abaixo do qtdMinima → alerta de estoque baixo
INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima) VALUES
(1,  'Tubo Aço Galvanizado 1"',           180, 'Tubo rígido galvanizado para rede de gás',                     50, 500),
(2,  'Registro de Esfera 3/4"',            95, 'Registro de esfera para gás com vedação reforçada',             30, 300),
(3,  'Medidor de Gás Industrial G16',       8, 'Medidor para instalação industrial de gás natural',             10,  50),
(4,  'Válvula Redutora de Pressão',         55, 'Válvula reguladora de pressão para rede de gás',               20, 200),
(5,  'Mangueira Flexível 3/4"',             42, 'Mangueira flexível para conexão de gás',                       50, 300),
(6,  'Cinta de Fixação Metálica',          150, 'Cinta metálica para fixação de tubulações',                    50, 500),
(7,  'Tubo PPR 32mm',                       63, 'Tubo de polipropileno para água e gás',                        20, 200),
(8,  'Filtro de Linha para Gás',            67, 'Filtro de linha de proteção para rede de gás',                 20, 150),
(9,  'Conector Curvo 90° 1/2"',            120, 'Conector em curva para tubulação de gás',                      30, 300),
(10, 'Adaptador Rosca 1/2" x 3/4"',       144, 'Adaptador de rosca para composições mistas',                   50, 500),
(11, 'Lanterna de Inspeção Antichama',      18, 'Lanterna para inspeção com proteção antichama',                10,  80),
(12, 'Detector de Vazão Portátil',           4, 'Detector portátil para vazamentos de gás',                      5,  40),
(13, 'Regulador de Pressão 1ª Família',     72, 'Regulador para GLP residencial, saída 2,8 kPa',                20, 200),
(14, 'Regulador de Pressão 2ª Família',     48, 'Regulador para GLP industrial, saída 15 kPa',                  15, 150),
(15, 'Mangueira GLP 1,20m Certificada',     85, 'Mangueira certificada INMETRO para botijão residencial',       30, 300),
(16, 'Abraçadeira Metálica 3/4"',          200, 'Abraçadeira para fixação de mangueiras e tubos 3/4"',          40, 600),
(17, 'Válvula de Alívio 1/2" 1,5 kgf',     36, 'Válvula de alívio de segurança para sistemas de GLP',          10, 100),
(18, 'Luva de Redução 3/4" x 1/2"',       160, 'Luva de redução roscada galvanizada',                          40, 500),
(19, 'Niple Duplo 1/2"',                   175, 'Niple duplo galvanizado para conexões de gás',                 40, 600),
(20, 'Tê 1/2" Galvanizado',               130, 'Tê roscado para ramificações em redes de gás',                 30, 400),
(21, 'Joelho 90° 1/2" Galvanizado',       145, 'Joelho 90° roscado para mudança de direção',                   30, 500),
(22, 'Joelho 90° 3/4" Galvanizado',       110, 'Joelho 90° roscado 3/4" para tubulações de gás',               25, 400),
(23, 'Tampão Macho 1/2"',                  90, 'Tampão macho roscado para fechamento de pontos de gás',         20, 300),
(24, 'Fita Veda Rosca 18mm x 50m',         95, 'Fita PTFE para vedação de roscas em instalações de gás',       20, 300),
(25, 'Selante para GLP 250ml',              58, 'Selante líquido específico para vedação de conexões GLP',       15, 200),
(26, 'Detector de Gás Natural/GLP',         22, 'Detector fixo de vazamento de gás para ambientes internos',     5, 100),
(27, 'Extintor CO2 6kg',                    15, 'Extintor de dióxido de carbono para áreas de equipamentos',     5,  50),
(28, 'Extintor Pó Químico Seco 4kg',        19, 'Extintor ABC 4kg para uso geral em obras e instalações',        5,  60),
(29, 'Manômetro 0-4 kgf/cm² 1/4"',         33, 'Manômetro para aferição de pressão em redes de GLP',            8, 100),
(30, 'Manifold GLP 4 Saídas',              17, 'Manifold para distribuição simultânea de GLP, 4 saídas',         4,  40),
(31, 'Tubo Flexível Metálico 1m',           38, 'Tubo flexível de aço inox corrugado para fogões industriais',   8, 100),
(32, 'Tubo Flexível Metálico 2m',           25, 'Tubo flexível de aço inox corrugado 2m para uso geral',         6,  80),
(33, 'Conector Rápido GLP 1/2"',            62, 'Engate rápido para mangueiras de GLP, 1/2"',                   15, 200),
(34, 'Válvula Solenóide GLP 1/2" 220V',    13, 'Válvula solenóide 220V para corte automático de GLP',           4,  30),
(35, 'Filtro de GLP Inline 3/4"',           40, 'Filtro de impurezas inline para linhas de GLP 3/4"',           10, 120),
(36, 'Queimador Industrial 50.000 BTU',     11, 'Queimador a gás para uso industrial, 50.000 BTU/h',             3,  30),
(37, 'Queimador Industrial 100.000 BTU',     7, 'Queimador a gás de alta potência para fornos industriais',       2,  20),
(38, 'Kit Reparo de Regulador GLP',         42, 'Kit com vedações e mola para manutenção de reguladores',        10, 150),
(39, 'Capacete de Segurança CA',            28, 'Capacete de proteção com certificado INMETRO',                   5,  60),
(40, 'Óculos de Segurança Incolor',         35, 'Óculos de proteção com lente incolor e vedação lateral',        8,  80),
(41, 'Luva de Couro Cano Longo',            20, 'Luva de couro para trabalhos com gás e maçarico',               5,  50),
(42, 'Bota de Segurança Bico de Aço',       16, 'Bota impermeável com bico de aço para trabalhos em campo',      4,  40),
(43, 'Tubo de Cobre 1/2" (metro)',          220, 'Tubo de cobre mole 1/2" para instalações de gás, por metro',  50, 800),
(44, 'Cano de Aço Preto 1/2" (metro)',     185, 'Cano de aço preto 1/2" para redes internas, por metro',        40, 600),
(45, 'Medidor de Gás Residencial G4',       30, 'Medidor volumétrico para instalações residenciais e comerciais', 8, 100);

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
  'Medidor de Gás Residencial G4'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'Conexão Flex Indústria e Comércio'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Mangueira Flexível 3/4"', 'Mangueira GLP 1,20m Certificada', 'Tubo Flexível Metálico 1m',
  'Tubo Flexível Metálico 2m', 'Conector Rápido GLP 1/2"'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'SafeWork Proteção Industrial'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Lanterna de Inspeção Antichama', 'Extintor CO2 6kg', 'Extintor Pó Químico Seco 4kg',
  'Capacete de Segurança CA', 'Óculos de Segurança Incolor', 'Luva de Couro Cano Longo',
  'Bota de Segurança Bico de Aço'
);

UPDATE produtos p
JOIN fornecedores f ON f.nomeFornecedor = 'QuimGás Insumos Técnicos'
SET p.idFornecedor = f.idFornecedor
WHERE p.nomeProduto IN (
  'Fita Veda Rosca 18mm x 50m', 'Selante para GLP 250ml', 'Kit Reparo de Regulador GLP'
);

SET SQL_SAFE_UPDATES = 1;

-- ── Obras ─────────────────────────────────────────────────────────────────────
-- Status: Concluida(14) | Em andamento(8) | Pausada(5) | À iniciar(2) | Cancelada(1)
INSERT INTO obras (codCliente, descObra, dataInicio, dataFim, statusObra, respObra, obsObra, orientacaoObra, tipoObra, clientePrimario, fieldObra, unidadeObra, emailContato, celular1, celular2) VALUES
-- idObra 1 — Concluida
(1,  'Instalação de ramal de gás em condomínio residencial',         '2026-01-25', '2026-02-17', 'Concluida',    'Carlos Souza',    'Testes de estanqueidade aprovados',           'Revisar juntas e conexões',            'Residencial', 'Supergásbras', 'Gás Canalizado', 'Un', 'caua.silva@sjcgas.com.br',            '(12) 98811-2233', NULL),
-- idObra 2 — Concluida
(1,  'Manutenção preventiva em medidor industrial',                   '2026-01-31', '2026-02-14', 'Concluida',    'Beatriz Almeida', 'Relatório enviado ao cliente',                'Confirmar próxima visita em 6 meses',  'Industrial', 'Supergásbras',  'Medidor',        'Un', 'caua.silva@sjcgas.com.br',            '(12) 98811-2233', NULL),
-- idObra 3 — Concluida
(2,  'Extensão de rede de gás em restaurante na região central',     '2026-02-07', '2026-03-23', 'Concluida',    'Renato Pereira',  'Liberação da prefeitura obtida',              'Agendar início após autorização',      'Comercial', 'Supergásbras',   'Rede de Gás',    'm',  'joao.vinicius@sjcgas.com.br',        '(12) 99777-4455', '(12) 98100-3344'),
-- idObra 4 — Concluida
(2,  'Correção de vazamento em cozinha industrial',                   '2026-02-13', '2026-03-13', 'Concluida',    'Ana Carolina',    'Válvula substituída e teste OK',              'Registrar em manutenção preventiva',   'Industrial', 'Supergásbras',  'Gás Natural',    'Un', 'joao.vinicius@sjcgas.com.br',        '(12) 99777-4455', NULL),
-- idObra 5 — Concluida
(3,  'Instalação de medidor privativo em prédio comercial',           '2026-02-20', '2026-04-11', 'Concluida',    'Carlos Souza',    'Peças entregues e instalação concluída',      'Revisar cronograma com fornecedor',    'Comercial', 'Supergásbras',   'Medidor',        'Un', 'mateus.alves@sjcgas.com.br',         '(12) 99666-7788', NULL),
-- idObra 6 — Concluida
(3,  'Troca de registro e conector em unidade logística',             '2026-02-26', '2026-03-18', 'Concluida',    'Beatriz Almeida', 'Obra entregue com novo certificado',          'Enviar notas fiscais',                 'Logística', 'Supergásbras',   'Conector',       'Un', 'mateus.alves@sjcgas.com.br',         '(12) 99666-7788', NULL),
-- idObra 7 — Pausada
(4,  'Instalação de ramal de gás para cozinha de pizzaria',           '2026-03-04', NULL,         'Pausada',      'Renato Pereira',  'Aguardando liberação do alvará de obra',      'Retomar após regularização',           'Comercial', 'Supergásbras',   'Gás Canalizado', 'm',  'lucia.martins@sjcgas.com.br',        '(12) 98123-4567', NULL),
-- idObra 8 — Concluida
(5,  'Revisão geral de rede de gás na unidade fabril',                '2026-03-11', '2026-04-20', 'Concluida',    'Ana Carolina',    'Painel de controle atualizado',               'Arquivar laudos de teste',             'Industrial', 'Supergásbras',  'Rede de Gás',    'm',  'fabricio.rocha@sjcgas.com.br',       '(12) 98222-3344', NULL),
-- idObra 9 — Em andamento
(6,  'Projeto de ramal de gás para nova loja de estética',            '2026-03-17', NULL,         'Em andamento', 'Carlos Souza',    'Levantamento concluído, execução em curso',   'Enviar orçamento final ao cliente',    'Comercial', 'Supergásbras',   'Projeto',        'Un', 'marina.nunes@sjcgas.com.br',         '(12) 98111-2233', NULL),
-- idObra 10 — Concluida
(7,  'Instalação de rede GLP para cozinha industrial',                '2026-03-24', '2026-04-07', 'Concluida',    'Renato Pereira',  'Instalação conforme ABNT NBR 15526',          'Utilizar tubulação de cobre 1/2"',     'Comercial', 'Supergásbras',   'GLP',            'Un', 'contato@bomsabor.com.br',            '(12) 3234-5678',  NULL),
-- idObra 11 — Em andamento
(8,  'Substituição de reguladores e mangueiras GLP',                  '2026-03-30', NULL,         'Em andamento', 'Carlos Souza',    'Aguardando chegada dos reguladores novos',    'Confirmar entrega com fornecedor',     'Manutenção', 'Supergásbras',  'GLP',            'Un', 'padaria@saobenedito.com.br',         '(12) 3123-4567',  NULL),
-- idObra 12 — Concluida
(9,  'Projeto de instalação GLP industrial - fase 1',                 '2026-04-05', '2026-05-18', 'Concluida',    'Beatriz Almeida', 'Projeto aprovado pela concessionária',        'Pressão de operação: 0,5 kgf/cm²',    'Industrial', 'Supergásbras',  'GLP',            'm',  'industria@textilvale.com.br',        '(12) 3456-7890',  '(12) 99611-1111'),
-- idObra 13 — Concluida
(10, 'Vistoria anual da central de GLP hospitalar',                   '2026-04-12', '2026-04-12', 'Concluida',    'Ana Carolina',    'Aprovada; válvula de segurança substituída',  NULL,                                   'Vistoria', 'Supergásbras',    'GLP',            'Un', 'adm@santacasataubate.org.br',        '(12) 3332-1000',  NULL),
-- idObra 14 — Pausada
(11, 'Adequação da rede GLP - setor de padaria',                      '2026-04-18', NULL,         'Pausada',      'Carlos Souza',    'Obra suspensa por reforma no teto do setor',  'Retomar após conclusão da reforma',    'Instalação', 'Supergásbras',  'GLP',            'm',  'gerencia@supbompreco.com.br',        '(12) 3251-8900',  '(12) 99388-0000'),
-- idObra 15 — Concluida
(12, 'Instalação industrial GLP - câmara fria',                       '2026-04-25', '2026-06-10', 'Concluida',    'Renato Pereira',  'Sistema de aquecimento de câmara fria OK',    'Pressão industrial: 1,5 kgf/cm²',     'Industrial', 'Supergásbras',  'GLP',            'm',  'compras@valecames.com.br',           '(12) 3612-5400',  '(12) 99166-8800'),
-- idObra 16 — Em andamento
(13, 'Revisão e adequação central GLP - hotel',                       '2026-05-01', NULL,         'Em andamento', 'Beatriz Almeida', 'Substituição de válvulas em curso',           'Adequar conforme NR-13',               'Manutenção', 'Supergásbras',  'GLP',            'Un', 'reservas@hotelfazendavale.com.br',  '(12) 3101-2200',  NULL),
-- idObra 17 — Concluida
(14, 'Instalação de rede GLP para cantina escolar',                   '2026-05-08', '2026-05-18', 'Concluida',    'Ana Carolina',    'Fogão 6 bocas instalado',                     NULL,                                   'Instalação', 'Supergásbras',  'GLP',            'm',  'secretaria@colegiodombosco.com.br', '(12) 3231-3300',  NULL),
-- idObra 18 — Cancelada
(15, 'Instalação de rede GLP para churrasqueiras - lote 1',           '2026-05-14', NULL,         'Cancelada',    'Carlos Souza',    'Cliente cancelou por mudança no projeto',     NULL,                                   'Instalação', 'Supergásbras',  'GLP',            'm',  'churrascaria@compadre.com.br',       '(12) 3153-8700',  '(12) 98389-9900'),
-- idObra 19 — Concluida
(16, 'Instalação de rede GLP para solda a gás',                       '2026-05-20', '2026-05-30', 'Concluida',    'Renato Pereira',  'Pontos de GLP para 6 postos de solda',        'Alta pressão de operação',             'Industrial', 'Supergásbras',  'GLP',            'm',  'producao@acoforte.com.br',           '(12) 3944-7600',  '(12) 98167-9000'),
-- idObra 20 — Pausada
(17, 'Instalação de fornos e fogões a GLP',                           '2026-05-27', NULL,         'Pausada',      'Beatriz Almeida', 'Equipamentos aguardando entrega do fornecedor','Confirmar prazo de entrega',           'Instalação', 'Supergásbras',  'GLP',            'Un', 'panificadora@delicia.com.br',        '(12) 3153-4400',  NULL),
-- idObra 21 — Concluida
(18, 'Instalação de forno industrial a gás cerâmica',                 '2026-06-02', '2026-06-27', 'Concluida',    'Carlos Souza',    'Queimadores de 100.000 BTU/h instalados',     'Temp. máxima: 1200°C',                 'Industrial', 'Supergásbras',  'GLP',            'Un', 'ceramica@ceramicasp.com.br',         '(12) 3241-9800',  '(12) 98944-6700'),
-- idObra 22 — Em andamento
(19, 'Instalação de GLP para cozinha escolar',                        '2026-06-09', NULL,         'Em andamento', 'Ana Carolina',    'Tubulação instalada, aguardando ligação final','Coordenar com equipe elétrica',        'Instalação', 'Supergásbras',  'GLP',            'm',  'escola@boavista.edu.br',             '(12) 3278-4500',  NULL),
-- idObra 23 — Concluida
(20, 'Ampliação da central de GLP - depósito 2',                      '2026-06-15', '2026-07-04', 'Concluida',    'Renato Pereira',  'Nova central com capacidade 12 botijões P45', NULL,                                   'Projeto', 'Supergásbras',     'GLP',            'Un', 'distribuidora@glpnorte.com.br',      '(12) 3627-9000',  '(12) 97834-5600'),
-- idObra 24 — Em andamento
(1,  'Manutenção corretiva - revisão geral pós-vistoria',             '2026-06-21', NULL,         'Em andamento', 'Carlos Souza',    'Aguardando laudo de estanqueidade',           'Emitir relatório técnico ao cliente',  'Manutenção', 'Supergásbras',  'GLP',            'Un', 'caua.silva@sjcgas.com.br',            '(12) 98811-2233', NULL),
-- idObra 25 — À iniciar
(10, 'Revisão semestral central de GLP hospitalar',                   '2026-07-22', NULL,         'À iniciar',    'Beatriz Almeida', 'Agendada para final de junho',                'Verificar normas ANVISA vigentes',     'Vistoria', 'Supergásbras',    'GLP',            'Un', 'adm@santacasataubate.org.br',        '(12) 3332-1000',  NULL),
-- idObra 26 — Em andamento
(9,  'Projeto de instalação GLP industrial - fase 2',                 '2026-06-28', NULL,         'Em andamento', 'Ana Carolina',    'Execução do setor de acabamento em curso',    'Integrar com rede existente da fase 1','Industrial', 'Supergásbras',  'GLP',            'm',  'industria@textilvale.com.br',        '(12) 3456-7890',  '(12) 99611-1111'),
-- idObra 27 — À iniciar
(12, 'Manutenção preventiva anual - frigorífico',                     '2026-07-22', NULL,         'À iniciar',    'Carlos Souza',    'Programada para julho; aguardando confirmação','Revisar todo o sistema de GLP',       'Manutenção', 'Supergásbras',  'GLP',            'Un', 'compras@valecames.com.br',           '(12) 3612-5400',  '(12) 99166-8800'),
-- idObra 28 — Pausada
(11, 'Instalação GLP - nova seção de frios supermercado',             '2026-07-04', NULL,         'Pausada',      'Renato Pereira',  'Obra embargada por fiscalização municipal',   'Resolver pendência com a prefeitura',  'Instalação', 'Supergásbras',  'GLP',            'm',  'gerencia@supbompreco.com.br',        '(12) 3251-8900',  '(12) 99388-0000'),
-- idObra 29 — Em andamento
(16, 'Ampliação da rede de GLP industrial - novo setor',              '2026-07-11', NULL,         'Em andamento', 'Beatriz Almeida', 'Integrar com rede existente',                 'Novo setor de produção em expansão',   'Instalação', 'Supergásbras',  'GLP',            'm',  'producao@acoforte.com.br',           '(12) 3944-7600',  '(12) 98167-9000'),
-- idObra 30 — Pausada
(15, 'Instalação de novo setor de churrasco - expansão',              '2026-07-17', NULL,         'Pausada',      'Carlos Souza',    'Cliente solicitou pausa para adequação civil', 'Aguardar liberação do cliente',        'Instalação', 'Supergásbras',  'GLP',            'm',  'churrascaria@compadre.com.br',       '(12) 3153-8700',  '(12) 98389-9900');

-- ── Produtos por Obra ─────────────────────────────────────────────────────────
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
-- Obra 1 — Instalação ramal residencial (Caua Silva)
(1,  1, 20), (1,  5, 10), (1,  6, 15),
-- Obra 2 — Manutenção medidor industrial (Caua Silva)
(2,  3,  1), (2, 11,  2),
-- Obra 3 — Extensão rede restaurante (João Vinicius)
(3,  2,  8), (3,  4,  5), (3,  9, 12),
-- Obra 4 — Correção vazamento cozinha (João Vinicius)
(4,  8,  3), (4, 10,  6),
-- Obra 5 — Medidor prédio comercial (Mateus Alves)
(5,  2,  4), (5,  5, 16), (5, 12,  1),
-- Obra 6 — Troca registro/conector logística (Mateus Alves)
(6,  1,  6), (6,  9,  3),
-- Obra 7 — Ramal pizzaria (Lúcia Martins)
(7,  7, 22), (7,  5,  8),
-- Obra 8 — Revisão rede fabril (Fabrício Rocha)
(8,  1,  5), (8,  4, 10),
-- Obra 9 — Projeto ramal loja de estética (Marina Nunes)
(9,  1,  4), (9,  2,  2), (9,  9,  5),
-- Obra 10 — Instalação GLP cozinha (Restaurante Bom Sabor)
(10, 13,  2), (10, 15,  3), (10, 21,  8),
-- Obra 11 — Substituição reguladores (Padaria São Benedito)
(11, 13,  2), (11, 15,  3), (11, 38,  1),
-- Obra 12 — Projeto GLP industrial fase 1 (Têxtil Vale)
(12,  1, 30), (12, 18, 20), (12, 20, 15), (12, 24,  5),
-- Obra 13 — Vistoria central GLP hospital
(13, 17,  2), (13, 29,  1), (13, 38,  2),
-- Obra 14 — Adequação rede padaria (Supermercado)
(14,  1, 15), (14, 21, 10), (14, 33,  6),
-- Obra 15 — Instalação câmara fria (Frigorífico)
(15, 14,  1), (15, 19, 20), (15, 22, 12), (15, 35,  2),
-- Obra 16 — Revisão central GLP hotel
(16, 17,  3), (16, 25,  2), (16, 38,  3),
-- Obra 17 — Rede GLP cantina escolar
(17,  5, 10), (17, 16, 20), (17, 21,  6),
-- Obra 18 — Rede GLP churrasqueiras
(18,  1, 20), (18, 19, 10), (18, 33,  8),
-- Obra 19 — Pontos GLP para solda (Metalúrgica)
(19, 43, 30), (19, 20, 10), (19, 29,  2),
-- Obra 20 — Fornos e fogões (Panificadora)
(20, 31,  4), (20, 13,  2), (20, 24,  3),
-- Obra 21 — Forno industrial cerâmica
(21, 37,  2), (21, 14,  1), (21, 43, 15),
-- Obra 22 — GLP cozinha escolar
(22, 15,  2), (22, 21,  4), (22, 16, 10),
-- Obra 23 — Ampliação central GLP (Distribuidora)
(23, 14,  2), (23, 17,  4), (23, 30,  2),
-- Obra 24 — Manutenção corretiva (Caua Silva)
(24, 15,  1), (24, 38,  1),
-- Obra 25 — Revisão hospitalar semestral
(25, 17,  2), (25, 29,  1), (25, 38,  2),
-- Obra 26 — Projeto GLP fase 2 (Têxtil Vale)
(26,  1, 25), (26, 18, 15), (26, 20, 12), (26, 44, 20),
-- Obra 27 — Manutenção preventiva frigorífico
(27, 35,  2), (27, 25,  2), (27, 38,  3),
-- Obra 28 — Seção de frios supermercado
(28,  1, 18), (28, 33,  6), (28, 21,  8),
-- Obra 29 — Ampliação industrial metalúrgica (em andamento)
(29, 44, 40), (29, 20, 15), (29, 22, 10),
-- Obra 30 — Expansão churrascaria (em andamento)
(30,  1, 25), (30, 15,  4), (30, 36,  3);

-- ── Histórico ─────────────────────────────────────────────────────────────────
-- Representa as ações realizadas pelos dois admins ao longo do período de uso.
-- idAdmin 1 = adm  |  idAdmin 2 = João
INSERT INTO historico (idAdmin, nomeAdmin, acao, entidade, descricao, dataHora) VALUES

-- ── Abril 2024 — configuração inicial do sistema ──────────────────────────────
(1, 'adm',  'Cadastrou', 'Administrador', 'Cadastrou o administrador ''João''',                                          '2024-04-01 08:15:00'),
(1, 'adm',  'Cadastrou', 'Field',         'Cadastrou o field ''Carlos Souza''',                                          '2024-04-01 09:00:00'),
(1, 'adm',  'Cadastrou', 'Field',         'Cadastrou o field ''Beatriz Almeida''',                                       '2024-04-01 09:05:00'),
(1, 'adm',  'Cadastrou', 'Field',         'Cadastrou o field ''Renato Pereira''',                                        '2024-04-01 09:10:00'),
(1, 'adm',  'Cadastrou', 'Field',         'Cadastrou o field ''Ana Carolina''',                                          '2024-04-01 09:15:00'),

(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''Caua Silva''',                                          '2024-04-03 10:00:00'),
(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''João Vinicius Oliveira''',                              '2024-04-03 10:10:00'),
(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''Mateus Alves''',                                        '2024-04-03 10:20:00'),
(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''Lúcia Martins''',                                       '2024-04-03 10:30:00'),
(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''Fabrício Rocha''',                                      '2024-04-03 10:40:00'),
(1, 'adm',  'Cadastrou', 'Cliente',       'Cadastrou o cliente ''Marina Nunes''',                                        '2024-04-03 10:50:00'),

(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Tubo Aço Galvanizado 1"''',                             '2024-04-05 09:00:00'),
(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Registro de Esfera 3/4"''',                             '2024-04-05 09:10:00'),
(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Medidor de Gás Industrial G16''',                       '2024-04-05 09:20:00'),
(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Válvula Redutora de Pressão''',                         '2024-04-05 09:30:00'),
(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Mangueira Flexível 3/4"''',                             '2024-04-05 09:40:00'),
(1, 'adm',  'Cadastrou', 'Produto',       'Cadastrou o produto ''Cinta de Fixação Metálica''',                           '2024-04-05 09:50:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Tubo PPR 32mm''',                                       '2024-04-05 10:00:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Filtro de Linha para Gás''',                            '2024-04-05 10:10:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Conector Curvo 90° 1/2"''',                             '2024-04-05 10:20:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Adaptador Rosca 1/2" x 3/4"''',                        '2024-04-05 10:30:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Lanterna de Inspeção Antichama''',                      '2024-04-05 10:40:00'),
(2, 'João', 'Cadastrou', 'Produto',       'Cadastrou o produto ''Detector de Vazão Portátil''',                          '2024-04-05 10:50:00'),

-- ── Abril 2024 — primeiro registro de obra ────────────────────────────────────
(2, 'João', 'Cadastrou', 'Obra',          'Cadastrou a obra ''Correção de vazamento em cozinha industrial''',            '2024-04-10 14:00:00'),

-- ── Maio 2024 ────────────────────────────────────────────────────────────────
(2, 'João', 'Editou',    'Obra',          'Alterou status da obra ID 4 para ''Concluida''',                              '2024-05-08 16:30:00'),
(1, 'adm',  'Cadastrou', 'Obra',          'Cadastrou a obra ''Troca de registro e conector em unidade logística''',      '2024-05-12 09:00:00'),

-- ── Junho 2024 ───────────────────────────────────────────────────────────────
(1, 'adm',  'Editou',    'Obra',          'Alterou status da obra ID 6 para ''Concluida''',                              '2024-06-01 17:00:00'),
(1, 'adm',  'Cadastrou', 'Obra',          'Cadastrou a obra ''Manutenção preventiva em medidor industrial''',            '2024-06-18 08:00:00'),

-- ── Julho 2024 ───────────────────────────────────────────────────────────────
(2, 'João', 'Cadastrou', 'Obra',          'Cadastrou a obra ''Revisão geral de rede de gás na unidade fabril''',        '2024-07-01 10:00:00'),
(1, 'adm',  'Editou',    'Obra',          'Alterou status da obra ID 2 para ''Concluida''',                              '2024-07-02 15:00:00'),
(1, 'adm',  'Editou',    'Produto',       'Editou o produto ''Tubo Aço Galvanizado 1"'' (ID: 1)',                        '2024-07-15 11:00:00'),
(2, 'João', 'Editou',    'Produto',       'Editou o produto ''Mangueira Flexível 3/4"'' (ID: 5)',                        '2024-07-15 11:15:00'),
(2, 'João', 'Cadastrou', 'Obra',          'Cadastrou a obra ''Instalação de medidor privativo em prédio comercial''',   '2024-07-22 09:00:00'),

-- ── Agosto 2024 ──────────────────────────────────────────────────────────────
(1, 'adm',  'Cadastrou', 'Obra',          'Cadastrou a obra ''Instalação de ramal de gás em condomínio residencial''',  '2024-08-05 08:30:00'),
(2, 'João', 'Editou',    'Obra',          'Alterou status da obra ID 8 para ''Concluida''',                              '2024-08-10 16:00:00'),
(1, 'adm',  'Cadastrou', 'Obra',          'Cadastrou a obra ''Instalação de ramal de gás para cozinha de pizzaria''',   '2024-08-12 09:00:00'),
(2, 'João', 'Editou',    'Obra',          'Alterou status da obra ID 5 para ''Pausada''',                                '2024-08-20 14:00:00'),

-- ── Setembro 2024 ────────────────────────────────────────────────────────────
(2, 'João', 'Cadastrou', 'Obra',          'Cadastrou a obra ''Extensão de rede de gás em restaurante na região central''', '2024-09-01 08:00:00'),
(1, 'adm',  'Editou',    'Cliente',       'Editou o cliente ''Fabrício Rocha'' (ID: 5)',                                 '2024-09-10 10:00:00'),
(1, 'adm',  'Cadastrou', 'Obra',          'Cadastrou a obra ''Projeto de ramal de gás para nova loja de estética''',    '2024-09-15 09:00:00'),
(2, 'João', 'Deletou',   'Produto',       'Deletou o produto ''Bucha de Redução 1/2"'' (ID: 13)',                       '2024-09-28 15:00:00'),

-- ── Outubro 2024 ─────────────────────────────────────────────────────────────
(2, 'João', 'Editou',    'Produto',       'Editou o produto ''Detector de Vazão Portátil'' (ID: 12)',                   '2024-10-05 11:30:00'),
(1, 'adm',  'Editou',    'Obra',          'Editou a obra ''Instalação de ramal de gás em condomínio residencial'' (ID: 1)', '2024-10-10 14:00:00'),
(1, 'adm',  'Editou',    'Field',         'Editou o field para ''Carlos Souza Técnico'' (ID: 1)',                        '2024-10-18 09:30:00'),
(2, 'João', 'Editou',    'Field',         'Editou o field para ''Carlos Souza'' (ID: 1)',                                '2024-10-18 10:00:00'),

-- ── Novembro 2024 ────────────────────────────────────────────────────────────
(1, 'adm',  'Deletou',   'Cliente',       'Deletou o cliente ''Empresa Teste Ltda.'' (ID: 7)',                           '2024-11-04 09:00:00'),
(2, 'João', 'Editou',    'Cliente',       'Editou o cliente ''Marina Nunes'' (ID: 6)',                                   '2024-11-12 14:30:00'),
(1, 'adm',  'Editou',    'Produto',       'Editou o produto ''Registro de Esfera 3/4"'' (ID: 2)',                        '2024-11-20 11:00:00'),
(2, 'João', 'Deletou',   'Administrador', 'Deletou o administrador ''teste'' (ID: 3)',                                   '2024-11-25 16:00:00');


-- ══════════════════════════════════════════════════════════════════════════════
-- CATÁLOGO DE SERVIÇOS (FICTÍCIO)
-- Dados fictícios para desenvolvimento — SUBSTITUIR pelo catálogo real
-- assim que recebido da TecnoVale Gás.
-- ══════════════════════════════════════════════════════════════════════════════

INSERT INTO servicos (idServico, nomeServico, precoServico) VALUES
(1, 'Instalação de Ramal Residencial',  850.00),
(2, 'Instalação de Ramal Comercial',   1450.00),
(3, 'Manutenção Preventiva de Medidor', 320.00),
(4, 'Correção de Vazamento',            480.00),
(5, 'Troca de Registro e Conector',     210.00),
(6, 'Extensão de Rede Comercial',      1200.00),
(7, 'Instalação de Medidor Privativo',  690.00),
(8, 'Vistoria e Laudo Técnico',         380.00);

-- ── Receita de produtos por serviço ────────────────────────────────────────────
-- idProduto buscado pelo nome exato já cadastrado na tabela produtos, para não
-- depender da ordem/IDs de quem rodar este script.

-- Serviço 1 — Instalação de Ramal Residencial
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 1, idProduto, qtd FROM (
  SELECT idProduto, 10 AS qtd FROM produtos WHERE nomeProduto = 'Tubo Aço Galvanizado 1"'
  UNION ALL SELECT idProduto, 1  FROM produtos WHERE nomeProduto = 'Registro de Esfera 3/4"'
  UNION ALL SELECT idProduto, 1  FROM produtos WHERE nomeProduto = 'Válvula Redutora de Pressão'
  UNION ALL SELECT idProduto, 2  FROM produtos WHERE nomeProduto = 'Mangueira Flexível 3/4"'
  UNION ALL SELECT idProduto, 4  FROM produtos WHERE nomeProduto = 'Cinta de Fixação Metálica'
) AS receita;

-- Serviço 2 — Instalação de Ramal Comercial
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 2, idProduto, qtd FROM (
  SELECT idProduto, 25 AS qtd FROM produtos WHERE nomeProduto = 'Tubo Aço Galvanizado 1"'
  UNION ALL SELECT idProduto, 2  FROM produtos WHERE nomeProduto = 'Registro de Esfera 3/4"'
  UNION ALL SELECT idProduto, 1  FROM produtos WHERE nomeProduto = 'Medidor de Gás Industrial G16'
  UNION ALL SELECT idProduto, 1  FROM produtos WHERE nomeProduto = 'Válvula Redutora de Pressão'
  UNION ALL SELECT idProduto, 10 FROM produtos WHERE nomeProduto = 'Cinta de Fixação Metálica'
) AS receita;

-- Serviço 3 — Manutenção Preventiva de Medidor
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 3, idProduto, qtd FROM (
  SELECT idProduto, 1 AS qtd FROM produtos WHERE nomeProduto = 'Filtro de Linha para Gás'
) AS receita;

-- Serviço 4 — Correção de Vazamento
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 4, idProduto, qtd FROM (
  SELECT idProduto, 1 AS qtd FROM produtos WHERE nomeProduto = 'Mangueira Flexível 3/4"'
  UNION ALL SELECT idProduto, 3 FROM produtos WHERE nomeProduto = 'Cinta de Fixação Metálica'
  UNION ALL SELECT idProduto, 1 FROM produtos WHERE nomeProduto = 'Registro de Esfera 3/4"'
) AS receita;

-- Serviço 5 — Troca de Registro e Conector
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 5, idProduto, qtd FROM (
  SELECT idProduto, 1 AS qtd FROM produtos WHERE nomeProduto = 'Registro de Esfera 3/4"'
  UNION ALL SELECT idProduto, 1 FROM produtos WHERE nomeProduto = 'Conector Curvo 90° 1/2"'
) AS receita;

-- Serviço 6 — Extensão de Rede Comercial
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 6, idProduto, qtd FROM (
  SELECT idProduto, 18 AS qtd FROM produtos WHERE nomeProduto = 'Tubo Aço Galvanizado 1"'
  UNION ALL SELECT idProduto, 8  FROM produtos WHERE nomeProduto = 'Tubo PPR 32mm'
  UNION ALL SELECT idProduto, 12 FROM produtos WHERE nomeProduto = 'Cinta de Fixação Metálica'
  UNION ALL SELECT idProduto, 1  FROM produtos WHERE nomeProduto = 'Válvula Redutora de Pressão'
) AS receita;

-- Serviço 7 — Instalação de Medidor Privativo
INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
SELECT 7, idProduto, qtd FROM (
  SELECT idProduto, 1 AS qtd FROM produtos WHERE nomeProduto = 'Medidor de Gás Industrial G16'
  UNION ALL SELECT idProduto, 1 FROM produtos WHERE nomeProduto = 'Registro de Esfera 3/4"'
  UNION ALL SELECT idProduto, 1 FROM produtos WHERE nomeProduto = 'Filtro de Linha para Gás'
) AS receita;

-- Serviço 8 — Vistoria e Laudo Técnico (sem consumo de produtos — apenas mão de obra)
-- Nenhum insert em servicoProdutos para este serviço.

-- ── Serviços por Obra ─────────────────────────────────────────────────────────
-- Vincula cada obra ao serviço do catálogo mais próximo do que foi descrito.
-- Precisa rodar depois do catálogo de serviços acima (FK idServico → servicos).
INSERT INTO obraServicos (idObra, idServico) VALUES
(1,  1), -- Instalação de ramal residencial            → Instalação de Ramal Residencial
(2,  3), -- Manutenção preventiva medidor industrial    → Manutenção Preventiva de Medidor
(3,  6), -- Extensão de rede restaurante                → Extensão de Rede Comercial
(4,  4), -- Correção de vazamento cozinha industrial    → Correção de Vazamento
(5,  7), -- Medidor privativo prédio comercial          → Instalação de Medidor Privativo
(6,  5), -- Troca de registro/conector logística        → Troca de Registro e Conector
(7,  2), -- Ramal pizzaria                              → Instalação de Ramal Comercial
(8,  8), -- Revisão geral rede fabril                   → Vistoria e Laudo Técnico
(9,  2), -- Projeto ramal loja de estética              → Instalação de Ramal Comercial
(10, 6), -- Instalação rede GLP cozinha industrial      → Extensão de Rede Comercial
(11, 5), -- Substituição reguladores/mangueiras GLP     → Troca de Registro e Conector
(12, 2), -- Projeto GLP industrial fase 1               → Instalação de Ramal Comercial
(13, 8), -- Vistoria central GLP hospitalar             → Vistoria e Laudo Técnico
(14, 6), -- Adequação rede GLP padaria                  → Extensão de Rede Comercial
(15, 2), -- Instalação industrial GLP câmara fria       → Instalação de Ramal Comercial
(16, 8), -- Revisão central GLP hotel                   → Vistoria e Laudo Técnico
(17, 6), -- Rede GLP cantina escolar                    → Extensão de Rede Comercial
(18, 6), -- Rede GLP churrasqueiras (Cancelada)         → Extensão de Rede Comercial
(19, 2), -- Rede GLP solda a gás                        → Instalação de Ramal Comercial
(20, 6), -- Fornos e fogões a GLP                       → Extensão de Rede Comercial
(21, 2), -- Forno industrial a gás cerâmica             → Instalação de Ramal Comercial
(22, 1), -- GLP cozinha escolar                         → Instalação de Ramal Residencial
(23, 6), -- Ampliação central GLP depósito 2            → Extensão de Rede Comercial
(24, 3), -- Manutenção corretiva pós-vistoria           → Manutenção Preventiva de Medidor
(25, 8), -- Revisão semestral central GLP hospitalar    → Vistoria e Laudo Técnico
(26, 2), -- Projeto GLP industrial fase 2               → Instalação de Ramal Comercial
(27, 3), -- Manutenção preventiva anual frigorífico     → Manutenção Preventiva de Medidor
(28, 6), -- Seção de frios supermercado                 → Extensão de Rede Comercial
(29, 6), -- Ampliação rede GLP industrial novo setor    → Extensão de Rede Comercial
(30, 1); -- Novo setor de churrasco expansão            → Instalação de Ramal Residencial

-- Recalcula valorObra das obras concluídas com base nos serviços vinculados,
-- replicando a regra de negócio real (ObraDAO.atualizar_status): soma do
-- precoServico de todos os serviços ligados à obra via obraServicos.
-- SQL_SAFE_UPDATES desligado temporariamente: o MySQL Workbench bloqueia
-- UPDATE...JOIN por não reconhecer a condição do join como uma cláusula de
-- chave simples, mesmo o WHERE final usando idObra (chave primária).
SET SQL_SAFE_UPDATES = 0;

UPDATE obras o
JOIN (
    SELECT os.idObra, SUM(s.precoServico) AS total
    FROM obraServicos os
    JOIN servicos s ON s.idServico = os.idServico
    GROUP BY os.idObra
) totais ON totais.idObra = o.idObra
SET o.valorObra = totais.total
WHERE o.statusObra = 'Concluida';

SET SQL_SAFE_UPDATES = 1;