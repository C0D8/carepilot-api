from flask_restx import Resource, Namespace
from carepilot_app.extensions.auth import auth
from carepilot_app.scripts.seed_data import seed_data
from carepilot_app.scripts.create_correlation import create_correlation, get_similar_users
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
        # print(data)
        #get no request param para pegar o id no usuario
        
        id_user = request.args.get("user_id")
        print("ECHEI AQUI22222", id_user)
        df = pd.DataFrame.from_dict(data)
        seed_data(df, id_user)

        #     df = pd.DataFrame(data)  # Construct DataFrame from JSON data
        #     seed_data(df)
        #     return {"message": "Data seeded"}, 201
        # except ValueError as ve:
        #     return {"error": str(ve)}, 400
        # except Exception as e:
        #     return {"error": "Internal Server Error"}, 500


@api.route('/correlation')
class Correlation(Resource):

    @auth.login_required(role='admin')
    def get(self):
        try:
            create_correlation()
            return {"message": "Correlation created"}, 201
        except Exception as e:
            print(e)
            return {"error": "Internal Server Error"}, 500
        
@api.route('/similar_users/<int:user_id>')
class SimilarUsers(Resource):

    @auth.login_required(role='admin')
    def get(self, user_id):
        
        user = get_similar_users(user_id)
        return {"message": "Similar users fetched",
                "users": user}, 200
    