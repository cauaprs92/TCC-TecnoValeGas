"""Parser de DANFE em PDF — lê a versão impressa da NF-e e devolve o mesmo
dicionário que nfeParser.parse_nfe devolve para o XML, para o resto do fluxo
(gravação, reabertura e conferência item a item) não precisar saber a origem.

O DANFE não tem estrutura, só texto posicionado, e cada sistema emissor monta
o PDF de um jeito. Por isso a leitura se apoia no que o layout oficial obriga:

- Chave de acesso (44 dígitos, validada pelo dígito verificador). É a âncora
  principal: dela saem CNPJ do emitente, série e número sem depender de onde
  esses campos foram impressos.
- Canhoto "RECEBEMOS DE <razão social> OS PRODUTOS..." para o nome do fornecedor.
- Linha de item ancorada em NCM + CST + CFOP + UN + números. A conta
  quantidade × valor unitário ≈ valor total confirma que as colunas foram
  lidas certo.

A tabela de produtos é lida pela posição das colunas (modo "layout" do pypdf);
se isso não encontrar itens, tenta de novo pelo texto corrido. PDF
digitalizado (imagem) não tem texto e é recusado com uma mensagem clara.
"""

import io
import logging
import re
import unicodedata

from pypdf import PdfReader

from src.service.nfeParser import NFeParserError

# avisos de PDF imperfeito ("texto rotacionado", "EOF") não interessam ao log
logging.getLogger("pypdf").setLevel(logging.ERROR)

# Um DANFE de 60 páginas já teria mais de mil itens; acima disso não é nota,
# e ler o texto de milhares de páginas travaria a requisição.
_MAX_PAGINAS = 60

# Número no formato brasileiro com vírgula decimal: 1.234,5670 / 89,90
_DEC = r"\d{1,3}(?:\.\d{3})+,\d+|\d+,\d+"
# A quantidade pode vir sem casas decimais em alguns emissores
_QTD = rf"(?:{_DEC}|\d+)"

# Final de uma linha de item: NCM, CST/CSOSN, CFOP, unidade, quantidade e os
# valores. Só a quantidade aceita inteiro: assim um código numérico do item
# seguinte (texto corrido) não é engolido como se fosse um valor.
# NCM e CFOP aceitam vir truncados: com fonte grande, alguns emissores quebram
# esses números dentro da célula ("7306300" + "0" na linha de baixo). Eles só
# servem de âncora — não são gravados.
_RE_ITEM = re.compile(
    r"(?<!\S)(?P<ncm>\d{4}\.?\d{2}\.?\d{0,2})\s+"
    r"(?P<cst>\d{1,2}/?\d{2,3})\s+"
    r"(?P<cfop>[1-7]\.?\d{1,3})\s+"
    r"(?P<un>[^\W\d_]\w{0,5})\s+"
    rf"(?P<nums>{_QTD}(?:\s+(?:{_DEC}))+)"
)

_FIM_TABELA = ("DADOS ADICIONAIS", "CALCULO DO ISSQN", "INFORMACOES COMPLEMENTARES",
               "RESERVADO AO FISCO")

_UFS = {11, 12, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        31, 32, 33, 35, 41, 42, 43, 50, 51, 52, 53}


# ─── utilitários ──────────────────────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    """Maiúsculas sem acento, preservando o comprimento — uma posição achada
    no texto normalizado vale também para o original."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in texto).upper()


def _br_float(valor: str) -> float:
    return float(valor.replace(".", "").replace(",", "."))


def _dv_chave(chave43: str) -> str:
    pesos, soma = (2, 3, 4, 5, 6, 7, 8, 9), 0
    for i, d in enumerate(reversed(chave43)):
        soma += int(d) * pesos[i % 8]
    resto = soma % 11
    return "0" if resto in (0, 1) else str(11 - resto)


def _chave_valida(c: str) -> bool:
    return (len(c) == 44 and int(c[:2]) in _UFS and 1 <= int(c[4:6]) <= 12
            and c[20:22] == "55" and _dv_chave(c[:43]) == c[43])


# ─── leitura do PDF ───────────────────────────────────────────────────────────

def _ler_paginas(conteudo: bytes) -> tuple:
    """Devolve (textos simples, textos em layout) de cada página."""
    if not conteudo:
        raise NFeParserError("Arquivo PDF vazio.")
    if not conteudo.lstrip()[:5].startswith(b"%PDF"):
        raise NFeParserError("O arquivo enviado não é um PDF válido.")

    try:
        leitor = PdfReader(io.BytesIO(conteudo))
        if leitor.is_encrypted and not leitor.decrypt(""):
            raise NFeParserError("O PDF está protegido por senha. Envie uma versão sem senha ou o XML da nota.")
        if len(leitor.pages) > _MAX_PAGINAS:
            raise NFeParserError(f"O PDF tem {len(leitor.pages)} páginas — não parece ser um DANFE.")
        simples = [p.extract_text() or "" for p in leitor.pages]
        layout  = [p.extract_text(extraction_mode="layout") or "" for p in leitor.pages]
    except NFeParserError:
        raise
    except Exception:
        # PDF malformado pode estourar vários tipos de erro dentro do pypdf;
        # o detalhe técnico não ajuda quem está importando a nota.
        raise NFeParserError("Não foi possível ler o PDF — o arquivo pode estar corrompido ou incompleto.")

    if len("".join(simples).strip()) < 50:
        raise NFeParserError(
            "Este PDF não tem texto legível — parece ser uma imagem digitalizada. "
            "Envie o XML da nota ou o PDF original gerado pelo sistema emissor."
        )
    return simples, layout


# ─── cabeçalho ────────────────────────────────────────────────────────────────

def _encontrar_chave(texto: str) -> str:
    """Primeira sequência de 44 dígitos (com ou sem espaços/pontos entre os
    grupos) que passe na validação da chave de acesso."""
    plano = texto.replace("\n", " ")
    for m in re.finditer(r"\d+(?:[ .]\d+)*", plano):
        digitos = re.sub(r"\D", "", m.group())
        for i in range(0, len(digitos) - 43):
            candidata = digitos[i:i + 44]
            if _chave_valida(candidata):
                return candidata
    raise NFeParserError(
        "Não encontrei a chave de acesso (44 dígitos) no PDF. "
        "Confira se o arquivo é o DANFE de uma NF-e."
    )


def _fornecedor(texto: str) -> str:
    norm = _normalizar(texto)
    m = re.search(r"RECEBEMOS DE\s+(.+?)\s+OS PRODUTOS", norm, re.S)
    if not m:
        return None
    nome = re.sub(r"\s+", " ", texto[m.start(1):m.end(1)]).strip()
    return nome or None


def _valor_em_coluna(linhas: list, rotulo: str, padrao: str):
    """Valor que fica logo abaixo de um rótulo, na mesma coluna (layout do
    DANFE: uma linha de rótulos e, embaixo, a linha de valores)."""
    for i, linha in enumerate(linhas):
        norm = _normalizar(linha)
        m = re.search(rotulo, norm)
        if not m:
            continue
        inicio = m.start()
        # a caixa do rótulo vai até o começo do próximo rótulo da mesma linha
        prox = re.search(r"\S", norm[m.end():])
        fim = m.end() + prox.start() if prox else len(norm) + 40

        # valor na própria linha, logo depois do rótulo ("EMISSÃO: 03/07/2026")
        achado = re.search(padrao, linha[m.end():fim])
        if achado:
            return achado.group()
        # ou nas linhas de baixo, dentro da largura da caixa. Os valores vêm
        # alinhados à direita: o da caixa vizinha à esquerda termina justo onde
        # esta começa — por isso o centro precisa estar estritamente depois do
        # início do rótulo.
        for abaixo in linhas[i + 1:i + 4]:
            for v in re.finditer(padrao, abaixo):
                meio = (v.start() + v.end()) / 2
                if inicio < meio <= fim + 6:
                    return v.group()
    return None


def _data_emissao(simples: str, linhas_layout: list, chave: str) -> str:
    padrao = r"\d{2}/\d{2}/\d{4}"
    candidatas = [
        _valor_em_coluna(linhas_layout, r"DATA\s+D[AE]\s+EMISSAO", padrao),
        *re.findall(r"DATA\s+D[AE]\s+EMISSAO[\s\S]{0,250}?(\d{2}/\d{2}/\d{4})", _normalizar(simples)),
        *re.findall(r"EMISSAO\s*:?\s*(\d{2}/\d{2}/\d{4})", _normalizar(simples)),
        *re.findall(r"PROTOCOLO[\s\S]{0,200}?(\d{2}/\d{2}/\d{4})", _normalizar(simples)),
    ]
    candidatas = [c for c in candidatas if c]
    # a chave traz ano e mês da emissão (AAMM): desempata entre datas impressas
    aamm = chave[2:6]
    for c in candidatas:
        dia, mes, ano = c.split("/")
        if ano[2:] + mes == aamm:
            return f"{ano}-{mes}-{dia} 00:00:00"
    if candidatas:
        dia, mes, ano = candidatas[0].split("/")
        return f"{ano}-{mes}-{dia} 00:00:00"
    return None


def _valor_total(simples: str, linhas_layout: list, itens: list) -> float:
    padrao = r"\d{1,3}(?:\.\d{3})*,\d{2}(?!\d)"
    valor = _valor_em_coluna(linhas_layout, r"VALOR\s+TOTAL\s+DA\s+NOTA", padrao)
    if not valor:
        m = re.search(r"VALOR\s+TOTAL\s+DA\s+NOTA[\s\S]{0,120}?(" + padrao + ")", _normalizar(simples))
        valor = m.group(1) if m else None
    if not valor:
        m = re.search(r"VALOR TOTAL\s*:?\s*R?\$?\s*(" + padrao + ")", _normalizar(simples))
        valor = m.group(1) if m else None
    if valor:
        return _br_float(valor)
    return round(sum(i["valorTotal"] for i in itens), 2)


# ─── itens ────────────────────────────────────────────────────────────────────

_RE_NUM = re.compile(rf"{_DEC}|\d+")


def _numeros(m, linha_abaixo: str = None) -> list:
    """Valores do final do item: quantidade, unitário, total, impostos...

    Com fonte grande o emissor pode quebrar um valor dentro da célula
    ("1.234,56" e o "70" que sobrou na linha de baixo). Se a linha de baixo não
    for outro item, o pedaço que estiver na faixa da mesma coluna é colado de
    volta. A sobra pertence ao valor cujo vão (do fim do valor anterior ao
    começo do próximo) contém o início dela — então sobras de NCM e CFOP, que
    ficam antes da unidade, nunca entram.
    """
    base = m.start("nums")
    tokens = [(base + t.start(), base + t.end(), t.group()) for t in _RE_NUM.finditer(m.group("nums"))]
    if not linha_abaixo or _RE_ITEM.search(linha_abaixo):
        return [_br_float(t) for _, _, t in tokens]

    sobras = [(s.start(), s.group()) for s in re.finditer(r"[\d.,]*\d", linha_abaixo)]
    reparados, anterior = [], m.end("un")
    for n, (inicio, fim, texto) in enumerate(tokens):
        proximo = tokens[n + 1][0] if n + 1 < len(tokens) else fim + 4
        for pos, pedaco in sobras:
            if anterior < pos < proximo and re.fullmatch(rf"{_DEC}|\d+", texto + pedaco):
                texto += pedaco
                break
        reparados.append(texto)
        anterior = fim
    return [_br_float(t) for t in reparados]


def _montar_item(codigo: str, descricao: str, unidade: str, nums: list) -> dict:
    qtd, unit = nums[0], nums[1]
    total = nums[2] if len(nums) > 2 else round(qtd * unit, 2)
    # Alguns layouts põem uma coluna (desconto, por exemplo) antes do total:
    # fica com o primeiro valor que bate com quantidade × unitário.
    for candidato in nums[2:5]:
        if abs(qtd * unit - candidato) <= max(0.05, candidato * 0.005):
            total = candidato
            break
    return {
        "codProdutoFornecedor": codigo.strip(),
        "nomeProdutoNota":      re.sub(r"\s+", " ", descricao).strip(),
        "unidade":              unidade,
        "quantidade":           qtd,
        "valorUnitario":        unit,
        "valorTotal":           total,
    }


_RE_CABECALHO_2A_LINHA = re.compile(
    r"^[^\d]*\b(PRODUTO|SERVICO|UNIT|ALIQ|ICMS|IPI|QUANT|VALOR|CSOSN|CALC)\b[^\d]*$")


def _itens_por_coluna(paginas_layout: list) -> tuple:
    """Lê a tabela pela posição das colunas: o código abre o item; o que vier
    na coluna da descrição até o próximo código é a descrição dele (cobre a
    descrição que quebra linha depois da linha do código).

    Devolve (itens, alinhado_no_topo). Se aparecer descrição antes do primeiro
    código, o emissor centraliza (ou alinha embaixo) código e números na
    linha da tabela — aí as primeiras linhas de cada descrição ficariam no item
    anterior, e quem chama deve preferir a leitura por texto corrido.
    """
    itens, alinhado_no_topo = [], True
    for pagina in paginas_layout:
        linhas = pagina.split("\n")
        col_desc = col_ncm = None
        bloco, pendente = None, []

        def fechar():
            if bloco and bloco["m"]:
                itens.append(_montar_item(bloco["cod"], " ".join(bloco["desc"]),
                                          bloco["m"].group("un"), bloco["nums"]))

        for idx, linha in enumerate(linhas):
            norm = _normalizar(linha)
            if "DESCRI" in norm and "NCM" in norm:
                fechar()
                bloco, pendente = None, []
                col_desc, col_ncm = norm.index("DESCRI"), norm.index("NCM")
                continue
            if col_desc is None:
                continue
            if any(marca in norm for marca in _FIM_TABELA):
                fechar()
                bloco, col_desc = None, None
                continue
            if not linha.strip():
                continue

            m = _RE_ITEM.search(linha)
            nums = _numeros(m, linhas[idx + 1] if idx + 1 < len(linhas) else None) if m else None
            esquerda = linha[:m.start()] if m else linha[:col_ncm]
            # se um código longo invadir a coluna da descrição, termina no espaço
            corte = col_desc
            while corte < len(esquerda) and corte > 0 and not esquerda[corte - 1].isspace() \
                    and not esquerda[corte].isspace():
                corte += 1
            codigo, descricao = esquerda[:corte].strip(), esquerda[corte:].strip()

            if codigo or (m and bloco and bloco["m"]):
                fechar()
                bloco = {"cod": codigo, "desc": pendente + ([descricao] if descricao else []),
                         "m": m, "nums": nums}
                pendente = []
            elif bloco:
                if descricao:
                    bloco["desc"].append(descricao)
                if m and not bloco["m"]:
                    bloco["m"], bloco["nums"] = m, nums
            elif descricao and not _RE_CABECALHO_2A_LINHA.match(norm.strip()):
                # texto antes do primeiro código (a 2ª linha de um cabeçalho
                # em duas linhas não conta)
                pendente.append(descricao)
                alinhado_no_topo = False
        fechar()
    return itens, alinhado_no_topo


def _itens_texto_corrido(paginas_simples: list) -> list:
    """Plano B: junta a tabela num texto só e usa cada final de item como
    separador — o que vem antes dele (desde o item anterior) é código + descrição."""
    itens = []
    for pagina in paginas_simples:
        # a tabela começa no cabeçalho (linha com DESCRIÇÃO e NCM) — nem todo
        # emissor imprime o título "DADOS DO PRODUTO" antes dela
        linhas, trecho, dentro = pagina.split("\n"), [], False
        for linha in linhas:
            norm = _normalizar(linha)
            if "DESCRI" in norm and "NCM" in norm:
                dentro = True
                continue
            if dentro and any(marca in norm for marca in _FIM_TABELA):
                dentro = False
            if dentro:
                trecho.append(linha)
        corrido = " ".join(trecho)
        anterior = 0
        for m in _RE_ITEM.finditer(corrido):
            texto = corrido[anterior:m.start()].strip()
            partes = texto.split(None, 1)
            codigo = partes[0] if partes else ""
            descricao = partes[1] if len(partes) > 1 else ""
            itens.append(_montar_item(codigo, descricao, m.group("un"), _numeros(m)))
            anterior = m.end()
    return itens


def _consistentes(itens: list) -> int:
    return sum(1 for i in itens
               if abs(i["quantidade"] * i["valorUnitario"] - i["valorTotal"])
               <= max(0.05, i["valorTotal"] * 0.005))


# ─── entrada ──────────────────────────────────────────────────────────────────

def parse_danfe_pdf(conteudoPdf: bytes) -> dict:
    """Lê o PDF de um DANFE e devolve cabeçalho + itens no formato de parse_nfe.

    :raises NFeParserError: PDF ilegível, sem chave de acesso ou sem itens
    """
    simples, layout = _ler_paginas(conteudoPdf)
    texto = "\n".join(simples)
    linhas_layout = "\n".join(layout).split("\n")

    chave = _encontrar_chave(texto)

    por_coluna, alinhado_no_topo = _itens_por_coluna(layout)
    corrido = _itens_texto_corrido(simples)
    # Fica com a leitura que fecha mais contas (qtd × unitário = total) e,
    # depois, a que achou mais itens. No empate decide o alinhamento da tabela:
    # com código e números no topo da linha, a leitura por colunas é a mais
    # segura; centralizados, o texto corrido acerta as descrições.
    ordem = (por_coluna, corrido) if alinhado_no_topo else (corrido, por_coluna)
    itens = max(ordem, key=lambda l: (_consistentes(l), len(l)))
    itens = [i for i in itens if i["quantidade"] > 0 and i["nomeProdutoNota"]]
    if not itens:
        raise NFeParserError(
            "Encontrei a nota no PDF, mas não consegui ler a tabela de produtos. "
            "Envie o XML da nota para importar."
        )

    return {
        "chaveAcesso":    chave,
        "numero":         str(int(chave[25:34])),
        "serie":          str(int(chave[22:25])),
        "dataEmissao":    _data_emissao(texto, linhas_layout, chave),
        "fornecedorNome": _fornecedor(texto),
        "fornecedorCNPJ": chave[6:20],
        "valorTotal":     _valor_total(texto, linhas_layout, itens),
        "itens":          itens,
    }
