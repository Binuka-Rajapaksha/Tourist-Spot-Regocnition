from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import numpy as np
import os
import MySQLdb
import re

app = Flask(__name__)

# MySQL connection parameters
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = ''  # If you didn't change the default password, just put ''
mysql_database = 'userdb'  # Name of the database


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
                'Nine Arch Bridge', 'Polonnaruwa watadageya', 'Ranmasu Uyana', 'Red Mosque', 'Ruwanwelisaya',
                'Sigiriya Rock', 'Temple of Tooth Relic', 'Thuparamaya Dagaba']


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
                        message = 'Please enter correct email / password !'

        except MySQLdb.Error as e:
            # Handle MySQL errors
            message = f"Error accessing MySQL: {e}"

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
            signup_message = f"Error accessing MySQL: {e}"

    elif request.method == 'POST':
        signup_message = 'Please fill out the form !'

    return render_template('Sign_up.html', message=signup_message)


@app.route('/Index.html')
def home():
    return render_template('Index.html')


@app.route('/explorer.html/')
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
        return jsonify({'result': 'Error processing image'})

    finally:
        # Remove the temporary image file
        os.remove(img_path)


if __name__ == '__main__':
    app.run(debug=False)
