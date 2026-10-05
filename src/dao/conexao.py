import os
import sys
import traceback
import mysql.connector

class Conexao:
    _host     = os.environ.get("DB_HOST", "localhost")
    _porta    = int(os.environ.get("DB_PORT", 3306))
    _usuario  = os.environ.get("DB_USER", "root")
    _senha    = os.environ.get("DB_PASSWORD", "")
    _banco    = os.environ.get("DB_NAME", "tcc")

    @staticmethod
    def obter_conexao():
        try:
            return mysql.connector.connect(
                host=Conexao._host, 
                port=Conexao._porta,
                user=Conexao._usuario, 
                password=Conexao._senha,
                database=Conexao._banco,
                ssl_disabled=True,  
                connection_timeout=10
            )
        except Exception as e:
            print(f"Erro ao conectar ao MySQL: {e}", flush=True)
            traceback.print_exc()
            sys.stdout.flush()
            return None

    @staticmethod
    def fechar_conexao(conexao, cursor=None):
        try:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()
        except Exception as e:
            print(f"Erro ao fechar conexão: {e}", flush=True)
