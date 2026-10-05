from src.dao.banco import consultar, consultar_um, executar


class ResponsavelDAO:

    def listar(self) -> list:
        return consultar("SELECT idResponsavel, nomeResponsavel FROM responsavel ORDER BY nomeResponsavel",
                         erro="Erro ao listar responsáveis:")

    def buscar_por_id(self, id_responsavel: int):
        return consultar_um(
            "SELECT idResponsavel, nomeResponsavel FROM responsavel WHERE idResponsavel = %s",
            (id_responsavel,), erro="Erro ao buscar responsável por ID:")

    def buscar_por_nome(self, nome: str, excluir_id: int = None):
        sql = "SELECT idResponsavel FROM responsavel WHERE LOWER(nomeResponsavel) = LOWER(%s)"
        params = [nome]
        if excluir_id:
            sql += " AND idResponsavel != %s"
            params.append(excluir_id)
        return consultar_um(sql, params, erro="Erro ao buscar responsável por nome:")

    def criar(self, nome: str) -> bool:
        return executar("INSERT INTO responsavel (nomeResponsavel) VALUES (%s)", (nome,),
                        erro="Erro ao criar responsável:")

    def atualizar(self, id_responsavel: int, nome: str) -> bool:
        return executar("UPDATE responsavel SET nomeResponsavel = %s WHERE idResponsavel = %s",
                        (nome, id_responsavel), erro="Erro ao atualizar responsável:")

    def deletar(self, id_responsavel: int) -> bool:
        return executar("DELETE FROM responsavel WHERE idResponsavel = %s", (id_responsavel,),
                        erro="Erro ao deletar responsável:")
