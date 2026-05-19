** Inserts para popular as tabelas com dados de exemplo **


INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima) VALUES
(1,  'Tubo Aço Galvanizado 1"',        200, 'Tubo rígido galvanizado para rede de gás', 50, 1000),
(2,  'Registro de Esfera 3/4"',         120, 'Registro de esfera para gás com vedação reforçada', 50, 2000),
(3,  'Medidor de Gás Industrial G16',   300, 'Medidor para instalação industrial de gás natural', 50, 5000),
(4,  'Válvula Redutora de Pressão',     80, 'Válvula reguladora de pressão para rede de gás', 50, 1000),
(5,  'Mangueira Flexível 3/4"',         25, 'Mangueira flexível para conexão de gás', 50, 1000),
(6,  'Cinta de Fixação Metálica',       42, 'Cinta metálica para fixação de tubulações', 50, 1000),
(7,  'Tubo PPR 32mm',                   34, 'Tubo de polipropileno para água e gás', 50, 1000),
(8,  'Filtro de Linha para Gás',         500, 'Filtro de linha de proteção para rede de gás', 50, 1000),
(9,  'Conector Curvo 90° 1/2"',         110, 'Conector em curva para tubulação de gás', 50, 1000),
(10, 'Adaptador Rosca 1/2" x 3/4"',     180, 'Adaptador de rosca para composições mistas', 50, 1000),
(11, 'Lanterna de Inspeção Antichama',   60, 'Lanterna para inspeção com proteção antichama', 50, 1000),
(12, 'Detector de Vazão Portátil',       20, 'Detector portátil para vazamentos de gás', 50, 1000);

INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, contatoCliente, emailCliente, telefone2, cep, rua, numero, complemento, bairro, cidade, estado) VALUES
(1, 'Caua Silva',             '123.456.789-00', 'Caua',         'caua.silva@sjcgas.com.br',       '(12) 98811-2233', '12245-000', 'Rua São Sebastião',      '112', 'Apto 101',          'Jardim Aquarius',         'São José dos Campos', 'SP'),
(2, 'João Vinicius Oliveira', '234.567.890-11', 'João Vinicius','joao.vinicius@sjcgas.com.br',   '(12) 99777-4455', '12244-550', 'Avenida Cassiano Ricardo', '4300', 'Sala 4',        'Jardim Aquarius',         'São José dos Campos', 'SP'),
(3, 'Mateus Alves',           '345.678.901-22', 'Mateus',       'mateus.alves@sjcgas.com.br',     '(12) 99666-7788', '12226-280', 'Rua Padre Francisco',    '98',  NULL,             'Jardim das Indústrias',   'São José dos Campos', 'SP'),
(4, 'Lúcia Martins',          '456.789.012-33', 'Lúcia',        'lucia.martins@sjcgas.com.br',    '(12) 98123-4567', '12234-010', 'Rua Câmara',            '428', NULL,             'Vila Adyana',             'São José dos Campos', 'SP'),
(5, 'Fabrício Rocha',         '567.890.123-44', 'Fabrício',     'fabricio.rocha@sjcgas.com.br',   '(12) 98222-3344', '12227-110', 'Rua Miguel Petroni',    '78',  NULL,             'Parque Industrial',       'São José dos Campos', 'SP'),
(6, 'Marina Nunes',           '678.901.234-55', 'Marina',       'marina.nunes@sjcgas.com.br',     '(12) 98111-2233', '12232-150', 'Avenida Andrômeda',     '5250','Casa 12',         'Urbanova',                'São José dos Campos', 'SP');

INSERT INTO responsavel (nomeResponsavel) VALUES
('Carlos Souza'),
('Beatriz Almeida'),
('Renato Pereira'),
('Ana Carolina');

INSERT INTO obras (codCliente, descObra, dataInicio, dataFim, statusObra, respObra, obsObra, orientacaoObra, tipoObra, fieldObra, unidadeObra, emailContato, celular1, celular2) VALUES
(1, 'Instalação de ramal de gás em condomínio residencial',         '2024-08-05', NULL,      'Em andamento', 'Carlos Souza',  'Falta finalizar testes de estanqueidade', 'Revisar juntas e conexões', 'Residencial', 'Gás Canalizado', 'Un', 'caua.contato@sjcgas.com.br',       '(12) 98811-2233', NULL),
(1, 'Manutenção preventiva em medidor industrial',                 '2024-06-18', '2024-07-02', 'Concluida',    'Beatriz Almeida','Relatório enviado ao cliente',       'Confirmar próxima visita em 6 meses',  'Industrial',  'Medidor',        'Un', 'caua.contato@sjcgas.com.br',       '(12) 98811-2233', NULL),
(2, 'Extensão de rede de gás em restaurante na região central',     '2024-09-01', NULL,      'À iniciar',    'Renato Pereira','Aguardando liberação de prefeitura',  'Agendar início após autorização',      'Comercial',   'Rede de Gás',    'm',  'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', '(12) 98100-3344'),
(2, 'Correção de vazamento em cozinha industrial',                  '2024-04-10', '2024-05-08', 'Concluida',    'Ana Carolina',  'Válvula substituída e teste OK',       'Registrar em manutenção preventiva',   'Industrial',  'Gás Natural',    'Un', 'joao.vinicius@sjcgas.com.br', '(12) 99777-4455', NULL),
(3, 'Instalação de medidor privativo em prédio comercial',         '2024-07-22', NULL,      'Pausada',      'Carlos Souza',  'Aguardando entrega de peças',           'Revisar cronograma com fornecedor',    'Comercial',   'Medidor',        'Un', 'mateus.alves@sjcgas.com.br', '(12) 99666-7788', NULL),
(3, 'Troca de registro e conector em unidade logística',            '2024-05-12', '2024-06-01', 'Concluida',    'Beatriz Almeida','Obra entregue com novo certificado',    'Enviar notas fiscais',                'Logística',   'Conector',       'Un', 'mateus.alves@sjcgas.com.br', '(12) 99666-7788', NULL),
(4, 'Instalação de ramal de gás para cozinha de pizzaria',          '2024-08-12', NULL,      'Em andamento', 'Renato Pereira','Instalação de mangueiras em andamento','Acompanhar equipe técnica',           'Comercial',   'Gás Canalizado', 'm',  'lucia.martins@sjcgas.com.br','(12) 98123-4567', NULL),
(5, 'Revisão geral de rede de gás na unidade fabril',                '2024-07-01', '2024-08-10', 'Concluida',    'Ana Carolina',  'Painel de controle atualizado',         'Arquivar laudos de teste',            'Industrial',  'Rede de Gás',    'm',  'fabricio.rocha@sjcgas.com.br','(12) 98222-3344', NULL),
(6, 'Projeto de ramal de gás para nova loja de estética',            '2024-09-15', NULL,      'À iniciar',    'Carlos Souza',  'Aguardando aprovação do cliente',      'Enviar orçamento final',              'Comercial',   'Projeto',        'Un', 'marina.nunes@sjcgas.com.br','(12) 98111-2233', NULL);

INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra) VALUES
(1, 1, 20),
(1, 5, 10),
(1, 6, 15),
(2, 3, 1),
(2, 11, 2),
(3, 2, 8),
(3, 4, 5),
(3, 9, 12),
(4, 8, 3),
(4, 10, 6),
(5, 2, 4),
(5, 5, 16),
(5, 12, 1),
(6, 1, 6),
(6, 9, 3),
(7, 7, 22),
(7, 5, 8),
(8, 1, 5),
(8, 4, 10);