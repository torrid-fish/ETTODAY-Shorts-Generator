from yating_tts_sdk import YatingClient as ttsClient
from concurrent.futures import ThreadPoolExecutor, wait
from pydub.generators import Sine
from pydub import AudioSegment
from pathlib import Path
from random import randint
import os
import time
import glob
import re

URL = "https://tts.api.yating.tw/v1/speeches/short"
KEY = "49e96b51964d290aa6fec7e220372a3fe84bd928"

def speed_change(sound, speed=1.0):
    rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
      })
    return rate.set_frame_rate(sound.frame_rate)


def effect_generator(gerne: str, keyword: str) -> str:
    """
    ## Args
    - gerne: What type of the news it is.
    - keyword: What keyword the sound effect applys on.
    ## Return
    - path2Sound: The path to the sound effect.
    """

    # Strategy 0: Use random assignment
    effects = glob.glob(f"./effect/*") 
    path2Sound = effects[randint(0, len(effects)-1)]

    return path2Sound

defult_speed = 1.5
def human_voice_generator(text: str, keywords: list, gerne: str, fileName: str, addEffect = True, advance = 0, speed = 1.5, reader: str = 'M') -> tuple[AudioSegment, int, list]:
    """
    ## Args
    - text: A script that only contains one sentence.
    - keywords: A list of keywords, will later be used to specified the location appears in the sentence.
    - gerne: The gerne of this news.
    - addBeep: Debugging function. Whether add beep on top of the sound.
    - advance: How many millisecond should the timestamp shift forward.
    - speed: The speed of the audio.
    - reader: The type of the reader. 'F1' 'F2' stand for MODEL_FEMALE_1, MODEL_FEMALE_1, `M` stands for MODEL_MALE_1.
    ## Return
    - AudioSegment: Generated audio segment.
    - length: The length of the voice. (In milisecond)
    - keywordsTimeStamp (list[int]): The list of timestamp. (In milisecond)
    """
    path2Voice = './audio_result/' + fileName

    # Set up the call to Yating TTS
    textType = ttsClient.TYPE_TEXT
    if reader[0] == 'F': # Female
        model = ttsClient.MODEL_FEMALE_1 if reader[1] == '1' else ttsClient.MODEL_FEMALE_2
    else: # Male
        model = ttsClient.MODEL_MALE_1
    encoding = ttsClient.ENCODING_LINEAR16
    sampleRate = ttsClient.SAMPLE_RATE_16K

    # Send request and create file
    client = ttsClient(URL, KEY)
    client.synthesize(text, textType, model, encoding, sampleRate, path2Voice)

    # Calculate lengths
    time.sleep(0.1) # Wait for the wav file to be completely stored
    # Load generated wav
    sound = AudioSegment.from_file(path2Voice+'.wav', format='wav')

    # Speed up
    rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
      })
    sound = rate.set_frame_rate(sound.frame_rate)

    length = len(sound) # Return the length of generated audio, in millisecond

    #########################################################################
    # Current Strategy: Directly compute based on the position of each char #
    #########################################################################   
    keywordsTimeStamp = []
    for key in keywords:
        if not key: continue # key might be empty ['']
        idx = text.find(key[0])
        timeStamp = int(length * idx / len(text) - advance)
        if addEffect:
            effect = AudioSegment.from_file(effect_generator(gerne, key))
            timeStamp -= max(0, timeStamp + len(effect) - length) # Last effect might exceed boundary
            sound = sound.overlay(effect, position=timeStamp)
        keywordsTimeStamp.append(timeStamp)
    #########################################################################

    # Sanity Check
    assert len(keywords) == len(keywordsTimeStamp), "Keywords lengths didn't match"
    
    # Return
    return sound, length, keywordsTimeStamp

def bgm_generator(gerne: str, length: str) -> AudioSegment:
    """
    ## Args
    - gerne: What type of the news it is.
    - length: The total length of the desired bgm.
    ## Return
    - path2Bgm: The path to the bgm.
    """
    path2Bgm = './audio_result/generated_bgm.wav'

    # Temporary only use news.wav to generate
    sound = AudioSegment.from_file('./bgm/news.wav', format='wav')

    # Reuse the clip and create enough length
    if length > len(sound):
        num = int(length / len(sound)) + 1
        sound = sound * num
    
    sound = sound[:length]
    
    sound -= 10 # Reduce 10dB
    # Fadein/out
    sound = sound.fade_in(1000)
    sound = sound.fade_out(1000)

    time.sleep(0.5)
    return sound


def audio_generator(sentences, gerne, singleThread=False):
    title = sentences[0]["title"]
    outro, intro = sentences[0]["outline"]
    
    ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords = [], [], [], [], []
    # Create ListOfText
    ListOfText.append(title)
    ListOfText.append(intro)
    for s in sentences[1:]: ListOfText.append(s["script"])
    ListOfText.append(outro)
    # Create ListOfKeywords
    ListOfKeywords.append(sentences[0]["keywords"])
    ListOfKeywords.append([])
    for s in sentences[1:]: ListOfKeywords.append(s["keywords"])
    ListOfKeywords.append([])

    assert len(ListOfKeywords) == len(ListOfText) and len(sentences) + 2 == len(ListOfText), "The length is not match."

    # Sigle Thread
    if singleThread:
        print(" - [Single Thread] Generating audio ... ", flush=True, end='')
        audio, length, timeStampes = human_voice_generator(ListOfText[0], ListOfKeywords[0], gerne, '0', addEffect=False, reader="F1")
        ListOfAudio.append(audio)
        ListOfLength.append(length)
        ListOfTimeStampes.append(timeStampes)
        for i in range(1, len(ListOfText)):
            audio, length, timeStampes = human_voice_generator(ListOfText[i], ListOfKeywords[i], gerne, str(i))
            ListOfAudio.append(audio)
            ListOfLength.append(length)
            ListOfTimeStampes.append(timeStampes)
    
    # Parallel generating audio
    else:
        print(" - [Multiple Threads] Generating audio ... ", flush=True, end='')
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            futures.append(executor.submit(human_voice_generator, ListOfText[0], ListOfKeywords[0], gerne, '0', addEffect=False, reader="F1"))

            for i in range(1, len(ListOfText)):
                futures.append(executor.submit(human_voice_generator, ListOfText[i], ListOfKeywords[i], gerne, str(i)))

        wait(futures)    
        
        for f in futures:
            audio, length, timeStampes = f.result()
            ListOfAudio.append(audio)
            ListOfLength.append(length)
            ListOfTimeStampes.append(timeStampes)

    print("Done!")

    return ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords