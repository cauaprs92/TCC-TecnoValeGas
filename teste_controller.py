from src.controller.loginController   import LoginController
from src.controller.clienteController import ClienteController
from src.controller.produtoController import ProdutoController
from src.controller.obraController    import ObraController

ctrlLogin   = LoginController()
ctrlCliente = ClienteController()
ctrlProduto = ProdutoController()
ctrlObra    = ObraController()


print("=== TESTE LOGIN ===")
sucesso, mensagem = ctrlLogin.autenticar("adm123@gmail.com", "adm123")
print(f"  Login correto     → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlLogin.autenticar("errado@gmail.com", "senhaerrada")
print(f"  Login incorreto   → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlLogin.autenticar("", "")
print(f"  Login vazio       → {sucesso} | {mensagem}")


print("\n=== TESTE CLIENTE ===")
sucesso, mensagem = ctrlCliente.cadastrar(1, "Joao Silva", "123.456.789-00", "Rua das Flores, 100", "(11) 99999-9999")
print(f"  Cadastro correto  → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlCliente.cadastrar(2, "Jo", "123.456.789-00", "Rua das Flores, 100", "")
print(f"  Nome curto        → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlCliente.cadastrar(3, "Joao2Silva", "123.456.789-00", "Rua X", "")
print(f"  Nome com numero   → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlCliente.cadastrar(4, "Maria", "123", "Rua X", "")
print(f"  CPF invalido      → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlCliente.cadastrar(1, "Pedro", "987.654.321-00", "Rua Y", "")
print(f"  ID duplicado      → {sucesso} | {mensagem}")


print("\n=== TESTE PRODUTO ===")
sucesso, mensagem, aviso = ctrlProduto.cadastrar(1, "Cano PVC", 50, "Cano 6 metros")
print(f"  Qtd ok            → {sucesso} | {mensagem}")

sucesso, mensagem, aviso = ctrlProduto.cadastrar(2, "Mangueira", 3, "Mangueira 1 metro")
print(f"  Qtd alerta (3)    → {sucesso} | {mensagem} | aviso: {aviso}")

sucesso, mensagem, aviso = ctrlProduto.cadastrar(3, "Valvula", 30, "Valvula 3/4")
print(f"  Qtd abaixo min    → {sucesso} | {mensagem} | aviso: {aviso}")

sucesso, mensagem, aviso = ctrlProduto.cadastrar(4, "Ab", 10, "Nome curto")
print(f"  Nome curto        → {sucesso} | {mensagem}")

sucesso, mensagem, aviso = ctrlProduto.cadastrar(5, "Registro", -1, "Desc")
print(f"  Qtd negativa      → {sucesso} | {mensagem}")

sucesso, mensagem, aviso = ctrlProduto.cadastrar(6, "Tubo", 99999, "Desc")
print(f"  Qtd acima max     → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlProduto.verificar_estoque(2, 1)
print(f"  Estoque baixo     → {sucesso} | {mensagem}")


print("\n=== TESTE OBRA ===")
dadosObra = {
    "idObra":     1,
    "codCliente": 1,
    "codProduto": 1,
    "descObra":   "Instalacao de gas residencial",
    "dataObra":   "2026-03-14",
    "statusObra": "Em andamento",
    "respObra":   "Carlos"
}

produtosUsados = [
    {"idProduto": 1, "quantidade": 5},
    {"idProduto": 3, "quantidade": 2},
]

sucesso, mensagem = ctrlObra.cadastrar(dadosObra, produtosUsados)
print(f"  Obra correta      → {sucesso} | {mensagem}")

dadosObraSemCliente = {**dadosObra, "idObra": 2, "codCliente": 999}
sucesso, mensagem = ctrlObra.cadastrar(dadosObraSemCliente, produtosUsados)
print(f"  Cliente inexist.  → {sucesso} | {mensagem}")

dadosObraSemResp = {**dadosObra, "idObra": 3, "respObra": ""}
sucesso, mensagem = ctrlObra.cadastrar(dadosObraSemResp, produtosUsados)
print(f"  Sem responsavel   → {sucesso} | {mensagem}")

dadosObraStatusInv = {**dadosObra, "idObra": 4, "statusObra": "Fazendo"}
sucesso, mensagem = ctrlObra.cadastrar(dadosObraStatusInv, produtosUsados)
print(f"  Status invalido   → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlObra.atualizar_status(1, "Concluida")
print(f"  Status valido     → {sucesso} | {mensagem}")

sucesso, mensagem = ctrlObra.atualizar_status(1, "Voando")
print(f"  Status invalido   → {sucesso} | {mensagem}")