"""Converte o PDF de um DANFE em XML de NF-e.

São duas etapas, e no fim a nota segue pelo mesmo parser do XML
(nfeParser.parse_nfe) — só existe um caminho de leitura de nota no sistema:

1. PDF → XML de layout, com o conversor nativo da pdfminer.six (o mesmo do
   `pdf2txt.py -t xml`): cada caractere e cada traço desenhado na página vira
   um elemento com suas coordenadas.
2. XML de layout → XML de NF-e: com as palavras e as bordas desenhadas, monta
   um <nfeProc> no layout oficial (chave, emitente, itens e total).

O que o DANFE garante e é usado como âncora:
- chave de acesso (44 dígitos, validada pelo dígito verificador): dela saem
  CNPJ do emitente, série e número, onde quer que tenham sido impressos;
- canhoto "RECEBEMOS DE <razão social> OS PRODUTOS..." para o fornecedor;
- tabela de produtos com cabeçalho (CÓDIGO, DESCRIÇÃO, NCM, QUANT., V. UNIT...).
  As colunas saem das bordas das células; sem bordas, dos títulos do
  cabeçalho, com o limite posto no vão real entre os textos — o título de uma
  coluna pode estar centralizado e o conteúdo começar bem antes dele.

PDF digitalizado (imagem), protegido por senha ou corrompido é recusado com
uma mensagem clara: nesses casos não há texto para converter.
"""

import io
import re
import unicodedata
import xml.etree.ElementTree as ET

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFPasswordIncorrect

from src.service.nfeParser import NFeParserError, NS

_NS = NS["nfe"]

# Um DANFE de 60 páginas já teria mais de mil itens; acima disso não é nota,
# e converter milhares de páginas travaria a requisição.
_MAX_PAGINAS = 60

_FIM_TABELA = ("DADOS ADICIONAIS", "CALCULO DO ISSQN", "INFORMACOES COMPLEMENTARES",
               "RESERVADO AO FISCO")

_UFS = {11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        31, 32, 33, 35, 41, 42, 43, 50, 51, 52, 53}

# número no formato brasileiro: 1.234,5670 / 84,87 / 5
_RE_NUMERO = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?")
_RE_DATA = re.compile(r"(\d{2})[/.-](\d{2})[/.-](\d{4})")


# ─── utilitários ──────────────────────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    """Maiúsculas sem acento, preservando o comprimento."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in texto).upper()


def _numero_br(texto: str):
    """'1.234,56' → 1234.56; None se não for um número brasileiro inteiro."""
    texto = (texto or "").strip()
    if not texto or not _RE_NUMERO.fullmatch(texto):
        return None
    return float(texto.replace(".", "").replace(",", "."))


def _dv_chave(chave43: str) -> str:
    pesos, soma = (2, 3, 4, 5, 6, 7, 8, 9), 0
    for i, d in enumerate(reversed(chave43)):
        soma += int(d) * pesos[i % 8]
    resto = soma % 11
    return "0" if resto in (0, 1) else str(11 - resto)


def _chave_valida(c: str) -> bool:
    return (len(c) == 44 and int(c[:2]) in _UFS and 1 <= int(c[4:6]) <= 12
            and c[20:22] == "55" and _dv_chave(c[:43]) == c[43])


class _Palavra:
    __slots__ = ("x0", "y0", "x1", "y1", "texto")

    def __init__(self, x0, y0, x1, y1, texto):
        self.x0, self.y0, self.x1, self.y1, self.texto = x0, y0, x1, y1, texto

    @property
    def cx(self):
        return (self.x0 + self.x1) / 2

    @property
    def cy(self):
        return (self.y0 + self.y1) / 2

    @property
    def norm(self):
        return _normalizar(self.texto)


class _Pagina:
    """Uma página do XML de layout: palavras, linhas de texto, traços e caixas.
    Coordenadas do PDF: y cresce para cima."""

    def __init__(self):
        self.palavras = []    # _Palavra
        self.textos = []      # texto de cada <textline>, na ordem da pdfminer
        self.verticais = []   # (x, y_baixo, y_cima)
        self.horizontais = []  # (y, x_esq, x_dir)
        self.caixas = []      # (x0, y0, x1, y1) de retângulos e caixas arredondadas
        self._linhas = None

    def linhas(self, palavras=None):
        """Agrupa palavras em linhas de texto (mesma altura), de cima para baixo."""
        if palavras is None:
            if self._linhas is None:
                self._linhas = self.linhas(self.palavras)
            return self._linhas
        linhas = []
        for p in sorted(palavras, key=lambda p: -p.cy):
            alvo = next((l for l in linhas
                         if abs(l[0].cy - p.cy) <= max(1.5, (l[0].y1 - l[0].y0) * 0.45)), None)
            if alvo:
                alvo.append(p)
            else:
                linhas.append([p])
        return [sorted(l, key=lambda p: p.x0) for l in linhas]


# ─── etapa 1: PDF → XML de layout ─────────────────────────────────────────────

def pdf_para_xml(conteudo: bytes) -> str:
    """Converte o PDF no XML de layout da pdfminer.six (texto com coordenadas,
    retângulos, linhas e curvas de cada página)."""
    if not conteudo:
        raise NFeParserError("Arquivo PDF vazio.")
    if not conteudo.lstrip()[:5].startswith(b"%PDF"):
        raise NFeParserError("O arquivo enviado não é um PDF válido.")

    saida = io.BytesIO()
    try:
        extract_text_to_fp(io.BytesIO(conteudo), saida, output_type="xml", codec="utf-8",
                           laparams=LAParams(detect_vertical=True),
                           maxpages=_MAX_PAGINAS + 1)
    except PDFPasswordIncorrect:
        raise NFeParserError("O PDF está protegido por senha. Envie uma versão sem senha ou o XML da nota.")
    except Exception:
        # PDF malformado estoura vários tipos de erro dentro da biblioteca; o
        # detalhe técnico não ajuda quem está importando a nota.
        raise NFeParserError("Não foi possível ler o PDF — o arquivo pode estar corrompido ou incompleto.")
    return saida.getvalue().decode("utf-8", errors="replace")


# ─── leitura do XML de layout ─────────────────────────────────────────────────

def _bbox(elemento):
    return [float(v) for v in elemento.get("bbox").split(",")]


def _ler_layout(xml_layout: str) -> list:
    try:
        raiz = ET.fromstring(xml_layout)
    except ET.ParseError:
        raise NFeParserError("Não foi possível ler o PDF — o arquivo pode estar corrompido ou incompleto.")

    paginas = []
    for elem_pag in raiz.iter("page"):
        pag = _Pagina()
        # Texto rotacionado (canhoto na lateral da página, por exemplo) entra
        # nas buscas por texto — chave, "RECEBEMOS DE" — mas não na leitura por
        # posição: atravessaria a página inteira e cairia dentro das colunas.
        verticais = {id(l) for caixa in elem_pag.iter("textbox") if caixa.get("wmode") == "vertical"
                     for l in caixa.iter("textline")}
        for linha in elem_pag.iter("textline"):
            pag.textos.append("".join(c.text or "" for c in linha.iter("text")).strip())
            if id(linha) in verticais:
                continue
            palavra = None
            for c in linha.iter("text"):
                # espaços e quebras vêm sem bbox: separam palavras
                if c.get("bbox") is None or not (c.text or "").strip():
                    palavra = None
                    continue
                x0, y0, x1, y1 = _bbox(c)
                altura = max(y1 - y0, 1.0)
                if palavra and 0 <= x0 - palavra.x1 <= altura * 0.3 and abs(palavra.cy - (y0 + y1) / 2) < altura:
                    palavra.x1, palavra.texto = x1, palavra.texto + c.text
                    palavra.y0, palavra.y1 = min(palavra.y0, y0), max(palavra.y1, y1)
                else:
                    palavra = _Palavra(x0, y0, x1, y1, c.text)
                    pag.palavras.append(palavra)

        for elem in elem_pag.iter():
            if elem.tag not in ("line", "rect", "curve") or elem.get("bbox") is None:
                continue
            x0, y0, x1, y1 = _bbox(elem)
            largura, altura = x1 - x0, y1 - y0
            if largura < 1.5 and altura > 2:
                pag.verticais.append(((x0 + x1) / 2, y0, y1))
            elif altura < 1.5 and largura > 2:
                pag.horizontais.append(((y0 + y1) / 2, x0, x1))
            elif elem.tag in ("rect", "curve") and largura > 3 and altura > 3:
                pag.caixas.append((x0, y0, x1, y1))
                if elem.tag == "rect":   # as bordas do retângulo também são traços
                    pag.verticais += [(x0, y0, y1), (x1, y0, y1)]
                    pag.horizontais += [(y0, x0, x1), (y1, x0, x1)]
        paginas.append(pag)

    if len(paginas) > _MAX_PAGINAS:
        raise NFeParserError(f"O PDF tem mais de {_MAX_PAGINAS} páginas — não parece ser um DANFE.")
    if sum(len(p.texto) for pag in paginas for p in pag.palavras) < 50:
        raise NFeParserError(
            "Este PDF não tem texto legível — parece ser uma imagem digitalizada. "
            "Envie o XML da nota ou o PDF original gerado pelo sistema emissor."
        )
    return paginas


# ─── cabeçalho da nota ────────────────────────────────────────────────────────

def _encontrar_chave(textos: list) -> str:
    """Primeira sequência de 44 dígitos (com ou sem espaços/pontos entre os
    grupos) que passe na validação da chave de acesso."""
    corrido = " ".join(textos)
    for m in re.finditer(r"\d+(?:[ .]\d+)*", corrido):
        digitos = re.sub(r"\D", "", m.group())
        for i in range(len(digitos) - 43):
            if _chave_valida(digitos[i:i + 44]):
                return digitos[i:i + 44]
    raise NFeParserError(
        "Não encontrei a chave de acesso (44 dígitos) no PDF. "
        "Confira se o arquivo é o DANFE de uma NF-e."
    )


def _fornecedor(textos: list):
    corrido = " ".join(textos)
    m = re.search(r"RECEBEMOS DE\s+(.+?)\s+OS PRODUTOS", _normalizar(corrido), re.S)
    if not m:
        return None
    return re.sub(r"\s+", " ", corrido[m.start(1):m.end(1)]).strip() or None


def _rotulo(pagina: _Pagina, padrao: str):
    """Caixa (x0, y0, x1, y1) de um rótulo de várias palavras, ex.: 'VALOR TOTAL DA NOTA'."""
    for linha in pagina.linhas():
        texto, posicoes = "", []
        for p in linha:
            posicoes.append((len(texto), p))
            texto += p.norm + " "
        m = re.search(padrao, texto)
        if m:
            usadas = [p for ini, p in posicoes if m.start() <= ini < m.end()]
            return (min(p.x0 for p in usadas), min(p.y0 for p in usadas),
                    max(p.x1 for p in usadas), max(p.y1 for p in usadas))
    return None


def _quadro(pag: _Pagina, rx0, ry0, rx1, ry1):
    """Quadro do DANFE em volta de um rótulo: a menor caixa desenhada que o
    contém; senão, a célula formada pelos traços mais próximos; senão, a faixa
    abaixo dele até o próximo rótulo da mesma linha."""
    caixas = [c for c in pag.caixas
              if c[0] - 1 <= rx0 and c[2] + 1 >= rx1 and c[1] - 1 <= ry0 and c[3] + 1 >= ry1
              and c[3] - c[1] < 40]
    if caixas:
        return min(caixas, key=lambda c: (c[2] - c[0]) * (c[3] - c[1]))

    meio = (ry0 + ry1) / 2
    esq = [x for x, yb, yc in pag.verticais if x <= rx0 + 1 and yb <= meio <= yc]
    dir_ = [x for x, yb, yc in pag.verticais if x >= rx1 - 1 and yb <= meio <= yc]
    base = [y for y, xe, xd in pag.horizontais if y <= ry0 + 1 and xe <= rx0 + 1 and xd >= rx1 - 1]
    if esq and dir_ and base and ry0 - max(base) < 30:
        return max(esq), max(base), min(dir_), ry1 + 1

    # o próximo texto à direita, na altura do rótulo, já é o rótulo do quadro ao lado
    vizinhos = [p.x0 for p in pag.palavras if p.x0 > rx1 + 2 and abs(p.cy - meio) < (ry1 - ry0)]
    return rx0 - 2, ry0 - 18, (min(vizinhos) - 1 if vizinhos else rx1 + 200), ry1


def _valor_do_campo(paginas: list, padrao_rotulo: str, padrao_valor) -> str:
    """Valor impresso no mesmo quadro de um rótulo do DANFE (logo abaixo dele)."""
    for pag in paginas:
        r = _rotulo(pag, padrao_rotulo)
        if not r:
            continue
        rx0, ry0, rx1, ry1 = r
        x0, y0, x1, y1 = _quadro(pag, rx0, ry0, rx1, ry1)
        candidatas = [p for p in pag.palavras
                      if x0 <= p.cx <= x1 and y0 <= p.cy <= y1 and p.cy < ry0 + 1]
        for linha in pag.linhas(candidatas):
            for p in linha:
                m = padrao_valor.search(p.texto)
                if m:
                    return m.group()
    return None


def _data_emissao(paginas: list, textos: list, chave: str):
    candidatas = []
    no_campo = _valor_do_campo(paginas, r"DATA\s+D[AE]\s+EMISSAO", _RE_DATA)
    if no_campo:
        candidatas.append(no_campo)
    corrido = _normalizar(" ".join(textos))
    for rotulo in (r"DATA\s+D[AE]\s+EMISSAO", r"EMISSAO\s*:?", r"PROTOCOLO"):
        for m in re.finditer(rotulo + r"[\s\S]{0,250}?(\d{2}[/.-]\d{2}[/.-]\d{4})", corrido):
            candidatas.append(m.group(1))
    # a chave traz ano e mês da emissão (AAMM): desempata entre datas impressas
    datas = [_RE_DATA.search(c).groups() for c in candidatas]
    for dia, mes, ano in datas:
        if ano[2:] + mes == chave[2:6]:
            return f"{ano}-{mes}-{dia}T00:00:00"
    if datas:
        dia, mes, ano = datas[0]
        return f"{ano}-{mes}-{dia}T00:00:00"
    return None


def _valor_total(paginas: list, textos: list, itens: list) -> float:
    re_valor = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}(?!\d)")
    valor = _valor_do_campo(paginas, r"VALOR\s+TOTAL\s+DA\s+NOTA", re_valor)
    if not valor:
        corrido = _normalizar(" ".join(textos))
        m = (re.search(r"VALOR\s+TOTAL\s+DA\s+NOTA[\s\S]{0,120}?(\d{1,3}(?:\.\d{3})*,\d{2})", corrido)
             or re.search(r"VALOR TOTAL\s*:?\s*\(?R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})", corrido)
             or re.search(r"\(R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})\)", corrido))
        valor = m.group(1) if m else None
    if valor:
        return _numero_br(valor)
    return round(sum(i["valorTotal"] for i in itens), 2)


# ─── tabela de produtos ───────────────────────────────────────────────────────

def _tipo_coluna(titulo: str):
    """Nome do campo a partir do título da coluna (já normalizado)."""
    t = " " + re.sub(r"[^A-Z0-9/%]+", " ", titulo) + " "
    if "DESCRI" in t:
        return "descricao"
    if re.search(r" COD", t):
        return "codigo"
    if "NCM" in t:
        return "ncm"
    if "CFOP" in t:
        return "cfop"
    if "CST" in t or "CSOSN" in t:
        return "cst"
    if "UNIT" in t:
        return "valorUnitario"
    if re.search(r" (QUANT|QTD|QTDE)", t):
        return "quantidade"
    if re.search(r" (UN|UNID|UNIDADE|UNID\.?) ", t):
        return "unidade"
    if re.search(r" (DESC|DESCONTO) ", t):
        return "desconto"
    if "TOTAL" in t and "BC" not in t and "BASE" not in t:
        return "valorTotal"
    return None


def _cabecalho_tabela(pagina: _Pagina):
    """Linha do cabeçalho da tabela de produtos: a que tem DESCRIÇÃO e NCM."""
    for linha in pagina.linhas():
        textos = [p.norm for p in linha]
        if any(t.startswith("DESCRI") for t in textos) and any("NCM" in t for t in textos):
            return linha
    return None


def _colunas(pagina: _Pagina, cabecalho: list, y_dados: float, palavras_dados: list) -> list:
    """Lista de (x_esq, x_dir, campo) das colunas da tabela."""
    y_cab = sum(p.cy for p in cabecalho) / len(cabecalho)
    altura = max(p.y1 - p.y0 for p in cabecalho)
    # palavras dos títulos: podem ocupar duas ou três linhas empilhadas, mas
    # ficam acima dos dados e não incluem o título da seção ("DADOS DOS PRODUTOS")
    secao = {id(p) for l in pagina.linhas() if "DADOS DO" in " ".join(p.norm for p in l) for p in l}
    faixa = [p for p in pagina.palavras
             if abs(p.cy - y_cab) <= altura * 1.6 and p.cy > y_dados and id(p) not in secao]

    # 1) bordas verticais que atravessam o cabeçalho
    xs = sorted(x for x, yb, yc in pagina.verticais if yb - 1 <= y_cab <= yc + 1)
    limites = []
    for x in xs:
        if not limites or x - limites[-1] > 2:
            limites.append(x)

    if len(limites) < 5:
        # 2) sem bordas: agrupa os títulos (palavras próximas ou empilhadas)
        grupos = []
        for p in sorted(faixa, key=lambda p: p.x0):
            if grupos and p.x0 <= grupos[-1][1] + 5:
                grupos[-1][1] = max(grupos[-1][1], p.x1)
            else:
                grupos.append([p.x0, p.x1])
        # vãos: faixas de x sem nenhum texto (títulos + dados)
        vaos, fim = [], None
        for o0, o1 in sorted((p.x0, p.x1) for p in faixa + palavras_dados):
            if fim is not None and o0 > fim:
                vaos.append((fim, o0))
            fim = o1 if fim is None else max(fim, o1)
        # O limite entre duas colunas é o maior vão entre o começo de uma e o
        # título da outra — o conteúdo pode começar bem antes do título, que
        # costuma vir centralizado. Sem vão, fica no meio dos títulos.
        limites = [min(p.x0 for p in faixa + palavras_dados) - 1]
        for (a0, a1), (b0, b1) in zip(grupos, grupos[1:]):
            entre = [v for v in vaos if v[0] >= a0 and v[1] <= b0 + 1]
            if entre:
                v0, v1 = max(entre, key=lambda v: v[1] - v[0])
                limites.append((v0 + v1) / 2)
            else:
                limites.append((a1 + b0) / 2)
        limites.append(max(p.x1 for p in faixa + palavras_dados) + 1)

    colunas = []
    for x0, x1 in zip(limites, limites[1:]):
        titulo = " ".join(p.norm for p in sorted(faixa, key=lambda p: (-round(p.cy), p.x0))
                          if x0 <= p.cx <= x1)
        colunas.append((x0, x1, _tipo_coluna(titulo)))
    return colunas


def _texto_celula(palavras: list, x0: float, x1: float, juntar_linhas: str, pagina: _Pagina) -> str:
    dentro = [p for p in palavras if x0 <= p.cx <= x1]
    return juntar_linhas.join(" ".join(p.texto for p in l) for l in pagina.linhas(dentro)).strip()


def _itens_da_pagina(pagina: _Pagina) -> list:
    cabecalho = _cabecalho_tabela(pagina)
    if not cabecalho:
        return []
    y_cab_base = min(p.y0 for p in cabecalho)

    # fim da tabela: primeiro bloco depois dela (dados adicionais, ISSQN...)
    y_fim = -1
    for linha in pagina.linhas():
        if linha[0].cy < y_cab_base and any(m in " ".join(p.norm for p in linha) for m in _FIM_TABELA):
            y_fim = max(y_fim, max(p.y1 for p in linha))
    # As palavras de títulos que ficam abaixo da linha principal (2ª linha de
    # títulos) não são dados: corta pela borda horizontal logo abaixo do
    # cabeçalho. Só vale borda que atravessa a coluna da descrição — o traço
    # que divide "ALÍQUOTA" em ICMS/IPI, por exemplo, não serve.
    x_desc = next(p.cx for p in cabecalho if p.norm.startswith("DESCRI"))
    abaixo = sorted((y for y, xe, xd in pagina.horizontais
                     if y < y_cab_base + 1 and xe <= x_desc <= xd), reverse=True)
    y_dados = abaixo[0] if abaixo and y_cab_base - abaixo[0] < 14 else y_cab_base - 0.5
    dados = [p for p in pagina.palavras if y_fim < p.cy < y_dados]

    colunas = _colunas(pagina, cabecalho, y_dados, dados)
    tipos = {c[2] for c in colunas}
    if "descricao" not in tipos or "quantidade" not in tipos:
        return []
    col = {tipo: (x0, x1) for x0, x1, tipo in colunas if tipo}

    def qtd_da_linha(linha):
        x0, x1 = col["quantidade"]
        return _numero_br("".join(p.texto for p in linha if x0 <= p.cx <= x1))

    # Cada item é uma faixa da tabela. Com bordas horizontais entre os itens,
    # a faixa é o espaço entre duas bordas.
    desc_x0, desc_x1 = col["descricao"]
    cortes = sorted({round(y, 1) for y, xe, xd in pagina.horizontais
                     if y_fim < y < y_dados + 1 and xe <= desc_x0 + 2 and xd >= desc_x1 - 2}, reverse=True)
    faixas = []
    if len(cortes) >= 2:
        for topo, base in zip(cortes, cortes[1:]):
            faixa = [p for p in dados if base < p.cy < topo]
            if faixa:
                faixas.append(faixa)
    # Sem bordas por item (ou se uma faixa juntou vários itens): agrupa as
    # linhas de texto em torno da linha que tem a quantidade.
    if not faixas or any(sum(1 for l in pagina.linhas(f) if qtd_da_linha(l) is not None) > 1 for f in faixas):
        linhas = pagina.linhas(dados)
        ancoras = [i for i, l in enumerate(linhas) if qtd_da_linha(l) is not None]
        if not ancoras:
            return []
        grupos = {a: list(linhas[a]) for a in ancoras}
        no_topo = ancoras[0] == 0  # quantidade na 1ª linha: emissor alinha no topo
        for i, linha in enumerate(linhas):
            if i in grupos:
                continue
            if no_topo:
                dono = max((a for a in ancoras if a < i), default=ancoras[0])
            else:
                # centralizado: a linha é do item cuja quantidade está mais perto
                dono = min(ancoras, key=lambda a: (abs(linhas[a][0].cy - linha[0].cy), a < i))
            grupos[dono] += linha
        faixas = [grupos[a] for a in ancoras]

    itens = []
    for faixa in faixas:
        celula = lambda tipo, juntar=" ": (_texto_celula(faixa, *col[tipo], juntar, pagina)
                                           if tipo in col else "")
        # números quebrados dentro da célula voltam a ficar juntos
        qtd = _numero_br(celula("quantidade", "").replace(" ", ""))
        unit = _numero_br(celula("valorUnitario", "").replace(" ", ""))
        total = _numero_br(celula("valorTotal", "").replace(" ", ""))
        descricao = re.sub(r"\s+", " ", celula("descricao")).strip()
        if not qtd or not descricao:
            continue
        if total is None and unit is not None:
            total = round(qtd * unit, 2)
        if unit is None and total is not None:
            unit = round(total / qtd, 10)
        if total is None:
            continue
        itens.append({
            "codigo":     celula("codigo", ""),
            "descricao":  descricao,
            "unidade":    celula("unidade", ""),
            "quantidade": qtd,
            "unitario":   unit,
            "total":      total,
        })
    return itens


# ─── etapa 2: XML de layout → XML de NF-e ─────────────────────────────────────

def _montar_nfe(chave, data, fornecedor, total, itens) -> bytes:
    ET.register_namespace("", _NS)
    q = lambda tag: f"{{{_NS}}}{tag}"

    def filho(pai, tag, texto=None):
        e = ET.SubElement(pai, q(tag))
        if texto is not None:
            e.text = texto
        return e

    proc = ET.Element(q("nfeProc"), versao="4.00")
    inf = filho(filho(proc, "NFe"), "infNFe")
    inf.set("Id", f"NFe{chave}")
    inf.set("versao", "4.00")

    ide = filho(inf, "ide")
    filho(ide, "mod", "55")
    filho(ide, "serie", str(int(chave[22:25])))
    filho(ide, "nNF", str(int(chave[25:34])))
    if data:
        filho(ide, "dhEmi", data)

    emit = filho(inf, "emit")
    filho(emit, "CNPJ", chave[6:20])
    if fornecedor:
        filho(emit, "xNome", fornecedor)

    for n, item in enumerate(itens, 1):
        det = filho(inf, "det")
        det.set("nItem", str(n))
        prod = filho(det, "prod")
        filho(prod, "cProd", item["codigo"])
        filho(prod, "xProd", item["descricao"])
        filho(prod, "uCom", item["unidade"])
        filho(prod, "qCom", f"{item['quantidade']:.4f}")
        filho(prod, "vUnCom", f"{item['unitario']:.10f}")
        filho(prod, "vProd", f"{item['total']:.2f}")

    filho(filho(filho(inf, "total"), "ICMSTot"), "vNF", f"{total:.2f}")
    filho(filho(inf, "infAdic"), "infCpl", "XML gerado a partir do DANFE em PDF")
    return ET.tostring(proc, encoding="utf-8", xml_declaration=True)


def danfe_pdf_para_nfe_xml(conteudoPdf: bytes) -> bytes:
    """PDF do DANFE → XML de NF-e (bytes), pronto para nfeParser.parse_nfe.

    :raises NFeParserError: PDF ilegível, sem chave de acesso ou sem itens
    """
    paginas = _ler_layout(pdf_para_xml(conteudoPdf))
    textos = [t for pag in paginas for t in pag.textos]

    chave = _encontrar_chave(textos)
    itens = [i for pag in paginas for i in _itens_da_pagina(pag)]
    if not itens:
        raise NFeParserError(
            "Encontrei a nota no PDF, mas não consegui ler a tabela de produtos. "
            "Envie o XML da nota para importar."
        )

    return _montar_nfe(
        chave,
        _data_emissao(paginas, textos, chave),
        _fornecedor(textos),
        _valor_total(paginas, textos, [{"valorTotal": i["total"]} for i in itens]),
        itens,
    )
