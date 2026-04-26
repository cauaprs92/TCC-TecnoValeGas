import mysql.connector
from mysql.connector import Error

class Conexao:
    _host     = "localhost"
    _usuario  = "root"
    _senha    = ""  #nois nao tem    
    _banco    = "tcc"

    @staticmethod
    def obter_conexao():
        try:
            conexao = mysql.connector.connect(
                host     = Conexao._host,
                user     = Conexao._usuario,
                password = Conexao._senha,
                database = Conexao._banco
            )
            if conexao.is_connected():
                return conexao
        except Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            return None

    @staticmethod
    def fechar_conexao(conexao, cursor=None):
        try:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()
        except Error as e:
            print(f"Erro ao fechar conexão: {e}")
