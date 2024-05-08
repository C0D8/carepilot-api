from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.blueprints.restapi.services.cliente import get_clientes, get_cliente, post_cliente, update_cliente, delete_cliente, produtos_comprados,cliente_similar, get_movimentos
from flask_restx import fields
from flask import request


api = Namespace('clientes', description='Clientes operations')

item = api.model('Cliente', {
    'nome': fields.String(required=True, description='The name'),
    'cpf': fields.String(required=True, description='The cpf'),
    'data_nascimento': fields.Date(required=True, description='The birth date')
})

update_item = api.model('Cliente', {
    'nome': fields.String(description='The name'),
    'cpf': fields.String(description='The cpf'),
    'data_nascimento': fields.Date(description='The birth date')
})

@api.route('')
class Clientes(Resource):

    @auth.login_required(role='admin')
    def get(self):
        return get_clientes()
    
    @auth.login_required(role='admin')
    @api.expect(item)
    def post(self):
        cliente_json = request.get_json()
        return post_cliente(cliente_json)


@api.route('/<int:cliente_id>')
class Cliente(Resource):

    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return get_cliente(cliente_id)
    
    
    @auth.login_required(role='admin')
    def delete(self, cliente_id):
        return delete_cliente(cliente_id)
    
    @auth.login_required(role='admin')
    @api.expect(update_item)
    def put(self, cliente_id):
        cliente_json = request.get_json()
        return update_cliente(cliente_id, cliente_json)
    
@api.route('/<int:cliente_id>/produtos')
class ProdutosCliente(Resource):
    
    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return produtos_comprados(cliente_id)
    
@api.route('/<int:cliente_id>/similar')
class ProdutosClientes(Resource):
    
    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return cliente_similar(cliente_id)
    
   


@api.route('/<int:cliente_id>/movimentos')
class MovimentosCliente(Resource):
    
    @auth.login_required(role='admin')
    def get(self, cliente_id):
        return get_movimentos(cliente_id)