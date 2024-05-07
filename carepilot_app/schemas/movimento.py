from carepilot_app.extensions.serializers import ma
from carepilot_app.models.movimento import Movimento


class MovimentoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Movimento
        load_instance = True
        unknown = 'exclude'
