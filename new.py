from flask import Flask,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

app=Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS']=True
app.config['JWT_SECRET_KEY']=''
app.config['PREFERRED_URL_SCHEME']=''
api=Api(app)
jwt=JWTManager(app)
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'error': 'authorization_required',
        "description": "Request does not contain an access token."
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'invalid_token',
        'message': 'Signature verification failed.'
    }), 401

api.add_resource(Adminlogin,'/Adminlogin')
api.add_resource(Safe,'/safe')

if __name__ == "__main__":
    app.run(debug=True)