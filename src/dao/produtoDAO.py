from src.dao.conexao import Conexao
from src.modelo.produto import Produto


class ProdutoDAO:

    def proximo_id(self) -> int:
        sql = "SELECT COALESCE(MAX(idProduto), 0) + 1 FROM produtos"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return 1
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Erro ao obter próximo ID: {e}")
            return 1
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def inserir(self, produto: Produto) -> bool:
        sql = """
            INSERT INTO produtos (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                produto._idProduto,
                produto._nomeProduto,
                produto._qtdProduto,
                produto._descProduto,
                produto._qtdMinima,
                produto._qtdMaxima,
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todos(self) -> list:
        sql = "SELECT idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima FROM produtos"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return [self._linha_para_produto(l) for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_produto: int):
        sql = """
            SELECT idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima
            FROM produtos WHERE idProduto = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_produto,))
            linha = cursor.fetchone()
            return self._linha_para_produto(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar produto por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar(self, produto: Produto) -> bool:
        sql = """
            UPDATE produtos
            SET nomeProduto=%s, qtdProduto=%s, descProduto=%s, qtdMinima=%s, qtdMaxima=%s
            WHERE idProduto=%s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                produto._nomeProduto,
                produto._qtdProduto,
                produto._descProduto,
                produto._qtdMinima,
                produto._qtdMaxima,
                produto._idProduto,
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar_estoque(self, idProduto: int, quantidadeUsada: int) -> bool:
        sql = """
            UPDATE produtos
            SET qtdProduto = qtdProduto - %s
            WHERE idProduto = %s AND qtdProduto >= %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (quantidadeUsada, idProduto, quantidadeUsada))
            conexao.commit()
            if cursor.rowcount == 0:
                print("Estoque insuficiente ou produto não encontrado.")
                return False
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar estoque: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def adicionar(self, idProduto: int, quantidadeAds: int) -> bool:
        sql = "UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (quantidadeAds, idProduto))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao adicionar estoque: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, idProduto: int) -> bool:
        sql = "DELETE FROM produtos WHERE idProduto = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idProduto,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _linha_para_produto(self, linha) -> Produto:
        p = Produto()
        p._idProduto   = linha[0]
        p._nomeProduto = linha[1]
        p._qtdProduto  = linha[2]
        p._descProduto = linha[3]
        p._qtdMinima   = linha[4] if linha[4] is not None else 0
        p._qtdMaxima   = linha[5] if linha[5] is not None else 9999
        return p
