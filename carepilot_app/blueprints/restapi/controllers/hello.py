# from flask import request
from flask_restx import Resource, Namespace
# from carepilot_app.extensions.db import db
# from carepilot_app.extensions.auth import auth
# from carepilot_app.server.instance import server
from carepilot_app.blueprints.restapi.services.hello import hello_service


api = Namespace('hello', description='Hello World')


@api.route('/')
class Hello(Resource):
    def get(self):
        return hello_service()