from werkzeug.security import check_password_hash
from carepilot_app.models.user import User



def auth_login(data):

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Invalid request. username and password hash are required."}, 400

    user = User.query.filter_by(username=username).first()
    print(user)

    if user and check_password_hash(user.password, password):
        return {"message": "Login successful"}, 200
    else:
        return {"message": "Invalid credentials"}, 401
    
def auth_roles(username):
    user = User.query.filter_by(username=username).first()
    if user:
        roles = user.roles
        id_vendedor = user.id
        return {"roles": [role.name for role in roles], 'id_vendedor' : id_vendedor}, 200
    else:
        return {"message": "User not found"}, 404