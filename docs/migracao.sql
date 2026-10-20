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

-- CHANGE COLUMN em vez de RENAME COLUMN: o RENAME só existe a partir do
-- MariaDB 10.5, e o XAMPP traz o 10.4 — lá a migração parava aqui e o banco
-- ficava sem as colunas novas (a listagem de produtos voltava vazia).
ALTER TABLE produtos
    CHANGE COLUMN qtdMinima qtdMinimaManual int DEFAULT NULL,
    ADD COLUMN prazoEntregaDias  int           DEFAULT NULL,
    ADD COLUMN consumoEstimado   DECIMAL(10,2) DEFAULT NULL,
    ADD COLUMN periodoEstimativa VARCHAR(6)    DEFAULT NULL,
    ADD CONSTRAINT ck_produto_periodo CHECK (periodoEstimativa IN ('dia', 'semana', 'mes')),
    ADD CONSTRAINT ck_produto_prazo   CHECK (prazoEntregaDias > 0);
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

-- ── 5. Histórico por item (idEntidade) ───────────────────────────────────────
-- O histórico de uma obra era filtrado procurando o ID dentro do texto da
-- descrição — frágil e, no caso do cadastro, impossível (a linha não tinha o
-- ID). Agora cada registro guarda o ID do item afetado em idEntidade.
ALTER TABLE historico ADD COLUMN idEntidade INT DEFAULT NULL AFTER entidade;
ALTER TABLE historico ADD INDEX ix_hist_entidade (entidade, idEntidade);

-- Backfill das obras: extrai o ID das descrições antigas que já o traziam, nos
-- formatos "(ID: 4)" e "... obra ID 4 ...". O número é ancorado em "ID" para
-- não pegar algum número que esteja na descrição da obra. Os cadastros antigos
-- não têm ID e ficam com idEntidade NULL (não há como recuperá-lo com segurança).
SET SQL_SAFE_UPDATES = 0;
UPDATE historico
SET idEntidade = CAST(REGEXP_SUBSTR(REGEXP_SUBSTR(descricao, 'ID:? [0-9]+'), '[0-9]+') AS UNSIGNED)
WHERE entidade = 'Obra'
  AND idEntidade IS NULL
  AND descricao REGEXP 'ID:? [0-9]+';
SET SQL_SAFE_UPDATES = 1;

-- ── 6. Custo, margem e lucro ─────────────────────────────────────────────────
-- Produto ganha custo (manual ou pela nota fiscal) e margem sobre a venda.
-- O material da obra guarda o custo (e, no avulso, o preço de venda) do
-- momento do vínculo. Obras antigas ficam sem custo congelado (NULL): o custo
-- da época não existe mais, e o sistema não chuta. Elas aparecem como "sem
-- custo" no lucro em vez de entrarem com custo zero.
ALTER TABLE produtos
    ADD COLUMN custoUnitario    DECIMAL(10,4) DEFAULT NULL,
    ADD COLUMN margemPercentual DECIMAL(5,2)  DEFAULT NULL,
    ADD CONSTRAINT ck_produto_custo  CHECK (custoUnitario >= 0),
    ADD CONSTRAINT ck_produto_margem CHECK (margemPercentual >= 0 AND margemPercentual < 100);

ALTER TABLE produtosObras
    ADD COLUMN custoUnitario DECIMAL(10,4) DEFAULT NULL,
    ADD COLUMN precoVenda    DECIMAL(10,4) DEFAULT NULL;
ALTER TABLE obraServicoProdutos
    ADD COLUMN custoUnitario DECIMAL(10,4) DEFAULT NULL;
ALTER TABLE obras
    ADD COLUMN custoObra DECIMAL(10,2) DEFAULT NULL;

-- Custo inicial pelas notas fiscais já conferidas: média ponderada de tudo
-- que entrou de cada produto.
SET SQL_SAFE_UPDATES = 0;
UPDATE produtos p
JOIN (
    SELECT idProduto, SUM(valorUnitario * quantidade) / SUM(quantidade) AS custo
    FROM notaFiscalItens
    WHERE statusItem = 'confirmado' AND idProduto IS NOT NULL
      AND valorUnitario IS NOT NULL AND quantidade > 0
    GROUP BY idProduto
) nf ON nf.idProduto = p.idProduto
SET p.custoUnitario = nf.custo;
SET SQL_SAFE_UPDATES = 1;

-- ── 7. Fotos e notas fiscais no banco (base64) ───────────────────────────────
-- Os arquivos deixam de ir para a pasta uploads/ e passam a ficar na própria
-- linha, em base64. As fotos antigas apontam para arquivos em disco que o
-- sistema não lê mais: são removidas e precisam ser enviadas de novo.
SET SQL_SAFE_UPDATES = 0;
DELETE FROM obra_fotos;
DELETE FROM produto_fotos;
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE obra_fotos
    ADD COLUMN tipoMime VARCHAR(100) NOT NULL AFTER nomeOriginal,
    ADD COLUMN conteudo LONGTEXT     NOT NULL AFTER tipoMime,
    ADD UNIQUE KEY uq_obra_foto_arquivo (nomeArquivo);
ALTER TABLE produto_fotos
    ADD COLUMN tipoMime VARCHAR(100) NOT NULL AFTER nomeOriginal,
    ADD COLUMN conteudo LONGTEXT     NOT NULL AFTER tipoMime,
    ADD UNIQUE KEY uq_produto_foto_arquivo (nomeArquivo);

-- ── 8. Ações do histórico padronizadas ───────────────────────────────────────
-- Só existem três ações: Inseriu, Editou e Deletou. As descrições antigas
-- ficam como estavam; só o tipo da ação é convertido.
SET SQL_SAFE_UPDATES = 0;
UPDATE historico SET acao = 'Inseriu' WHERE acao IN ('Cadastrou', 'Importou');
UPDATE historico SET acao = 'Editou'  WHERE acao IN ('Reabriu', 'Repôs', 'Ignorou');
SET SQL_SAFE_UPDATES = 1;

-- ── 9. Preço de venda por markup ─────────────────────────────────────────────
-- A margem passa a ser acréscimo sobre o custo: preço = custo × (1 + margem),
-- e pode passar de 100%. (Antes: custo ÷ (1 − margem), limitada a < 100%.)
ALTER TABLE produtos
    DROP CONSTRAINT ck_produto_margem,
    ADD CONSTRAINT ck_produto_margem CHECK (margemPercentual >= 0 AND margemPercentual < 1000);

-- Recalcula o preço gravado nas obras com a regra nova, a partir do custo
-- gravado no vínculo e da margem atual do produto (NULL = padrão de 30%).
-- Para manter os valores antigos das obras, NÃO rode este bloco.
SET SQL_SAFE_UPDATES = 0;
UPDATE produtosObras po
JOIN produtos p ON p.idProduto = po.idProduto
SET po.precoVenda = ROUND(po.custoUnitario * (1 + COALESCE(p.margemPercentual, 30) / 100), 2)
WHERE po.custoUnitario IS NOT NULL;

-- Valor das obras concluídas com os preços recalculados (mesma conta de
-- ProdutosObrasDAO.recalcular_valor: serviços + avulsos × preço gravado).
UPDATE obras o
SET o.valorObra =
        (SELECT COALESCE(SUM(s.precoServico), 0)
         FROM obraServicos os
         JOIN servicos s ON s.idServico = os.idServico
         WHERE os.idObra = o.idObra)
      + (SELECT COALESCE(SUM(po.qtdProdutosObra * po.precoVenda), 0)
         FROM produtosObras po
         WHERE po.idObra = o.idObra)
WHERE o.statusObra = 'Concluida';
SET SQL_SAFE_UPDATES = 1;
