from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.scripts.seed_data import seed_data
from flask_restx import fields
from flask import request
import pandas as pd




api = Namespace('Seed', description='Seed operations')



@api.route('')
class Seed(Resource):

    @auth.login_required(role='admin')
    def post(self):
        data = request.get_json()
        df = pd.DataFrame(data)
        seed_data(df)
        return {"message": "Data seeded"}, 201