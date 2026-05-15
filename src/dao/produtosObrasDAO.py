from src.dao.conexao import Conexao

class ProdutosObrasDAO:

    def cadastrar_obra_com_produtos(self, obra: dict, produtos_usados: list) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO obras
                  (codCliente, descObra, dataInicio, dataFim, statusObra, respObra,
                   obsObra, orientacaoObra, tipoObra, fieldObra, unidadeObra,
                   emailContato, celular1, celular2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                obra["codCliente"],
                obra["descObra"],
                obra["dataInicio"],
                obra.get("dataFim"),
                obra.get("statusObra"),
                obra.get("respObra", ""),
                obra.get("obsObra"),
                obra.get("orientacaoObra"),
                obra.get("tipoObra"),
                obra.get("fieldObra"),
                obra.get("unidadeObra"),
                obra.get("emailContato"),
                obra.get("celular1"),
                obra.get("celular2"),
            ))

            id_obra_gerado = cursor.lastrowid

            for item in produtos_usados:
                cursor.execute("""
                    INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra)
                    VALUES (%s, %s, %s)
                """, (
                    id_obra_gerado,
                    item["idProduto"],
                    item["quantidade"]
                ))

                cursor.execute("""
                    UPDATE produtos
                    SET qtdProduto = qtdProduto - %s
                    WHERE idProduto = %s AND qtdProduto >= %s
                """, (
                    item["quantidade"],
                    item["idProduto"],
                    item["quantidade"]
                ))

                if cursor.rowcount == 0:
                    raise Exception(f"Estoque insuficiente para o produto ID {item['idProduto']}")

            conexao.commit()
            print("Obra cadastrada e estoque atualizado com sucesso!")
            return True

        except Exception as e:
            conexao.rollback()
            print(f"Erro ao cadastrar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def adicionar_produtos_obra(self, id_obra: int, produtos: list) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            for item in produtos:
                cursor.execute("""
                    INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra)
                    VALUES (%s, %s, %s)
                """, (id_obra, item["idProduto"], item["quantidade"]))

                cursor.execute("""
                    UPDATE produtos
                    SET qtdProduto = qtdProduto - %s
                    WHERE idProduto = %s AND qtdProduto >= %s
                """, (item["quantidade"], item["idProduto"], item["quantidade"]))

                if cursor.rowcount == 0:
                    raise Exception(f"Estoque insuficiente para o produto ID {item['idProduto']}")

            conexao.commit()
            print("Produtos adicionados à obra com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao adicionar produtos à obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def restaurar_estoque_obra(self, id_obra: int) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT idProduto, qtdProdutosObra FROM produtosObras WHERE idObra = %s
            """, (id_obra,))
            produtos = cursor.fetchall()

            for id_produto, qtd in produtos:
                cursor.execute("""
                    UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s
                """, (qtd, id_produto))

            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao restaurar estoque da obra {id_obra}: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def baixar_estoque_obra(self, id_obra: int) -> tuple:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False, "Sem conexão com o banco."
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT po.idProduto, p.nomeProduto, po.qtdProdutosObra
                FROM produtosObras po
                JOIN produtos p ON p.idProduto = po.idProduto
                WHERE po.idObra = %s
            """, (id_obra,))
            produtos = cursor.fetchall()

            for id_produto, nome_produto, qtd in produtos:
                cursor.execute("""
                    UPDATE produtos
                    SET qtdProduto = qtdProduto - %s
                    WHERE idProduto = %s AND qtdProduto >= %s
                """, (qtd, id_produto, qtd))

                if cursor.rowcount == 0:
                    raise Exception(f"Estoque insuficiente para '{nome_produto}' (necessário: {qtd}).")

            conexao.commit()
            return True, "Estoque atualizado."
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao baixar estoque da obra {id_obra}: {e}")
            return False, str(e)
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar_obra_com_reposicao(self, id_obra: int) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT idProduto, qtdProdutosObra FROM produtosObras WHERE idObra = %s
            """, (id_obra,))
            produtos = cursor.fetchall()

            for id_produto, qtd in produtos:
                cursor.execute("""
                    UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s
                """, (qtd, id_produto))

            cursor.execute("DELETE FROM produtosObras WHERE idObra = %s", (id_obra,))
            cursor.execute("DELETE FROM obras WHERE idObra = %s", (id_obra,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar obra com reposição: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar_quantidade_produto_obra(self, id_obra: int, id_produto: int, nova_qtd: int) -> tuple:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False, "Sem conexão com o banco."
        cursor = conexao.cursor()
        try:
            cursor.execute(
                "SELECT qtdProdutosObra FROM produtosObras WHERE idObra = %s AND idProduto = %s",
                (id_obra, id_produto)
            )
            row = cursor.fetchone()
            if not row:
                return False, "Produto não vinculado a esta obra."

            qtd_atual = row[0]
            diferenca = nova_qtd - qtd_atual

            if diferenca > 0:
                cursor.execute(
                    "UPDATE produtos SET qtdProduto = qtdProduto - %s WHERE idProduto = %s AND qtdProduto >= %s",
                    (diferenca, id_produto, diferenca)
                )
                if cursor.rowcount == 0:
                    raise Exception(f"Estoque insuficiente para o produto ID {id_produto}.")
            elif diferenca < 0:
                cursor.execute(
                    "UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s",
                    (abs(diferenca), id_produto)
                )

            cursor.execute(
                "UPDATE produtosObras SET qtdProdutosObra = %s WHERE idObra = %s AND idProduto = %s",
                (nova_qtd, id_obra, id_produto)
            )
            conexao.commit()
            return True, "Quantidade atualizada com sucesso!"
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar quantidade do produto na obra: {e}")
            return False, str(e)
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_produtos_da_obra(self, id_obra: int) -> list:
        sql = """
            SELECT p.idProduto, p.nomeProduto, po.qtdProdutosObra
            FROM produtosObras po
            JOIN produtos p ON po.idProduto = p.idProduto
            WHERE po.idObra = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra,))
            linhas = cursor.fetchall()
            return [
                {
                    "idProduto":       linha[0],
                    "nomeProduto":     linha[1],
                    "qtdProdutosObra": linha[2]
                }
                for linha in linhas
            ]
        except Exception as e:
            print(f"Erro ao buscar produtos da obra: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)
