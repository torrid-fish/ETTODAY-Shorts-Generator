# ettoday_shorts_generator

## Structure

- `main.py`
    - The entrance into our system, will finally generate a "shorts" video

- `audio.py`
    - Functions regarding audio
    - `human_voice_generator(text, keywords, gerne, addEffect, advance, speed, reader:)`
    - `bgm_generator(gerne, length)`
- `/bgm`
    - The bgm list
- `/effect`
    - The sound effect list
- `/audio_result`
    - Store generated audio result
- `script.py`
    - The function that will generate the script for TTS
    - `script_generator(text, length, imgsDescription)`
- `image.py`
    - The fun tions that will generate image
    - `get_img(imgDescription)`
    - `picture_generator(imageDescription)`
## Dependencies
Please check `requirement.txt`.

Use `pip install requirement.txt` to install those dependencies.

```
Yating-TTS-SDK==0.1.2
pydub==0.25.1
aiohttp==3.8.6 
aiosignal==1.3.1 
async-timeout==4.0.3 
frozenlist==1.4.0 
multidict==6.0.4 
openai==0.28.1 
yarl==1.9.2
requests==2.26.0
```
> You also need to install `ffmpeg` to edit audio (pydub relies on it):

```
apt-get install ffmpeg
```

## Done List
- Basic audio processing
- Script generator
- Image Done (Generate image)
- Main function merged (half)

## Todo List
The are few things that we must complete:
- Apply video editing based on what we have
- Merge the front end with main function

There are few things that we might be able to imporve:
- Use threads to speed up API querying
- Use neural network to choose proper sound effect
- Use neural network to choose proper bgm

