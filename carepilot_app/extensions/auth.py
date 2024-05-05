from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from carepilot_app.models.user import User


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user


@auth.get_user_roles
def get_user_roles(user):
    roles = User.query.filter_by(username=user.username).first().roles
    return [role.name for role in roles]

