from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.blueprints.restapi.services.produto import get_produtos, get_produto, post_produto, update_produto, delete_produto, product_cliente
from flask_restx import fields
from flask import request


api = Namespace('produtos', description='Produtos operations')

item = api.model('Produto', {

    'valor': fields.Float(required=True, description='The value'),
    'data': fields.Date(required=True, description='The date'),
    'descricao': fields.String(required=True, description='The description'),
    'tipo': fields.String(required=False, description='The type')
})

update_item = api.model('Produto', {
    'valor': fields.Float(required=False, description='The value'),
    'data': fields.Date(required=False, description='The date'),
    'descricao': fields.String(required=False, description='The description'),
    'tipo': fields.String(required=False, description='The type')
})

@api.route('')
class Produtos(Resource):

    @auth.login_required(role='admin')
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        print(page, per_page)
        return get_produtos(page, per_page)
    
    @auth.login_required(role='admin')
    @api.expect(item)
    def post(self):
        produto_json = request.get_json()
        return post_produto(produto_json)


@api.route('/<int:produto_id>')
class Produto(Resource):

    @auth.login_required(role='admin')
    def get(self, produto_id):
        return get_produto(produto_id)
    
    
    @auth.login_required(role='admin')
    def delete(self, produto_id):
        return delete_produto(produto_id)
    
    @auth.login_required(role='admin')
    @api.expect(update_item)
    def put(self, produto_id):
        produto_json = request.get_json()
        return update_produto(produto_id, produto_json)
    
   
@api.route('/<int:produto_id>/clientes')
class ProdutosCliente(Resource):
    
    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return product_cliente(cliente_id)
    

@api.route('/<int:produto_id>/grafico')
class ProdutosCliente(Resource):
    
    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return product_grafico(cliente_id)