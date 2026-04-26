from src.dao.conexao import Conexao

class ProdutosObrasDAO:

    # ── Cadastrar obra + produtos + baixa no estoque (tudo junto) ─────────────
    def cadastrar_obra_com_produtos(self, obra: dict, produtos_usados: list) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:

            primeiro_produto = produtos_usados[0]["idProduto"] if produtos_usados else None
            cursor.execute("""
                INSERT INTO obras (codCliente, codProduto, descObra, dataObra, statusObra, respObra)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                obra["codCliente"],
                primeiro_produto,
                obra["descObra"],
                obra["dataObra"],
                obra.get("statusObra"),
                obra.get("respObra", ""),
            ))

            id_obra_gerado = cursor.lastrowid

            # 2. Para cada produto usado na obra...
            for item in produtos_usados:
                cursor.execute("""
                    INSERT INTO produtosObras (idObra, idProduto, qtdProdutosObra)
                    VALUES (%s, %s, %s)
                """, (
                    id_obra_gerado,
                    item["idProduto"],
                    item["quantidade"]
                ))

                # 3. Dá baixa no estoque
                cursor.execute("""
                    UPDATE produtos
                    SET qtdProduto = qtdProduto - %s
                    WHERE idProduto = %s AND qtdProduto >= %s
                """, (
                    item["quantidade"],
                    item["idProduto"],
                    item["quantidade"]
                ))

                # Verifica se tinha estoque suficiente
                if cursor.rowcount == 0:
                    raise Exception(f"Estoque insuficiente para o produto ID {item['idProduto']}")

            # Tudo certo → confirma no banco
            conexao.commit()
            print("Obra cadastrada e estoque atualizado com sucesso!")
            return True

        except Exception as e:
            conexao.rollback()
            print(f"Erro ao cadastrar obra: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # ── Buscar produtos de uma obra ───────────────────────────────────────────
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
            produtos = []
            for linha in linhas:
                produtos.append({
                    "idProduto":  linha[0],
                    "nome":       linha[1],
                    "quantidade": linha[2]
                })
            return produtos
        except Exception as e:
            print(f"Erro ao buscar produtos da obra: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)