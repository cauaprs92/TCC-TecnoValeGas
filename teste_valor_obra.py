import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from src.controller.obraController import ObraController

ctrlObra = ObraController()

# Serviços usados nos cenários (ver docs/inserts.sql):
#   1 → Instalação de Ramal Residencial  → R$ 850,00
#   5 → Troca de Registro e Conector     → R$ 210,00
#   8 → Vistoria e Laudo Técnico         → R$ 380,00
# Cliente 1 e Produto 1 já existem via docs/inserts.sql.


def _buscar_id_obra(desc_obra: str):
    """Localiza o idObra da obra recém-cadastrada pelo descObra (único por cenário)."""
    candidatos = [o for o in ctrlObra.listar() if o[2] == desc_obra]
    if not candidatos:
        return None
    return max(candidatos, key=lambda o: o[0])[0]


def _valor_obra(id_obra: int):
    """valorObra é a última coluna retornada por buscar_por_id (ver _COLS_SELECT em obraDAO.py)."""
    obra = ctrlObra.buscar_por_id(id_obra)
    if not obra:
        return None
    valor = obra[-1]
    return float(valor) if valor is not None else None


print("=== CENÁRIO 1 — Obra com serviços vinculados ===")
descObra1 = "TESTE_VALOR_OBRA - Cenario 1 (2 servicos)"
dadosObra1 = {
    "codCliente": 1,
    "descObra":   descObra1,
    "dataInicio": "2026-01-10",
    "statusObra": "Em andamento",
    "respObra":   "Tecnico Teste",
}
sucesso, mensagem = ctrlObra.cadastrar(dadosObra1, [], [1, 5])
print(f"  Cadastro obra     → {sucesso} | {mensagem}")

idObra1 = _buscar_id_obra(descObra1)
sucesso, mensagem = ctrlObra.atualizar_status(idObra1, "Concluida")
print(f"  Concluir obra     → {sucesso} | {mensagem}")

valor1 = _valor_obra(idObra1)
bateu1 = valor1 is not None and abs(valor1 - 1060.00) < 0.01
print(f"  Obra com 2 serviços → valorObra esperado 1060.00 | valorObra real: {valor1} | {'OK' if bateu1 else 'FALHOU'}")


print("\n=== CENÁRIO 2 — Obra sem nenhum serviço vinculado ===")
descObra2 = "TESTE_VALOR_OBRA - Cenario 2 (sem servicos)"
dadosObra2 = {
    "codCliente": 1,
    "descObra":   descObra2,
    "dataInicio": "2026-01-11",
    "statusObra": "Em andamento",
    "respObra":   "Tecnico Teste",
}
produtosUsados2 = [{"idProduto": 1, "quantidade": 1}]
sucesso, mensagem = ctrlObra.cadastrar(dadosObra2, produtosUsados2, [])
print(f"  Cadastro obra     → {sucesso} | {mensagem}")

idObra2 = _buscar_id_obra(descObra2)
sucesso, mensagem = ctrlObra.atualizar_status(idObra2, "Concluida")
print(f"  Concluir obra     → {sucesso} | {mensagem}")

valor2 = _valor_obra(idObra2)
bateu2 = valor2 is not None and abs(valor2 - 0.00) < 0.01
print(f"  Obra sem serviços → valorObra esperado 0.00 | valorObra real: {valor2} | {'OK' if bateu2 else 'FALHOU'}")


print("\n=== CENÁRIO 3 — Reverter obra concluída para outro status ===")
sucesso, mensagem = ctrlObra.atualizar_status(idObra1, "Em andamento")
print(f"  Reverter status   → {sucesso} | {mensagem}")

valor3 = _valor_obra(idObra1)
bateu3 = valor3 is None
print(f"  Reverter obra concluída → valorObra esperado None | valorObra real: {valor3} | {'OK' if bateu3 else 'FALHOU'}")


print("\n=== CENÁRIO EXTRA — Obra com 3 serviços somados ===")
descObraExtra = "TESTE_VALOR_OBRA - Cenario Extra (3 servicos)"
dadosObraExtra = {
    "codCliente": 1,
    "descObra":   descObraExtra,
    "dataInicio": "2026-01-12",
    "statusObra": "Em andamento",
    "respObra":   "Tecnico Teste",
}
sucesso, mensagem = ctrlObra.cadastrar(dadosObraExtra, [], [1, 5, 8])
print(f"  Cadastro obra     → {sucesso} | {mensagem}")

idObraExtra = _buscar_id_obra(descObraExtra)
sucesso, mensagem = ctrlObra.atualizar_status(idObraExtra, "Concluida")
print(f"  Concluir obra     → {sucesso} | {mensagem}")

valorExtra = _valor_obra(idObraExtra)
bateuExtra = valorExtra is not None and abs(valorExtra - 1440.00) < 0.01
print(f"  Obra com 3 serviços → valorObra esperado 1440.00 | valorObra real: {valorExtra} | {'OK' if bateuExtra else 'FALHOU'}")


print("\n=== RESUMO ===")
print("Todos os testes devem mostrar OK. Se algum mostrar FALHOU, revisar a lógica em obraDAO.atualizar_status.")
