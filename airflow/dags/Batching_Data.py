import requests #to make a request acces for scrapping 
import numpy as np #to make an array/slice
import pandas as pd #to manipulate data
import urllib
import urllib.request
from urllib.request import urlopen
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from msedge.selenium_tools import Edge, EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options
import openpyxl
import boto3
from tensorflow.keras.models import model_from_json
from joblib import load
from requests_toolbelt.multipart.encoder import MultipartEncoder

options = EdgeOptions()
options.use_chromium = True  # Use Chromium-based Edge
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-logging') 
# Set the page load timeout to 10 seconds
options.set_capability("pageLoadStrategy", "eager")
options.set_capability("unhandledPromptBehavior", "accept")

driver = Edge(EdgeChromiumDriverManager().install(), options=options)

url = "https://www.huntstreet.com/shop/all/{}?type={}&page={}"

Photos = []

category = ['bags', 'shoes', 'accessories', 'clothing', 'beauty']

for categories in category:
    for sub_categories in (range(1,3)):
        for pages in (range(1,2)):
            driver.get(url.format(categories, sub_categories, pages))
            # time.sleep(2)
            try:
                for index in range(1,3):
                    photo = driver.find_element(by=By.XPATH, value=f'//*[@id="v-product-list"]/div[2]/div[4]/div[{index}]/div[1]/div/a/img').get_attribute('src')
                    Photos.append(photo)
            except:
                continue
driver.quit()

# Load the model architecture from JSON
with open("C:/Users/bobse/Downloads/Dibimbing-AI & ML Bootcamp/Final Project/streamlit/model/sub_category_model.json", "r") as json_file:
    model_json = json_file.read()

# Load the model
model = model_from_json(model_json)

# Load the model weights
model.load_weights("C:/Users/bobse/Downloads/Dibimbing-AI & ML Bootcamp/Final Project/streamlit/model/sub_category_model.h5")

# Load the label encoder
label_encoder = load("C:/Users/bobse/Downloads/Dibimbing-AI & ML Bootcamp/Final Project/streamlit/model/label_encoder.pkl")

# Set your DigitalOcean Spaces credentials
access_key = 'DO00DWEELX2ZDW7WBPV6'
secret_key = '/thlL+garnLLrdOoAaR70WlyYsUzIxPybF7yGAjLz48'
endpoint_url = 'https://image-bucket-finalproject.sgp1.digitaloceanspaces.com'
space_name = 'image-bucket-finalproject'
folder_name = 'sub-category'

# Create a client for Spaces
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, endpoint_url=endpoint_url)

for photo in Photos:
    image_name = photo.split('/')[-1]  # Extract the image file name
    image_data = urllib.request.urlopen(photo).read()  # Read image data from URL

    # Upload image to the bucket
    s3.put_object(Bucket=space_name, Key=f"{folder_name}/{image_name}", Body=image_data)

    # Make a request to the FastAPI endpoint for prediction
    image_data = {'file': ('filename', photo, 'image/jpeg')}
    image_multipart = MultipartEncoder(fields=image_data)
    headers = {'Content-Type': image_multipart.content_type}
    response = requests.post('http://127.0.0.1:8001/classify/',
                                data=image_multipart,
                                headers=headers,
                                timeout=60)
    
    if response.status_code == 200:
        prediction = response.json()
        predicted_class = prediction['prediction']
        print(f"Image: {image_name}, Predicted Class: {predicted_class}")
    else:
        print(f"Error processing image: {image_name}")