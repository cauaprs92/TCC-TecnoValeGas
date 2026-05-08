from src.dao.conexao import Conexao

class ProdutosObrasDAO:

    def cadastrar_obra_com_produtos(self, obra: dict, produtos_usados: list) -> bool:
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO obras (codCliente, descObra, dataInicio, dataFim, statusObra, respObra)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                obra["codCliente"],
                obra["descObra"],
                obra["dataInicio"],
                obra.get("dataFim"),
                obra.get("statusObra"),
                obra.get("respObra", ""),
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
