from carepilot_app.extensions.db import db #noqa
from carepilot_app.models.cliente import Cliente
from carepilot_app.schemas.cliente import ClienteSchema
from carepilot_app.models.movimento import Movimento
from carepilot_app.schemas.movimento import MovimentoSchema

import pandas as pd

list_clientes = ClienteSchema(many=True)
cliente_schema = ClienteSchema()
movimento_schema = MovimentoSchema()
list_movimentos = MovimentoSchema(many=True)


def get_clientes(page, per_page, nome=None, usuario_id=None):
    if nome:
        clientes = db.session.query(Cliente).filter(Cliente.id == nome and Cliente.user_id == usuario_id).paginate(page=page, per_page=per_page)
        return {
            "page": clientes.page,
            "per_page": clientes.per_page,
            "total_clientes": clientes.total,
            "clientes": list_clientes.dump(clientes.items)
        }
    
    cleintes = db.session.query(Cliente).paginate(page=page, per_page=per_page)
    
    return{
        "page": cleintes.page,
        "per_page": cleintes.per_page,
        "total_clientes": cleintes.total,
        "clientes": list_clientes.dump(cleintes.items)
    }
    


def get_all():
    clientes = Cliente.find_all()
    clientes = list_clientes.dump(clientes)
    # print(clientes)
    return clientes


def get_movimentos(cliente_id): 
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404

    movimentos = cliente.movimentos
    movimentos = list_movimentos.dump(movimentos)
    return movimentos


def get_movimentos_pag(cliente_id): 
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404

    # Query para obter os movimentos paginados
    mov_paginated = Movimento.query.filter_by(cliente_id=cliente_id).paginate(page=1, per_page=10)

    # Serializa os movimentos
    movimentos = list_movimentos.dump(mov_paginated.items)

    return {
        "page": mov_paginated.page,
        "per_page": mov_paginated.per_page,
        "total_movimentos": mov_paginated.total,
        "movimentos": movimentos
    }


def get_cliente(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404
    cliente = cliente_schema.dump(cliente)
    return cliente

def post_cliente(data):
    cliente = cliente_schema.load(data, session=db.session)
    cliente.save_to_db()
    return cliente_schema.dump(cliente), 201


def update_cliente(cliente_id, data):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404
    for key, value in data.items():
        setattr(cliente, key, value)
    cliente.update_to_db()
    return cliente_schema.dump(cliente), 200

    
    

def delete_cliente(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404

    cliente.delete_from_db()
    return {"message": "Cliente deleted"}, 200



def produtos_comprados(cliente_id):

    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404
    
    movimentos = cliente.movimentos
    #Pegar os produtos que ele mais comprou

    produtos = []

    for movimento in movimentos:
        produtos.append(movimento.produto_id)
    
    #retornar os 5 ids que mais aparecem 
    produtos = pd.Series(produtos)
    produtos = produtos.value_counts()
    produtos = produtos.head(5)
    produtos = produtos.reset_index()
    produtos.columns = ["produto", "quantidade"]
    produtos = produtos.to_dict(orient='records')
    return produtos


# # Criando a sessão do SQLAlchemy
# Session = sessionmaker(bind=engine)
# session = Session()

# # Exemplo de uso
# cliente_id = 1  # Suponha que o ID do cliente seja 1
# print(produtos_comprados(session, cliente_id))

    # produtos = []
    # for movimento in movimentos:
    #     produtos.append(movimento.produto.json())
    # return produtos



def cliente_similar(cliente_id) :
    # return []






    # df_produto = movimentos.groupby(["codigo_cliente", "cod_produto"]).agg({'quantidade': 'sum'}).reset_index()
    # df_user = df_produto[df_produto["codigo_cliente"] == userid]
    # df_user = df_user.sort_values("quantidade", ascending=False)
    # df_others = df_produto[df_produto["codigo_cliente"] != userid]
    # # Pega os clientes que mais compraram os mesmos top 3 produtos
    # content = df_others[df_others["cod_produto"].isin(df_user["cod_produto"])]
    # content = content.groupby("codigo_cliente")["cod_produto"].count().reset_index()
    # content = content.sort_values("cod_produto", ascending=False)
    # content = content[content["codigo_cliente"] != 1]
    # content = content.head(5)
    # content.columns = ["Cliente", "Quantidade de produtos em comum"]


    movimentos = Movimento.find_all()

    movimentos = pd.DataFrame([movimento.json() for movimento in movimentos])

    # movimentos = movimentos.groupby(["cliente_id", "produto_id"]).agg({'quantidade': 'sum'}).reset_index()
    df_produto = movimentos.groupby(["cliente_id", "produto_id"]).agg({'quantidade': 'sum'}).reset_index()
    df_user = df_produto[df_produto["cliente_id"] == cliente_id]
    df_user = df_user.sort_values("quantidade", ascending=False)
    df_others = df_produto[df_produto["cliente_id"] != cliente_id]
    # Pega os clientes que mais compraram os mesmos top 3 produtos
    content = df_others[df_others["produto_id"].isin(df_user["produto_id"])]
    content = content.groupby("cliente_id")["produto_id"].count().reset_index()
    content = content.sort_values("produto_id", ascending=False)
    content = content[content["cliente_id"] != 1]
    content = content.head(5)
    content.columns = ["Cliente", "Quantidade de produtos em comum"]

    return content.to_dict(orient='records')





    # cliente = Cliente.find_by_id(cliente_id)

    # if not cliente:
    #     return {"message": "Cliente not found"}, 404
    
    # #pegar os produtos mais comprados por ele
    # produtos_mais_comprados = produtos_comprados(cliente_id)
    # #pegar os 3 produtos mais comprados
    # produtos_mais_comprados = produtos_mais_comprados[:3]

    # ids = [produto["produto"] for produto in produtos_mais_comprados]

    # #ver para todos os clientes quem tem os mesmos produtos mais comprados

    # clientes = Cliente.find_all()
    # for cliente in clientes:
    #     prodds = produtos_comprados(cliente.id)
    #     prodds = prodds[:3]
    #     prodds = [produto["produto"] for produto in prodds]

    #     if set(ids) == set(prodds):
    #         print(cliente.id)