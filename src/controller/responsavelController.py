from src.dao.responsavelDAO import ResponsavelDAO


class ResponsavelController:

    def __init__(self):
        self.dao = ResponsavelDAO()

    def listar(self) -> list:
        rows = self.dao.listar()
        return [{"idResponsavel": r[0], "nomeResponsavel": r[1]} for r in rows]

    def criar(self, nome: str) -> tuple:
        if not nome or not nome.strip():
            return False, "Nome é obrigatório."
        if len(nome.strip()) < 2:
            return False, "Nome deve ter ao menos 2 caracteres."
        if self.dao.buscar_por_nome(nome.strip()):
            return False, "Já existe um responsável com esse nome."
        ok = self.dao.criar(nome.strip())
        if ok:
            return True, f"Responsável '{nome.strip()}' criado com sucesso!"
        return False, "Erro ao criar responsável."

    def atualizar(self, id_responsavel: int, nome: str) -> tuple:
        if not self.dao.buscar_por_id(id_responsavel):
            return False, "Responsável não encontrado."
        if not nome or not nome.strip():
            return False, "Nome é obrigatório."
        if len(nome.strip()) < 2:
            return False, "Nome deve ter ao menos 2 caracteres."
        if self.dao.buscar_por_nome(nome.strip(), excluir_id=id_responsavel):
            return False, "Já existe outro responsável com esse nome."
        ok = self.dao.atualizar(id_responsavel, nome.strip())
        if ok:
            return True, "Responsável atualizado com sucesso!"
        return False, "Erro ao atualizar responsável."

    def deletar(self, id_responsavel: int) -> tuple:
        if not self.dao.buscar_por_id(id_responsavel):
            return False, "Responsável não encontrado."
        ok = self.dao.deletar(id_responsavel)
        if ok:
            return True, "Responsável removido com sucesso!"
        return False, "Erro ao remover responsável."
