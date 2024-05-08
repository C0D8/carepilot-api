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
        # try:
        data = request.get_json(force=True)  # Force to parse data as JSON even if content type is not set to application/json
        print(data)
        df = pd.DataFrame.from_dict(data)
        seed_data(df)

        #     df = pd.DataFrame(data)  # Construct DataFrame from JSON data
        #     seed_data(df)
        #     return {"message": "Data seeded"}, 201
        # except ValueError as ve:
        #     return {"error": str(ve)}, 400
        # except Exception as e:
        #     return {"error": "Internal Server Error"}, 500