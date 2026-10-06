from src.dao.historicoDAO import HistoricoDAO


class HistoricoController:

    def __init__(self):
        self.dao = HistoricoDAO()

    def registrar(self, idAdmin: int, nomeAdmin: str, acao: str, entidade: str,
                  descricao: str, idEntidade: int = None) -> None:
        """Registra uma ação no histórico. Falhas são silenciosas para não interromper o fluxo principal.
        idEntidade (opcional) vincula o registro ao item afetado — ex.: a obra."""
        try:
            self.dao.inserir(idAdmin, nomeAdmin, acao, entidade, descricao, idEntidade)
        except Exception as e:
            print(f"Aviso: falha ao registrar histórico — {e}")

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def listar_por_entidade(self, entidade: str, idEntidade: int) -> list:
        return self.dao.buscar_por_entidade(entidade, idEntidade)
