import re
import unicodedata
from difflib import SequenceMatcher

from src.dao.conexao import Conexao
from src.modelo.notaFiscal import NotaFiscal, NotaFiscalItem

# similaridade mínima para sugerir um produto já cadastrado na tela de conferência
_LIMIAR_SUGESTAO = 0.55


def _normalizar(texto: str) -> str:
    """Deixa o nome comparável: sem acento, minúsculo e sem espaços repetidos."""
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _similaridade(nomeNota: str, nomeProduto: str) -> float:
    a, b = _normalizar(nomeNota), _normalizar(nomeProduto)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    # um nome contido no outro (ex.: "TUBO PPR 25MM" x "Tubo PPR 25mm Azul")
    if a in b or b in a:
        return 0.9
    return SequenceMatcher(None, a, b).ratio()


class NotaFiscalDAO:

    # ─── Importação ───────────────────────────────────────────────────────────

    def buscar_id_por_chave(self, chaveAcesso: str):
        """Retorna o idNotaFiscal de uma chave já importada, ou None."""
        sql = "SELECT idNotaFiscal FROM notasFiscais WHERE chaveAcesso = %s"
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (chaveAcesso,))
            linha = cursor.fetchone()
            return linha[0] if linha else None
        except Exception as e:
            print(f"Erro ao verificar chave da nota fiscal: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def verificar_chave_existe(self, chaveAcesso: str) -> bool:
        """True se a chave de acesso já foi importada anteriormente."""
        return self.buscar_id_por_chave(chaveAcesso) is not None

    def reabrir_itens(self, idNotaFiscal: int) -> int:
        """Devolve para 'pendente' os itens da nota que não afetam mais o estoque.

        Um item sem idProduto ou é ignorado, ou teve o produto excluído depois
        (a exclusão desfaz o vínculo) — nos dois casos ele pode ser conferido de
        novo. Itens que ainda apontam para um produto vivo continuam confirmados,
        para que a mesma nota não some estoque duas vezes.

        Retorna quantos itens voltaram para a conferência.
        """
        sql = """
            UPDATE notaFiscalItens
            SET statusItem = 'pendente'
            WHERE idNotaFiscal = %s AND statusItem <> 'pendente' AND idProduto IS NULL
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return 0
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idNotaFiscal,))
            conexao.commit()
            return cursor.rowcount
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao reabrir itens da nota fiscal: {e}")
            return 0
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def _obter_ou_criar_fornecedor(self, cursor, nome: str, cnpj: str):
        """Resolve o fornecedor da nota pelo CNPJ do <emit>, criando-o se necessário.

        Reaproveita o cadastro existente quando o CNPJ já é conhecido; quando o
        fornecedor só existia pelo nome (cadastro manual antigo), grava o CNPJ nele.
        Usa o cursor da transação em andamento — não abre conexão própria.
        """
        nome = (nome or "").strip()
        cnpj = (cnpj or "").strip()

        if cnpj:
            cursor.execute(
                "SELECT idFornecedor FROM fornecedores WHERE cnpjFornecedor = %s", (cnpj,)
            )
            linha = cursor.fetchone()
            if linha:
                return linha[0]

        if nome:
            cursor.execute(
                "SELECT idFornecedor, cnpjFornecedor FROM fornecedores WHERE LOWER(nomeFornecedor) = LOWER(%s)",
                (nome,),
            )
            linha = cursor.fetchone()
            if linha:
                if cnpj and not linha[1]:
                    cursor.execute(
                        "UPDATE fornecedores SET cnpjFornecedor = %s WHERE idFornecedor = %s",
                        (cnpj, linha[0]),
                    )
                return linha[0]

        cursor.execute(
            "INSERT INTO fornecedores (nomeFornecedor, cnpjFornecedor) VALUES (%s, %s)",
            (nome or f"Fornecedor {cnpj}", cnpj or None),
        )
        return cursor.lastrowid

    def inserir_nota(self, dadosNota: dict):
        """Insere a nota (com upsert do fornecedor) e devolve o idNotaFiscal."""
        sql = """
            INSERT INTO notasFiscais
                (chaveAcesso, numero, serie, idFornecedor, dataEmissao, valorTotal, nomeArquivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            idFornecedor = self._obter_ou_criar_fornecedor(
                cursor, dadosNota.get("fornecedorNome"), dadosNota.get("fornecedorCNPJ")
            )
            cursor.execute(sql, (
                dadosNota.get("chaveAcesso"),
                dadosNota.get("numero"),
                dadosNota.get("serie"),
                idFornecedor,
                dadosNota.get("dataEmissao"),
                dadosNota.get("valorTotal"),
                dadosNota.get("nomeArquivo"),
            ))
            idNotaFiscal = cursor.lastrowid
            conexao.commit()
            return idNotaFiscal
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir nota fiscal: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    def inserir_itens(self, idNotaFiscal: int, itens: list) -> bool:
        """Insere os itens da nota como pendentes, ainda sem produto vinculado."""
        sql = """
            INSERT INTO notaFiscalItens
                (idNotaFiscal, idProduto, codProdutoFornecedor, nomeProdutoNota,
                 quantidade, valorUnitario, valorTotal, statusItem)
            VALUES (%s, NULL, %s, %s, %s, %s, %s, 'pendente')
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False
        cursor = conexao.cursor()
        try:
            for item in itens:
                cursor.execute(sql, (
                    idNotaFiscal,
                    item.get("codProdutoFornecedor"),
                    item.get("nomeProdutoNota"),
                    item.get("quantidade"),
                    item.get("valorUnitario"),
                    item.get("valorTotal"),
                ))
            conexao.commit()
            return True
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao inserir itens da nota fiscal: {e}")
            return False
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # ─── Consulta ─────────────────────────────────────────────────────────────

    def buscar_nota_com_itens(self, idNotaFiscal: int):
        """Retorna a nota, seus itens e a sugestão de produto para cada item pendente."""
        sql_nota = """
            SELECT n.idNotaFiscal, n.chaveAcesso, n.numero, n.serie, n.idFornecedor,
                   n.dataEmissao, n.valorTotal, n.nomeArquivo, n.dataImportacao,
                   f.nomeFornecedor, f.cnpjFornecedor
            FROM notasFiscais n
            LEFT JOIN fornecedores f ON f.idFornecedor = n.idFornecedor
            WHERE n.idNotaFiscal = %s
        """
        sql_itens = """
            SELECT idItem, idNotaFiscal, idProduto, codProdutoFornecedor, nomeProdutoNota,
                   quantidade, valorUnitario, valorTotal, statusItem
            FROM notaFiscalItens
            WHERE idNotaFiscal = %s
            ORDER BY idItem
        """
        sql_produtos = "SELECT idProduto, nomeProduto, qtdProduto FROM produtos"

        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql_nota, (idNotaFiscal,))
            linha = cursor.fetchone()
            if not linha:
                return None
            nota = self._linha_para_nota(linha)

            cursor.execute(sql_itens, (idNotaFiscal,))
            itens = [self._linha_para_item(l) for l in cursor.fetchall()]

            cursor.execute(sql_produtos)
            produtos = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar nota fiscal com itens: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

        for item in itens:
            item._sugestao = self._sugerir_produto(item, produtos)
        nota._itens = itens
        return nota

    def _sugerir_produto(self, item: NotaFiscalItem, produtos: list):
        """Escolhe o produto cadastrado mais parecido com o nome que veio na nota."""
        if item._idProduto:
            for idProduto, nomeProduto, qtdProduto in produtos:
                if idProduto == item._idProduto:
                    return {"idProduto": idProduto, "nomeProduto": nomeProduto,
                            "qtdProduto": qtdProduto, "similaridade": 1.0}
            return None

        melhor, melhorScore = None, 0.0
        for idProduto, nomeProduto, qtdProduto in produtos:
            score = _similaridade(item._nomeProdutoNota, nomeProduto)
            if score > melhorScore:
                melhor, melhorScore = (idProduto, nomeProduto, qtdProduto), score

        if not melhor or melhorScore < _LIMIAR_SUGESTAO:
            return None
        return {"idProduto": melhor[0], "nomeProduto": melhor[1],
                "qtdProduto": melhor[2], "similaridade": round(melhorScore, 2)}

    def buscar_item_por_id(self, idItem: int):
        sql = """
            SELECT idItem, idNotaFiscal, idProduto, codProdutoFornecedor, nomeProdutoNota,
                   quantidade, valorUnitario, valorTotal, statusItem
            FROM notaFiscalItens
            WHERE idItem = %s
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return None
        cursor = conexao.cursor()
        try:
            cursor.execute(sql, (idItem,))
            linha = cursor.fetchone()
            return self._linha_para_item(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar item da nota fiscal: {e}")
            return None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # ─── Conferência ──────────────────────────────────────────────────────────

    def confirmar_item(self, idItem: int, acao: str, idProduto: int = None,
                       quantidadeMinima: int = None, quantidadeMaxima: int = None,
                       dadosNovoProduto: dict = None) -> tuple:
        """Aplica a decisão do usuário sobre um item da nota.

        acao='repor'   → soma a quantidade do item ao estoque do produto informado
        acao='criar'   → cadastra um produto novo com a quantidade do item como estoque
        acao='ignorar' → não mexe no estoque, apenas marca o item

        Retorna (sucesso, mensagem, idProduto).
        """
        conexao = Conexao.obter_conexao()
        if not conexao:
            return False, "Não foi possível conectar ao banco de dados.", None
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT i.idItem, i.idNotaFiscal, i.quantidade, i.nomeProdutoNota, i.statusItem,
                       n.idFornecedor
                FROM notaFiscalItens i
                JOIN notasFiscais n ON n.idNotaFiscal = i.idNotaFiscal
                WHERE i.idItem = %s
            """, (idItem,))
            linha = cursor.fetchone()
            if not linha:
                return False, "Item da nota fiscal não encontrado.", None

            if linha[4] != 'pendente':
                return False, "Este item já foi conferido anteriormente.", None

            quantidade   = int(round(float(linha[2] or 0)))
            idFornecedor = linha[5]

            if acao == 'ignorar':
                cursor.execute(
                    "UPDATE notaFiscalItens SET statusItem = 'ignorado' WHERE idItem = %s",
                    (idItem,)
                )
                conexao.commit()
                return True, "Item ignorado.", None

            if acao == 'repor':
                cursor.execute("SELECT idProduto FROM produtos WHERE idProduto = %s", (idProduto,))
                if not cursor.fetchone():
                    return False, f"Produto ID {idProduto} não encontrado.", None
                cursor.execute(
                    "UPDATE produtos SET qtdProduto = qtdProduto + %s WHERE idProduto = %s",
                    (quantidade, idProduto)
                )

            elif acao == 'criar':
                dados = dadosNovoProduto or {}
                cursor.execute("SELECT COALESCE(MAX(idProduto), 0) + 1 FROM produtos")
                idProduto = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO produtos
                        (idProduto, nomeProduto, qtdProduto, descProduto, qtdMinima, qtdMaxima, idFornecedor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    idProduto,
                    (dados.get("nomeProduto") or linha[3] or "").strip(),
                    quantidade,
                    (dados.get("descProduto") or "").strip(),
                    quantidadeMinima if quantidadeMinima is not None else 0,
                    quantidadeMaxima if quantidadeMaxima is not None else 9999,
                    idFornecedor,
                ))

            else:
                return False, f"Ação inválida: {acao}.", None

            cursor.execute(
                "UPDATE notaFiscalItens SET idProduto = %s, statusItem = 'confirmado' WHERE idItem = %s",
                (idProduto, idItem)
            )
            conexao.commit()
            return True, "Item confirmado com sucesso!", idProduto
        except Exception as e:
            conexao.rollback()
            print(f"Erro ao confirmar item da nota fiscal: {e}")
            return False, "Erro ao confirmar item da nota fiscal.", None
        finally:
            Conexao.fechar_conexao(conexao, cursor)

    # ─── Conversão ────────────────────────────────────────────────────────────

    def _linha_para_nota(self, linha) -> NotaFiscal:
        n = NotaFiscal()
        n._idNotaFiscal   = linha[0]
        n._chaveAcesso    = linha[1]
        n._numero         = linha[2]
        n._serie          = linha[3]
        n._idFornecedor   = linha[4]
        n._dataEmissao    = linha[5]
        n._valorTotal     = float(linha[6]) if linha[6] is not None else 0.0
        n._nomeArquivo    = linha[7]
        n._dataImportacao = linha[8]
        n._nomeFornecedor = linha[9]
        n._cnpjFornecedor = linha[10]
        n._itens          = []
        return n

    def _linha_para_item(self, linha) -> NotaFiscalItem:
        i = NotaFiscalItem()
        i._idItem               = linha[0]
        i._idNotaFiscal         = linha[1]
        i._idProduto            = linha[2]
        i._codProdutoFornecedor = linha[3]
        i._nomeProdutoNota      = linha[4]
        i._quantidade           = float(linha[5]) if linha[5] is not None else 0.0
        i._valorUnitario        = float(linha[6]) if linha[6] is not None else 0.0
        i._valorTotal           = float(linha[7]) if linha[7] is not None else 0.0
        i._statusItem           = linha[8]
        i._sugestao             = None
        return i
