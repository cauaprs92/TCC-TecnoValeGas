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
