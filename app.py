from flask import Flask , render_template

from flask import request, redirect,Response , url_for, jsonify

from flask import Flask , render_template

from flask import request, redirect,Response , url_for
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import tensorflow as tf
import os
from tensorflow.keras.models import load_model
from PIL import Image

#import cv2
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///db.sqlite3"

app.config['UPLOAD_FOLDER_FLOWER'] = './static/imagedata/flower'
alzmodel=load_model('models/flower.h5')
alzmodel.summary()
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
with app.app_context():
    db.create_all()

ALLOWED_EXTENSIONS = {'webp', 'jpg', 'jpeg', 'gif', 'svg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Flower(db.Model):
    __tablename__= 'flower'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True,nullable = False)
    image = db.Column(db.String)
    target = db.Column(db.String)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods = ["GET"])
def predict():
    if request.method =="GET":
        return render_template("predict.html")
    if request.method =="POST":
        return render_template("predict.html")

@app.route("/result", methods = ["GET","POST"])
def result():
    if request.method =="GET":
        return render_template("result.html")
    if request.method =="POST":
        data = db.session.query(Flower).all()
        a = str(data[-1].id)
        a = int(a)+1
        print(request.files)
        file = request.files['photo']
        person_name =  'abc'
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            ext = filename.split(".")[-1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER_FLOWER'], str(a)+"."+ext))
            
            image_path = os.path.join(app.config['UPLOAD_FOLDER_FLOWER'], str(a)+"."+ext)
            image = Image.open(image_path)

            # Preprocess the image
            img = image.resize((224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)

            # Make predictions
            predictions = alzmodel.predict(img_array)
            class_labels = ['Bougainvillea',
                            'Bright Eyes',
                            'Cape Jasmine',
                            'Chandni',
                            'Dhalia',
                            'Hibiscus',
                            'Marigold',
                            'Pink Oleander',
                            'Rose',
                            'Tecoma']
            score = tf.nn.softmax(predictions[0])
            print(score)
            print(predictions)
            accuracy = round(max(predictions[0])*100,2)
            print(accuracy)
            max_index = np.array(predictions).argmax()
            target = class_labels[max_index]
            data = Flower(image = str(a)+"."+ext, target = target)
            db.session.add(data)
            db.session.commit()
            text = '<h4 class="result-s">'+ target+ '</h4>'
            print(text)
            imagename = str(a)+"."+ext
            return render_template("result.html", accuracy = accuracy,text = target,image_name = image_path)

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
  app.run(host = '0.0.0.0',debug = True,port = 8080)