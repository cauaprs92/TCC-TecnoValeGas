-- =============================================================================
-- Migração de um banco `tcc` já existente para o schema atual de codigo.sql.
-- Rodar uma vez, na ordem. Quem cria o banco do zero (install.py) não precisa.
-- =============================================================================
USE tcc;

-- ── 1. Receita dos serviços vinculada à obra + vínculos únicos ──────────────
-- Antes, a devolução de estoque de um serviço lia a receita ATUAL dele; se a
-- receita tivesse sido editada, voltava a quantidade errada. Agora a receita
-- é copiada para obraServicoProdutos no momento do vínculo.
CREATE TABLE obraServicoProdutos (
    idObraServicoProduto int primary key NOT NULL AUTO_INCREMENT,
    idObraServico        int NOT NULL,
    idProduto            int NOT NULL,
    quantidade           int NOT NULL,
    FOREIGN KEY (idObraServico) REFERENCES obraServicos(idObraServico) ON DELETE CASCADE,
    FOREIGN KEY (idProduto)     REFERENCES produtos(idProduto)
);

-- Os vínculos existentes recebem a receita atual — é a melhor informação
-- disponível sobre o que já saiu do estoque.
INSERT INTO obraServicoProdutos (idObraServico, idProduto, quantidade)
SELECT os.idObraServico, sp.idProduto, sp.quantidade
FROM obraServicos os
JOIN servicoProdutos sp ON sp.idServico = os.idServico;

-- Falha se houver linhas duplicadas; nesse caso, consolide-as antes.
ALTER TABLE produtosObras ADD UNIQUE KEY uq_obra_produto (idObra, idProduto);
ALTER TABLE obraServicos  ADD UNIQUE KEY uq_obra_servico (idObra, idServico);

CREATE VIEW vw_consumo_obra AS
    SELECT idObra, idProduto, qtdProdutosObra AS quantidade
    FROM produtosObras
    UNION ALL
    SELECT os.idObra, osp.idProduto, osp.quantidade
    FROM obraServicoProdutos osp
    JOIN obraServicos os ON os.idObraServico = osp.idObraServico;

-- ── 2. Histórico não impede mais a exclusão de usuários ─────────────────────
ALTER TABLE historico DROP FOREIGN KEY historico_ibfk_1;
ALTER TABLE historico MODIFY COLUMN idAdmin INT DEFAULT NULL;
ALTER TABLE historico
    ADD CONSTRAINT historico_ibfk_1
    FOREIGN KEY (idAdmin) REFERENCES login(idLogin) ON DELETE SET NULL;

-- ── 3. IDs gerados pelo banco, CPF/CNPJ único e valores fechados ────────────
-- idProduto e idCliente eram calculados com MAX()+1 no Python; dois cadastros
-- simultâneos pegavam o mesmo ID. As FKs precisam ficar desligadas só durante
-- o MODIFY (o MySQL não deixa alterar coluna referenciada com elas ligadas).
SET FOREIGN_KEY_CHECKS = 0;
ALTER TABLE produtos MODIFY COLUMN idProduto int NOT NULL AUTO_INCREMENT;
ALTER TABLE clientes MODIFY COLUMN idCliente int NOT NULL AUTO_INCREMENT;
SET FOREIGN_KEY_CHECKS = 1;

-- Falha se já houver CPF/CNPJ repetido; nesse caso, corrija antes.
ALTER TABLE clientes ADD UNIQUE KEY uq_clientes_cnpjcpf (CNPJCPF);

ALTER TABLE login ADD CONSTRAINT ck_login_cargo
    CHECK (cargoLogin IN ('Administracao', 'Almoxarifado', 'Obra'));
ALTER TABLE obras ADD CONSTRAINT ck_obras_status
    CHECK (statusObra IN ('À iniciar', 'Em andamento', 'Concluida', 'Cancelada', 'Pausada'));

-- ── 4. Estoque mínimo automático ─────────────────────────────────────────────
-- O mínimo passa a ser calculado: consumo médio diário × prazo de entrega +
-- margem. O valor digitado antes vira "mínimo manual" (qtdMinimaManual) e é
-- zerado para NULL, que significa "usar o cálculo". Para manter algum valor
-- manual, preencha qtdMinimaManual dele depois desta migração.
ALTER TABLE fornecedores
    ADD COLUMN prazoEntregaDias int NOT NULL DEFAULT 7,
    ADD CONSTRAINT ck_fornecedor_prazo CHECK (prazoEntregaDias > 0);

ALTER TABLE produtos
    RENAME COLUMN qtdMinima TO qtdMinimaManual,
    ADD COLUMN prazoEntregaDias  int           DEFAULT NULL,
    ADD COLUMN consumoEstimado   DECIMAL(10,2) DEFAULT NULL,
    ADD COLUMN periodoEstimativa VARCHAR(6)    DEFAULT NULL,
    ADD CONSTRAINT ck_produto_periodo CHECK (periodoEstimativa IN ('dia', 'semana', 'mes')),
    ADD CONSTRAINT ck_produto_prazo   CHECK (prazoEntregaDias > 0);
ALTER TABLE produtos MODIFY COLUMN qtdMinimaManual int DEFAULT NULL;
SET SQL_SAFE_UPDATES = 0;
UPDATE produtos SET qtdMinimaManual = NULL;
SET SQL_SAFE_UPDATES = 1;

CREATE TABLE movimentacoesEstoque (
    idMovimentacao int primary key NOT NULL AUTO_INCREMENT,
    idProduto      int          NOT NULL,
    idObra         int          DEFAULT NULL,
    tipo           VARCHAR(7)   NOT NULL,
    origem         VARCHAR(12)  NOT NULL,
    quantidade     int          NOT NULL,
    dataMov        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_mov_produto_data (idProduto, dataMov),
    FOREIGN KEY (idProduto) REFERENCES produtos(idProduto) ON DELETE CASCADE,
    FOREIGN KEY (idObra)    REFERENCES obras(idObra) ON DELETE SET NULL,
    CONSTRAINT ck_mov_tipo   CHECK (tipo IN ('entrada', 'saida')),
    CONSTRAINT ck_mov_origem CHECK (origem IN ('obra', 'nota_fiscal', 'ajuste')),
    CONSTRAINT ck_mov_qtd    CHECK (quantidade > 0)
);

-- Histórico a partir do que já foi consumido: a saída é datada no início da
-- obra (ou hoje, se ela ainda vai começar). Obras canceladas já devolveram o
-- material e ficam de fora.
INSERT INTO movimentacoesEstoque (idProduto, idObra, tipo, origem, quantidade, dataMov)
SELECT v.idProduto, v.idObra, 'saida', 'obra', v.quantidade, LEAST(o.dataInicio, CURDATE())
FROM vw_consumo_obra v
JOIN obras o ON o.idObra = v.idObra
WHERE o.statusObra <> 'Cancelada';
