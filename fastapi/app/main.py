import asyncpg
import asyncio
from fastapi import FastAPI, File, UploadFile
from tensorflow.keras.models import model_from_json
from joblib import load
import cv2
import numpy as np
from datetime import datetime, timedelta
import boto3

app = FastAPI()

# Load the model architecture from JSON
with open("app/model/sub_category_model.json", "r") as json_file:
    model_json = json_file.read()

# Load the model
model = model_from_json(model_json)

# Load the model weights
model.load_weights("app/model/sub_category_model.h5")

# Load the label encoder
label_encoder = load("app/model/label_encoder.pkl")

# Set your DigitalOcean Spaces credentials
access_key = 'DO00DWEELX2ZDW7WBPV6'
secret_key = '/thlL+garnLLrdOoAaR70WlyYsUzIxPybF7yGAjLz48'
endpoint_url = 'https://image-bucket-finalproject.sgp1.digitaloceanspaces.com'
space_name = 'image-bucket-finalproject'
folder_name = 'sub-category'

# Create a client for Spaces
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, endpoint_url=endpoint_url)

# Function to preprocess an image
def preprocess_image(file):
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    resized_img = cv2.resize(img, (128, 128))
    normalized_img = resized_img / 255.0
    processed_img = np.expand_dims(normalized_img, axis=0)
    return processed_img

# Create a connection pool
async def get_pool():
    return await asyncpg.create_pool(
        user='postgres',
        password='Dakota123',
        database='final_project',
        host='128.199.252.10'
    )

# Decorator for handling POST request to /classify
@app.post("/classify/")
async def classify_image(file: UploadFile = File(...)):
    try:
        # Preprocess the image
        img_array = preprocess_image(file.file)

        # Get a connection pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            prediction = model.predict(img_array)
            predicted_class = label_encoder.inverse_transform([np.argmax(prediction)])[0]

            # Insert input and output data into PostgreSQL database
            await conn.execute("INSERT INTO database_prediction (image, prediction, datetime) VALUES ($1, $2, $3)",
                               f"{endpoint_url}/{space_name}/{folder_name}/{file.filename}", 
                               predicted_class, 
                               datetime.now() + timedelta(hours=14))

        # Upload image to DigitalOcean Spaces
        image_data = await file.read()  # Read image data
        s3.put_object(Bucket=space_name, Key=f"{folder_name}/{file.filename}", Body=image_data, ACL='public-read')

        return {"prediction": predicted_class}

    except Exception as e:
        print(f"Error processing request: {e}")
        return {"error": "Internal Server Error"}