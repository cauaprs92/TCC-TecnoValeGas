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

    def buscar_historico_obra(self, id_obra: int, desc_obra: str = None) -> list:
        """Todo o histórico ligado a uma obra: criação, edições e exclusão.

        Casa por idEntidade (registros novos) e, como rede de segurança para os
        registros antigos que não tinham essa coluna, também pelo texto:
        o ID citado ("(ID: 4)", "obra ID 4 ") e o nome da obra entre aspas
        (é assim que o cadastro é descrito, e descObra é única)."""
        like_id   = f"%(ID: {id_obra})%"
        like_id2  = f"%obra ID {id_obra} %"
        # '!' como ESCAPE: % e _ que existam no nome viram literais no LIKE.
        nome_esc  = (desc_obra or "").replace("!", "!!").replace("%", "!%").replace("_", "!_")
        like_nome = f"%'{nome_esc}'%"
        usa_nome  = 1 if desc_obra else 0
        linhas = consultar("""
            SELECT idHistorico, idAdmin, nomeAdmin, acao, entidade, idEntidade, descricao, dataHora
            FROM historico
            WHERE entidade = 'Obra'
              AND ( idEntidade = %s
                 OR descricao LIKE %s
                 OR descricao LIKE %s
                 OR (%s = 1 AND descricao LIKE %s ESCAPE '!') )
            ORDER BY dataHora DESC
        """, (id_obra, like_id, like_id2, usa_nome, like_nome),
            erro="Erro ao buscar histórico da obra:")
        return [self._linha_para_historico(l) for l in linhas]

    def _linha_para_historico(self, linha) -> Historico:
        h = Historico()
        (h._idHistorico, h._idAdmin, h._nomeAdmin, h._acao,
         h._entidade, h._idEntidade, h._descricao, h._dataHora) = linha
        return h
