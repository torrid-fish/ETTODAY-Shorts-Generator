import requests
from PIL import Image
from io import BytesIO
import openai
import os

def picture_generator(imageDescription: str) -> Image:
    """
    Generate an image based on the provided description using the OpenAI API.

    ## Args
    - imageDescription: The description of the desired image.

    ## Return
    - (Image): Return an image with class Image (PIL).
    """
    # 定義您的OpenAI API金鑰
    API_KEY = '<YOUR OPENAPI API KEY>'
    openai.api_key = API_KEY

    #Translate to English
    response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=f"Translate the following text into English: {imageDescription}\n",
    max_tokens=60,
    n=1,
    stop=None,
    temperature=0.7, )
    imgDescription = response.choices[0].text.strip()
    message = imgDescription
    size = "512x512"

    # 發送請求
    r = requests.post(
    "https://api.deepai.org/api/text2img",
    data={
        'text': message,
        'grid_size': '1',
    },
    headers={'api-key': '<YOUR DEEPAI API KEY>'},
    )

    image_url = r.json()["output_url"]
    #image_url = response.data[0].url
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))
    return img

def get_img(imgDescription: str, imgs) -> Image:
    if imgDescription[:3] == "img":
        img = imgs[int(imgDescription[3:])]
        return img, True
    else:
        return picture_generator(imgDescription), False
