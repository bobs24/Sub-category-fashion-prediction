from airflow.utils.dates import days_ago
from airflow.models.connection import Connection
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import requests #to make a request acces for scrapping 
import numpy as np #to make an array/slice
import pandas as pd #to manipulate data
import urllib
import urllib.request
from urllib.request import urlopen
import selenium
import pytz
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from msedge.selenium_tools import Edge, EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import openpyxl
import os
import io
import boto3
from tensorflow.keras.models import model_from_json
from joblib import load
from requests_toolbelt.multipart.encoder import MultipartEncoder

load_dotenv()

def batching_data():
    options = webdriver.ChromeOptions()
    options.use_chromium = True  # Use Chromium-based Edge
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-logging') 
    # Set the page load timeout to 10 seconds
    options.set_capability("pageLoadStrategy", "eager")
    options.set_capability("unhandledPromptBehavior", "accept")

    remote_webdriver = 'remote_chromedriver'
    driver = webdriver.Remote(f'{remote_webdriver}:4444/wd/hub', options=options)

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
    with open(os.getenv("weight_model"), "r") as json_file:
        model_json = json_file.read()

    # Load the model
    model = model_from_json(model_json)

    # Load the model weights
    model.load_weights(os.getenv("model_cnn"))

    # Load the label encoder
    label_encoder = load(os.getenv("label_encoder"))

    # Set your DigitalOcean Spaces credentials
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")
    endpoint_url = os.getenv("endpoint_url")
    space_name = os.getenv("space_name")
    folder_name = os.getenv("folder_name")

    # Create a client for Spaces
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, endpoint_url=endpoint_url)

    for photo_url in Photos:
        image_name = photo_url.split('/')[-1]  # Extract the image file name

        # Read image data from URL
        image_data = urllib.request.urlopen(photo_url).read()

        # Create a file-like object from the image data
        # image_file = io.BytesIO(image_data)

        image_data = {'file': (image_name, image_data, 'image/jpeg')}
        image_multipart = MultipartEncoder(fields=image_data)
        headers = {'Content-Type': image_multipart.content_type}

        # Make the POST request
        response = requests.post(os.getenv("fastapi_post"),
                                    data=image_multipart,
                                    headers=headers,
                                    timeout=60)
        
        print(response.text)  # Print the response text

args = {
    'owner': 'Bob Sebastian',
    #'depends_on_past': False,
    'start_date': datetime(2023,2,7, tzinfo=pytz.timezone('Asia/Jakarta')),
    # 'start_date':datetime(2023,2,7),
    # 'email': ['bob@voila.id','bobsebastian1997@gmail.com'],
    # 'email_on_failure': True,
    # 'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(seconds=20),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    'execution_timeout': timedelta(seconds=600),
    'on_failure_callback': batching_data
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
        }

with DAG(dag_id="Batching_Data", 
     schedule_interval="10,40 * * * *", catchup=False, tags=["Final","Project"], default_args=args) as dag: 
     #schedule_interval pake UTC default postgreSQL bukan UTC+7 Jakarta,
     #makanya kalau ngasih schedule_interval harus -7 (contoh "*/10 2-12 * * *" 
     # berarti akan jalan di jam 9-20 setiap 10 menit)
    
    Batching_Data = PythonOperator(task_id='Scrapping',
                    python_callable=batching_data,
                    dag=dag)
    
    Batching_Data