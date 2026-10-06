from src.dao.banco import consultar, executar
from src.modelo.historico import Historico


class HistoricoDAO:

    def inserir(self, idAdmin: int, nomeAdmin: str, acao: str, entidade: str,
                descricao: str, idEntidade: int = None) -> bool:
        return executar("""
            INSERT INTO historico (idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao),
            erro="Erro ao inserir histórico:")

    def buscar_todos(self) -> list:
        linhas = consultar("""
            SELECT idHistorico, idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao, dataHora
            FROM historico
            ORDER BY dataHora DESC
        """, erro="Erro ao buscar histórico:")
        return [self._linha_para_historico(l) for l in linhas]

    def buscar_por_entidade(self, entidade: str, idEntidade: int) -> list:
        """Histórico de um registro específico (ex.: uma obra)."""
        linhas = consultar("""
            SELECT idHistorico, idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao, dataHora
            FROM historico
            WHERE entidade = %s AND idEntidade = %s
            ORDER BY dataHora DESC
        """, (entidade, idEntidade), erro="Erro ao buscar histórico da entidade:")
        return [self._linha_para_historico(l) for l in linhas]

    def _linha_para_historico(self, linha) -> Historico:
        h = Historico()
        (h._idHistorico, h._idAdmin, h._nomeAdmin, h._acao,
         h._entidade, h._idEntidade, h._descricao, h._dataHora) = linha
        return h
