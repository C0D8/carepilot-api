from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.blueprints.restapi.services.movimento import get_movimentos, get_movimento, post_movimento, update_movimento, delete_movimento
from flask_restx import fields
from flask import request


api = Namespace('movimentos', description='Movimentos operations')

item = api.model('Movimento', {
    
    'valor': fields.Float(required=True, description='The value'),
    'data': fields.Date(required=True, description='The date'),
    'descricao': fields.String(required=True, description='The description'),
    'cliente_id': fields.Integer(required=True, description='The client id'),
    'produto_id': fields.Integer(required=True, description='The product id')

})

update_item = api.model('Movimento', {
    'valor': fields.Float(required=False, description='The value'),
    'data': fields.Date(required=False, description='The date'),
    'descricao': fields.String(required=False, description='The description'),
    'cliente_id': fields.Integer(required=False, description='The client id'),
    'produto_id': fields.Integer(required=False, description='The product id')
})

@api.route('')
class Movimentos(Resource):

    @auth.login_required(role='admin')
    def get(self):
        return get_movimentos()
    
    @auth.login_required(role='admin')
    @api.expect(item)
    def post(self):
        movimento_json = request.get_json()
        return post_movimento(movimento_json)


@api.route('/<int:movimento_id>')
class Movimento(Resource):

    @auth.login_required(role='admin')
    def get(self, movimento_id):
        return get_movimento(movimento_id)
    
    
    @auth.login_required(role='admin')
    def delete(self, movimento_id):
        return delete_movimento(movimento_id)
    
    @auth.login_required(role='admin')
    @api.expect(update_item)
    def put(self, movimento_id):
        movimento_json = request.get_json()
        return update_movimento(movimento_id, movimento_json)
    
   
