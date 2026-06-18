from src.dao.conexao import Conexao
from src.modelo.historico import Historico


class HistoricoDAO:

    def inserir(self, idAdmin: int, nomeAdmin: str, acao: str, entidade: str, descricao: str) -> bool:
        sql = """
            INSERT INTO historico (idAdmin, nomeAdmin, acao, entidade, descricao)
            VALUES (%s, %s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idAdmin, nomeAdmin, acao, entidade, descricao))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir historico: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todos(self) -> list:
        sql = """
            SELECT idHistorico, idAdmin, nomeAdmin, acao, entidade, descricao, dataHora
            FROM historico
            ORDER BY dataHora DESC
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return [self._linha_para_historico(l) for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar historico: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _linha_para_historico(self, linha) -> Historico:
        h = Historico()
        h._idHistorico = linha[0]
        h._idAdmin     = linha[1]
        h._nomeAdmin   = linha[2]
        h._acao        = linha[3]
        h._entidade    = linha[4]
        h._descricao   = linha[5]
        h._dataHora    = linha[6]
        return h
