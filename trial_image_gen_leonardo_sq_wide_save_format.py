import streamlit as st
import requests
import base64
import time
import pandas as pd


github_token = st.secrets["github_token_leonardo"]
github_repository = "modelearth/requests"

# Function to generate images with specified aspect ratios
def generate_images(api_key, model_id, prompt, aspect_ratios):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    generation_ids = []
    for aspect_ratio in aspect_ratios:
        width, height = aspect_ratio
        data = {
            'height': height,
            'width': width,
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
                generation_ids.append(response_json['sdGenerationJob']['generationId'])
            else:
                st.error('Error in response for aspect ratio {}: {}'.format(aspect_ratio, response_json))
        else:
            st.error(f'Failed to generate images for aspect ratio {aspect_ratio}: HTTP Status Code {response.status_code}')
            st.json(response.json())
    
    return generation_ids

# Function to get the images
def get_images(api_key, generation_ids):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    
    image_urls = []
    for generation_id in generation_ids:
        while True:
            response = requests.get(
                f'https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}',
                headers=headers
            )
            if response.status_code == 200:
                response_json = response.json()
                if response_json['generations_by_pk']['status'] != 'PENDING':
                    if response_json['generations_by_pk']['generated_images']:
                        for img in response_json['generations_by_pk']['generated_images']:
                            image_urls.append(img['url'])
                        break
                    else:
                        st.error('No images found for generation ID {}'.format(generation_id))
                        break
                else:
                    time.sleep(10)
            else:
                st.error(f'Failed to fetch images for generation ID {generation_id}: HTTP Status Code {response.status_code}')
                st.json(response.json())
                break
    
    return image_urls

# Function to save the image to GitHub
def save_image_to_github(image_content, filename, repo_name, path_in_repo, commit_message, github_token):
    url = f"https://api.github.com/repos/{repo_name}/contents/{path_in_repo}/{filename}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "message": commit_message,
        "content": base64.b64encode(image_content).decode('utf-8'),
        "branch": "main",
    }
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success("Image successfully uploaded to GitHub.")
    else:
        st.error(f"Failed to upload image: {response.content}")

# Streamlit interface
st.title('Image Generation with Leonardo AI')

# Fetch the API key and model ID from secrets.toml or directly (as an example)
api_key = "915fb846-4ab0-4349-b535-bf45e1fbc613"
model_id = "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"

# Reading prompts from CSV file
df = pd.read_csv("ME-prompts-2021.csv")  # Replace with your CSV file path
df['Display Prompt'] = df['Prompt'].str.replace("--no signage", "").str.strip()
prompt_options = df['Display Prompt'].tolist()

# Sidebar for prompt selection
st.sidebar.title("Choose Your Prompt")
selected_display_prompt = st.sidebar.selectbox('', prompt_options, index=0, help="Select a prompt from the list")

# Fetching the actual prompt
selected_row = df[df['Display Prompt'] == selected_display_prompt]
prompt = selected_row['Prompt'].values[0]
naics_value = selected_row['Naics'].values[0]  # If applicable
first_five_words = "-".join(prompt.split()[:5])

aspect_ratios = [(512, 512), (1224, 512)]  # Example aspect ratios

if st.button('Generate Image'):
    with st.spinner('Generating images...'):
        generation_ids = generate_images(api_key, model_id, prompt, aspect_ratios)
        if generation_ids:
            st.success('Image generation initiated successfully!')
            with st.spinner('Fetching the generated images...'):
                image_urls = get_images(api_key, generation_ids)
                if image_urls:
                    for i, url in enumerate(image_urls):
                        st.image(url)
                        img_data = requests.get(url).content
                        # Adjusted filename format
                        filename = f"ME-Naics-{naics_value}-{first_five_words}_{i}.jpeg"
                        save_image_to_github(
                            img_data,
                            filename,
                            github_repository,
                            "images/leonardo",
                            "Upload generated image",
                            github_token
                        )
                else:
                    st.error('No images were found or an error occurred.')
        else:
            st.error('Image generation failed.')