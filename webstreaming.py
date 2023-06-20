
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 03:45:25 2020

@author: Prasun
"""

from packages import social_distancing_config as config
from packages.Object_detection import detect_people
from scipy.spatial import distance as dist
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import numpy as np
import imutils
import cv2
import requests
import os
from flask import Flask,render_template,Response, flash, redirect, request
from flask import Flask,jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from api import Adminlogin, User, UnSafe, Register, UserLogin, Admin
from flask_jwt_extended import create_access_token,jwt_required
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
api.add_resource(UnSafe,'/unsafe')
api.add_resource(Register, '/Register')
api.add_resource(UserLogin, '/UserLogin')

app.config['SECRET_KEY'] = ''

db = SQLAlchemy(app)
migrate = Migrate(app, db)

p=''
r=''
context=''
app.config.from_object(Config)


labelsPath =os.path.sep.join([config.MODEL_PATH,"coco.names"])
LABELS =open(labelsPath).read().strip().split("\n")

weightsPath =os.path.sep.join([config.MODEL_PATH,"yolov3.weights"])

configPath= os.path.sep.join([config.MODEL_PATH,"yolov3.cfg"])
print("[INFO] loading YOLO from disk")
net =cv2.dnn.readNetFromDarknet(configPath,weightsPath)

if config.USE_GPU:
	net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
	net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
ln =net.getLayerNames()
ln = [ln[i-1]for i in net.getUnconnectedOutLayers()]
print("[INFO] accesing video stream")

vs =cv2.VideoCapture(r"pedestrian.mp4"if "pedestrian.mp4"else 0)
global writer
writer =None

@app.route("/hello")
def home():
    # global p
    # if(p):
    data = requests.get("http://127.0.0.1:5000/unsafe") 
    res = data.json()
    # if(p==''):
    # return redirect('loginpage')
    #     else:
    global context
    context={'data': res} 
    # else:
    #     return redirect('loginpage')
    return render_template("index1.html", context=context)
@app.route("/hi")
def hi():
    return render_template("index.html")

@app.route('/communications/')
def communications():
    return render_template('base1.html', value=max1)

@app.route('/socialdistancing/')
def index():
    return render_template('base.html')
def gen():
    global max1
    max1=0
    i=0
    while(i<20):
        (grabbed,frame) = vs.read()
        if not grabbed:
            break
        frame = imutils.resize(frame,width =700)
        results =detect_people(frame,net,ln,personIdx=LABELS.index("person"))
        violate =set()
        if len(results)>=2:
            centroids = np.array([r[2] for r in results])
            D = dist.cdist(centroids,centroids,metric="euclidean")
    
            for i in range(0,D.shape[0]):
                for j in range(i+1,D.shape[1]):
                    if D[i,j]<config.MIN_DISTANCE:
                        violate.add(i)
                        violate.add(j)
        for(i,(prob,bbox,centroid)) in enumerate(results):
            (startX,startY,endX,endY)=bbox
            (cX,cY)= centroid
            color =(0,255,0)
        
            if i in violate:
                color = (0,0,255)
            cv2.rectangle(frame,(startX,startY),(endX,endY),color,2)
            cv2.circle(frame,(cX,cY),5,color,1)
        text ="Social Distancing Violations: {}".format(len(violate))
        max1= max(max1, len(violate))
        cv2.putText(frame,text,(10,frame.shape[0]-25),cv2.FONT_HERSHEY_SIMPLEX,0.85,(0,0,255),3)
        cv2.imwrite("1.jpg",frame)
        (flag,encodedImage) =cv2.imencode(".jpg",frame)
        yield(b' --frame\r\n' b'Content-Type:image/jpeg\r\n\r\n'+bytearray(encodedImage)+b'\r\n')
        i=i+1

@app.route('/loginpage', methods=["GET", "POST"])
def loginpage() :
   if (request.method)=="POST":
       userid=request.form.get('userid') 
       passw=request.form.get('passw')
       global r 
       global p
       global context
       try:
        r = requests.post('http://127.0.0.1:5000/Adminlogin',data={'userid':userid,'passw':passw})
        p= r.json()['access_token']
        return render_template('index1.html' , context=context)
       except KeyError:
        return render_template( "login.html")

   return render_template( "login.html")


    
@app.route('/signup')
def signup():
    return render_template('indexrecent.html')


    

@app.route('/video_feed')
def video_feed():
	return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__== '__main__':
     app.run(debug =True)
     #vs.release()
     #cv2.destroyAllWindows()


    