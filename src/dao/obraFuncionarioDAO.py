from src.dao.conexao import Conexao


class ObraFuncionarioDAO:
    """Equipe da obra — quais usuários de cargo 'Obra' trabalham em cada obra.

    É essa tabela que define o que um funcionário de obra enxerga: ele só tem
    acesso às obras em que está vinculado aqui.
    """

    def listar_por_obra(self, id_obra: int) -> list:
        sql = """
            SELECT l.idLogin, l.nomeLogin, l.email
            FROM obraFuncionarios ofu
            JOIN login l ON l.idLogin = ofu.idLogin
            WHERE ofu.idObra = %s
            ORDER BY l.nomeLogin
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra,))
            return [
                {"idLogin": r[0], "nomeLogin": r[1], "email": r[2]}
                for r in cursor.fetchall()
            ]
        except Exception as e:
            print(f"Erro ao listar equipe da obra {id_obra}: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def listar_por_obras(self, ids_obras: list) -> dict:
        """Equipe de várias obras de uma vez, no formato {idObra: [funcionários]}.
        Evita uma consulta por obra ao montar a listagem geral."""
        if not ids_obras:
            return {}

        marcadores = ", ".join(["%s"] * len(ids_obras))
        sql = f"""
            SELECT ofu.idObra, l.idLogin, l.nomeLogin
            FROM obraFuncionarios ofu
            JOIN login l ON l.idLogin = ofu.idLogin
            WHERE ofu.idObra IN ({marcadores})
            ORDER BY l.nomeLogin
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return {}
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, tuple(ids_obras))
            equipes = {}
            for id_obra, id_login, nome_login in cursor.fetchall():
                equipes.setdefault(id_obra, []).append(
                    {"idLogin": id_login, "nomeLogin": nome_login}
                )
            return equipes
        except Exception as e:
            print(f"Erro ao listar equipes das obras: {e}")
            return {}
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def listar_ids_obras_do_funcionario(self, id_login: int) -> list:
        sql = "SELECT idObra FROM obraFuncionarios WHERE idLogin = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_login,))
            return [r[0] for r in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao listar obras do funcionário {id_login}: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def pertence_a_obra(self, id_obra: int, id_login: int) -> bool:
        sql = "SELECT 1 FROM obraFuncionarios WHERE idObra = %s AND idLogin = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_obra, id_login))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erro ao verificar equipe da obra {id_obra}: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def substituir_equipe(self, id_obra: int, ids_login: list) -> bool:
        """Troca a equipe inteira da obra pela lista informada. Lista vazia
        remove todo mundo — é assim que a edição desvincula funcionários."""
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute("DELETE FROM obraFuncionarios WHERE idObra = %s", (id_obra,))
            for id_login in dict.fromkeys(ids_login or []):
                cursor.execute(
                    "INSERT INTO obraFuncionarios (idObra, idLogin) VALUES (%s, %s)",
                    (id_obra, id_login)
                )
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao salvar equipe da obra {id_obra}: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
