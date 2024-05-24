from carepilot_app.extensions.serializers import ma
from carepilot_app.models.produto import Produto


class ProdutoSchema (ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Produto
        load_instance = True
        unknown = 'exclude'
        include_fk = True

