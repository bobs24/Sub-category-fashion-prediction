import streamlit as st
import requests
from PIL import Image
from requests_toolbelt.multipart.encoder import MultipartEncoder
import io

# Streamlit UI
st.title('Sub-Category Prediction')
uploaded_file = st.file_uploader('Upload an image file', type=['jpg', 'jpeg', 'png'])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    if st.button('Predict'):
        # Make a request to the FastAPI endpoint for prediction
        image_data = {'file': ('filename', uploaded_file, 'image/jpeg')}
        image_multipart = MultipartEncoder(fields=image_data)
        headers = {'Content-Type': image_multipart.content_type}
        response = requests.post('http://host.docker.internal:8001/classify/',
                                 data=image_multipart,
                                 headers=headers,
                                 timeout=60)
        
        # Display the prediction result or error message
        if response.status_code == 200:
            prediction = response.json()
            st.write('Predicted sub-category:', prediction['prediction'])
        else:
            st.error(f'Failed to make prediction: {response.text}')
            # Log the error message
            with open('error.log', 'a') as f:
                f.write(f'Failed to make prediction: {response.text}\n')