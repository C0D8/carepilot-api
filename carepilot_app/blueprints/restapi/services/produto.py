from carepilot_app.extensions.db import db #noqa
from carepilot_app.models.produto import Produto
from carepilot_app.schemas.produto import ProdutoSchema
from carepilot_app.models.movimento import Movimento
from carepilot_app.schemas.movimento import MovimentoSchema

import pandas as pd

list_produtos = ProdutoSchema(many=True)
produto_schema = ProdutoSchema()
movimento_schema = MovimentoSchema()
list_movimentos = MovimentoSchema(many=True)

# def get_produtos():
#     produtos = Produto.find_all()
#     produtos = list_produtos.dump(produtos)
#     return produtos

def get_produtos(page, per_page):
    prod = db.session.query(Produto).paginate(page=page, per_page=per_page)
    
    return{
        "page": prod.page,
        "per_page": prod.per_page,
        "total_produtos": prod.total,
        "produtos": list_produtos.dump(prod.items)
    }

def get_produto(produto_id):
    produto = Produto.find_by_id(produto_id)

    if not produto:
        return {"message": "produto not found"}, 404
    produto = produto_schema.dump(produto)
    return produto

def post_produto(data):
    produto = produto_schema.load(data)
    produto.save_to_db()
    return produto_schema.dump(produto), 201


def update_produto(produto_id, data):
    produto = Produto.find_by_id(produto_id)

    if not produto:
        return {"message": "Produto not found"}, 404
    for key, value in data.items():
        setattr(produto, key, value)
    produto.update_to_db()
    return produto_schema.dump(produto), 200


def delete_produto(produto_id):
    produto = Produto.find_by_id(produto_id)

    if not produto:
        return {"message": "Produto not found"}, 404

    produto.delete_from_db()
    return {"message": "Produto deleted"}, 200

def product_cliente(product_id):

    movimentos = Movimento.find_all()
    movimentos = pd.DataFrame([movimento.json() for movimento in movimentos])

    df_produto = movimentos.groupby(["cliente_id", "produto_id"]).agg({'quantidade': 'sum'}).reset_index()
    content = df_produto[df_produto["cod_produto"] == product_id]
    content = content.drop("cod_produto", axis=1)
    content = content.sort_values("quantidade", ascending=False)
    content = content.head(5)
    content.columns = ["Cliente", "Quantidade"]

    return content.to_dict(orient='records')

def product_grafico(product_id):

    movimentos = Movimento.find_all()
    movimentos = pd.DataFrame([movimento.json() for movimento in movimentos])
    
    content = movimentos[movimentos["cod_produto"] == product_id]
    content = content.drop("cod_produto", axis=1)
    content["data_documento"] = pd.to_datetime(content["data_documento"], format="%d/%m/%Y %H:%M:%S")

    # Agrupar por semana
    content.set_index("data_documento", inplace=True)
    content = content.resample('W').sum()
    content = content.reset_index()

    return content.to_dict(orient='records')