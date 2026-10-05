from src.dao.banco              import OperacaoInvalida, executar_transacao, consultar, consultar_um
from src.dao.produtosObrasDAO   import ProdutosObrasDAO, STATUS_CANCELADA
from src.dao.obraFuncionarioDAO import ObraFuncionarioDAO

_COLS_SELECT = """
    idObra, codCliente, descObra, dataInicio, dataFim,
    statusObra, respObra, obsObra, orientacaoObra,
    tipoObra, clientePrimario, fieldObra, unidadeObra, emailContato, celular1, celular2,
    valorObra, setorObra
"""

# Campos que o formulário grava diretamente. statusObra fica de fora: mudar o
# status mexe no estoque e no valor da obra, então passa por _mudar_status.
_COLS_EDITAVEIS = [
    "codCliente", "descObra", "dataInicio", "dataFim", "respObra", "obsObra",
    "orientacaoObra", "tipoObra", "clientePrimario", "fieldObra", "unidadeObra",
    "emailContato", "celular1", "celular2", "setorObra",
]


def _valores(obra: dict) -> list:
    return [obra.get(c) for c in _COLS_EDITAVEIS]


class ObraDAO:

    def __init__(self):
        self.materiais = ProdutosObrasDAO()
        self.equipe    = ObraFuncionarioDAO()

    # ─── Escrita (cada método é uma transação só) ─────────────────────────────

    def cadastrar(self, obra: dict, produtos: list, servicos: list, funcionarios: list) -> tuple:
        """Retorna (True, idObra) ou (False, mensagem)."""
        def operacao(cursor):
            colunas = _COLS_EDITAVEIS + ["statusObra"]
            cursor.execute(
                f"INSERT INTO obras ({', '.join(colunas)}) VALUES ({', '.join(['%s'] * len(colunas))})",
                _valores(obra) + [obra["statusObra"]]
            )
            id_obra = cursor.lastrowid
            ativa   = obra["statusObra"] != STATUS_CANCELADA

            self.equipe.salvar_equipe(cursor, id_obra, funcionarios)
            self.materiais.vincular_produtos(cursor, id_obra, produtos, ativa)
            self.materiais.vincular_servicos(cursor, id_obra, servicos, ativa)
            self.materiais.recalcular_valor(cursor, id_obra)
            return id_obra
        return executar_transacao(operacao, "Erro ao cadastrar obra.")

    def atualizar(self, id_obra: int, obra: dict, produtos_novos: list,
                  servicos_novos: list, funcionarios: list = None) -> tuple:
        """funcionarios=None mantém a equipe; lista vazia esvazia."""
        def operacao(cursor):
            status_atual = self.materiais.status_obra(cursor, id_obra)
            sets = ", ".join(f"{c} = %s" for c in _COLS_EDITAVEIS)
            cursor.execute(f"UPDATE obras SET {sets} WHERE idObra = %s", _valores(obra) + [id_obra])

            if funcionarios is not None:
                self.equipe.salvar_equipe(cursor, id_obra, funcionarios)

            # O status muda antes do material novo: assim o material entra já
            # com a regra do status novo (obra cancelada não baixa estoque).
            novo_status = obra["statusObra"]
            self._mudar_status(cursor, id_obra, status_atual, novo_status)
            ativa = novo_status != STATUS_CANCELADA
            self.materiais.vincular_produtos(cursor, id_obra, produtos_novos, ativa)
            self.materiais.vincular_servicos(cursor, id_obra, servicos_novos, ativa)
            self.materiais.recalcular_valor(cursor, id_obra)
        return executar_transacao(operacao, "Erro ao atualizar obra.")

    def deletar(self, id_obra: int) -> tuple:
        """Devolve o estoque (se a obra não estava cancelada) e exclui a obra.
        Retorna (True, [arquivos de foto a apagar do disco]) ou (False, mensagem)."""
        def operacao(cursor):
            if self.materiais.status_obra(cursor, id_obra) != STATUS_CANCELADA:
                self.materiais.repor_obra(cursor, id_obra)

            cursor.execute("SELECT nomeArquivo FROM obra_fotos WHERE idObra = %s", (id_obra,))
            arquivos = [r[0] for r in cursor.fetchall()]

            # Equipe, fotos e a receita dos serviços saem por ON DELETE CASCADE.
            cursor.execute("DELETE FROM produtosObras WHERE idObra = %s", (id_obra,))
            cursor.execute("DELETE FROM obraServicos  WHERE idObra = %s", (id_obra,))
            cursor.execute("DELETE FROM obras         WHERE idObra = %s", (id_obra,))
            return arquivos
        return executar_transacao(operacao, "Erro ao deletar obra.")

    def _mudar_status(self, cursor, id_obra: int, status_atual: str, novo_status: str):
        if novo_status == status_atual:
            return
        if novo_status == STATUS_CANCELADA:
            self.materiais.repor_obra(cursor, id_obra)
        elif status_atual == STATUS_CANCELADA:
            try:
                self.materiais.baixar_obra(cursor, id_obra)
            except OperacaoInvalida as e:
                raise OperacaoInvalida(f"Não foi possível reativar a obra: {e}")
        cursor.execute("UPDATE obras SET statusObra = %s WHERE idObra = %s", (novo_status, id_obra))

    # ─── Consulta ─────────────────────────────────────────────────────────────

    def buscar_todas(self) -> list:
        return consultar(f"SELECT {_COLS_SELECT} FROM obras ORDER BY dataInicio DESC",
                         erro="Erro ao buscar obras:")

    def buscar_por_id(self, id_obra: int):
        return consultar_um(f"SELECT {_COLS_SELECT} FROM obras WHERE idObra = %s", (id_obra,),
                            erro="Erro ao buscar obra por ID:")
