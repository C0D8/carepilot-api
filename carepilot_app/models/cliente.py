from carepilot_app.extensions.db import db


class Cliente(db.Model) :
    __tabelname__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    movimentos = db.relationship('Movimento', backref='cliente', lazy=True)
                                 
    def json(self):
        return {"id": self.id, "nome": self.nome, "cpf": self.cpf, "data_nascimento": self.data_nascimento}
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def update_to_db(self):
        db.session.commit()
