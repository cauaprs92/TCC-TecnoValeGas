from src.dao.banco import consultar, consultar_um


class ObraFuncionarioDAO:
    """Equipe da obra — quais usuários de cargo 'Obra' trabalham em cada obra.

    É essa tabela que define o que um funcionário de obra enxerga: ele só tem
    acesso às obras em que está vinculado aqui.
    """

    def listar_por_obra(self, id_obra: int) -> list:
        linhas = consultar("""
            SELECT l.idLogin, l.nomeLogin, l.email
            FROM obraFuncionarios ofu
            JOIN login l ON l.idLogin = ofu.idLogin
            WHERE ofu.idObra = %s
            ORDER BY l.nomeLogin
        """, (id_obra,), erro=f"Erro ao listar equipe da obra {id_obra}:")
        return [{"idLogin": r[0], "nomeLogin": r[1], "email": r[2]} for r in linhas]

    def listar_por_obras(self, ids_obras: list) -> dict:
        """Equipe de várias obras de uma vez, no formato {idObra: [funcionários]}.
        Evita uma consulta por obra ao montar a listagem geral."""
        if not ids_obras:
            return {}
        marcadores = ", ".join(["%s"] * len(ids_obras))
        linhas = consultar(f"""
            SELECT ofu.idObra, l.idLogin, l.nomeLogin
            FROM obraFuncionarios ofu
            JOIN login l ON l.idLogin = ofu.idLogin
            WHERE ofu.idObra IN ({marcadores})
            ORDER BY l.nomeLogin
        """, tuple(ids_obras), erro="Erro ao listar equipes das obras:")
        equipes = {}
        for id_obra, id_login, nome_login in linhas:
            equipes.setdefault(id_obra, []).append({"idLogin": id_login, "nomeLogin": nome_login})
        return equipes

    def listar_ids_obras_do_funcionario(self, id_login: int) -> list:
        linhas = consultar("SELECT idObra FROM obraFuncionarios WHERE idLogin = %s", (id_login,),
                           erro=f"Erro ao listar obras do funcionário {id_login}:")
        return [r[0] for r in linhas]

    def pertence_a_obra(self, id_obra: int, id_login: int) -> bool:
        return consultar_um(
            "SELECT 1 FROM obraFuncionarios WHERE idObra = %s AND idLogin = %s", (id_obra, id_login),
            erro=f"Erro ao verificar equipe da obra {id_obra}:") is not None

    def salvar_equipe(self, cursor, id_obra: int, ids_login: list):
        """Troca a equipe inteira da obra pela lista informada, dentro da
        transação de quem chama. Lista vazia remove todo mundo — é assim que a
        edição desvincula funcionários."""
        cursor.execute("DELETE FROM obraFuncionarios WHERE idObra = %s", (id_obra,))
        for id_login in dict.fromkeys(ids_login or []):
            cursor.execute(
                "INSERT INTO obraFuncionarios (idObra, idLogin) VALUES (%s, %s)",
                (id_obra, id_login)
            )
