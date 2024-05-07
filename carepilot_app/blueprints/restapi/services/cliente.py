from carepilot_app.extensions.db import db #noqa
from carepilot_app.models.cliente import Cliente
from carepilot_app.schemas.cliente import ClienteSchema

list_clientes = ClienteSchema(many=True)
cliente_schema = ClienteSchema()


def get_clientes():
    clientes = Cliente.find_all()
    clientes = list_clientes.dump(clientes)
    return clientes


def get_cliente(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404
    cliente = cliente_schema.dump(cliente)
    return cliente

def post_cliente(data):
    cliente = cliente_schema.load(data)
    cliente.save_to_db()
    return cliente_schema.dump(cliente), 201


def update_cliente(cliente_id, data):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404
    for key, value in data.items():
        setattr(cliente, key, value)
    cliente.update_to_db()
    return cliente_schema.dump(cliente), 200

    
    

def delete_cliente(cliente_id):
    cliente = Cliente.find_by_id(cliente_id)

    if not cliente:
        return {"message": "Cliente not found"}, 404

    cliente.delete_from_db()
    return {"message": "Cliente deleted"}, 200

