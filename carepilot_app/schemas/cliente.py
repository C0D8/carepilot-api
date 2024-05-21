from carepilot_app.extensions.serializers import ma
from carepilot_app.models.cliente import Cliente


class ClienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cliente
        load_instance = True
        unknown = 'exclude'
        include_fk = True
