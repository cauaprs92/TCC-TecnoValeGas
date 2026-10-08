from src.dao.banco import OperacaoInvalida, executar_transacao, consultar
from src.dao.movimentacaoDAO import registrar_movimentacao
from src.service import precificacao

STATUS_CANCELADA = "Cancelada"


class ProdutosObrasDAO:
    """Material da obra: produtos avulsos e serviços vinculados, com a baixa e a
    devolução de estoque que cada movimentação causa.

    Os métodos que recebem `cursor` rodam dentro da transação de quem chama
    (inclusive do ObraDAO), para que obra, vínculos e estoque mudem juntos.
    Obra cancelada não consome estoque: vincular ou mexer em material dela só
    altera o registro, e a baixa acontece se a obra for reativada.
    """

    # ─── Estoque ──────────────────────────────────────────────────────────────

    def baixar(self, cursor, id_obra: int, id_produto: int, qtd: int, origem: str = ""):
        """Tira material do estoque para a obra e registra a saída (é ela que
        entra no consumo médio do cálculo do estoque mínimo)."""
        cursor.execute("""
            UPDATE produtos SET qtdProduto = qtdProduto - %s
            WHERE idProduto = %s AND qtdProduto >= %s
        """, (qtd, id_produto, qtd))
        if cursor.rowcount == 0:
            cursor.execute("SELECT nomeProduto, qtdProduto FROM produtos WHERE idProduto = %s", (id_produto,))
            row = cursor.fetchone()
            if not row:
                raise OperacaoInvalida(f"Produto ID {id_produto} não encontrado.")
            raise OperacaoInvalida(
                f"Estoque insuficiente para '{row[0]}'{origem} (necessário: {qtd}, disponível: {row[1]})."
            )
        registrar_movimentacao(cursor, id_produto, "saida", "obra", qtd, id_obra)

    def repor(self, cursor, id_obra: int, id_produto: int, qtd: int):
        """Devolve material da obra ao estoque; a entrada desconta o consumo."""
        cursor.execute(
            "UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s",
            (qtd, id_produto)
        )
        registrar_movimentacao(cursor, id_produto, "entrada", "obra", qtd, id_obra)

    def consumo_da_obra(self, cursor, id_obra: int) -> list:
        """(idProduto, quantidade) de tudo que a obra tira do estoque."""
        cursor.execute(
            "SELECT idProduto, quantidade FROM vw_consumo_obra WHERE idObra = %s", (id_obra,)
        )
        return cursor.fetchall()

    def repor_obra(self, cursor, id_obra: int):
        for id_produto, qtd in self.consumo_da_obra(cursor, id_obra):
            self.repor(cursor, id_obra, id_produto, qtd)

    def baixar_obra(self, cursor, id_obra: int):
        for id_produto, qtd in self.consumo_da_obra(cursor, id_obra):
            self.baixar(cursor, id_obra, id_produto, qtd)

    # ─── Vínculos (dentro da transação de quem chama) ─────────────────────────

    def status_obra(self, cursor, id_obra: int) -> str:
        cursor.execute("SELECT statusObra FROM obras WHERE idObra = %s FOR UPDATE", (id_obra,))
        row = cursor.fetchone()
        if not row:
            raise OperacaoInvalida("Obra não encontrada.")
        return row[0]

    def vincular_produtos(self, cursor, id_obra: int, produtos: list, baixar_estoque: bool):
        """Produto que já está na obra tem a quantidade somada, não duplicada.

        Custo e preço de venda são congelados no vínculo. Se o produto já estava
        na obra, os dois viram a média ponderada entre o que já estava e o que
        entra agora — por isso são atualizados ANTES da quantidade (o MySQL
        aplica as atribuições do ON DUPLICATE KEY UPDATE em ordem)."""
        for item in produtos or []:
            id_produto, qtd = int(item["idProduto"]), int(item["quantidade"])
            custo, preco = self._custo_e_preco_atuais(cursor, id_produto)
            cursor.execute("""
                INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra, custoUnitario, precoVenda)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    custoUnitario   = (custoUnitario * qtdProdutosObra + VALUES(custoUnitario) * VALUES(qtdProdutosObra))
                                      / (qtdProdutosObra + VALUES(qtdProdutosObra)),
                    precoVenda      = (precoVenda * qtdProdutosObra + VALUES(precoVenda) * VALUES(qtdProdutosObra))
                                      / (qtdProdutosObra + VALUES(qtdProdutosObra)),
                    qtdProdutosObra = qtdProdutosObra + VALUES(qtdProdutosObra)
            """, (id_obra, id_produto, qtd, custo, preco))
            if baixar_estoque:
                self.baixar(cursor, id_obra, id_produto, qtd)

    def vincular_servicos(self, cursor, id_obra: int, servicos: list, baixar_estoque: bool):
        """Vincula cada serviço guardando a receita do momento em
        obraServicoProdutos — é ela que volta ao estoque se o vínculo for
        desfeito, mesmo que a receita do serviço seja editada depois."""
        for id_servico in dict.fromkeys(int(s) for s in servicos or []):
            cursor.execute("SELECT nomeServico FROM servicos WHERE idServico = %s", (id_servico,))
            row = cursor.fetchone()
            if not row:
                raise OperacaoInvalida(f"Serviço ID {id_servico} não encontrado.")
            nome_servico = row[0]

            cursor.execute(
                "SELECT 1 FROM obraServicos WHERE idObra = %s AND idServico = %s", (id_obra, id_servico)
            )
            if cursor.fetchone():
                raise OperacaoInvalida(f"O serviço '{nome_servico}' já está vinculado a esta obra.")

            cursor.execute(
                "INSERT INTO obraServicos (idObra, idServico) VALUES (%s, %s)", (id_obra, id_servico)
            )
            id_obra_servico = cursor.lastrowid
            cursor.execute("""
                INSERT INTO obraServicoProdutos (idObraServico, idProduto, quantidade, custoUnitario)
                SELECT %s, sp.idProduto, sp.quantidade, p.custoUnitario
                FROM servicoProdutos sp
                JOIN produtos p ON p.idProduto = sp.idProduto
                WHERE sp.idServico = %s
            """, (id_obra_servico, id_servico))

            if baixar_estoque:
                for id_produto, qtd in self._receita_vinculada(cursor, id_obra_servico):
                    self.baixar(cursor, id_obra, id_produto, qtd, f" (serviço '{nome_servico}')")

    def recalcular_valor(self, cursor, id_obra: int):
        """Valor e custo da obra, preenchidos só quando ela está concluída
        (NULL nos demais status).

        valorObra = serviços + produtos avulsos × preço de venda congelado.
        Avulso sem preço de venda entra como zero: ele saiu sem ser cobrado.
        custoObra = todo o material consumido × custo congelado. Se algum item
        não tem custo, custoObra fica NULL: um custo parcial faria o lucro
        parecer maior do que é."""
        cursor.execute("""
            UPDATE obras SET
                valorObra = CASE WHEN statusObra = 'Concluida' THEN
                    (SELECT COALESCE(SUM(s.precoServico), 0)
                     FROM obraServicos os
                     JOIN servicos s ON s.idServico = os.idServico
                     WHERE os.idObra = %s)
                  + (SELECT COALESCE(SUM(po.qtdProdutosObra * po.precoVenda), 0)
                     FROM produtosObras po
                     WHERE po.idObra = %s)
                END,
                custoObra = CASE WHEN statusObra = 'Concluida' THEN (
                    SELECT IF(COUNT(*) = COUNT(c.custo), COALESCE(SUM(c.quantidade * c.custo), 0), NULL)
                    FROM (
                        SELECT qtdProdutosObra AS quantidade, custoUnitario AS custo
                        FROM produtosObras WHERE idObra = %s
                        UNION ALL
                        SELECT osp.quantidade, osp.custoUnitario
                        FROM obraServicoProdutos osp
                        JOIN obraServicos os ON os.idObraServico = osp.idObraServico
                        WHERE os.idObra = %s
                    ) c
                ) END
            WHERE idObra = %s
        """, (id_obra, id_obra, id_obra, id_obra, id_obra))

    def _custo_e_preco_atuais(self, cursor, id_produto: int) -> tuple:
        cursor.execute(
            "SELECT custoUnitario, margemPercentual FROM produtos WHERE idProduto = %s", (id_produto,)
        )
        row = cursor.fetchone()
        if not row:
            raise OperacaoInvalida(f"Produto ID {id_produto} não encontrado.")
        return row[0], precificacao.preco_venda(row[0], row[1])

    def _receita_vinculada(self, cursor, id_obra_servico: int) -> list:
        cursor.execute(
            "SELECT idProduto, quantidade FROM obraServicoProdutos WHERE idObraServico = %s",
            (id_obra_servico,)
        )
        return cursor.fetchall()

    def _id_obra_servico(self, cursor, id_obra: int, id_servico: int) -> int:
        cursor.execute(
            "SELECT idObraServico FROM obraServicos WHERE idObra = %s AND idServico = %s",
            (id_obra, id_servico)
        )
        row = cursor.fetchone()
        if not row:
            raise OperacaoInvalida("Serviço não vinculado a esta obra.")
        return row[0]

    def _desvincular_servico(self, cursor, id_obra: int, id_obra_servico: int, devolver_estoque: bool):
        if devolver_estoque:
            for id_produto, qtd in self._receita_vinculada(cursor, id_obra_servico):
                self.repor(cursor, id_obra, id_produto, qtd)
        # obraServicoProdutos sai junto pelo ON DELETE CASCADE
        cursor.execute("DELETE FROM obraServicos WHERE idObraServico = %s", (id_obra_servico,))

    def _total_vinculos(self, cursor, id_obra: int) -> int:
        cursor.execute("""
            SELECT (SELECT COUNT(*) FROM produtosObras WHERE idObra = %s)
                 + (SELECT COUNT(*) FROM obraServicos  WHERE idObra = %s)
        """, (id_obra, id_obra))
        return cursor.fetchone()[0]

    # ─── Edição do material de uma obra existente ─────────────────────────────

    def atualizar_quantidade_produto_obra(self, id_obra: int, id_produto: int, nova_qtd: int) -> tuple:
        def operacao(cursor):
            ativa = self.status_obra(cursor, id_obra) != STATUS_CANCELADA
            cursor.execute(
                "SELECT qtdProdutosObra FROM produtosObras WHERE idObra = %s AND idProduto = %s FOR UPDATE",
                (id_obra, id_produto)
            )
            row = cursor.fetchone()
            if not row:
                raise OperacaoInvalida("Produto não vinculado a esta obra.")

            diferenca = nova_qtd - row[0]
            if ativa and diferenca > 0:
                self.baixar(cursor, id_obra, id_produto, diferenca)
            elif ativa and diferenca < 0:
                self.repor(cursor, id_obra, id_produto, -diferenca)

            # Custo e preço congelados no vínculo continuam valendo para a
            # quantidade nova — a edição corrige a quantidade, não reprecifica.
            cursor.execute(
                "UPDATE produtosObras SET qtdProdutosObra = %s WHERE idObra = %s AND idProduto = %s",
                (nova_qtd, id_obra, id_produto)
            )
            self.recalcular_valor(cursor, id_obra)
            return "Quantidade atualizada com sucesso!"
        return executar_transacao(operacao, "Erro ao atualizar quantidade do produto na obra.")

    def remover_produto_obra(self, id_obra: int, id_produto: int) -> tuple:
        def operacao(cursor):
            ativa = self.status_obra(cursor, id_obra) != STATUS_CANCELADA
            cursor.execute(
                "SELECT qtdProdutosObra FROM produtosObras WHERE idObra = %s AND idProduto = %s FOR UPDATE",
                (id_obra, id_produto)
            )
            row = cursor.fetchone()
            if not row:
                raise OperacaoInvalida("Produto não vinculado a esta obra.")
            if self._total_vinculos(cursor, id_obra) <= 1:
                raise OperacaoInvalida("A obra precisa ter ao menos um produto ou serviço vinculado.")

            if ativa:
                self.repor(cursor, id_obra, id_produto, row[0])
            cursor.execute(
                "DELETE FROM produtosObras WHERE idObra = %s AND idProduto = %s", (id_obra, id_produto)
            )
            self.recalcular_valor(cursor, id_obra)
            return "Produto removido da obra com sucesso!"
        return executar_transacao(operacao, "Erro ao remover produto da obra.")

    def atualizar_servico_obra(self, id_obra: int, id_servico_atual: int, id_servico_novo: int) -> tuple:
        def operacao(cursor):
            ativa = self.status_obra(cursor, id_obra) != STATUS_CANCELADA
            id_obra_servico = self._id_obra_servico(cursor, id_obra, id_servico_atual)
            if id_servico_atual == id_servico_novo:
                return "Nenhuma alteração necessária."

            self._desvincular_servico(cursor, id_obra, id_obra_servico, ativa)
            self.vincular_servicos(cursor, id_obra, [id_servico_novo], ativa)
            self.recalcular_valor(cursor, id_obra)
            return "Serviço atualizado com sucesso!"
        return executar_transacao(operacao, "Erro ao atualizar serviço da obra.")

    def remover_servico_obra(self, id_obra: int, id_servico: int) -> tuple:
        def operacao(cursor):
            ativa = self.status_obra(cursor, id_obra) != STATUS_CANCELADA
            id_obra_servico = self._id_obra_servico(cursor, id_obra, id_servico)
            if self._total_vinculos(cursor, id_obra) <= 1:
                raise OperacaoInvalida("A obra precisa ter ao menos um produto ou serviço vinculado.")

            self._desvincular_servico(cursor, id_obra, id_obra_servico, ativa)
            self.recalcular_valor(cursor, id_obra)
            return "Serviço removido da obra com sucesso!"
        return executar_transacao(operacao, "Erro ao remover serviço da obra.")

    # ─── Consulta ─────────────────────────────────────────────────────────────

    def buscar_produtos_da_obra(self, id_obra: int) -> list:
        linhas = consultar("""
            SELECT p.idProduto, p.nomeProduto, po.qtdProdutosObra, po.custoUnitario, po.precoVenda
            FROM produtosObras po
            JOIN produtos p ON po.idProduto = p.idProduto
            WHERE po.idObra = %s
        """, (id_obra,), erro="Erro ao buscar produtos da obra:")
        return [{"idProduto": l[0], "nomeProduto": l[1], "qtdProdutosObra": l[2],
                 "custoUnitario": float(l[3]) if l[3] is not None else None,
                 "precoVenda":    float(l[4]) if l[4] is not None else None} for l in linhas]

    def buscar_servicos_da_obra(self, id_obra: int) -> list:
        linhas = consultar("""
            SELECT s.idServico, s.nomeServico, s.precoServico
            FROM obraServicos os
            JOIN servicos s ON s.idServico = os.idServico
            WHERE os.idObra = %s
        """, (id_obra,), erro="Erro ao buscar serviços da obra:")
        return [{"idServico": l[0], "nomeServico": l[1], "precoServico": float(l[2])} for l in linhas]
