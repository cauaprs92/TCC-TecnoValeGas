from src.dao.conexao import Conexao


class FornecedorDAO:

    def listar(self) -> list:
        sql = "SELECT idFornecedor, nomeFornecedor FROM fornecedores ORDER BY nomeFornecedor"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar fornecedores: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_nome(self, nome: str):
        sql = "SELECT idFornecedor, nomeFornecedor FROM fornecedores WHERE LOWER(nomeFornecedor) = LOWER(%s)"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (nome,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar fornecedor por nome: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def criar(self, nome: str):
        sql = "INSERT INTO fornecedores (nomeFornecedor) VALUES (%s)"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (nome,))
            conexao.commit()
            return cursor.lastrowid
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao criar fornecedor: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def obter_ou_criar(self, nome: str):
        """Retorna o idFornecedor existente para o nome informado ou cria um novo registro."""
        existente = self.buscar_por_nome(nome)
        if existente:
            return existente[0]
        return self.criar(nome)
