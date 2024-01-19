from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import numpy as np
import os

app = Flask(__name__)

# Load the trained model
model_path = 'C:/Users/rmdmc/OneDrive/Desktop/Study Materials/2nd Year/DSGP/Model/tourist_places_model_02.keras'
model = load_model(model_path)


# Function to preprocess an image for prediction
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(299, 299))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array


# Function to make predictions
def predict_class(image_path):
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array)
    # Get the class with the highest probability
    predicted_class = np.argmax(predictions, axis=1)
    return predicted_class[0]


# Map the predicted class index to the class label
class_labels = [
    "Chancellor Hall", "Chancellor Tower", "Clock Tower",
    "Colorful Stairway", "DKP Baru", "Library",
    "Recital Hall", "UMS Aquarium", "UMS Mosque"
]


@app.route('/')
def index():
    return render_template('index_2.html')


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
        # Predict the class
        predicted_class = predict_class(img_path)
        predicted_label = class_labels[predicted_class]

        return jsonify({'result': predicted_label})

    except Exception as e:
        return jsonify({'result': 'Error processing image'})

    finally:
        # Remove the temporary image file
        os.remove(img_path)


if __name__ == '__main__':
    app.run(debug=True)
