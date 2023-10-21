from script import script_generator
from image import get_img
from audio import multithread_audio_generator, bgm_generator
import PIL

def main(length: int, text: str, imgs: list[str], imgsDescription: list[str], gerne: str, dest: str) -> bool:
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
        print("Generating script ... ", end='', flush=True)
        sentences = script_generator(text, length, imgsDescription)

        print(sentences)

        print("Complete!", flush=True)

        print("Generating audio and images ... ", end='', flush=True)
        # Parallelly create audios
        ListOfAudio, ListOfLength, ListOfTimeStampes, ListOfText, ListOfKeywords = multithread_audio_generator(sentences)

        # Create images
        ListOfImage = []
        ListOfImageReal = []
        for s in sentences:
            if s["imageDescription"]:
                img, r = get_img(s["imageDescription"])
                ListOfImage.append(img)
                ListOfImageReal.append(r)

        # Create data
        data = []
        for i in range(len(ListOfAudio)):
            data.append({
                "text": ListOfText[i],
                "length": ListOfLength[i],
                "keywords": ListOfKeywords[i],
                "timeStamps": ListOfTimeStampes[i],
                # First sentence and second sentence is title and intro, they share the same image
                "image": ListOfImage[i-1] if i >= 2 else ListOfImage[0], 
                "imageReal": ListOfImageReal[i-1] if i >= 2 else ListOfImageReal[0] 
            })

        # Merge audios
        audio = ListOfAudio[0]
        for a in ListOfAudio[1:]:
            audio += a
    
        # Generate bgm
        totalLength = len(audio)
        bgm = bgm_generator(gerne, totalLength)
        audio = audio.overlay(bgm, position=0)

        print("Complete!", flush=True)

        # Start producing video
        # print("Generating video ... ", end='', flush=True)
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
        # print("Complete!")
        return True
    except ...:
        return False

length = 10
text = "在清華大學的梅竹黑客松，有超過100位學生參加。許多人都非常期待這次比賽的結果。"
imgsDescription = ["學生在電腦前認真編寫程式碼"]
gerne="科技"

main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=["./temp.png"], dest="none")
