from src.dao.produtoDAO       import ProdutoDAO
from src.dao.clienteDAO       import ClienteDAO
from src.dao.produtosObrasDAO import ProdutosObrasDAO
from src.modelo.produto       import produto as Produto
from src.modelo.cliente       import cliente as Cliente

dao_produto = ProdutoDAO()
dao_cliente = ClienteDAO()
dao_obras   = ProdutosObrasDAO()


print("=== CADASTRO DE CLIENTE ===")

while True:
    dadosCliente = Cliente()
    dadosCliente._idCliente       = int(input("ID do cliente: "))
    dadosCliente._nomeCliente     = input("Nome do cliente: ")
    dadosCliente._CNPJCPF         = input("CPF ou CNPJ: ")
    dadosCliente._enderecoCliente = input("Endereco: ")
    dadosCliente._contatoCliente  = input("Contato: ")
    dao_cliente.inserir(dadosCliente)

    continuar = input("Cadastrar mais um cliente? (s/n): ").strip().lower()
    if continuar != "s":
        break


print("\n=== CADASTRO DE PRODUTOS NO ESTOQUE ===")

while True:
    dadoProduto = Produto()
    dadoProduto._idProduto   = int(input("ID do produto: "))
    dadoProduto._nomeProduto = input("Nome do produto: ")
    dadoProduto._qtdProduto  = int(input("Quantidade em estoque: "))
    dadoProduto._descProduto = input("Descricao: ")
    dao_produto.inserir(dadoProduto)

    continuar = input("Cadastrar mais um produto? (s/n): ").strip().lower()
    if continuar != "s":
        break


print("\n=== ESTOQUE ATUAL ===")
produtos = dao_produto.buscar_todos()
for prod in produtos:
    print(f"  ID: {prod._idProduto} | Nome: {prod._nomeProduto} | Qtd: {prod._qtdProduto}")


print("\n=== CADASTRO DE OBRA ===")

dadosObra = {
    "idObra":     int(input("\nID da obra: ")),
    "codCliente": int(input("ID do cliente da obra: ")),
    "codProduto": int(input("ID do produto principal: ")),
    "descObra":   input("Descricao da obra: "),
    "dataObra":   input("Data da obra (AAAA-MM-DD): "),
    "statusObra": input("Status da obra: ")
}

produtosUsados = []

while True:
    idProduto  = int(input("ID do produto usado: "))
    quantidade = int(input("Quantidade a usar: "))
    produtosUsados.append({"idProduto": idProduto, "quantidade": quantidade})

    continuar = input("Adicionar mais um produto na obra? (s/n): ").strip().lower()
    if continuar != "s":
        break

dao_obras.cadastrar_obra_com_produtos(dadosObra, produtosUsados)


print("\n=== ESTOQUE APOS A OBRA ===")
produtos = dao_produto.buscar_todos()
for prod in produtos:
    print(f"  ID: {prod._idProduto} | Nome: {prod._nomeProduto} | Qtd: {prod._qtdProduto}")


print("\n=== PRODUTOS USADOS NA OBRA ===")
produtosDaObra = dao_obras.buscar_produtos_da_obra(id_obra=dadosObra["idObra"])
for item in produtosDaObra:
    print(f"  {item['nome']}: {item['quantidade']} unidades")