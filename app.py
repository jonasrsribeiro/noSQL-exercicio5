import json
from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://a49d8831.databases.neo4j.io"
AUTH = ("neo4j", "1R0AP46xZDoDj6FvwgIkGXExhY1pWkuc20etOeuZP4U")


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self._uri = uri
        self._user = user
        self._password = pwd
        self._driver = None

    def connect(self):
        self._driver = GraphDatabase.driver(
            self._uri, auth=(self._user, self._password)
        )

    def close(self):
        if self._driver is not None:
            self._driver.close()


create_usuario_query = """
CREATE (u:Usuario {id: $id, nome: $nome, sobrenome: $sobrenome, cpf: $cpf, senha: $senha, email: $email, enderecos: $enderecos})
"""

create_vendedor_query = """
CREATE (v:Vendedor {id: $id, nome: $nome, sobrenome: $sobrenome, cpf: $cpf, email: $email, cnpj: $cnpj, enderecos: $enderecos})
"""

create_produto_query = """
CREATE (p:Produto {id: $id, nome: $nome, preco: $preco, descricao: $descricao, categoria: $categoria})
"""

create_compra_query = """
MATCH (u:Usuario {id: $usuario_id}), (p:Produto {id: $produto_id})
CREATE (u)-[:FEZ_COMPRA {id: $id, data_compra: $data_compra, data_entrega: $data_entrega, status_compra: $status_compra}]->(p)
"""

create_favorito_query = """
MATCH (u:Usuario {id: $usuario_id}), (p:Produto {id: $produto_id})
CREATE (u)-[:ADICIONOU_FAVORITO {id: $id}]->(p)
"""


def get_all(collection_name):
    query = f"MATCH (n:{collection_name}) RETURN n"
    
    with connection._driver.session() as session:
        result = session.run(query)

        for record in result:
            node = record['n']
            print(f"{collection_name}s disponíveis:")
            print("ID:", node.id)
            print("Propriedades:", node.properties)


def create_usuario(tx, nome, sobrenome, cpf, email, enderecos):
    result = tx.run(
        "CREATE (u:Usuario {nome: $nome, sobrenome: $sobrenome, cpf: $cpf, email: $email}) RETURN id(u) as user_id",
        nome=nome,
        sobrenome=sobrenome,
        cpf=cpf,
        email=email,
    )

    user_id = result.single()["user_id"]

    for endereco in enderecos:
        tx.run(
            "MATCH (u:Usuario) WHERE id(u) = $user_id "
            "CREATE (u)-[:MORA_EM]->(e:Endereco {rua: $rua, num: $num, bairro: $bairro, cidade: $cidade, estado: $estado, cep: $cep})",
            user_id=user_id,
            **endereco,
        )

    return user_id


def read_usuario(tx, nome):
    result = tx.run(
        "MATCH (u:Usuario) WHERE u.nome CONTAINS $nome "
        "RETURN u.nome, u.sobrenome, u.cpf, u.email",
        nome=nome,
    )
    for record in result:
        print(record)


def create_vendedor(tx, nome, sobrenome, cpf, email, cnpj, enderecos):
    result = tx.run(
        "CREATE (v:Vendedor {nome: $nome, sobrenome: $sobrenome, cpf: $cpf, email: $email, cnpj: $cnpj}) "
        "RETURN id(v) as vendedor_id",
        nome=nome,
        sobrenome=sobrenome,
        cpf=cpf,
        email=email,
        cnpj=cnpj,
    )

    vendedor_id = result.single()["vendedor_id"]

    for endereco in enderecos:
        tx.run(
            "MATCH (v:Vendedor) WHERE id(v) = $vendedor_id "
            "CREATE (v)-[:MORA_EM]->(e:Endereco {rua: $rua, num: $num, bairro: $bairro, "
            "cidade: $cidade, estado: $estado, cep: $cep})",
            vendedor_id=vendedor_id,
            **endereco,
        )

    return vendedor_id


def read_vendedor(tx, nome):
    result = tx.run(
        "MATCH (v:Vendedor) WHERE v.nome CONTAINS $nome "
        "RETURN v.nome, v.sobrenome, v.cpf, v.email",
        nome=nome,
    )
    for record in result:
        print(record)


def create_produto(tx, nome, preco, descricao, categoria):
    result = tx.run(
        "CREATE (p:Produto {nome: $nome, preco: $preco, descricao: $descricao, categoria: $categoria}) "
        "RETURN id(p) as produto_id",
        nome=nome,
        preco=preco,
        descricao=descricao,
        categoria=categoria,
    )

    return result.single()["produto_id"]


def read_produto(tx, nome):
    result = tx.run(
        "MATCH (p:Produto) WHERE p.nome CONTAINS $nome "
        "RETURN p.nome, p.preco, p.descricao, p.categoria",
        nome=nome,
    )
    for record in result:
        print(record)


def create_compra(tx, data_compra, data_entrega, status_compra, usuario_id, produto_id):
    result = tx.run(
        "MATCH (u:Usuario), (p:Produto) "
        "WHERE id(u) = $usuario_id AND id(p) = $produto_id "
        "CREATE (u)-[:FEZ_COMPRA {data_compra: $data_compra, data_entrega: $data_entrega, status_compra: $status_compra}]->(p)",
        data_compra=data_compra,
        data_entrega=data_entrega,
        status_compra=status_compra,
        usuario_id=usuario_id,
        produto_id=produto_id,
    )

    return result.single()


def read_compra(tx, compra_id):
    result = tx.run(
        "MATCH (u:Usuario)-[c:FEZ_COMPRA]->(p:Produto) "
        "WHERE c.id = $compra_id "
        "RETURN u.nome, p.nome, c.data_compra, c.data_entrega, c.status_compra",
        compra_id=compra_id,
    )
    for record in result:
        print(record)


def create_favorito(tx, usuario_id, produto_id):
    result = tx.run(
        "MATCH (u:Usuario), (p:Produto) "
        "WHERE id(u) = $usuario_id AND id(p) = $produto_id "
        "CREATE (u)-[:ADICIONOU_FAVORITO]->(p)",
        usuario_id=usuario_id,
        produto_id=produto_id,
    )

    return result.single()["favorito_id"]


def list_favoritos(tx, usuario_id):
    result = tx.run(
        "MATCH (u:Usuario)-[:ADICIONOU_FAVORITO]->(p:Produto) "
        "WHERE u.id = $usuario_id "
        "RETURN p.nome",
        usuario_id=usuario_id,
    )
    for record in result:
        print(record)


# Conectar ao banco de dados Neo4j
connection = Neo4jConnection(
    URI, "neo4j", "1R0AP46xZDoDj6FvwgIkGXExhY1pWkuc20etOeuZP4U"
)
connection.connect()


def cli():
    key = ""
    sub = 0
    while key.upper() != "S":
        print("1-CRUD Usuário")
        print("2-CRUD Vendedor")
        print("3-CRUD Produto")
        print("4-CRUD Comprar")
        print("5-CRUD Favoritos")
        key = input("Digite a opção desejada? (S para sair) ")

        if key == "1":
            usuario_menu()

        elif key == "2":
            vendedor_menu()

        elif key == "3":
            produto_menu()

        elif key == "4":
            compra_menu()

        elif key == "5":
            favorito_menu()

        else:
            print("Opção inválida. Tente novamente.")


def usuario_menu():
    sub = 0
    print("Menu do Usuário")
    print("1-Create Usuário")
    print("2-Read Usuário")
    sub = input("Digite a opção desejada? (V para voltar) ")

    if sub == "1":
        print("Create usuario")
        nome = input("Digite o nome do usuário: ")
        sobrenome = input("Digite o sobrenome do usuário: ")
        cpf = input("Digite o CPF do usuário: ")
        email = input("Digite o email do usuário: ")

        enderecos = []
        key = input("Deseja cadastrar um novo endereço (S/N)? ")

        while key.upper() == "S":
            rua = input("Rua: ")
            num = input("Num: ")
            bairro = input("Bairro: ")
            cidade = input("Cidade: ")
            estado = input("Estado: ")
            cep = input("CEP: ")

            endereco = {
                "rua": rua,
                "num": num,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado,
                "cep": cep,
            }

            enderecos.append(endereco)
            key = input("Deseja cadastrar um novo endereço (S/N)? ")

        with connection._driver.session() as session:
            session.write_transaction(
                create_usuario, nome, sobrenome, cpf, email, enderecos
            )

    elif sub == "2":
        nome = input("Read usuário, deseja algum nome específico? ")
        with connection._driver.session() as session:
            session.read_transaction(read_usuario, nome)


def vendedor_menu():
    sub = 0
    print("Menu do Vendedor")
    print("1-Create Vendedor")
    print("2-Read Vendedor")
    sub = input("Digite a opção desejada? (V para voltar) ")

    if sub == "1":
        print("Create Vendedor")
        nome = input("Digite o nome do vendedor: ")
        sobrenome = input("Digite o sobrenome do vendedor: ")
        cpf = input("Digite o CPF do vendedor: ")
        email = input("Digite o email do vendedor: ")
        cnpj = input("Digite o CNPJ do vendedor: ")

        enderecos = []
        key = input("Deseja cadastrar um novo endereço (S/N)? ")

        while key.upper() == "S":
            rua = input("Rua: ")
            num = input("Num: ")
            bairro = input("Bairro: ")
            cidade = input("Cidade: ")
            estado = input("Estado: ")
            cep = input("CEP: ")

            endereco = {
                "rua": rua,
                "num": num,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado,
                "cep": cep,
            }

            enderecos.append(endereco)
            key = input("Deseja cadastrar um novo endereço (S/N)? ")

        with connection._driver.session() as session:
            session.write_transaction(
                create_vendedor, nome, sobrenome, cpf, email, cnpj, enderecos
            )

    elif sub == "2":
        nome = input("Read usuário, deseja algum nome especifico? ")
        with connection._driver.session() as session:
            session.read_transaction(read_vendedor, nome)


def produto_menu():
    sub = 0
    print("Menu do Produto")
    print("1. Create Produto")
    print("2. Read Produto")
    sub = input("Digite a opção desejada? (V para voltar) ")

    if sub == "1":
        print("Create Produto")
        nome = input("Digite o nome do produto: ")
        preco = float(input("Digite o preço do produto: "))
        descricao = input("Digite a descrição do produto: ")
        categoria = input("Digite a categoria do produto: ")

        with connection._driver.session() as session:
            session.write_transaction(create_produto, nome, preco, descricao, categoria)

    elif sub == "2":
        nome = input("Read Produto, deseja algum nome específico? ")
        with connection._driver.session() as session:
            session.read_transaction(read_produto, nome)


def compra_menu():
    sub = 0
    print("Menu da Compra")
    print("1. Create Compra")
    print("2. Read Compra")
    sub = input("Digite a opção desejada? (V para voltar) ")

    if sub == "1":
        print("Create Compra")
        data_compra = input("Digite a data da compra: ")
        data_entrega = input("Digite a data de entrega: ")
        status_compra = input("Digite o status da compra: ")
        usuario_id = int(input("Digite o ID do usuário: "))
        produto_id = int(input("Digite o ID do produto: "))

        with connection._driver.session() as session:
            session.write_transaction(
                create_compra,
                data_compra,
                data_entrega,
                status_compra,
                usuario_id,
                produto_id,
            )

    elif sub == "2":
        compra_id = input("Read Compra, deseja algum ID específico? ")
        with connection._driver.session() as session:
            session.read_transaction(read_compra, compra_id)


def favorito_menu():
    sub = 0
    print("Menu de Favoritos")
    print("1. Adicionar Favorito")
    print("2. Listar Favoritos")
    sub = input("Digite a opção desejada? (V para voltar) ")

    if sub == "1":
        print("Adicionar Favorito")
        usuario_id = int(input("Digite o ID do usuário: "))
        produto_id = int(input("Digite o ID do produto: "))

        with connection._driver.session() as session:
            session.write_transaction(create_favorito, usuario_id, produto_id)

    elif sub == "2":
        get_all("usuario")
        usuario_id = int(input("Digite o ID do usuário para listar seus favoritos: "))
        with connection._driver.session() as session:
            session.read_transaction(list_favoritos, usuario_id)


if __name__ == "__main__":
    with connection._driver.session() as session:
        cli()

connection.close()
