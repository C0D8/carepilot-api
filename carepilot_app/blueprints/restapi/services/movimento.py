from carepilot_app.extensions.db import db #noqa
from carepilot_app.models.movimento import Movimento
from carepilot_app.schemas.movimento import MovimentoSchema

list_movimentos = MovimentoSchema(many=True)
movimento_schema = MovimentoSchema()


def get_movimentos():
    movimentos = Movimento.find_all()
    movimentos = list_movimentos.dump(movimentos)
    return movimentos

def get_movimento(movimento_id):
    movimento = Movimento.find_by_id(movimento_id)

    if not movimento:
        return {"message": "movimento not found"}, 404
    movimento = movimento_schema.dump(movimento)
    
    return movimento

def post_movimento(data):
    movimento = movimento_schema.load(data)
    movimento.save_to_db()
    return movimento_schema.dump(movimento), 201


def update_movimento(movimento_id, data):
    movimento = Movimento.find_by_id(movimento_id)

    if not movimento:
        return {"message": "Movimento not found"}, 404
    for key, value in data.items():
        setattr(movimento, key, value)
    movimento.update_to_db()
    return movimento_schema.dump(movimento), 200

    
    

def delete_movimento(movimento_id):
    movimento = Movimento.find_by_id(movimento_id)

    if not movimento:
        return {"message": "Movimento not found"}, 404

    movimento.delete_from_db()
    return {"message": "Movimento deleted"}, 200

