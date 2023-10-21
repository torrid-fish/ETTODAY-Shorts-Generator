# ettoday_shorts_generator

## Structure

- `./main.py`
    - The entrance into our system, will finally generate a "shorts" video
- `./audio.py`
    - Functions regarding audio
    - `human_voice_generator()`
    - `effect_generator()`
    - `bgm_generator()`
- `/bgm`
    - The bgm list
- `/effect`
    - The sound effect list
- `audio_result`
    - Store generated audio result
- script.py
    - The function that will generate the script for TTS
    - `script_generator()`
- image.py
    - The fun tions that will generate image

## Dependencies
Please check `requirement.txt`.

Use `pip install requirement.txt` to install those dependencies.

```
Yating-TTS-SDK==0.1.2
pydub==0.25.1
```
> You also need to install `ffmpeg` to edit audio (pydub relies on it):

```
apt-get install ffmpeg
```

## Done List
- Basic audio processing
- Script generator
- Image (Still processing...)
## Todo List
The are few things that we must complete:
- Merge all functions

There are few things that we might be able to imporve:
- Use threads to speed up API querying
- Use neural network to choose proper sound effect
- Use neural network to choose proper bgm

