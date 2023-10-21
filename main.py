from script import script_generator
from image import get_img
from audio import human_voice_generator, effect_generator, bgm_generator
from PIL import Image

def main(length: int, text: str, imgs: list[Image.Image], imgsDescription: list[str], gerne: str, dest: str) -> bool:
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
        title = sentences[0]["title"]
        titleKeywords = sentences[0]["keyword"]
        intro = sentences[0]["outline"][1]
        outro = sentences[0]["outline"][0] 

        print("Complete!", flush=True)

        print("Generating audio and images ... ", end='', flush=True)
        data = []
        # Generate title audio
        audio, length, timeStampes = human_voice_generator(title, titleKeywords, gerne, addEffect=False, reader="F1")
        data.append({
            "text": title,
            "length": length,
            "keywords": titleKeywords,
            "timeStamps": timeStampes,
            "image": None
        })
        # Generate intro audio
        _audio, length, timeStampes = human_voice_generator(intro, [], gerne) # No keywords
        audio += _audio
        data.append({
            "text": intro,
            "length": length,
            "keywords": None,
            "timeStamps": None,
            "image": None
        })
        # Generate content audio
        for setence in sentences[1:]:
            script = setence["script"]
            imageDescription = setence["imageDescription"]
            keywords = setence["keywords"]
            _audio, length, timeStampes = human_voice_generator(script, keywords, gerne)
            audio += _audio
            data.append({
                "text": script,
                "length": length,
                "keywords": keywords,
                "timeStamps": timeStampes,
                "image": get_img(imageDescription, imgs)
            })
        # Generate outro audio
        _audio, length, timeStampes = human_voice_generator(outro, [], gerne) # No keywords
        audio += _audio
        data.append({
            "text": outro,
            "length": length,
            "keywords": None,
            "timeStamps": None,
            "image": None
        })
        totalLength = len(audio)
        bgm = bgm_generator(gerne, totalLength)
        audio = audio.overlay(bgm, position=0)
        print("Complete!", flush=True)

        # Start producing video
        print("Generating video ... ", end='', flush=True)
        '''
        # Start to apply video editing here: 
        - audio: Final audio data
        - totalLength: The length of this audio data
        - data: Data of each sentence, which contains 
            - "text"
            - "length"
            - "keywords"
            - "timeStamps"
            - "images"
        '''

        print("Complete!")
        return True
    except ...:
        return False

length = 10
text = "在清華大學的梅竹黑客松，有超過100位學生參加。許多人都非常期待這次比賽的結果。"
imgsDescription = ["學生在電腦前認真編寫程式碼"]
gerne="科技"

main(length=length, text=text, imgsDescription=imgsDescription, gerne=gerne, imgs=["./temp.png"], dest="none")
