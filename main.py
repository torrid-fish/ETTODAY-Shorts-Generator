from video import video_generator, generate_requirements
from pathlib import Path
import os
import sys
import json
from pydub import AudioSegment
from PIL import Image

def move_cursor(row, col):
    sys.stdout.write("\x1b[{};{}H".format(row, col))
    sys.stdout.flush()

def preserve(data, audio):
    # Preserve
    if not Path('./preserve').exists():
        os.mkdir('./preserve')
    else:
        os.system("rm preserve/*")

    audio.export("./preserve/audio.wav", format="wav")

    if not Path('./preserve/imgs').exists():
        os.mkdir('./preserve/imgs')
    else: 
        os.system("rm preserve/imgs/*")
    idx = 0
    for d in data:
        img = d["image"]
        p = f'./preserve/imgs/photo{idx}.jpg'
        img.save(p)
        d["image"] = p
        idx += 1

    with open("./preserve/data.txt", "w") as f:
        json.dump(data, f, indent=4)

def load():
    audio = AudioSegment.from_file('./preserve/audio.wav')
    with open("./preserve/data.txt", "r") as f:
        data = json.load(f)

    idx = 0
    for d in data:
        p = d["image"]
        d["image"] = Image.open(p)
        idx += 1

    return data, audio

def main(length: int, text: str, imgs: list, imgsDescription: list[str], gerne: str, dest: str) -> bool:
    """
    ## Args
    - length: The length of the video.
    - text: The text of the news.
    - imgs: The list of string represents path to those images that are used in the news.
    - imgsDescription: The list of string that describe the images.
    - gerne: What type of the news it is.
    - dest: The destination path of the output videos.
    ## Return
    - (bool): Whether the video is successfully generated.
    """
    os.system('')  # start VT-100 in windows console
    try:
        # Generate requirements
        data, audio = generate_requirements(length, text, imgs, imgsDescription, gerne)
    
        # Preserve files
        # preserve(data, audio)

        # data, audio = load()

        # Start to generate video
        video_generator(data, dest, audio)

        return True
    except ...:
        return False
    