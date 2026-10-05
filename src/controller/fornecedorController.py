import re
from src.dao.fornecedorDAO import FornecedorDAO


class FornecedorController:

    def __init__(self):
        self.dao = FornecedorDAO()

    def listar(self) -> list:
        return [
            {"idFornecedor": r[0], "nomeFornecedor": r[1], "prazoEntregaDias": r[2],
             "qtdProdutos": r[3], "cnpjFornecedor": r[4]}
            for r in self.dao.listar()
        ]

    def _validar_prazo(self, prazo) -> tuple:
        try:
            prazo = int(prazo)
        except (ValueError, TypeError):
            return False, "Prazo de entrega deve ser um número inteiro de dias.", None
        if prazo <= 0 or prazo > 365:
            return False, "Prazo de entrega deve estar entre 1 e 365 dias.", None
        return True, "", prazo

    def criar(self, nome, cnpj, prazo) -> tuple:
        """Retorna (sucesso, mensagem, idFornecedor)."""
        nome = (nome or "").strip()
        if len(nome) < 2:
            return False, "Informe o nome do fornecedor (ao menos 2 caracteres).", None
        if len(nome) > 150:
            return False, "Nome do fornecedor muito longo (máximo 150 caracteres).", None

        # Gravado só com dígitos: é o formato que a importação de NF-e procura,
        # assim a nota reconhece o fornecedor cadastrado aqui.
        cnpj = re.sub(r"\D", "", cnpj or "") or None
        if cnpj and len(cnpj) != 14:
            return False, "CNPJ deve ter 14 dígitos.", None

        valido, mensagem, prazo = self._validar_prazo(7 if prazo in (None, "") else prazo)
        if not valido:
            return False, mensagem, None

        duplicado = self.dao.existe(nome, cnpj)
        if duplicado == "nome":
            return False, "Já existe um fornecedor com esse nome.", None
        if duplicado == "cnpj":
            return False, "Já existe um fornecedor com esse CNPJ.", None

        id_fornecedor = self.dao.criar(nome, cnpj, prazo)
        if not id_fornecedor:
            return False, "Erro ao cadastrar fornecedor.", None
        return True, f"Fornecedor '{nome}' cadastrado!", id_fornecedor

    def atualizar_prazo(self, id_fornecedor: int, prazo) -> tuple:
        """O prazo de entrega entra no cálculo do estoque mínimo de todos os
        produtos do fornecedor que não têm prazo próprio."""
        fornecedor = self.dao.buscar_por_id(id_fornecedor)
        if not fornecedor:
            return False, "Fornecedor não encontrado.", None
        valido, mensagem, prazo = self._validar_prazo(prazo)
        if not valido:
            return False, mensagem, None
        if not self.dao.atualizar_prazo(id_fornecedor, prazo):
            return False, "Erro ao atualizar o prazo do fornecedor.", None
        return True, "Prazo de entrega atualizado!", fornecedor[1]

    def obter_ou_criar_id(self, nome: str):
        """Resolve o nome de um fornecedor para seu ID, criando-o se ainda não existir.
        Retorna None se nenhum nome for informado (fornecedor é opcional)."""
        if not nome or not nome.strip():
            return None
        return self.dao.obter_ou_criar(nome.strip())
