"""Importa o schema e os dados de exemplo no MySQL do Aiven.

Uso (na pasta do projeto, onde estão as pastas docs/ e src/):
    python docs/importar_aiven.py

A senha é pedida no terminal e não fica gravada em nenhum arquivo.
"""
import getpass
import os
import sys

import mysql.connector

HOST = os.environ.get("DB_HOST", "banco-tecnovale-tcc-tecnovaleagas.j.aivencloud.com")
PORTA = int(os.environ.get("DB_PORT", 19796))
USUARIO = os.environ.get("DB_USER", "avnadmin")
BANCO = os.environ.get("DB_NAME", "defaultdb")

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVOS = ["codigo-aiven.sql", "inserts-aiven.sql"]


def dividir(sql):
    """Separa o script em comandos, respeitando aspas e comentários."""
    comandos, buf, i, n, aspas = [], [], 0, len(sql), None
    while i < n:
        c = sql[i]
        if aspas:
            buf.append(c)
            if c == "\\" and aspas != "`" and i + 1 < n:
                buf.append(sql[i + 1])
                i += 2
                continue
            if c == aspas:
                if i + 1 < n and sql[i + 1] == aspas:
                    buf.append(sql[i + 1])
                    i += 2
                    continue
                aspas = None
            i += 1
            continue
        if c in "'\"`":
            aspas = c
            buf.append(c)
            i += 1
            continue
        if c == "#" or (sql.startswith("--", i) and (i + 2 >= n or sql[i + 2] in " \t\r\n")):
            fim = sql.find("\n", i)
            i = n if fim == -1 else fim
            continue
        if sql.startswith("/*", i):
            fim = sql.find("*/", i + 2)
            i = n if fim == -1 else fim + 2
            continue
        if c == ";":
            cmd = "".join(buf).strip()
            if cmd:
                comandos.append(cmd)
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    resto = "".join(buf).strip()
    if resto:
        comandos.append(resto)
    return comandos


def main():
    senha = getpass.getpass(f"Senha do usuário {USUARIO} no Aiven (não aparece ao digitar): ")
    try:
        cnx = mysql.connector.connect(host=HOST, port=PORTA, user=USUARIO, password=senha,
                                      database=BANCO, connection_timeout=20)
    except Exception as e:
        print(f"\nNão consegui conectar: {e}")
        sys.exit(1)

    cur = cnx.cursor()
    cur.execute("SHOW TABLES LIKE 'login'")
    if cur.fetchone():
        print("\nO banco já tem a tabela 'login'. Nada foi alterado, para não duplicar dados.")
        sys.exit(0)

    for nome in ARQUIVOS:
        caminho = os.path.join(PASTA, nome)
        with open(caminho, encoding="utf-8") as f:
            comandos = dividir(f.read())
        print(f"\n{nome}: {len(comandos)} comandos")
        for n, cmd in enumerate(comandos, 1):
            try:
                cur.execute(cmd)
            except mysql.connector.Error as e:
                print(f"\nERRO no comando {n} de {nome}:\n{e}\n\nTrecho: {cmd[:200]}")
                cnx.rollback()
                sys.exit(1)
        cnx.commit()
        print("  ok")

    cur.execute("SELECT COUNT(*) FROM login")
    print(f"\nPronto! Usuários na tabela login: {cur.fetchone()[0]}")
    cur.close()
    cnx.close()


if __name__ == "__main__":
    main()
