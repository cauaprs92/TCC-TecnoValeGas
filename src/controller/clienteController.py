import re
from src.dao.clienteDAO import ClienteDAO
from src.modelo.cliente import Cliente

class ClienteController:
    
    def __init__(self):
        self.dao = ClienteDAO()

    def _validar_cpf_cnpj(self, valor: str) -> bool: #funcao para validacao de cnpj ou cpf
        apenas_numeros = re.sub(r'\D', '', valor) #re.sub - funcao da biblioteca que remove tudo que não é número (pontos, traços, barras) 
        return len(apenas_numeros) == 11 or len(apenas_numeros) == 14

    def numeroNoNome(self, nome: str) -> bool: #funcao para verificar se tem numero no nome
        return bool(re.search(r'\d', nome)) # retorna True se encontrar numero no nome

    def _validar_nome(self, nome: str) -> tuple:
        if not nome.strip(): #le tudo e remove os espaços
            return False, "Nome do cliente nao pode ser vazio."
        if len(nome.strip()) < 3: 
            return False, "Nome deve ter pelo menos 3 caracteres."
        if self.numeroNoNome(nome):
            return False, "Nome do cliente nao pode conter numeros."
        return True, ""

    def cadastrar(self, idCliente, nomeCliente, CNPJCPF, enderecoCliente, contatoCliente) -> tuple:
        valido, mensagem = self._validar_nome(nomeCliente)  # valida o nome e retorna se é valido e a mensagem de erro
        if not valido:
            return False, mensagem  # interrompe e devolve o erro se o nome for invalido

        if not self._validar_cpf_cnpj(CNPJCPF):
            return False, "CPF deve ter 11 digitos ou CNPJ deve ter 14 digitos."

        if not enderecoCliente.strip(): #se o endereço nao tiver nenhuma caracter ele retorna falso 
            return False, "Endereco nao pode ser vazio."

        clienteExistente = self.dao.buscar_por_id(int(idCliente)) #se o cliente existe, ent ja busca por id
        if clienteExistente:
            return False, f"Ja existe um cliente com o ID {idCliente}."

        dadosCliente = Cliente()
        dadosCliente._idCliente       = int(idCliente)
        dadosCliente._nomeCliente     = nomeCliente.strip()
        dadosCliente._CNPJCPF         = CNPJCPF.strip()
        dadosCliente._enderecoCliente = enderecoCliente.strip()
        dadosCliente._contatoCliente  = contatoCliente.strip()

        sucesso = self.dao.inserir(dadosCliente)
        if sucesso:
            return True, "Cliente cadastrado com sucesso!"
        return False, "Erro ao cadastrar cliente."

    def listar(self) -> list:
        return self.dao.buscar_todos()

    def buscar_por_id(self, idCliente: int):
        return self.dao.buscar_por_id(idCliente)

    def editar(self, idCliente, nomeCliente, CNPJCPF, enderecoCliente, contatoCliente) -> tuple:
        valido, mensagem = self._validar_nome(nomeCliente)
        if not valido:
            return False, mensagem

        if not self._validar_cpf_cnpj(CNPJCPF):
            return False, "CPF deve ter 11 digitos ou CNPJ deve ter 14 digitos."

        if not enderecoCliente.strip():
            return False, "Endereco nao pode ser vazio."

        dadosCliente = Cliente()
        dadosCliente._idCliente       = int(idCliente)
        dadosCliente._nomeCliente     = nomeCliente.strip()
        dadosCliente._CNPJCPF         = CNPJCPF.strip()
        dadosCliente._enderecoCliente = enderecoCliente.strip()
        dadosCliente._contatoCliente  = contatoCliente.strip()

        sucesso = self.dao.atualizar(dadosCliente)
        if sucesso:
            return True, "Cliente atualizado com sucesso!"
        return False, "Erro ao atualizar cliente."

    def deletar(self, idCliente: int) -> tuple:
        clienteExistente = self.dao.buscar_por_id(idCliente)
        if not clienteExistente:
            return False, "Cliente nao encontrado."

        sucesso = self.dao.deletar(idCliente)
        if sucesso:
            return True, "Cliente deletado com sucesso!"
        return False, "Erro ao deletar cliente."