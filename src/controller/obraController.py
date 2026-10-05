from src.dao.obraDAO            import ObraDAO
from src.dao.produtosObrasDAO   import ProdutosObrasDAO
from src.dao.clienteDAO         import ClienteDAO
from src.dao.servicoDAO         import ServicoDAO
from src.dao.obraFuncionarioDAO import ObraFuncionarioDAO
from src.dao.adminDAO           import AdminDAO
from src.controller.produtoController import ProdutoController

CARGO_OBRA = "Obra"

class ObraController:
    """Regras de negócio da obra. O formato do corpo (campos obrigatórios,
    datas, status) já chega validado pelo ObraMiddleware."""

    def __init__(self):
        self.dao          = ObraDAO()
        self.daoProdObras = ProdutosObrasDAO()
        self.daoCliente   = ClienteDAO()
        self.daoServico   = ServicoDAO()
        self.daoEquipe    = ObraFuncionarioDAO()
        self.daoAdmin     = AdminDAO()
        self.ctrlProduto  = ProdutoController()

    def _validar_equipe(self, funcionarios: list) -> tuple:
        """Cada id da equipe precisa existir e ter cargo 'Obra' — é esse cargo
        que dá ao usuário acesso às obras em que ele está vinculado."""
        for id_login in (funcionarios or []):
            usuario = self.daoAdmin.buscar_por_id(id_login)
            if not usuario:
                return False, f"Funcionario ID {id_login} nao encontrado."
            if usuario[3] != CARGO_OBRA:
                return False, f"'{usuario[2]}' nao tem cargo de Obra e nao pode entrar na equipe."
        return True, ""

    def listar_funcionarios_disponiveis(self) -> list:
        rows = self.daoAdmin.listar()
        return [
            {"idLogin": r[0], "email": r[1], "nomeLogin": r[2]}
            for r in rows if r[3] == CARGO_OBRA
        ]

    def buscar_equipe_da_obra(self, id_obra: int) -> list:
        return self.daoEquipe.listar_por_obra(id_obra)

    def buscar_cliente_da_obra(self, id_obra: int):
        """Cliente de uma obra específica. Existe para o funcionário de obra ver
        os dados do cliente da obra dele sem abrir a lista inteira de clientes."""
        obra = self.dao.buscar_por_id(id_obra)
        if not obra:
            return None
        return self.daoCliente.buscar_por_id(obra[1])

    def buscar_equipes_das_obras(self, ids_obras: list) -> dict:
        return self.daoEquipe.listar_por_obras(ids_obras)

    def buscar_nomes_clientes(self, ids_clientes: list) -> dict:
        return self.daoCliente.buscar_nomes_por_ids(ids_clientes)

    def cadastrar(self, dadosObra: dict, produtosUsados: list,
                  servicosVinculados: list = None, funcionarios: list = None) -> tuple:
        clienteExistente = self.daoCliente.buscar_por_id(dadosObra["codCliente"])
        if not clienteExistente:
            return False, "Cliente nao encontrado. Cadastre o cliente antes de criar a obra."

        valido, mensagem = self._validar_equipe(funcionarios)
        if not valido:
            return False, mensagem

        servicosVinculados = servicosVinculados or []
        avisos = self._avisos_de_estoque(dadosObra, produtosUsados, servicosVinculados)

        sucesso, resultado = self.dao.cadastrar(
            dadosObra, produtosUsados, servicosVinculados, funcionarios
        )
        if not sucesso:
            return False, resultado
        return True, "\n".join(["Obra cadastrada com sucesso!"] + avisos)

    def atualizar(self, idObra: int, dadosObra: dict,
                  produtosNovos: list = None, servicosNovos: list = None,
                  funcionarios: list = None) -> tuple:
        obraExistente = self.dao.buscar_por_id(idObra)
        if not obraExistente:
            return False, "Obra nao encontrada."

        clienteExistente = self.daoCliente.buscar_por_id(dadosObra["codCliente"])
        if not clienteExistente:
            return False, "Cliente nao encontrado."

        if funcionarios is not None:
            valido, mensagem = self._validar_equipe(funcionarios)
            if not valido:
                return False, mensagem

        avisos = self._avisos_de_estoque(dadosObra, produtosNovos, servicosNovos)

        # Dados, equipe, status (com a baixa/devolução de estoque que ele
        # implica) e material novo são gravados juntos: ou tudo, ou nada.
        # funcionarios=None = o formulário não mandou equipe, então não mexemos nela.
        sucesso, resultado = self.dao.atualizar(
            idObra, dadosObra, produtosNovos or [], servicosNovos or [], funcionarios
        )
        if not sucesso:
            return False, resultado
        return True, "\n".join(["Obra atualizada com sucesso!"] + avisos)

    def _avisos_de_estoque(self, dadosObra: dict, produtos: list, servicos: list) -> list:
        """Avisos de estoque baixo para o material que a obra vai consumir. A
        checagem que bloqueia de fato é feita na transação de gravação; aqui
        só se avisa quem salva. Obra cancelada não consome estoque."""
        if dadosObra.get("statusObra") == "Cancelada":
            return []
        necessarios = [(i["idProduto"], i["quantidade"]) for i in produtos or []]
        for id_servico in servicos or []:
            necessarios += [(i["idProduto"], i["quantidade"])
                            for i in self.daoServico.buscar_produtos_do_servico(id_servico)]

        avisos = []
        for id_produto, qtd in necessarios:
            _, mensagem = self.ctrlProduto.verificar_estoque(id_produto, qtd)
            if "ATENCAO" in mensagem or "AVISO" in mensagem:
                avisos.append(mensagem)
        return avisos

    def listar_para_usuario(self, cargo: str, id_login) -> list:
        """Funcionário de obra enxerga só as obras em que está na equipe.
        Os demais cargos recebem a lista inteira."""
        obras = self.dao.buscar_todas()
        if cargo != CARGO_OBRA:
            return obras
        permitidas = set(self.daoEquipe.listar_ids_obras_do_funcionario(id_login))
        return [o for o in obras if o[0] in permitidas]

    def usuario_pode_ver_obra(self, cargo: str, id_login, id_obra: int) -> bool:
        if cargo != CARGO_OBRA:
            return True
        return self.daoEquipe.pertence_a_obra(id_obra, id_login)

    def buscar_por_id(self, idObra: int):
        return self.dao.buscar_por_id(idObra)

    def deletar(self, idObra: int) -> tuple:
        """Retorna (sucesso, mensagem, arquivos de foto a apagar do disco)."""
        obraExistente = self.dao.buscar_por_id(idObra)
        if not obraExistente:
            return False, "Obra nao encontrada.", []

        sucesso, resultado = self.dao.deletar(idObra)
        if sucesso:
            return True, "Obra deletada com sucesso!", resultado
        return False, resultado, []

    def buscar_produtos_da_obra(self, idObra: int) -> list:
        return self.daoProdObras.buscar_produtos_da_obra(idObra)

    def buscar_servicos_da_obra(self, idObra: int) -> list:
        return self.daoProdObras.buscar_servicos_da_obra(idObra)

    def atualizar_produto_obra(self, idObra: int, idProduto: int, nova_qtd: int) -> tuple:
        if not self.dao.buscar_por_id(idObra):
            return False, "Obra não encontrada."
        if nova_qtd < 1:
            return False, "Quantidade deve ser maior que zero."
        return self.daoProdObras.atualizar_quantidade_produto_obra(idObra, idProduto, nova_qtd)

    def remover_produto_obra(self, idObra: int, idProduto: int) -> tuple:
        if not self.dao.buscar_por_id(idObra):
            return False, "Obra não encontrada."
        return self.daoProdObras.remover_produto_obra(idObra, idProduto)

    def atualizar_servico_obra(self, idObra: int, idServicoAtual: int, idServicoNovo: int) -> tuple:
        if not self.dao.buscar_por_id(idObra):
            return False, "Obra não encontrada."
        if not self.daoServico.buscar_por_id(idServicoNovo):
            return False, "Serviço não encontrado."
        return self.daoProdObras.atualizar_servico_obra(idObra, idServicoAtual, idServicoNovo)

    def remover_servico_obra(self, idObra: int, idServico: int) -> tuple:
        if not self.dao.buscar_por_id(idObra):
            return False, "Obra não encontrada."
        return self.daoProdObras.remover_servico_obra(idObra, idServico)
