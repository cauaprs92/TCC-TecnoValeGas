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

-- ── Clientes ──────────────────────────────────────────────────────────────────
INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, contatoCliente, emailCliente, telefone2, cep, rua, numero, complemento, bairro, cidade, estado) VALUES
(1, 'Caua Silva',             '123.456.789-00', 'Caua',          'caua.silva@sjcgas.com.br',       '(12) 98811-2233', '12245-000', 'Rua São Sebastião',         '112',  'Apto 101', 'Jardim Aquarius',       'São José dos Campos', 'SP'),
(2, 'João Vinicius Oliveira', '234.567.890-11', 'João Vinicius', 'joao.vinicius@sjcgas.com.br',   '(12) 99777-4455', '12244-550', 'Avenida Cassiano Ricardo', '4300', 'Sala 4',   'Jardim Aquarius',       'São José dos Campos', 'SP'),
(3, 'Mateus Alves',           '345.678.901-22', 'Mateus',        'mateus.alves@sjcgas.com.br',     '(12) 99666-7788', '12226-280', 'Rua Padre Francisco',       '98',   NULL,       'Jardim das Indústrias', 'São José dos Campos', 'SP'),
(4, 'Lúcia Martins',          '456.789.012-33', 'Lúcia',         'lucia.martins@sjcgas.com.br',    '(12) 98123-4567', '12234-010', 'Rua Câmara',               '428',  NULL,       'Vila Adyana',           'São José dos Campos', 'SP'),
(5, 'Fabrício Rocha',         '567.890.123-44', 'Fabrício',      'fabricio.rocha@sjcgas.com.br',   '(12) 98222-3344', '12227-110', 'Rua Miguel Petroni',        '78',   NULL,       'Parque Industrial',     'São José dos Campos', 'SP'),
(6, 'Marina Nunes',           '678.901.234-55', 'Marina',        'marina.nunes@sjcgas.com.br',     '(12) 98111-2233', '12232-150', 'Avenida Andrômeda',         '5250', 'Casa 12',  'Urbanova',              'São José dos Campos', 'SP');

-- ── Produtos ──────────────────────────────────────────────────────────────────
-- qtdProduto = estoque atual (já descontadas as quantidades usadas nas obras abaixo)
-- Produtos 3, 5 e 12 estão abaixo do qtdMinima → gerarão alertas de estoque baixo
INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima) VALUES
(1,  'Tubo Aço Galvanizado 1"',        180, 'Tubo rígido galvanizado para rede de gás',              50, 500),
(2,  'Registro de Esfera 3/4"',          95, 'Registro de esfera para gás com vedação reforçada',     30, 300),
(3,  'Medidor de Gás Industrial G16',     8, 'Medidor para instalação industrial de gás natural',     10,  50),
(4,  'Válvula Redutora de Pressão',       55, 'Válvula reguladora de pressão para rede de gás',       20, 200),
(5,  'Mangueira Flexível 3/4"',           42, 'Mangueira flexível para conexão de gás',               50, 300),
(6,  'Cinta de Fixação Metálica',        150, 'Cinta metálica para fixação de tubulações',            50, 500),
(7,  'Tubo PPR 32mm',                     63, 'Tubo de polipropileno para água e gás',                20, 200),
(8,  'Filtro de Linha para Gás',           67, 'Filtro de linha de proteção para rede de gás',         20, 150),
(9,  'Conector Curvo 90° 1/2"',           120, 'Conector em curva para tubulação de gás',              30, 300),
(10, 'Adaptador Rosca 1/2" x 3/4"',      144, 'Adaptador de rosca para composições mistas',           50, 500),
(11, 'Lanterna de Inspeção Antichama',     18, 'Lanterna para inspeção com proteção antichama',        10,  80),
(12, 'Detector de Vazão Portátil',          4, 'Detector portátil para vazamentos de gás',              5,  40);

-- ── Obras ─────────────────────────────────────────────────────────────────────
INSERT INTO obras (codCliente, descObra, dataInicio, dataFim, statusObra, respObra, obsObra, orientacaoObra, tipoObra, fieldObra, unidadeObra, emailContato, celular1, celular2) VALUES
-- idObra 1
(1, 'Instalação de ramal de gás em condomínio residencial',      '2024-08-05', NULL,         'Em andamento', 'Carlos Souza',   'Falta finalizar testes de estanqueidade',    'Revisar juntas e conexões',           'Residencial', 'Gás Canalizado', 'Un', 'caua.contato@sjcgas.com.br',   '(12) 98811-2233', NULL),
-- idObra 2
(1, 'Manutenção preventiva em medidor industrial',               '2024-06-18', '2024-07-02', 'Concluida',    'Beatriz Almeida','Relatório enviado ao cliente',              'Confirmar próxima visita em 6 meses', 'Industrial',  'Medidor',        'Un', 'caua.contato@sjcgas.com.br',   '(12) 98811-2233', NULL),
-- idObra 3
(2, 'Extensão de rede de gás em restaurante na região central',  '2024-09-01', NULL,         'À iniciar',    'Renato Pereira', 'Aguardando liberação de prefeitura',        'Agendar início após autorização',     'Comercial',   'Rede de Gás',    'm',  'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', '(12) 98100-3344'),
-- idObra 4
(2, 'Correção de vazamento em cozinha industrial',               '2024-04-10', '2024-05-08', 'Concluida',    'Ana Carolina',   'Válvula substituída e teste OK',            'Registrar em manutenção preventiva',  'Industrial',  'Gás Natural',    'Un', 'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', NULL),
-- idObra 5
(3, 'Instalação de medidor privativo em prédio comercial',       '2024-07-22', NULL,         'Pausada',      'Carlos Souza',   'Aguardando entrega de peças',              'Revisar cronograma com fornecedor',   'Comercial',   'Medidor',        'Un', 'mateus.alves@sjcgas.com.br',  '(12) 99666-7788', NULL),
-- idObra 6
(3, 'Troca de registro e conector em unidade logística',         '2024-05-12', '2024-06-01', 'Concluida',    'Beatriz Almeida','Obra entregue com novo certificado',       'Enviar notas fiscais',                'Logística',   'Conector',       'Un', 'mateus.alves@sjcgas.com.br',  '(12) 99666-7788', NULL),
-- idObra 7
(4, 'Instalação de ramal de gás para cozinha de pizzaria',       '2024-08-12', NULL,         'Em andamento', 'Renato Pereira', 'Instalação de mangueiras em andamento',    'Acompanhar equipe técnica',           'Comercial',   'Gás Canalizado', 'm',  'lucia.martins@sjcgas.com.br', '(12) 98123-4567', NULL),
-- idObra 8
(5, 'Revisão geral de rede de gás na unidade fabril',            '2024-07-01', '2024-08-10', 'Concluida',    'Ana Carolina',   'Painel de controle atualizado',            'Arquivar laudos de teste',            'Industrial',  'Rede de Gás',    'm',  'fabricio.rocha@sjcgas.com.br','(12) 98222-3344', NULL),
-- idObra 9
(6, 'Projeto de ramal de gás para nova loja de estética',        '2024-09-15', NULL,         'À iniciar',    'Carlos Souza',   'Aguardando aprovação do cliente',          'Enviar orçamento final',              'Comercial',   'Projeto',        'Un', 'marina.nunes@sjcgas.com.br',  '(12) 98111-2233', NULL);

-- ── Produtos por Obra ─────────────────────────────────────────────────────────
-- Consumo total por produto:
--   Tubo 1"  (1): 20+6+5+4 = 35   Mangueira (5): 10+16+8 = 34  Cinta   (6): 15
--   Registro (2): 8+4+2   = 14    Cinta     (6): 15             Tubo PPR(7): 22
--   Medidor  (3): 1                Tubo PPR  (7): 22             Filtro  (8): 3
--   Válvula  (4): 5+10    = 15    Conector  (9): 12+3+5 = 20   Adapta (10): 6
--   Lanterna(11): 2               Detector (12): 1
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
-- Obra 1 — Instalação ramal residencial (Caua Silva)
(1,  1, 20),
(1,  5, 10),
(1,  6, 15),
-- Obra 2 — Manutenção medidor industrial (Caua Silva)
(2,  3,  1),
(2, 11,  2),
-- Obra 3 — Extensão rede restaurante (João Vinicius)
(3,  2,  8),
(3,  4,  5),
(3,  9, 12),
-- Obra 4 — Correção vazamento cozinha (João Vinicius)
(4,  8,  3),
(4, 10,  6),
-- Obra 5 — Medidor prédio comercial (Mateus Alves)
(5,  2,  4),
(5,  5, 16),
(5, 12,  1),
-- Obra 6 — Troca registro/conector logística (Mateus Alves)
(6,  1,  6),
(6,  9,  3),
-- Obra 7 — Ramal pizzaria (Lúcia Martins)
(7,  7, 22),
(7,  5,  8),
-- Obra 8 — Revisão rede fabril (Fabrício Rocha)
(8,  1,  5),
(8,  4, 10),
-- Obra 9 — Projeto ramal loja de estética (Marina Nunes)
(9,  1,  4),
(9,  2,  2),
(9,  9,  5);

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
