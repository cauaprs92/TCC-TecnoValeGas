from src.dao.conexao import Conexao
from src.modelo.cliente import Cliente

class ClienteDAO:

    def inserir(self, cliente: Cliente) -> bool:
        sql = """
            INSERT INTO clientes
                (nomeCliente, CNPJCPF, contatoCliente,
                 emailCliente, telefone2,
                 cep, rua, numero, complemento, bairro, cidade, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                cliente._emailCliente,
                cliente._telefone2,
                cliente._cep,
                cliente._rua,
                cliente._numero,
                cliente._complemento,
                cliente._bairro,
                cliente._cidade,
                cliente._estado,
            ))
            conexao.commit()
            cliente._idCliente = cursor.lastrowid
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
                   emailCliente, telefone2,
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

    def buscar_nomes_por_ids(self, ids_clientes: list) -> dict:
        """Só os nomes, no formato {idCliente: nomeCliente}. A listagem de obras
        usa isto para mostrar o cliente sem depender da lista completa, que nem
        todo cargo pode acessar."""
        ids = [i for i in dict.fromkeys(ids_clientes or []) if i]
        if not ids:
            return {}

        marcadores = ", ".join(["%s"] * len(ids))
        sql = f"SELECT idCliente, nomeCliente FROM clientes WHERE idCliente IN ({marcadores})"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return {}
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, tuple(ids))
            return {linha[0]: linha[1] for linha in cursor.fetchall()}
        except Exception as e:
            print(f"Erro ao buscar nomes de clientes: {e}")
            return {}
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def existe_documento(self, digitos: str, excluir_id: int = None) -> bool:
        """True se outro cliente já usa este CPF/CNPJ (comparado só pelos
        dígitos, para '123.456.789-00' e '12345678900' contarem como iguais)."""
        sql = "SELECT 1 FROM clientes WHERE REGEXP_REPLACE(CNPJCPF, '[^0-9]', '') = %s"
        params = [digitos]
        if excluir_id:
            sql += " AND idCliente <> %s"
            params.append(excluir_id)
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erro ao verificar CPF/CNPJ: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def buscar_por_id(self, id_cliente: int):
        sql = """
            SELECT idCliente, nomeCliente, CNPJCPF, contatoCliente,
                   emailCliente, telefone2,
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
                emailCliente=%s, telefone2=%s,
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
                cliente._emailCliente,
                cliente._telefone2,
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
        c._idCliente      = linha[0]
        c._nomeCliente    = linha[1]
        c._CNPJCPF        = linha[2]
        c._contatoCliente = linha[3]
        c._emailCliente   = linha[4]
        c._telefone2      = linha[5]
        c._cep            = linha[6]
        c._rua            = linha[7]
        c._numero         = linha[8]
        c._complemento    = linha[9]
        c._bairro         = linha[10]
        c._cidade         = linha[11]
        c._estado         = linha[12]
        return c
