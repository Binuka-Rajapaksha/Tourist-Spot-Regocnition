from keras.models import load_model
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input
import numpy as np

# Load the trained model
model = load_model("C:/Users/rmdmc/OneDrive/Desktop/Study Materials/2nd Year/DSGP/Model/tourist_places_model_03.keras")

# Function to preprocess an image for prediction
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
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


# Load and preprocess a new image for testing

# img_path = "ZAM_1577.JPG"

img_path = 'UMS Dataset/Chancellor Hall/ZAM_1400.JPG'
# img_path = 'UMS Dataset/Chancellor Tower/ZAM_1883.JPG'
# img_path = 'UMS Dataset/Clock Tower/ZAM_1244.JPG'
# img_path = 'UMS Dataset/Colorfull Stairway/ZAM_1346.JPG'
# img_path = 'UMS Dataset/DKP Baru/ZAM_1980.JPG'
# img_path = 'UMS Dataset/Library/ZAM_1559.JPG'
# img_path = 'UMS Dataset/Recital Hall/ZAM_1660.JPG'
# img_path = 'UMS Dataset/UMS Aquarium/ZAM_1784.JPG'
# img_path = 'UMS Dataset/UMS Mosque/ZAM_2102.JPG'


predicted_class = predict_class(img_path)

# Map the predicted class index to the class label
class_labels = [
    "Chancellor Hall", "Chancellor Tower", "Clock Tower",
    "Colorful Stairway", "DKP Baru", "Library",
    "Recital Hall", "UMS Aquarium", "UMS Mosque"
]

predicted_label = class_labels[predicted_class]
print(f"The predicted class is: {predicted_label}")
