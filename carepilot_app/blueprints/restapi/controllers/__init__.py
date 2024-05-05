from .hello import api as hello_api
from flask import Blueprint
from flask_restx import Api

bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    bp,
    title="FLASK RESTPLUS API FOR CASAMED",
    version="1.0",
    doc="/docs",
)

api.add_namespace(hello_api)

def init_app(app):
    app.register_blueprint(bp)
    return app

