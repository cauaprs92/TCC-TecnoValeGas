"""Acesso ao banco usado pelos DAOs.

Cada função abre a conexão, executa e fecha. Erro de banco é logado e vira o
valor "vazio" do tipo de retorno ([], None ou False) — o DAO não precisa
repetir o try/except/finally em cada método.
"""
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


def consultar(sql: str, params=(), erro: str = "Erro na consulta.") -> list:
    """Todas as linhas do SELECT, ou [] em caso de erro."""
    conexao = Conexao.obter_conexao()
    if not conexao:
        return []
    cursor = conexao.cursor()
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"{erro} {e}", flush=True)
        return []
    finally:
        Conexao.fechar_conexao(conexao, cursor)


def consultar_um(sql: str, params=(), erro: str = "Erro na consulta."):
    """Primeira linha do SELECT, ou None se não houver ou em caso de erro."""
    linhas = consultar(sql, params, erro)
    return linhas[0] if linhas else None


def executar(sql: str, params=(), erro: str = "Erro ao gravar.") -> bool:
    """Executa uma escrita numa transação. True se deu certo."""
    sucesso, _ = executar_transacao(lambda cursor: cursor.execute(sql, params), erro)
    return sucesso


def inserir(sql: str, params=(), erro: str = "Erro ao inserir."):
    """Executa um INSERT e devolve o id gerado, ou None em caso de erro."""
    def operacao(cursor):
        cursor.execute(sql, params)
        return cursor.lastrowid
    sucesso, resultado = executar_transacao(operacao, erro)
    return resultado if sucesso else None
