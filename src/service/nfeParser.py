"""Parser de NF-e (XML) — extrai cabeçalho e itens de uma nota fiscal eletrônica.

O layout da NF-e usa o namespace http://www.portalfiscal.inf.br/nfe em todas as
tags, então toda busca precisa ser qualificada. O XML pode vir tanto no formato
<nfeProc><NFe><infNFe>... (nota autorizada, com protocolo) quanto direto em
<NFe><infNFe>... — os dois casos são tratados.
"""

import xml.etree.ElementTree as ET

NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


class NFeParserError(Exception):
    """Erro de leitura/estrutura do XML da NF-e."""


def _texto(elemento, caminho: str, padrao: str = "") -> str:
    """Retorna o texto de um nó filho (caminho com prefixo nfe:) ou o padrão."""
    if elemento is None:
        return padrao
    alvo = elemento.find(caminho, NS)
    if alvo is None or alvo.text is None:
        return padrao
    return alvo.text.strip()


def _decimal(elemento, caminho: str, padrao: float = 0.0) -> float:
    valor = _texto(elemento, caminho)
    try:
        return float(valor)
    except (ValueError, TypeError):
        return padrao


def _data_emissao(valor: str) -> str:
    """Converte o dhEmi da NF-e (2026-07-03T10:15:00-03:00) para DATETIME do MySQL.

    Notas antigas usam <dEmi> (apenas a data) — nesse caso completa com 00:00:00.
    """
    if not valor:
        return None
    valor = valor.strip()
    if "T" in valor:
        data, _, hora = valor.partition("T")
        # remove o fuso horário (-03:00 / Z), que o MySQL não aceita em DATETIME
        for separador in ("-", "+"):
            if separador in hora:
                hora = hora.split(separador)[0]
        hora = hora.replace("Z", "").strip()
        return f"{data} {hora[:8]}"
    return f"{valor} 00:00:00"


def parse_nfe(conteudoXml) -> dict:
    """Lê o conteúdo de um arquivo .xml de NF-e e devolve cabeçalho + itens.

    :param conteudoXml: str ou bytes com o XML da nota
    :return: {"chaveAcesso", "numero", "serie", "dataEmissao", "fornecedorNome",
              "fornecedorCNPJ", "valorTotal", "itens": [...]}
    :raises NFeParserError: XML malformado ou fora do layout de NF-e
    """
    if not conteudoXml:
        raise NFeParserError("Arquivo XML vazio.")

    try:
        raiz = ET.fromstring(conteudoXml)
    except ET.ParseError as e:
        raise NFeParserError(f"XML inválido ou corrompido: {e}")

    # <infNFe> pode estar sob <nfeProc><NFe> ou direto sob <NFe>
    infNFe = raiz.find(".//nfe:infNFe", NS)
    if infNFe is None:
        raise NFeParserError("Este arquivo não parece ser uma NF-e (tag <infNFe> não encontrada).")

    chaveAcesso = (infNFe.get("Id") or "").strip()
    if chaveAcesso.upper().startswith("NFE"):
        chaveAcesso = chaveAcesso[3:]
    if not chaveAcesso:
        raise NFeParserError("Chave de acesso não encontrada no XML.")

    ide   = infNFe.find("nfe:ide", NS)
    emit  = infNFe.find("nfe:emit", NS)
    total = infNFe.find("nfe:total/nfe:ICMSTot", NS)

    dataEmissao = _data_emissao(_texto(ide, "nfe:dhEmi") or _texto(ide, "nfe:dEmi"))

    itens = []
    for det in infNFe.findall("nfe:det", NS):
        prod = det.find("nfe:prod", NS)
        if prod is None:
            continue
        itens.append({
            "codProdutoFornecedor": _texto(prod, "nfe:cProd"),
            "nomeProdutoNota":      _texto(prod, "nfe:xProd"),
            "unidade":              _texto(prod, "nfe:uCom"),
            "quantidade":           _decimal(prod, "nfe:qCom"),
            "valorUnitario":        _decimal(prod, "nfe:vUnCom"),
            "valorTotal":           _decimal(prod, "nfe:vProd"),
        })

    if not itens:
        raise NFeParserError("Nenhum produto encontrado na nota fiscal.")

    return {
        "chaveAcesso":    chaveAcesso,
        "numero":         _texto(ide, "nfe:nNF"),
        "serie":          _texto(ide, "nfe:serie"),
        "dataEmissao":    dataEmissao,
        "fornecedorNome": _texto(emit, "nfe:xNome"),
        "fornecedorCNPJ": _texto(emit, "nfe:CNPJ") or _texto(emit, "nfe:CPF"),
        "valorTotal":     _decimal(total, "nfe:vNF"),
        "itens":          itens,
    }
