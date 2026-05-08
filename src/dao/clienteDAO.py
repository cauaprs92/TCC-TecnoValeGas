from src.dao.conexao import Conexao
from src.modelo.cliente import Cliente

class ClienteDAO:

    def proximo_id(self) -> int:
        sql = "SELECT COALESCE(MAX(idCliente), 0) + 1 FROM clientes"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return 1
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Erro ao obter próximo ID: {e}")
            return 1
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def inserir(self, cliente: Cliente) -> bool:
        sql = """
            INSERT INTO clientes
                (idCliente, nomeCliente, CNPJCPF, contatoCliente,
                 cep, rua, numero, complemento, bairro, cidade, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                cliente._idCliente,
                cliente._nomeCliente,
                cliente._CNPJCPF,
                cliente._contatoCliente,
                cliente._cep,
                cliente._rua,
                cliente._numero,
                cliente._complemento,
                cliente._bairro,
                cliente._cidade,
                cliente._estado,
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_todos(self) -> list:
        sql = """
            SELECT idCliente, nomeCliente, CNPJCPF, contatoCliente,
                   cep, rua, numero, complemento, bairro, cidade, estado
            FROM clientes
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor()
        try:
            cursor.execute(sql)
            return [self._linha_para_cliente(l) for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar clientes: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_cliente: int):
        sql = """
            SELECT idCliente, nomeCliente, CNPJCPF, contatoCliente,
                   cep, rua, numero, complemento, bairro, cidade, estado
            FROM clientes WHERE idCliente = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_cliente,))
            linha = cursor.fetchone()
            return self._linha_para_cliente(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def atualizar(self, cliente: Cliente) -> bool:
        sql = """
            UPDATE clientes
            SET nomeCliente=%s, CNPJCPF=%s, contatoCliente=%s,
                cep=%s, rua=%s, numero=%s, complemento=%s,
                bairro=%s, cidade=%s, estado=%s
            WHERE idCliente=%s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                cliente._nomeCliente,
                cliente._CNPJCPF,
                cliente._contatoCliente,
                cliente._cep,
                cliente._rua,
                cliente._numero,
                cliente._complemento,
                cliente._bairro,
                cliente._cidade,
                cliente._estado,
                cliente._idCliente,
            ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao atualizar cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def deletar(self, id_cliente: int) -> bool:
        sql = "DELETE FROM clientes WHERE idCliente = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_cliente,))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao deletar cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _linha_para_cliente(self, linha) -> Cliente:
        c = Cliente()
        c._idCliente     = linha[0]
        c._nomeCliente   = linha[1]
        c._CNPJCPF       = linha[2]
        c._contatoCliente = linha[3]
        c._cep           = linha[4]
        c._rua           = linha[5]
        c._numero        = linha[6]
        c._complemento   = linha[7]
        c._bairro        = linha[8]
        c._cidade        = linha[9]
        c._estado        = linha[10]
        return c
