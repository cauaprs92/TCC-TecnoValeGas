import subprocess
import sys
import mysql.connector
from mysql.connector import errorcode

# --------- Passo 1: Instalar bibliotecas ---------
def install_packages():
    packages = ["flask", "mysql-connector-python", "pyjwt", "flask-cors", "bcrypt"]
    for pkg in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# --------- Passo 2: Criar banco de dados a partir do arquivo SQL ---------
def setup_database(host="127.0.0.1", user="root", password="", database="tcc", port=3306, sql_file="./docs/codigo.sql"):
    try:
        cnx = mysql.connector.connect(host=host, user=user, password=password, port=port)
        cursor = cnx.cursor()

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Remove linhas de comentário ## que não são SQL válido
        linhas_validas = []
        for linha in sql_script.splitlines():
            stripped = linha.strip()
            if stripped.startswith('##'):
                continue
            linhas_validas.append(linha)
        sql_script = '\n'.join(linhas_validas)

        commands = sql_script.split(';')

        for command in commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                except mysql.connector.Error as err:
                    print(f"Aviso ao executar comando: {err}")

        cnx.commit()
        print(f"Banco de dados '{database}' configurado com sucesso!")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erro: usuário ou senha do MySQL incorretos.")
        else:
            print(f"Erro MySQL: {err}")
    finally:
        try:
            cursor.close()
            cnx.close()
        except:
            pass

# --------- Execução ---------
if __name__ == "__main__":
    print("=" * 45)
    print("  TecnoValeGAS — Instalação do Sistema")
    print("=" * 45)

    print("\n[1/2] Instalando dependências Python...")
    install_packages()

    print("\n[2/2] Configurando banco de dados...")
    # Se o seu MySQL tiver senha, coloque em password=""
    setup_database(password="")

    print("\nInstalação concluída!")
    print("Execute 'python app.py' para iniciar o servidor.")
    print("Acesse: http://localhost:5000")
    print("\nCredenciais padrão:")
    print("  E-mail: adm123@gmail.com")
    print("  Senha:  adm123")
