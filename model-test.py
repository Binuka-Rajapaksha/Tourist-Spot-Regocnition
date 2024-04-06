from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from sentiment import preprocessing, vectorizer, get_prediction
from logger import logging
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import numpy as np
import os
import MySQLdb
import re

app = Flask(__name__)

logging.info('Flask server started')

# MySQL connection parameters
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = ''  
mysql_database = 'userdb'  


# Load the trained model
model_path = 'E:\InceptionV3_final.keras'
model = load_model(model_path)


# Function to preprocess an image for prediction
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(512, 512))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array


# Function to make predictions with thresholding
def predict_class(image_path, threshold=0.85):
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array)

    # Get the class with the highest probability
    predicted_class = np.argmax(predictions, axis=1)

    # Get the maximum confidence score
    max_confidence = np.max(predictions)

    # Check if the maximum confidence is below the threshold
    if max_confidence < threshold:
        return -1
    else:
        return predicted_class[0]


# Map the predicted class index to the class label
class_labels = ['Abhayagiriya', 'Adam_s Peak', 'Colombo Municipal Council', 'Colombo National Museum',
                'Galle Light House', 'Gampola Kingdom_s Ambuluwawa Tower', 'Lotus Tower', 'Maligawila Buddha Statue',
                'Nine Arch Bridge', 'Polonnaruwa watadageya', 'Ranmasu Uyana', 'Jami Ul-Alfar Mosque', 'Ruwanwelisaya',
                'Sigiriya Rock', 'Sri Dalada Maligawa', 'Thuparamaya Dagaba']


@app.route('/')
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:

        email = request.form['email']
        password = request.form['password']

        try:
            # Establish a connection to the MySQL server
            with MySQLdb.connect(host=mysql_host, user=mysql_user, password=mysql_password,
                                 database=mysql_database) as connection:
                # Create a cursor object to execute queries
                with connection.cursor() as cursor:

                    cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))

                    user = cursor.fetchone()

                    if user:
                        message = 'Logged in successfully !'
                        return render_template('Index.html', message=message)
                    else:
                        message = 'Invalid email / password !'

        except MySQLdb.Error as e:
            # Handle MySQL errors
            print(f"Error accessing MySQL: {e}")
            message = "Error accessing MySQL"

    print(message)

    return render_template('login.html', message=message)


@app.route('/Sign_up.html', methods=['GET', 'POST'])
def register():
    signup_message = ''
    if request.method == 'POST' and 'user_name' in request.form and 'password' in request.form and 'email' in request.form:
        user_name = request.form['user_name']
        password = request.form['password']
        email = request.form['email']

        try:
            # Establish a connection to the MySQL server
            with MySQLdb.connect(host=mysql_host, user=mysql_user, password=mysql_password,
                                 database=mysql_database) as connection:
                # Create a cursor object to execute queries
                with connection.cursor() as cursor:
                    # Check if the email already exists in the database
                    cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
                    account = cursor.fetchone()

                    if account:
                        signup_message = 'Account already exists !'
                    elif not user_name or not password or not email:
                        signup_message = 'Please fill out the form !'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        signup_message = 'Invalid email address !'

                    else:
                        # Insert the new user into the database
                        cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s)', (user_name, email, password,))
                        connection.commit()
                        signup_message = 'You have successfully registered !'
                        return render_template('Index.html', message=signup_message)
        except MySQLdb.Error as e:
            # Handle MySQL errors
            print(f"Error accessing MySQL: {e}")
            signup_message = "Error accessing MySQL"

    elif request.method == 'POST':
        signup_message = 'Please fill out the form !'

    return render_template('Sign_up.html', message=signup_message)


@app.route('/Index.html')
def home():
    return render_template('Index.html')


@app.route('/explorer.html')
def index():
    return render_template('explorer.html')


@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'result': 'No image provided'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'result': 'No image selected'})

    # Save the image temporarily
    img_path = 'temp_image.jpg'
    file.save(img_path)

    try:
        # Predict the class with thresholding
        predicted_class = predict_class(img_path)

        if predicted_class == -1:
            return jsonify({'result': 'Unknown place'})

        predicted_label = class_labels[predicted_class]
        return jsonify({'result': predicted_label})

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({'result': 'Error processing image'})

    finally:
        # Remove the temporary image file
        os.remove(img_path)


# Global variables for Sentiment Analysis
data = dict()
reviews = []
positive = 0
negative = 0

# Function for Sentiment Analysis
@app.route("/reviews_sentiment", methods=['POST']) 
def reviews_sentiment():
    text = request.json['text']
    logging.info(f'Text : {text}')

    preprocessed_txt = preprocessing(text)
    vectorized_txt = vectorizer(preprocessed_txt)
    prediction = get_prediction(vectorized_txt)

    if prediction == 'negative':
        global negative
        negative += 1
    else:
        global positive
        positive += 1

    reviews.insert(0, text)
    logging.info(f'All Negative: {negative} All Positive:{positive}')
    
    # Return sentiment counts along with the response
    return jsonify({'positive': positive, 'negative': negative})


# Function to Get the no of Positive Reviews
@app.route("/get_global_positive_count", methods=['GET'])
def get_global_positive_count():
    global positive
    return jsonify({'positive_count': positive})

# Function to Clear Global Variables
@app.route("/clear_global_variables", methods=['POST'])
def clear_global_variables():
    global positive, negative, reviews
    positive = 0
    negative = 0
    reviews = []
    logging.info('Global variables cleared')
    return jsonify({'message': 'Global variables cleared'})


if __name__ == '__main__':
    app.run(debug=False)
