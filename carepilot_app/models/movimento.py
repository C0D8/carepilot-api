from carepilot_app.extensions.db import db
from carepilot_app.models.cliente import Cliente
from carepilot_app.models.produto import Produto

class Movimento(db.Model) :
    __tabelname__ = "movimento"

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True, default=1)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=True, default=1)


    def json(self):
        return {"id": self.id, "valor": self.valor, "data": self.data, "descricao": self.descricao, "cliente_id": self.cliente_id, "produto_id": self.produto_id, "quantidade": self.quantidade}
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def find_by_cliente_id(cls, cliente_id):
        return cls.query.filter_by(cliente_id=cliente_id).all()
    
    @classmethod  
    def find_by_data(cls, data):
        return cls.query.filter_by(data=data).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    @classmethod
    def delete_all(cls):
        cls.query.delete()
        db.session.commit()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def update_to_db(self):
        db.session.commit()
