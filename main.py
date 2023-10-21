from script import script_generator
from image import get_img
from audio import audio_generator, bgm_generator
from pathlib import Path
import sys
import os

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
    
    try:
        # Generate scipt to read
        print("Generating script ... ", flush=True, end='')
        sentences = script_generator(text, length, imgsDescription)

        print("Complete!", flush=True)

        print(sentences)

        print("Generating audio and images ... ", flush=True)
        before_sysout = sys.stdout

        # Create folder if not exist
        if not Path('./audio_result').exists():
            os.mkdir(Path('./audio_result'))
        # Parallelly create audios
        ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords = audio_generator(sentences, gerne)

        # Create images
        ListOfImage = []
        ListOfImageReal = []
        print(" - Generating Images ... ", flush=True, end='')
        for s in sentences:
            if s["imageDescription"]:
                img, r = get_img(s["imageDescription"], imgs)
                ListOfImage.append(img)
                ListOfImageReal.append(r)
        
        assert len(ListOfImage) == len(ListOfAudio) - 2, "The number of images and sentences are not matched"
        print("Done!", flush=True)

        # Create data
        print(" - Generating Data Lists ... ", flush=True, end='')
        data = []
        for i in range(len(ListOfAudio)):
            if i < 2: 
                image, imageReal = ListOfImage[0], ListOfImageReal[0]
            elif i == len(ListOfAudio)-1:
                image, imageReal = ListOfImage[-1], ListOfImageReal[-1]
            else:
                image, imageReal = ListOfImage[i-1], ListOfImageReal[-1]
            data.append({
                "text": ListOfText[i],
                "length": ListOfLength[i],
                "keywords": ListOfKeywords[i],
                "timeStamps": ListOfTimeStampes[i],
                # First sentence and second sentence is title and intro, they share the same image
                "image": image,
                "imageReal": imageReal 
            })
        print("Done!", flush=True)

        print(" - Merging audio with bgm ... ", flush=True, end='')
        # Merge audio
        audio = ListOfAudio[0]
        for a in ListOfAudio[1:]:
            audio += a
    
        # Generate bgm
        totalLength = len(audio)
        bgm = bgm_generator(gerne, totalLength)
        audio = audio.overlay(bgm, position=0)
        print("Done!", flush=True)

        sys.stdout = before_sysout
        print("Complete!", flush=True)

        audio.export("./result.wav", format="wav")

        # Start producing video
        # print("Generating video ... ", flush=True)
        '''
        # Start to apply video editing here: 
        - audio: Final audio data
        - totalLength: The length of this audio data
        - data: Data of each sentence, which contains 
            - "text"
            - "length"
            - "keywords"
            - "timeStamps"
            - "image"
            - "imageReal"
        '''
        i = 0
        for d in data:
            print(d["text"])
            if d["image"] != None and not isinstance(d["image"], str):
                d["image"].save(f"./temp{i}.png")
                i += 1
        # print("Complete!", flush=True)
        return True
    except ...:
        return False

length = 10
text = "在清華大學的梅竹黑客松，有超過100位學生參加。許多人都非常期待這次比賽的結果。"
imgsDescription = ["學生在電腦前認真編寫程式碼"]
gerne="科技"

main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=["./temp.png"], dest="none")
