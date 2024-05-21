from flask import Blueprint
from flask_restx import Api
from .hello import api as hello_api
from .cliente import api as cliente_api
from .produto import api as produto_api
from .movimento import api as movimento_api
from .seed import api as seed_api
from .auth import api as auth_api
bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    bp,
    title="FLASK RESTPLUS API FOR CASAMED",
    version="1.0",
    doc="/docs",
)

api.add_namespace(hello_api)
api.add_namespace(cliente_api)
api.add_namespace(produto_api)
api.add_namespace(movimento_api)
api.add_namespace(seed_api)
api.add_namespace(auth_api)

def init_app(app):
    app.register_blueprint(bp)
    return app

