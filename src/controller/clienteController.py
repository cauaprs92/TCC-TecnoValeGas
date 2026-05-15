import re
from src.dao.clienteDAO import ClienteDAO
from src.modelo.cliente import Cliente

class ClienteController:

    def __init__(self):
        self.dao = ClienteDAO()

    def _validar_cpf_cnpj(self, valor: str) -> bool:
        apenas_numeros = re.sub(r'\D', '', valor)
        return len(apenas_numeros) == 11 or len(apenas_numeros) == 14

    def _validar_nome(self, nome: str) -> tuple:
        if not nome.strip():
            return False, "Nome do cliente não pode ser vazio."
        if len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."
        if re.search(r'\d', nome):
            return False, "Nome do cliente não pode conter números."
        return True, ""

    def cadastrar(self, nomeCliente, CNPJCPF, contatoCliente,
                  emailCliente, telefone2,
                  cep, rua, numero, complemento, bairro, cidade, estado) -> tuple:
        valido, mensagem = self._validar_nome(nomeCliente)
        if not valido:
            return False, mensagem

        if not self._validar_cpf_cnpj(CNPJCPF):
            return False, "CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos."

        if not rua or not rua.strip():
            return False, "Rua é obrigatória."
        if not numero or not str(numero).strip():
            return False, "Número é obrigatório."
        if not cidade or not cidade.strip():
            return False, "Cidade é obrigatória."
        if not estado or not estado.strip():
            return False, "Estado é obrigatório."

        idCliente = self.dao.proximo_id()

        dadosCliente = Cliente()
        dadosCliente._idCliente      = idCliente
        dadosCliente._nomeCliente    = nomeCliente.strip()
        dadosCliente._CNPJCPF        = CNPJCPF.strip()
        dadosCliente._contatoCliente = contatoCliente.strip() if contatoCliente else ""
        dadosCliente._emailCliente   = emailCliente.strip() if emailCliente else None
        dadosCliente._telefone2      = telefone2.strip() if telefone2 else None
        dadosCliente._cep            = cep.strip() if cep else ""
        dadosCliente._rua            = rua.strip()
        dadosCliente._numero         = str(numero).strip()
        dadosCliente._complemento    = complemento.strip() if complemento else ""
        dadosCliente._bairro         = bairro.strip() if bairro else ""
        dadosCliente._cidade         = cidade.strip()
        dadosCliente._estado         = estado.strip().upper()

        sucesso = self.dao.inserir(dadosCliente)
        if sucesso:
            return True, "Cliente cadastrado com sucesso!"
        return False, "Erro ao cadastrar cliente."

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idCliente: int):
        return self.dao.buscar_por_id(idCliente)

    def editar(self, idCliente, nomeCliente, CNPJCPF, contatoCliente,
               emailCliente, telefone2,
               cep, rua, numero, complemento, bairro, cidade, estado) -> tuple:
        valido, mensagem = self._validar_nome(nomeCliente)
        if not valido:
            return False, mensagem

        if not self._validar_cpf_cnpj(CNPJCPF):
            return False, "CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos."

        if not rua or not rua.strip():
            return False, "Rua é obrigatória."
        if not numero or not str(numero).strip():
            return False, "Número é obrigatório."
        if not cidade or not cidade.strip():
            return False, "Cidade é obrigatória."
        if not estado or not estado.strip():
            return False, "Estado é obrigatório."

        dadosCliente = Cliente()
        dadosCliente._idCliente      = int(idCliente)
        dadosCliente._nomeCliente    = nomeCliente.strip()
        dadosCliente._CNPJCPF        = CNPJCPF.strip()
        dadosCliente._contatoCliente = contatoCliente.strip() if contatoCliente else ""
        dadosCliente._emailCliente   = emailCliente.strip() if emailCliente else None
        dadosCliente._telefone2      = telefone2.strip() if telefone2 else None
        dadosCliente._cep            = cep.strip() if cep else ""
        dadosCliente._rua            = rua.strip()
        dadosCliente._numero         = str(numero).strip()
        dadosCliente._complemento    = complemento.strip() if complemento else ""
        dadosCliente._bairro         = bairro.strip() if bairro else ""
        dadosCliente._cidade         = cidade.strip()
        dadosCliente._estado         = estado.strip().upper()

        sucesso = self.dao.atualizar(dadosCliente)
        if sucesso:
            return True, "Cliente atualizado com sucesso!"
        return False, "Erro ao atualizar cliente."

    def deletar(self, idCliente: int) -> tuple:
        clienteExistente = self.dao.buscar_por_id(idCliente)
        if not clienteExistente:
            return False, "Cliente não encontrado."

        sucesso = self.dao.deletar(idCliente)
        if sucesso:
            return True, "Cliente deletado com sucesso!"
        return False, "Erro ao deletar cliente."
