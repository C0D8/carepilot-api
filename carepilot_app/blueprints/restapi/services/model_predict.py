from carepilot_app.extensions.db import db

from carepilot_app.models.movimento import Movimento









def predict(cliete_info):


    movimento = Movimento.query.filter_by(cliente_id=cliete_info['cliente_id']).first()

    if movimento is None:
        return 0
    