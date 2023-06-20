from flask_restful import Resource,reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token,jwt_required
from db import query
class Adminlogin(Resource):#admin login
    parser=reqparse.RequestParser()
    parser.add_argument('userid',type=int,required=True,help="Admin userid cannot be left blank!")
    parser.add_argument('passw',type=str,required=True,help="Password cannot be left blank!")
    
    def post(self):
        data=self.parser.parse_args()
        admin=Admin.getAdminById(data['userid'])
        if admin and safe_str_cmp(admin.passw,data['passw']):
            access_token=create_access_token(identity=admin.userid,expires_delta=False)
            return {'access_token':access_token},200
        return {"message":"Invalid Credentials!"}, 401
class Admin():
    def __init__(self,userid,passw):
        self.userid=userid
        self.passw=passw
    @classmethod
    def getAdminById(cls,userid):
        result=query(f"""select userid,passw from admin where userid='{userid}'""",return_json=False)
        if len(result)>0:
            return Admin(result[0]['userid'],result[0]['passw'])
        else:
            return None

class User():
    def __init__(self,userid,passw):
        self.userid=userid
        self.passw=passw
    @classmethod
    def getUserById(cls,userid):
        result=query(f"""select userid,passw from Users where userid='{userid}'""",return_json=False)
        if len(result)>0:
            return User(result[0]['userid'],result[0]['passw'])
        else:
            return None

class UnSafe(Resource):
    # @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        try:
            return query(f"""SELECT * FROM Unsafe;""")
        except:
            return {"message":"There has been an error retrieving unsafe areas"},500
        return {"message":"Unsafe areas retrieved succesfully."}

# class InsertUnsafe(Resource):
    

class Register(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('userid',type=int,required=True,help="Admin userid cannot be left blank!")
        parser.add_argument('passw',type=str,required=True,help="Password cannot be left blank!")
        parser.add_argument('LastName',type=str,required=True,help="Last Name cannot be left blank!")
        parser.add_argument('FirstName',type=str,required=True,help="First Name cannot be left blank!")
        parser.add_argument('Areas',type=str,required=True,help="Areas cannot be left blank!")
        parser.add_argument('email',type=str,required=True,help="safe cannot be left blank!")
        data=parser.parse_args()
        if User.getUserById(data['userid']):
                return {"message": "A user with that id already exists"}, 400
        try:
            query(f"""INSERT INTO Users
                                    VALUES('{data['userid']}','{data['passw']}','{data['LastName']}','{data['FirstName']}','{data['Areas']}', '{data['email']}')""")
        except:
            return {"message": "An error occurred while registering."}, 500
        return {"message": "User created successfully."}, 201

class UserLogin(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('userid',type=str,required=True,help="ID cannot be blank.")
    parser.add_argument('passw',type=str,required=True,help="Password cannot be blank.")
    def post(self):
        data=self.parser.parse_args()
        user=User.getUserById(data['userid'])
        if user and safe_str_cmp(user.passw,data['passw']):
            access_token=create_access_token(identity=user.userid,expires_delta=False)
            return {'access_token':access_token},200
        return {"message":"Invalid Credentials!"}, 401




    
