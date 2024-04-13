import requests
import time

api_key = "[Your Leonardo API Key here]"
authorization = "Bearer %s" % api_key

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": authorization
}

# Generate an image
url = "https://cloud.leonardo.ai/api/rest/v1/generations"

payload = {
    "height": 768,
    "modelId": "1e60896f-3c26-4296-8ecc-53e2afecc132",
    "prompt": "Golden hour photograph of family biking under a tree canopy near a location with Building Equipment Contractors in Maine in 2021.",
    "width": 1024,
    "num_images": 1,
    "alchemy": True
}

response = requests.post(url, json=payload, headers=headers)

print("Generate an image: %s" % response.status_code)

# Get the generation of images
generation_id = response.json()['sdGenerationJob']['generationId']

url = "https://cloud.leonardo.ai/api/rest/v1/generations/%s" % generation_id

time.sleep(60)

response = requests.get(url, headers=headers)

print("Get the generation of images: %s" % response.status_code)

image_id = response.json()['generations_by_pk']['generated_images'][0]['id']

# Create a variation of image (upscale variation)
url = "https://cloud.leonardo.ai/api/rest/v1/variations/upscale"

payload = {"id": image_id}

response = requests.post(url, json=payload, headers=headers)

variation_id = response.json()['sdUpscaleJob']['id']

print("Create a variation of image: %s" % response.status_code)

# Get the image variation
url = "https://cloud.leonardo.ai/api/rest/v1/variations/%s" % variation_id

time.sleep(100) # Original 60 second wait was not always enough

response = requests.get(url, headers=headers)

print("Get the image variation: %s" % response.status_code)

image_variation_id = response.json(
)['generated_image_variation_generic'][0]['id']

# Generate video with a generated image
url = "https://cloud.leonardo.ai/api/rest/v1/generations-motion-svd"

payload = {
    "imageId": image_variation_id,
    "motionStrength": 10,
    "isVariation": True,
}

response = requests.post(url, json=payload, headers=headers)

print("Generate video with a generated image: %s" % response.status_code)

# Get the generation of images
generation_id = response.json()['motionSvdGenerationJob']['generationId']

url = "https://cloud.leonardo.ai/api/rest/v1/generations/%s" % generation_id

time.sleep(60)

response = requests.get(url, headers=headers)

print(response.text)