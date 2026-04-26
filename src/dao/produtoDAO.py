from src.dao.conexao import Conexao
from src.modelo.produto import Produto

class ProdutoDAO:


    #  Inserir
    def inserir(self, produto: Produto) -> bool:
        sql = """
            INSERT INTO produtos (idProduto, qtdProduto, nomeProduto, descProduto)
            VALUES (%s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                produto._idProduto,
                produto._qtdProduto,
                produto._nomeProduto,
                produto._descProduto
            ))
            conexao.commit()
            print("Produto inserido com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Buscar todos 
    def buscar_todos(self) -> list:
        sql = "SELECT idProduto, qtdProduto, nomeProduto, descProduto FROM produtos"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            linhas = cursor.fetchall()
            produtos = []
            for linha in linhas:
                dadosProduto = Produto()
                dadosProduto._idProduto   = linha[0]
                dadosProduto._qtdProduto  = linha[1]
                dadosProduto._nomeProduto = linha[2]
                dadosProduto._descProduto = linha[3]
                produtos.append(dadosProduto)
            return produtos
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # Buscar p/ ID 
    def buscar_por_id(self, id_produto: int):
        sql = """
            SELECT idProduto, qtdProduto, nomeProduto, descProduto
            FROM produtos WHERE idProduto = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_produto,))
            linha = cursor.fetchone()
            if not linha:
                return None
            dadosProduto = Produto()
            dadosProduto._idProduto   = linha[0]
            dadosProduto._qtdProduto  = linha[1]
            dadosProduto._nomeProduto = linha[2]
            dadosProduto._descProduto = linha[3]
            return dadosProduto
        except Exception as e:
            print(f"Erro ao buscar produto por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # Atualizar
    def atualizar(self, produto: Produto) -> bool:
        sql = """
            UPDATE produtos
            SET qtdProduto = %s, nomeProduto = %s, descProduto = %s
            WHERE idProduto = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                produto._qtdProduto,
                produto._nomeProduto,
                produto._descProduto,
                produto._idProduto
            ))
            conexao.commit()
            print("Produto atualizado com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Atualizar estoque (baixa automática)
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
            print(f"Estoque atualizado: -{quantidadeUsada} unidades do produto {idProduto}")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar estoque: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Deletar
    def deletar(self, idProduto: int) -> bool:
        sql = "DELETE FROM produtos WHERE idProduto = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idProduto,))
            conexao.commit()
            print("Produto deletado com sucesso!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar produto: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
    
    #adicionar quantidade de produto existente
    def adicionar(self, idProduto: int, quantidadeAds : int) -> bool:
        sql = """
            UPDATE produtos
            SET qtdProduto = qtdProduto + %s
            WHERE idProduto = %s 
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor() 
        try:
            cursor.execute(sql, (idProduto, quantidadeAds, ))
            conexao.commit()
            print(f"Estoque atualizado: +{quantidadeAds} unidades do produto {idProduto}")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar estoque: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)


            
                