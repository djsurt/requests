import streamlit as st
import pandas as pd
import replicate
import base64
import requests
import io
from PIL import Image

# UI configurations
st.set_page_config(page_title="Replicate Image Generator based on CSV Input", page_icon="🌟")

# API Tokens and endpoints from `.streamlit/secrets.toml` file
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["REPLICATE_MODEL_ENDPOINTSTABILITY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPOSITORY = "modelearth/requests"

# Function to convert the image to JPEG
def convert_to_jpeg(image_content):
    """
    Convert image content to JPEG format.
    """
    image = Image.open(io.BytesIO(image_content))
    with io.BytesIO() as output_stream:
        image.save(output_stream, format="JPEG")
        return output_stream.getvalue()

# Function to save the image to GitHub
def save_image_to_github(image_content, filename, repo_name, path_in_repo, commit_message, github_token):
    """
    Saves an image to GitHub repository.
    """
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

def main():
    # Sidebar with CSV prompt selection
    df = pd.read_csv("OR-prompts-2021.csv")
    df['Display Prompt'] = df['Prompt'].str.replace("--no signage", "").str.strip()
    options = df['Display Prompt'].tolist()
    st.sidebar.title("Choose Your Prompt")
    selected_display_prompt = st.sidebar.selectbox('', options, index=0, help="Select a prompt from the list")

    # Main area
    st.title("Replicate AI Image Generator")
    st.markdown("### Transform your ideas into stunning visuals!")
    
    if st.button('Generate Image', key='generate'):
        with st.spinner('🧚‍♂️ Creating magic...'):
            try:
                selected_row = df[df['Display Prompt'] == selected_display_prompt]
                selected_prompt = selected_row['Prompt'].values[0]
                naics_value = selected_row['Naics'].values[0]
                first_five_words = "-".join(selected_prompt.split()[:5])

                # Loop for generating images in specified aspect ratios
                for ratio, dimensions, suffix in [("square", (1024, 1024), "sq"), ("horizontal", (1792, 896), "wide")]:
                    output = replicate.run(
                        REPLICATE_MODEL_ENDPOINTSTABILITY,
                        input={
                            "prompt": selected_prompt,
                            "width": dimensions[0],
                            "height": dimensions[1],
                            "num_outputs": 1
                        }
                    )

                    if output:
                        response = requests.get(output[0])
                        if response.status_code == 200:
                            jpeg_content = convert_to_jpeg(response.content)
                            filename = f"OR-Naics-{naics_value}-{first_five_words}_{suffix}.jpg"
                            commit_message = "Add generated image"
                            save_image_to_github(
                                jpeg_content, 
                                filename, 
                                GITHUB_REPOSITORY, 
                                "images", 
                                commit_message, 
                                GITHUB_TOKEN
                            )
                            st.image(output[0], caption=f"Generated Image - {ratio}", use_column_width=True)
                        else:
                            st.error(f"Failed to fetch the generated image for saving. Status code: {response.status_code}")
            except Exception as e:
                st.error(f'Encountered an error: {e}')

if __name__ == "__main__":
    main()