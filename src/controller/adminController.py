import re
import bcrypt
from src.dao.adminDAO import AdminDAO

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


class AdminController:

    def __init__(self):
        self.dao = AdminDAO()

    def _validar_campos(self, email: str, nome: str, senha: str = None) -> tuple:
        if not nome or not nome.strip():
            return False, "Nome é obrigatório."
        if len(nome.strip()) < 2:
            return False, "Nome deve ter ao menos 2 caracteres."
        if not email or not email.strip():
            return False, "Email é obrigatório."
        if not EMAIL_REGEX.match(email.strip()):
            return False, "Email inválido."
        if senha is not None:
            if len(senha) < 6:
                return False, "Senha deve ter ao menos 6 caracteres."
        return True, ""

    def listar(self) -> list:
        rows = self.dao.listar()
        return [{"idLogin": r[0], "email": r[1], "nomeLogin": r[2]} for r in rows]

    def criar(self, email: str, senha: str, nome: str) -> tuple:
        valido, msg = self._validar_campos(email, nome, senha)
        if not valido:
            return False, msg

        if self.dao.buscar_por_email(email.strip()):
            return False, "Já existe um administrador com esse email."

        hash_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")
        sucesso = self.dao.criar(email.strip(), hash_senha, nome.strip())
        if sucesso:
            return True, f"Administrador '{nome.strip()}' criado com sucesso!"
        return False, "Erro ao criar administrador."

    def atualizar(self, id_login: int, email: str, nome: str, nova_senha: str = None) -> tuple:
        if not self.dao.buscar_por_id(id_login):
            return False, "Administrador não encontrado."

        valido, msg = self._validar_campos(email, nome, nova_senha)
        if not valido:
            return False, msg

        if self.dao.buscar_por_email(email.strip(), excluir_id=id_login):
            return False, "Já existe outro administrador com esse email."

        hash_senha = None
        if nova_senha:
            hash_senha = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

        sucesso = self.dao.atualizar(id_login, email.strip(), nome.strip(), hash_senha)
        if sucesso:
            return True, "Administrador atualizado com sucesso!"
        return False, "Erro ao atualizar administrador."

    def deletar(self, id_login: int) -> tuple:
        if not self.dao.buscar_por_id(id_login):
            return False, "Administrador não encontrado."

        if self.dao.contar() <= 1:
            return False, "Não é possível excluir o único administrador do sistema."

        sucesso = self.dao.deletar(id_login)
        if sucesso:
            return True, "Administrador removido com sucesso!"
        return False, "Erro ao remover administrador."
