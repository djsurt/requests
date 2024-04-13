import streamlit as st
import requests

# Function to generate images
def generate_images(api_key, model_id, prompt):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'height': 512,
        'width': 512,
        'modelId': model_id,
        'prompt': prompt,
    }
    
    response = requests.post(
        'https://cloud.leonardo.ai/api/rest/v1/generations',
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        response_json = response.json()
        if 'sdGenerationJob' in response_json and 'generationId' in response_json['sdGenerationJob']:
            return response_json['sdGenerationJob']['generationId']
        else:
            st.error('The expected keys "sdGenerationJob" and/or "generationId" were not found in the response.')
            st.json(response_json)  # This will print the entire JSON response in the app
            return None
    else:
        st.error(f'Failed to generate images: HTTP Status Code {response.status_code}')
        st.json(response.json())  # This will print the entire JSON response in the app
        return None

# Function to get the images
import time

def get_images(api_key, generation_id):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    
    # Polling for the completion of image generation
    while True:
        response = requests.get(
            f'https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}',
            headers=headers
        )
        if response.status_code == 200:
            response_json = response.json()
            # Check if the generation is still pending
            if response_json['generations_by_pk']['status'] != 'PENDING':
                # Assuming the image URLs will be in the 'generated_images' key once completed
                if response_json['generations_by_pk']['generated_images']:
                    image_urls = [img['url'] for img in response_json['generations_by_pk']['generated_images']]
                    return image_urls
                else:
                    st.error('The image generation is completed, but no images were found.')
                    return None
            else:
                # If still pending, wait for some time before the next check
                time.sleep(10)  # Wait for 10 seconds before rechecking
        else:
            st.error(f'Failed to fetch images: HTTP Status Code {response.status_code}')
            st.json(response.json())  # This will print the entire JSON response in the app
            return None


# Streamlit interface
st.title('Image Generation with Leonardo AI')

api_key = st.text_input('Enter your Leonardo AI API key', type='password')
model_id = st.text_input('Enter the model ID')
prompt = st.text_input('Enter your prompt for image generation')

if st.button('Generate Image'):
    if not api_key or not model_id or not prompt:
        st.warning('Please fill in all the fields.')
    else:
        with st.spinner('Generating images...'):
            generation_id = generate_images(api_key, model_id, prompt)
            if generation_id:
                st.success('Image generated successfully!')
                with st.spinner('Fetching the generated image...'):
                    image_urls = get_images(api_key, generation_id)
                    if image_urls:
                        for url in image_urls:
                            st.image(url)
                    else:
                        st.error('No images were found or an error occurred.')
            else:
                st.error('Image generation failed.')
