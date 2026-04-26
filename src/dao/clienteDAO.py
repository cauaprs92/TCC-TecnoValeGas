from src.dao.conexao import Conexao
from src.modelo.cliente import Cliente

class ClienteDAO:

    #  Inserir 
    def inserir(self, cliente: Cliente) -> bool:
        sql = """
            INSERT INTO clientes (idCliente, nomeCliente, CNPJCPF, enderecoCliente, contatoCliente)
            VALUES (%s, %s, %s, %s, %s)
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
                cliente._enderecoCliente,
                cliente._contatoCliente
            ))
            conexao.commit()
            print("Cliente inserido com sucesso!")
            return True
        except Exception as e:
            conexao.rollback() #desfaz oq foi feito, para que não entre informações pela metade no banco
            print(f"Erro ao inserir cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Buscar todos 
    def buscar_todos(self) -> list:
        sql = "SELECT idCliente, nomeCliente, CNPJCPF, enderecoCliente, contatoCliente FROM clientes"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return []
        cursor = conexao.cursor() #envia o select pro banco
        try:
            cursor.execute(sql)
            linhas = cursor.fetchall() #busca todas linhas e retorna uma lista                                                                                                          
            clientes = []
            for linha in linhas:
                c = Cliente()
                c._idCliente       = linha[0]
                c._nomeCliente     = linha[1]
                c._CNPJCPF         = linha[2]
                c._enderecoCliente = linha[3]
                c._contatoCliente  = linha[4]
                clientes.append(c)
            return clientes
        except Exception as e:
            print(f"Erro ao buscar clientes: {e}")
            return []
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # Buscar por ID
    def buscar_por_id(self, id_cliente: int):
        sql = """
            SELECT idCliente, nomeCliente, CNPJCPF, enderecoCliente, contatoCliente
            FROM clientes WHERE idCliente = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_cliente,))
            linha = cursor.fetchone()
            if not linha:
                return None
            dadosCliente = Cliente()
            dadosCliente._idCliente       = linha[0]
            dadosCliente._nomeCliente     = linha[1]
            dadosCliente._CNPJCPF         = linha[2]
            dadosCliente._enderecoCliente = linha[3]
            dadosCliente._contatoCliente  = linha[4]
            return dadosCliente
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Atualizar 
    def atualizar(self, cliente: Cliente) -> bool:
        sql = """
            UPDATE clientes
            SET nomeCliente = %s, CNPJCPF = %s, enderecoCliente = %s, contatoCliente = %s
            WHERE idCliente = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (
                cliente._nomeCliente,
                cliente._CNPJCPF,
                cliente._enderecoCliente,
                cliente._contatoCliente,
                cliente._idCliente
            ))
            conexao.commit()
            print("Cliente atualizado com sucesso!")
            return True
        except Exception as e:
            conexao.rollback() #desfaz oq foi feito, para que não entre informações pela metade no banco
            print(f"Erro ao atualizar cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    #  Deletar
    def deletar(self, id_cliente: int) -> bool:
        sql = "DELETE FROM clientes WHERE idCliente = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (id_cliente,))
            conexao.commit()
            print("Cliente deletado com sucesso!")
            return True
        except Exception as e:
            conexao.rollback() #desfaz oq foi feito, para que não entre informações pela metade no banco
            print(f"Erro ao deletar cliente: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)
