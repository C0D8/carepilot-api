from flask_restx import Resource, fields, Namespace
from flask import request
from carepilot_app.models.user import User
#check_password_hash
from carepilot_app.blueprints.restapi.services.auth import auth_login, auth_roles


api = Namespace("auth", description="Auth related operations", path="/auth")




item = api.model(
    "auth",
    {
        "username": fields.String(50),
        "password": fields.String(50),
    },
)

@api.route("/login")
class Auth(Resource):
    @api.expect(item)
    def post(self):
        data = request.get_json()
        return auth_login(data)


#rota que recebe o nome do usuário e devolve o as roles do usuário
        
@api.route("/roles")
class AuthRoles(Resource):
    def get(self):
        username = request.args.get("username")
        return auth_roles(username)