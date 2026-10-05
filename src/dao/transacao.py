from contextlib import contextmanager
from src.dao.conexao import Conexao


class OperacaoInvalida(Exception):
    """Regra de negócio violada dentro de uma transação. A mensagem é mostrada
    ao usuário e a transação é desfeita."""


@contextmanager
def transacao():
    """Cursor de uma transação: commit ao sair do bloco sem erro, rollback se
    qualquer exceção escapar dele."""
    conexao = Conexao.obter_conexao()
    if not conexao:
        raise ConnectionError("Não foi possível conectar ao banco de dados.")
    cursor = conexao.cursor()
    try:
        yield cursor
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        Conexao.fechar_conexao(conexao, cursor)


def executar_transacao(operacao, erro_generico: str) -> tuple:
    """Roda operacao(cursor) numa transação e devolve (sucesso, resultado).

    OperacaoInvalida vira (False, mensagem da regra); qualquer outro erro é
    logado e vira (False, erro_generico), sem expor detalhes do banco."""
    try:
        with transacao() as cursor:
            resultado = operacao(cursor)
        return True, resultado
    except OperacaoInvalida as e:
        return False, str(e)
    except Exception as e:
        print(f"{erro_generico} {e}", flush=True)
        return False, erro_generico
