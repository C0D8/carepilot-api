from carepilot_app.extensions.db import db
# from carepilot_app.models.movimento import Movimento



class Produto(db.Model) :
    __tabelname__ = "produto"

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=True)
    descricao = db.Column(db.String(255), nullable=True)
    tipo = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def json(self):
        return {"id": self.id, "valor": self.valor, "data": self.data, "descricao": self.descricao, "tipo": self.tipo}
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
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
