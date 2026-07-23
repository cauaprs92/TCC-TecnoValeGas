from src.dao.conexao import Conexao
from src.modelo.servico import Servico


class ServicoDAO:

    def inserir(self, servico: Servico) -> bool:
        sql_servico = """
            INSERT INTO servicos (nomeServico, precoServico, fornecedorServico)
            VALUES (%s, %s, %s)
        """
        sql_item = """
            INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
            VALUES (%s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql_servico, (servico._nomeServico, servico._precoServico, servico._fornecedorServico))
            servico._idServico = cursor.lastrowid
            for item in servico._produtos:
                cursor.execute(sql_item, (servico._idServico, item["idProduto"], item["quantidade"]))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir serviço: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todos(self) -> list:
        sql = "SELECT idServico, nomeServico, precoServico, fornecedorServico FROM servicos"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        servicos = []
        try:
            cursor.execute(sql)
            servicos = [self._linha_para_servico(l) for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar serviços: {e}")
        finally:
            Conexao.fechar_conexao(conexao, cursor)

        for s in servicos:
            s._produtos = self.buscar_produtos_do_servico(s._idServico)
        return servicos

    def buscar_por_id(self, idServico: int):
        sql = """
            SELECT idServico, nomeServico, precoServico, fornecedorServico
            FROM servicos WHERE idServico = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        servico = None
        try:
            cursor.execute(sql, (idServico,))
            linha = cursor.fetchone()
            if linha:
                servico = self._linha_para_servico(linha)
        except Exception as e:
            print(f"Erro ao buscar serviço por ID: {e}")
        finally:
            Conexao.fechar_conexao(conexao, cursor)

        if servico:
            servico._produtos = self.buscar_produtos_do_servico(servico._idServico)
        return servico

    def atualizar(self, servico: Servico) -> bool:
        sql_update = """
            UPDATE servicos
            SET nomeServico=%s, precoServico=%s, fornecedorServico=%s
            WHERE idServico=%s
        """
        sql_delete = "DELETE FROM servicoProdutos WHERE idServico = %s"
        sql_item   = """
            INSERT INTO servicoProdutos (idServico, idProduto, quantidade)
            VALUES (%s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql_update, (servico._nomeServico, servico._precoServico, servico._fornecedorServico, servico._idServico))
            cursor.execute(sql_delete, (servico._idServico,))
            for item in servico._produtos:
                cursor.execute(sql_item, (servico._idServico, item["idProduto"], item["quantidade"]))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar serviço: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, idServico: int) -> bool:
        sql_produtos = "DELETE FROM servicoProdutos WHERE idServico = %s"
        sql_servico  = "DELETE FROM servicos WHERE idServico = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql_produtos, (idServico,))
            cursor.execute(sql_servico, (idServico,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar serviço: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_produtos_do_servico(self, idServico: int) -> list:
        sql = """
            SELECT idProduto, quantidade
            FROM servicoProdutos
            WHERE idServico = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idServico,))
            return [{"idProduto": l[0], "quantidade": l[1]} for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar produtos do serviço: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _linha_para_servico(self, linha) -> Servico:
        s = Servico()
        s._idServico         = linha[0]
        s._nomeServico       = linha[1]
        s._precoServico      = float(linha[2]) if linha[2] is not None else 0.0
        s._produtos          = []
        s._fornecedorServico = linha[3] or 'Tecnovale Gás'
        return s
