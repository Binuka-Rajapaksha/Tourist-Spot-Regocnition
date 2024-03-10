from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import numpy as np
import os

app = Flask(__name__)

# Load the trained model
model_path = 'C:/Users/rmdmc/OneDrive/Desktop/Study Materials/2nd Year/DSGP/Model/Our Dataset/InceptionV3_model02.keras'
model = load_model(model_path)


# Function to preprocess an image for prediction
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(299, 299))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array


# Function to make predictions with thresholding
def predict_class(image_path, threshold=0.75):
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
class_labels = ['Adam_s Peak', 'Bentota Beach', 'Clock Tower Jaffna', 'Clock Tower Kandy', 'Colombo National Museum',
                'Dematamal Viharaya', 'Galle Light House', 'Gampola Kingdom_s Ambuluwawa Tower', 'Hikkaduwa Beach',
                'Lotus Tower', 'Maligawila Buddha Statue', 'Mirissa Beach', 'Negombo Beach', 'Nine Arch Bridge',
                'Pidurangala Rock', 'Ranmasu Uyana', 'Ravana Falls', 'Ruwanwelisaya', 'Sigiriya Rock', 'Thuparamaya Dagaba']


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
