-- ============================================================
-- SEED — TecnoValeGás
-- Rodar APÓS codigo.sql (banco tcc já criado)
-- Senha de todos os logins extras: adm123
-- ============================================================

USE tcc;

-- ── LIMPEZA (preserva o login admin padrão idLogin=1) ─────────
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM produtosObras;
DELETE FROM obras;
DELETE FROM produtos;
DELETE FROM clientes;
DELETE FROM responsavel;
DELETE FROM login WHERE idLogin != 1;
SET FOREIGN_KEY_CHECKS = 1;

-- Reset AUTO_INCREMENT
ALTER TABLE produtosObras AUTO_INCREMENT = 1;
ALTER TABLE obras         AUTO_INCREMENT = 1;
ALTER TABLE responsavel   AUTO_INCREMENT = 1;

-- ── RESPONSÁVEIS ──────────────────────────────────────────────
INSERT INTO responsavel (nomeResponsavel) VALUES
  ('Carlos Mendes'),
  ('Rafael Oliveira'),
  ('Fernanda Costa'),
  ('Bruno Lima'),
  ('Patrícia Souza'),
  ('Marcelo Santos');

-- ── LOGINS EXTRAS (senha: adm123) ────────────────────────────
INSERT INTO login (email, senha, nomeLogin) VALUES
  ('carlos.mendes@tecnovale.com.br',   '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Carlos Mendes'),
  ('fernanda.costa@tecnovale.com.br',  '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Fernanda Costa'),
  ('rafael.oliveira@tecnovale.com.br', '$2b$12$kBRKSWOo6.maB7H6G/g.OOVXvjXN5k/vv0VP348VMN0SzCy0mDuaO', 'Rafael Oliveira');

-- ── PRODUTOS ──────────────────────────────────────────────────
-- Alguns propositalmente abaixo do mínimo para acionar alertas no dashboard
INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima) VALUES
  (1,  'Tubo Aço Galvanizado 1/2"',       52, 'Tubo aço galvanizado p/ gás, DN 1/2". Barra 6m.',                   30,  500),
  (2,  'Tubo Aço Galvanizado 3/4"',       43, 'Tubo aço galvanizado p/ gás, DN 3/4". Barra 6m.',                   25,  400),
  (3,  'Tubo Aço Galvanizado 1"',         18, 'Tubo aço galvanizado p/ gás, DN 1". Barra 6m.',                     20,  300),  -- abaixo do mínimo
  (4,  'Registro de Esfera 1/2"',         37, 'Registro esfera latão niquelado p/ gás, 1/2". Máx. 10 kgf/cm².',   10,  200),
  (5,  'Registro de Esfera 3/4"',          7, 'Registro esfera latão niquelado p/ gás, 3/4". Máx. 10 kgf/cm².',   10,  150),  -- abaixo do mínimo
  (6,  'Medidor de Gás Residencial G4',   21, 'Medidor diafragma G4, cap. 6 m³/h. Residencial/comercial leve.',    5,  100),
  (7,  'Medidor de Gás Industrial G16',    3, 'Medidor diafragma G16, cap. 25 m³/h. Uso industrial.',              5,   30),  -- abaixo do mínimo
  (8,  'Redutor de Pressão Doméstico',    44, 'Regulador p/ botijão P13. Saída 28 mbar. Cert. INMETRO.',           15,  200),
  (9,  'Válvula de Segurança Automática', 28, 'Válvula corte automático GLP/GN. Exc. fluxo.',                      10,  150),
  (10, 'Flexível para Gás 1,20m',         51, 'Mangueira inox trançado 1/2" × 1,20m. Cert. INMETRO.',             20,  300),
  (11, 'Flexível para Gás 0,60m',         66, 'Mangueira inox trançado 1/2" × 0,60m. Cert. INMETRO.',             25,  350),
  (12, 'Conector de Compressão 1/2"',    140, 'Conector compressão latão p/ tubo cobre/aço, 1/2".',               50,  600),
  (13, 'Curva 90° Aço Galvanizado 1/2"', 108, 'Curva 90° rosqueada aço galvanizado, 1/2".',                       40,  500),
  (14, 'Nipple Galvanizado 1/2"',        204, 'Nipple curto aço galvanizado rosqueado, 1/2". Comp. 5cm.',          80,  800),
  (15, 'Bucha de Redução 3/4"x1/2"',     92, 'Bucha redução rosqueada aço galvanizado, 3/4" → 1/2".',            30,  400);

-- ── CLIENTES ──────────────────────────────────────────────────
INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, contatoCliente, emailCliente, telefone2, cep, rua, numero, complemento, bairro, cidade, estado) VALUES
  (1,  'Cond. Residencial Jardim das Flores', '12.345.678/0001-90', '(11) 3456-7890', 'sindico@jardimdaflores.com.br',         '(11) 97456-1234', '01310-100', 'Av. Paulista',             '1578', 'Apto 201',     'Bela Vista',      'São Paulo',             'SP'),
  (2,  'Construtora Horizonte Ltda',          '23.456.789/0001-01', '(11) 4567-8901', 'obras@construthoriz.com.br',            '(11) 98567-2345', '04779-000', 'Rua Vergueiro',            '3456', 'Sala 5',       'Vila Mariana',    'São Paulo',             'SP'),
  (3,  'Ind. Metalúrgica Vitória S.A.',       '34.567.890/0001-12', '(11) 5678-9012', 'manutencao@metalvitoria.ind.br',        '(11) 99678-3456', '09426-460', 'Av. dos Metalúrgicos',     '890',  NULL,           'Centro',          'Santo André',           'SP'),
  (4,  'Supermercado Central Eireli',         '45.678.901/0001-23', '(11) 6789-0123', 'gerencia@supercentral.com.br',          '(11) 91789-4567', '13015-001', 'Rua Barão de Jaguara',     '1200', NULL,           'Centro',          'Campinas',              'SP'),
  (5,  'Escola Est. Dom Pedro II',            '56.789.012/0001-34', '(11) 7890-1234', 'diretoria@eedompedro.sp.gov.br',        '(11) 92890-5678', '01525-000', 'Rua da Mooca',             '2340', NULL,           'Mooca',           'São Paulo',             'SP'),
  (6,  'Hospital Municipal São Lucas',        '67.890.123/0001-45', '(13) 8901-2345', 'infraestrutura@hsaolucas.sp.gov.br',   '(13) 93901-6789', '11015-020', 'Av. Ana Costa',            '160',  NULL,           'Gonzaga',         'Santos',                'SP'),
  (7,  'Shopping Vale Norte S.A.',            '78.901.234/0001-56', '(11) 9012-3456', 'operacoes@shoppingvalenorte.com.br',   '(11) 94012-7890', '02401-000', 'Av. Brás Leme',            '3000', NULL,           'Santana',         'São Paulo',             'SP'),
  (8,  'Restaurante Sabor da Terra Ltda',     '89.012.345/0001-67', '(11) 1234-5678', 'contato@sabordaterra.com.br',           '(11) 95123-8901', '04101-300', 'Rua Domingos de Morais',   '2187', 'Loja 12',      'Vila Mariana',    'São Paulo',             'SP'),
  (9,  'Universidade do Vale Paulista',       '90.123.456/0001-78', '(17) 2345-6789', 'facilities@univale.edu.br',             '(17) 96234-9012', '15025-000', 'Av. Bady Bassitt',         '3775', 'Bloco A',      'Vila Redentora',  'São José do Rio Preto', 'SP'),
  (10, 'Cond. Empresarial TechPark',          '01.234.567/0001-89', '(11) 3456-7891', 'gestao@techparkcondominio.com.br',      '(11) 97345-0123', '06453-000', 'Av. das Nações Unidas',    '12901','Torre 3 Sl 42','Brooklin',         'São Paulo',             'SP');

-- ── MIGRAÇÃO — colunas extras de obras (ignora se já existirem) ─
ALTER TABLE obras
  ADD COLUMN IF NOT EXISTS tipoObra     VARCHAR(100),
  ADD COLUMN IF NOT EXISTS fieldObra    VARCHAR(100),
  ADD COLUMN IF NOT EXISTS unidadeObra  VARCHAR(20),
  ADD COLUMN IF NOT EXISTS emailContato VARCHAR(100),
  ADD COLUMN IF NOT EXISTS celular1     VARCHAR(20),
  ADD COLUMN IF NOT EXISTS celular2     VARCHAR(20);

-- ── OBRAS ─────────────────────────────────────────────────────
-- idObra AUTO_INCREMENT → 1..19 na ordem dos INSERTs abaixo
INSERT INTO obras (codCliente, descObra, dataInicio, dataFim, statusObra, respObra, obsObra, orientacaoObra, tipoObra, fieldObra, unidadeObra, emailContato, celular1, celular2) VALUES
-- 1
('1',  'Instalação rede de gás — Bloco A',         '2024-02-10', '2024-03-05', 'Concluída',         'Carlos Mendes',   '24 unidades, instalação completa.',              'Entrar pela portaria lateral.',          'Instalação',   'Residencial',  'Unidade',         'sindico@jardimdaflores.com.br',         '(11) 99111-0001', NULL),
-- 2
('1',  'Instalação rede de gás — Bloco B',         '2024-03-08', '2024-04-02', 'Concluída',         'Rafael Oliveira', '24 unidades, instalação completa.',              'Entrar pela portaria lateral.',          'Instalação',   'Residencial',  'Unidade',         'sindico@jardimdaflores.com.br',         '(11) 99111-0001', NULL),
-- 3
('2',  'Implantação GN — Obra Vila das Pedras',    '2024-04-15', '2024-07-20', 'Concluída',         'Fernanda Costa',  '120 unidades residenciais.',                     'Seguir planta técnica RT-024.',          'Implantação',  'Residencial',  'Condomínio',      'obras@construthoriz.com.br',            '(11) 98567-2345', '(11) 98567-2346'),
-- 4
('3',  'Manutenção preventiva — rede industrial',  '2024-05-03', '2024-05-08', 'Concluída',         'Bruno Lima',      'Revisão geral, troca de 3 registros.',           'Área restrita — uso obrigatório de EPI.','Manutenção',   'Industrial',   'Planta',          'manutencao@metalvitoria.ind.br',        '(11) 99678-3456', NULL),
-- 5
('4',  'Adequação rede GLP — loja principal',      '2024-06-01', '2024-06-10', 'Concluída',         'Marcelo Santos',  'Troca de medidor e adequação à ABNT 15526.',     'Acesso pela entrada de serviço.',        'Adequação',    'Comercial',    'Estabelecimento', 'gerencia@supercentral.com.br',          '(11) 91789-4567', NULL),
-- 6
('7',  'Instalação GN — praça de alimentação',     '2024-07-14', '2024-09-30', 'Concluída',         'Fernanda Costa',  '18 restaurantes. Central de gás.',               'Planta fornecida pela engenharia.',      'Instalação',   'Comercial',    'Shopping',        'operacoes@shoppingvalenorte.com.br',   '(11) 94012-7890', '(11) 94012-7891'),
-- 7
('9',  'Renovação rede GN — Bloco Engenharias',    '2024-08-20', '2024-10-15', 'Concluída',         'Carlos Mendes',   'Substituição de tubulação obsoleta.',            'Coordenar com TI para uso de andaimes.', 'Renovação',    'Educacional',  'Bloco',           'facilities@univale.edu.br',             '(17) 96234-9012', NULL),
-- 8
('6',  'Instalação GN — ala cirúrgica',            '2025-01-10', NULL,         'Em andamento',      'Patrícia Souza',  'Alta complexidade — gases medicinais e GN.',     'Acesso somente com crachá hospitalar.',  'Instalação',   'Hospitalar',   'Ala',             'infraestrutura@hsaolucas.sp.gov.br',   '(13) 93901-6789', NULL),
-- 9
('2',  'Implantação GN — Obra Pinheiros',          '2025-02-03', NULL,         'Em andamento',      'Rafael Oliveira', '80 unidades, condomínio misto.',                 'Planta RT-031, revisão 2.',              'Implantação',  'Residencial',  'Condomínio',      'obras@construthoriz.com.br',            '(11) 98567-2345', '(11) 98567-2347'),
-- 10
('10', 'Adequação ABNT 15526 — Torre 3',           '2025-02-17', NULL,         'Em andamento',      'Bruno Lima',      '42 empresas impactadas.',                        'Obra em ambiente corporativo ativo.',    'Adequação',    'Comercial',    'Condomínio',      'gestao@techparkcondominio.com.br',      '(11) 97345-0123', NULL),
-- 11
('5',  'Instalação GN — cozinha industrial',       '2025-03-05', NULL,         'Em andamento',      'Marcelo Santos',  'Nova cozinha para 1200 alunos/dia.',             'Acesso somente no período matutino.',    'Instalação',   'Educacional',  'Estabelecimento', 'diretoria@eedompedro.sp.gov.br',        '(11) 92890-5678', NULL),
-- 12
('3',  'Ampliação rede — setor de estamparia',     '2025-03-20', NULL,         'Em andamento',      'Carlos Mendes',   'Ampliação para novos fornos a gás.',             'Área de produção — EPI obrigatório.',    'Ampliação',    'Industrial',   'Planta',          'manutencao@metalvitoria.ind.br',        '(11) 99678-3456', '(11) 99678-3457'),
-- 13
('8',  'Instalação GN — cozinha do restaurante',   '2025-04-10', NULL,         'Aguardando início', 'Rafael Oliveira', 'Conversão GLP → GN, 4 queimadores indust.',     'Acesso fora do horário comercial.',      'Instalação',   'Comercial',    'Estabelecimento', 'contato@sabordaterra.com.br',           '(11) 95123-8901', NULL),
-- 14
('6',  'Manutenção preventiva — rede existente',   '2025-04-28', NULL,         'Aguardando início', 'Fernanda Costa',  'Revisão anual contratual.',                      'Coordenar com equipe de manutenção.',    'Manutenção',   'Hospitalar',   'Ala',             'infraestrutura@hsaolucas.sp.gov.br',   '(13) 93901-6789', NULL),
-- 15
('9',  'Instalação GN — labs de química',          '2025-05-12', NULL,         'Aguardando início', 'Patrícia Souza',  'Instalação com requisitos NR-20.',               'Planta a ser fornecida pelo cliente.',   'Instalação',   'Educacional',  'Bloco',           'facilities@univale.edu.br',             '(17) 96234-9012', NULL),
-- 16
('7',  'Extensão rede — cinema e lazer',           '2024-11-05', '2024-11-15', 'Cancelada',         'Bruno Lima',      'Cancelado por reformulação do projeto.',         NULL,                                     'Extensão',     'Comercial',    'Shopping',        'operacoes@shoppingvalenorte.com.br',   '(11) 94012-7890', NULL),
-- 17
('4',  'Instalação GN — depósito central',         '2025-01-20', NULL,         'Pausada',           'Marcelo Santos',  'Aguardando aprovação do corpo de bombeiros.',    'Retomar após vistoria.',                 'Instalação',   'Comercial',    'Estabelecimento', 'gerencia@supercentral.com.br',          '(11) 91789-4567', NULL),
-- 18
('10', 'Manutenção corretiva — Torre 1',           '2025-02-25', '2025-03-01', 'Concluída',         'Carlos Mendes',   'Vazamento em registro detectado e corrigido.',   'Acesso 24h disponível.',                 'Manutenção',   'Comercial',    'Condomínio',      'gestao@techparkcondominio.com.br',      '(11) 97345-0123', NULL),
-- 19
('1',  'Manutenção preventiva — Blocos A e B',     '2025-03-15', NULL,         'Em andamento',      'Rafael Oliveira', 'Revisão anual dos dois blocos.',                 'Portaria lateral — chamar Rafael.',      'Manutenção',   'Residencial',  'Condomínio',      'sindico@jardimdaflores.com.br',         '(11) 99111-0001', NULL);

-- ── PRODUTOS POR OBRA ─────────────────────────────────────────
-- Obra 1 — Bloco A (24 unid. residenciais)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (1,  1, 48), (1,  4, 24), (1,  8, 24),
  (1, 10, 24), (1, 13, 72), (1, 14, 96);

-- Obra 2 — Bloco B (24 unid. residenciais)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (2,  1, 48), (2,  4, 24), (2,  8, 24),
  (2, 10, 24), (2, 13, 72), (2, 14, 96);

-- Obra 3 — Vila das Pedras (120 unid.)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (3,  1, 240), (3,  2,  60), (3,  4, 120),
  (3,  6, 120), (3,  8, 120), (3, 10, 120),
  (3, 12, 480), (3, 13, 360), (3, 14, 480);

-- Obra 4 — Manutenção industrial
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (4,  5,  3), (4,  9,  2), (4, 15,  6);

-- Obra 5 — Supermercado
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (5,  2, 10), (5,  5,  4), (5,  7,  1),
  (5,  9,  2), (5, 11,  6);

-- Obra 6 — Shopping (praça alimentação)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (6,  2, 80), (6,  3, 40), (6,  5, 18),
  (6,  7,  6), (6,  9, 18), (6, 11, 36),
  (6, 12,120), (6, 15, 60);

-- Obra 7 — Universidade (bloco engenharias)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (7,  1, 60), (7,  2, 30), (7,  4, 20),
  (7,  5, 10), (7, 13, 80), (7, 14,120);

-- Obra 8 — Hospital (em andamento — consumo parcial)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (8,  3, 15), (8,  5,  8), (8,  7,  2),
  (8,  9, 10), (8, 12, 30);

-- Obra 9 — Pinheiros (em andamento — consumo parcial)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (9,  1, 160), (9,  4, 80), (9,  8, 40),
  (9, 13, 200), (9, 14,300);

-- Obra 10 — TechPark Torre 3 (em andamento)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (10,  2, 25), (10,  5, 12), (10,  9,  8), (10, 15, 20);

-- Obra 11 — Escola cozinha (em andamento)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (11,  2,  8), (11,  5,  4), (11,  7,  1),
  (11,  9,  3), (11, 11,  8);

-- Obra 12 — Metalúrgica estamparia (em andamento)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (12,  3, 20), (12,  5,  6), (12,  7,  2), (12, 12, 40);

-- Obra 18 — TechPark Torre 1 manutenção corretiva
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (18,  5,  1), (18,  9,  1), (18, 15,  4);

-- Obra 19 — Cond. Jardim manutenção preventiva (em andamento)
INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
  (19,  9,  4), (19, 13, 20), (19, 14, 40);

-- ── FIM DO SEED ───────────────────────────────────────────────
-- Verificação rápida:
-- SELECT 'responsavel' t, COUNT(*) n FROM responsavel
-- UNION SELECT 'login',    COUNT(*) FROM login
-- UNION SELECT 'produtos', COUNT(*) FROM produtos
-- UNION SELECT 'clientes', COUNT(*) FROM clientes
-- UNION SELECT 'obras',    COUNT(*) FROM obras
-- UNION SELECT 'produtosObras', COUNT(*) FROM produtosObras;
