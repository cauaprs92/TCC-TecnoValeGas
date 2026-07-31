import re
import bcrypt
from src.dao.adminDAO import AdminDAO

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class AdminController:

    # Valores gravados sem acento; o front exibe os rótulos acentuados.
    CARGO_ADMIN    = "Administracao"
    CARGO_OBRA     = "Obra"
    CARGOS_VALIDOS = [CARGO_ADMIN, "Almoxarifado", CARGO_OBRA]

    def __init__(self):
        self.dao = AdminDAO()

    def _validar_campos(self, email: str, nome: str, cargo: str, senha: str = None) -> tuple:
        if not nome or not nome.strip():
            return False, "Nome é obrigatório."
        if len(nome.strip()) < 2:
            return False, "Nome deve ter ao menos 2 caracteres."
        if not email or not email.strip():
            return False, "Email é obrigatório."
        if not EMAIL_REGEX.match(email.strip()):
            return False, "Email inválido."
        if cargo not in self.CARGOS_VALIDOS:
            opcoes = ", ".join(self.CARGOS_VALIDOS)
            return False, f"Cargo inválido. Use: {opcoes}."
        if senha is not None:
            if len(senha) < 6:
                return False, "Senha deve ter ao menos 6 caracteres."
        return True, ""

    def listar(self) -> list:
        rows = self.dao.listar()
        return [{"idLogin": r[0], "email": r[1], "nomeLogin": r[2], "cargoLogin": r[3]} for r in rows]

    def listar_por_cargo(self, cargo: str) -> list:
        return [u for u in self.listar() if u["cargoLogin"] == cargo]

    def criar(self, email: str, senha: str, nome: str, cargo: str) -> tuple:
        valido, msg = self._validar_campos(email, nome, cargo, senha)
        if not valido:
            return False, msg

        if self.dao.buscar_por_email(email.strip()):
            return False, "Já existe um usuário com esse email."

        hash_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        sucesso = self.dao.criar(email.strip(), hash_senha, nome.strip(), cargo)
        if sucesso:
            return True, f"Usuário '{nome.strip()}' criado com sucesso!"
        return False, "Erro ao criar usuário."

    def atualizar(self, id_login: int, email: str, nome: str, cargo: str,
                  nova_senha: str = None, senha_atual: str = None) -> tuple:
        existente = self.dao.buscar_por_id(id_login)
        if not existente:
            return False, "Usuário não encontrado."

        # Verificação de senha atual obrigatória para edição de perfil próprio
        if senha_atual is not None:
            hash_salvo = self.dao.buscar_hash_senha(id_login)
            if not hash_salvo:
                return False, "Erro ao verificar credenciais."
            hash_bytes = hash_salvo.encode("utf-8") if isinstance(hash_salvo, str) else hash_salvo
            if not bcrypt.checkpw(senha_atual.encode("utf-8"), hash_bytes):
                return False, "Senha atual incorreta."

        valido, msg = self._validar_campos(email, nome, cargo, nova_senha)
        if not valido:
            return False, msg

        if self.dao.buscar_por_email(email.strip(), excluir_id=id_login):
            return False, "Já existe outro usuário com esse email."

        # Rebaixar o último usuário de Administração deixaria o sistema sem
        # ninguém capaz de gerenciar usuários, obras e clientes.
        cargo_atual = existente[3]
        if cargo_atual == self.CARGO_ADMIN and cargo != self.CARGO_ADMIN:
            if self.dao.contar_por_cargo(self.CARGO_ADMIN) <= 1:
                return False, "Não é possível trocar o cargo do único usuário de Administração."

        hash_senha = None
        if nova_senha:
            hash_senha = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

        sucesso = self.dao.atualizar(id_login, email.strip(), nome.strip(), cargo, hash_senha)
        if sucesso:
            return True, "Usuário atualizado com sucesso!"
        return False, "Erro ao atualizar usuário."

    def deletar(self, id_login: int) -> tuple:
        existente = self.dao.buscar_por_id(id_login)
        if not existente:
            return False, "Usuário não encontrado."

        if self.dao.contar() <= 1:
            return False, "Não é possível excluir o único usuário do sistema."

        if existente[3] == self.CARGO_ADMIN and self.dao.contar_por_cargo(self.CARGO_ADMIN) <= 1:
            return False, "Não é possível excluir o único usuário de Administração."

        sucesso = self.dao.deletar(id_login)
        if sucesso:
            return True, "Usuário removido com sucesso!"
        return False, "Erro ao remover usuário."
