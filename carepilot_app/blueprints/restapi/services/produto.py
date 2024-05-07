from carepilot_app.extensions.db import db #noqa
from carepilot_app.models.produto import Produto
from carepilot_app.schemas.produto import ProdutoSchema

list_produtos = ProdutoSchema(many=True)
produto_schema = ProdutoSchema()


def get_produtos():
    produtos = Produto.find_all()
    produtos = list_produtos.dump(produtos)
    return produtos


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

