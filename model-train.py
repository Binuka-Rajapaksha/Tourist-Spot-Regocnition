from keras.preprocessing.image import ImageDataGenerator
from keras.applications.inception_v3 import InceptionV3
from keras.layers import GlobalAveragePooling2D, Dense
from keras.models import Model
from keras.optimizers import Adam

# Data augmentation for training set
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2  # 80% for training, 20% for validation
)

# Load the dataset
dataset_path = 'C:/Users/rmdmc/OneDrive/Desktop/Study Materials/2nd Year/DSGP/Data Set/UMS Dataset'

# training set
train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(299, 299),
    batch_size=16,
    class_mode='categorical',
    subset='training'  # Specify the subset as 'training' for the training set
)

# Validation set
validation_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(299, 299),
    batch_size=16,
    class_mode='categorical',
    subset='validation'  # Specify the subset as 'validation' for the validation set
)


# Base InceptionV3 model
base_model = InceptionV3(weights='imagenet', include_top=False)

# Additional layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)

# Add a fully connected layer with softmax activation
predictions = Dense(9, activation='softmax')(x)

# Create the final model
model = Model(inputs=base_model.input, outputs=predictions)

# Freeze the layers of the base model
for layer in base_model.layers:
    layer.trainable = False

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# Train the Model
model.fit(train_generator, epochs=10, steps_per_epoch=len(train_generator), validation_data=validation_generator,
          validation_steps=len(validation_generator))


# Save the Model
# model.save('C:/Users/rmdmc/OneDrive/Desktop/Study Materials/2nd Year/DSGP/Model/tourist_places_model_03.keras')