from src.dao.historicoDAO import HistoricoDAO


class HistoricoController:

    def __init__(self):
        self.dao = HistoricoDAO()

    def registrar(self, idAdmin: int, nomeAdmin: str, acao: str, entidade: str, descricao: str) -> None:
        """Registra uma ação no histórico. Falhas são silenciosas para não interromper o fluxo principal."""
        try:
            self.dao.inserir(idAdmin, nomeAdmin, acao, entidade, descricao)
        except Exception as e:
            print(f"Aviso: falha ao registrar histórico — {e}")

    def listar(self) -> list:
        return self.dao.buscar_todos()
