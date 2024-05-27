from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.blueprints.restapi.services.movimento import get_movimentos, get_movimento, post_movimento, update_movimento, delete_movimento
from flask_restx import fields
from flask import request
import pandas as pd
import numpy as np

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
        print(movimento_json)
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
    
   
@api.route('/intervalo')
class MovimentoIntervalo(Resource):

    @auth.login_required(role='admin')
    def get(self):
        movimentos = get_movimentos()
        df = pd.DataFrame(movimentos)

        # Convertendo a data de documento para datetime
        df['data'] = pd.to_datetime(df['data'], format="%Y-%m-%d")
        print(df.info)
        # Count the number of unique dates for each client
        date_counts = df.groupby('cliente_id')['data'].nunique()
        valid_clients = date_counts[date_counts >= 1].index

        # Filter the dataframe to keep only the valid clients
        df = df[df['cliente_id'].isin(valid_clients)]
        print(df.info())
        # Calculate the maximum time difference between data dates for each group
        df['time_diff'] = df.groupby('cliente_id')['data'].diff().dt.days
        df['max_time_diff'] = df.groupby('cliente_id')['time_diff'].transform('max')

        # Get the maximum time difference for each client
        max_time_diff = df.groupby('cliente_id')['max_time_diff'].first()

        return max_time_diff.tolist()
