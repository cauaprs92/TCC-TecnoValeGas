from src.dao.banco import consultar, consultar_um, executar, inserir
from src.modelo.cliente import Cliente

# Colunas editáveis, na mesma ordem dos atributos _<coluna> do modelo Cliente.
_CAMPOS = [
    "nomeCliente", "CNPJCPF", "contatoCliente", "emailCliente", "telefone2",
    "cep", "rua", "numero", "complemento", "bairro", "cidade", "estado",
]
_SELECT = f"SELECT idCliente, {', '.join(_CAMPOS)} FROM clientes"


def _valores(cliente: Cliente) -> list:
    return [getattr(cliente, f"_{c}") for c in _CAMPOS]


def _linha_para_cliente(linha) -> Cliente:
    c = Cliente()
    c._idCliente = linha[0]
    for campo, valor in zip(_CAMPOS, linha[1:]):
        setattr(c, f"_{campo}", valor)
    return c


class ClienteDAO:

    def inserir(self, cliente: Cliente) -> bool:
        id_gerado = inserir(
            f"INSERT INTO clientes ({', '.join(_CAMPOS)}) VALUES ({', '.join(['%s'] * len(_CAMPOS))})",
            _valores(cliente), erro="Erro ao inserir cliente:")
        if id_gerado is None:
            return False
        cliente._idCliente = id_gerado
        return True

    def buscar_todos(self) -> list:
        return [_linha_para_cliente(l) for l in consultar(_SELECT, erro="Erro ao buscar clientes:")]

    def buscar_por_id(self, id_cliente: int):
        linha = consultar_um(f"{_SELECT} WHERE idCliente = %s", (id_cliente,),
                             erro="Erro ao buscar cliente por ID:")
        return _linha_para_cliente(linha) if linha else None

    def buscar_nomes_por_ids(self, ids_clientes: list) -> dict:
        """Só os nomes, no formato {idCliente: nomeCliente}. A listagem de obras
        usa isto para mostrar o cliente sem depender da lista completa, que nem
        todo cargo pode acessar."""
        ids = [i for i in dict.fromkeys(ids_clientes or []) if i]
        if not ids:
            return {}
        marcadores = ", ".join(["%s"] * len(ids))
        linhas = consultar(
            f"SELECT idCliente, nomeCliente FROM clientes WHERE idCliente IN ({marcadores})",
            tuple(ids), erro="Erro ao buscar nomes de clientes:")
        return dict(linhas)

    def existe_documento(self, digitos: str, excluir_id: int = None) -> bool:
        """True se outro cliente já usa este CPF/CNPJ (comparado só pelos
        dígitos, para '123.456.789-00' e '12345678900' contarem como iguais)."""
        sql = "SELECT 1 FROM clientes WHERE REGEXP_REPLACE(CNPJCPF, '[^0-9]', '') = %s"
        params = [digitos]
        if excluir_id:
            sql += " AND idCliente <> %s"
            params.append(excluir_id)
        return consultar_um(sql, params, erro="Erro ao verificar CPF/CNPJ:") is not None

    def atualizar(self, cliente: Cliente) -> bool:
        sets = ", ".join(f"{c} = %s" for c in _CAMPOS)
        return executar(f"UPDATE clientes SET {sets} WHERE idCliente = %s",
                        _valores(cliente) + [cliente._idCliente], erro="Erro ao atualizar cliente:")

    def deletar(self, id_cliente: int) -> bool:
        return executar("DELETE FROM clientes WHERE idCliente = %s", (id_cliente,),
                        erro="Erro ao deletar cliente:")
