from src.dao.banco import consultar, consultar_um, executar_transacao
from src.modelo.servico import Servico

_SELECT = "SELECT idServico, nomeServico, precoServico, fornecedorServico FROM servicos"


class ServicoDAO:

    def inserir(self, servico: Servico) -> bool:
        def operacao(cursor):
            cursor.execute(
                "INSERT INTO servicos (nomeServico, precoServico, fornecedorServico) VALUES (%s, %s, %s)",
                (servico._nomeServico, servico._precoServico, servico._fornecedorServico)
            )
            servico._idServico = cursor.lastrowid
            self._gravar_receita(cursor, servico)
        sucesso, _ = executar_transacao(operacao, "Erro ao inserir serviço:")
        return sucesso

    def atualizar(self, servico: Servico) -> bool:
        def operacao(cursor):
            cursor.execute(
                "UPDATE servicos SET nomeServico = %s, precoServico = %s, fornecedorServico = %s WHERE idServico = %s",
                (servico._nomeServico, servico._precoServico, servico._fornecedorServico, servico._idServico)
            )
            cursor.execute("DELETE FROM servicoProdutos WHERE idServico = %s", (servico._idServico,))
            self._gravar_receita(cursor, servico)
        sucesso, _ = executar_transacao(operacao, "Erro ao atualizar serviço:")
        return sucesso

    def deletar(self, idServico: int) -> bool:
        def operacao(cursor):
            cursor.execute("DELETE FROM servicoProdutos WHERE idServico = %s", (idServico,))
            cursor.execute("DELETE FROM servicos WHERE idServico = %s", (idServico,))
        sucesso, _ = executar_transacao(operacao, "Erro ao deletar serviço:")
        return sucesso

    def buscar_todos(self) -> list:
        servicos = [self._linha_para_servico(l) for l in consultar(_SELECT, erro="Erro ao buscar serviços:")]
        # Uma consulta só para a receita de todos os serviços (antes era uma por serviço).
        receitas = {}
        for id_servico, id_produto, qtd in consultar(
                "SELECT idServico, idProduto, quantidade FROM servicoProdutos",
                erro="Erro ao buscar receitas dos serviços:"):
            receitas.setdefault(id_servico, []).append({"idProduto": id_produto, "quantidade": qtd})
        for s in servicos:
            s._produtos = receitas.get(s._idServico, [])
        return servicos

    def buscar_por_id(self, idServico: int):
        linha = consultar_um(f"{_SELECT} WHERE idServico = %s", (idServico,),
                             erro="Erro ao buscar serviço por ID:")
        if not linha:
            return None
        servico = self._linha_para_servico(linha)
        servico._produtos = self.buscar_produtos_do_servico(idServico)
        return servico

    def buscar_produtos_do_servico(self, idServico: int) -> list:
        linhas = consultar("SELECT idProduto, quantidade FROM servicoProdutos WHERE idServico = %s",
                           (idServico,), erro="Erro ao buscar produtos do serviço:")
        return [{"idProduto": l[0], "quantidade": l[1]} for l in linhas]

    def _gravar_receita(self, cursor, servico: Servico):
        for item in servico._produtos:
            cursor.execute(
                "INSERT INTO servicoProdutos (idServico, idProduto, quantidade) VALUES (%s, %s, %s)",
                (servico._idServico, item["idProduto"], item["quantidade"])
            )

    def _linha_para_servico(self, linha) -> Servico:
        s = Servico()
        s._idServico         = linha[0]
        s._nomeServico       = linha[1]
        s._precoServico      = float(linha[2]) if linha[2] is not None else 0.0
        s._produtos          = []
        s._fornecedorServico = linha[3] or 'Tecnovale Gás'
        return s
